from __future__ import annotations

import logging
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import (
    User, Profile, Preferences, ApplicationProfile, Resume,
    JobListing, JobMatch, Application, ApplicationEvent,
    AutomationTask, Notification, CreditBalance
)
from app.services.matching_engine import match_job_for_user
from app.services.credit_service import (
    check_has_sufficient_credits,
    deduct_credit_for_application,
    refund_credit_for_application,
)
from app.services.browser_executor import BrowserExecutor

logger = logging.getLogger(__name__)


class UserAutomationController:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.is_running = False
        self.is_paused = False
        self.stop_requested = False
        self.thread: Optional[threading.Thread] = None
        self.current_action = "Idle"
        self.current_executor: Optional[BrowserExecutor] = None

        # Live session metrics
        self.jobs_discovered = 0
        self.jobs_analyzed = 0
        self.jobs_matched = 0
        self.eligible_applications = 0
        self.applications_submitted = 0
        self.verification_required = 0
        self.login_required = 0
        self.failed = 0

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self.stop_requested = False
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def pause(self) -> None:
        self.is_paused = True
        self.current_action = "Paused"

    def resume(self) -> None:
        self.is_paused = False
        self.current_action = "Resuming..."

    def stop(self) -> None:
        self.stop_requested = True
        self.is_running = False
        self.is_paused = False
        self.current_action = "Stopping..."
        if self.current_executor:
            try:
                self.current_executor.close()
            except Exception:
                pass
            self.current_executor = None

    def _run_loop(self) -> None:
        logger.info(f"Starting automation loop for user {self.user_id}")
        db = SessionLocal()
        try:
            self._execute_pipeline(db)
        except Exception as e:
            logger.error(f"Automation pipeline error for user {self.user_id}: {e}", exc_info=True)
            self.failed += 1
        finally:
            self.is_running = False
            self.current_action = "Completed"
            if self.current_executor:
                try:
                    self.current_executor.close()
                except Exception:
                    pass
                self.current_executor = None
            db.close()

    def _execute_pipeline(self, db: Session) -> None:
        # 1. Fetch user data
        user = db.query(User).filter(User.id == self.user_id).first()
        if not user:
            return

        profile = user.profile
        preferences = user.preferences
        app_profile = user.application_profile
        active_resume = db.query(Resume).filter(Resume.user_id == self.user_id, Resume.is_active == True).first()

        if not preferences:
            self.current_action = "Error: Job preferences not configured"
            return

        # 2. Discovery Phase
        self.current_action = "Discovering matching jobs from portals..."
        roles = preferences.preferred_roles or ["Software Engineer", "AI Engineer"]
        locations = preferences.preferred_locations or ["India"]

        # Run real portal discovery for the user's preferred roles and locations
        try:
            self.current_action = f"Searching live portals for {', '.join(roles[:2])}..."
            from app.services.portal_job_discovery import discover_real_jobs_for_criteria
            discovered_results = discover_real_jobs_for_criteria(
                roles=roles,
                locations=locations,
                limit=25,
                headless=True,
            )
            for res in discovered_results:
                existing = db.query(JobListing).filter(JobListing.url == res.url).first()
                if not existing:
                    new_job = JobListing(
                        source=res.source,
                        external_id=res.url.split("/")[-1][:64],
                        url=res.url,
                        title=res.title,
                        company=res.company,
                        location=res.location,
                        description=res.snippet or f"Live {res.title} opportunity at {res.company}.",
                        raw_data={"discovered_source": res.source},
                    )
                    db.add(new_job)
            db.commit()
        except Exception as disc_err:
            logger.warning(f"Live portal discovery notice: {disc_err}")

        # Fetch real candidate jobs for matching (excluding test fixtures)
        candidate_jobs = (
            db.query(JobListing)
            .filter(
                ~JobListing.url.ilike("%example.com%"),
                ~JobListing.url.ilike("%127.0.0.1%"),
            )
            .order_by(JobListing.created_at.desc())
            .limit(30)
            .all()
        )

        self.jobs_discovered = len(candidate_jobs)

        # 3. Matching Phase
        self.current_action = "Analyzing and matching jobs against resume..."
        for job in candidate_jobs:
            if self.stop_requested:
                break
            while self.is_paused and not self.stop_requested:
                time.sleep(1)

            # Match
            match_res = match_job_for_user(job, preferences, profile, active_resume)
            self.jobs_analyzed += 1

            # Save / Update JobMatch
            existing_match = (
                db.query(JobMatch)
                .filter(JobMatch.user_id == self.user_id, JobMatch.job_id == job.id)
                .first()
            )
            if not existing_match:
                existing_match = JobMatch(
                    user_id=self.user_id,
                    job_id=job.id,
                    match_score=match_res.match_score,
                    relevance=match_res.relevance,
                    matched_skills=match_res.matched_skills,
                    missing_skills=match_res.missing_skills,
                    reason=match_res.reason,
                    apply_decision=match_res.apply_decision,
                )
                db.add(existing_match)
            else:
                existing_match.match_score = match_res.match_score
                existing_match.relevance = match_res.relevance
                existing_match.matched_skills = match_res.matched_skills
                existing_match.missing_skills = match_res.missing_skills
                existing_match.reason = match_res.reason
                existing_match.apply_decision = match_res.apply_decision

            db.commit()

            if match_res.apply_decision:
                self.jobs_matched += 1

        # 4. Application Submission Phase
        self.current_action = "Processing eligible job applications..."
        matched_records = (
            db.query(JobMatch)
            .filter(
                JobMatch.user_id == self.user_id,
                JobMatch.apply_decision == True,
            )
            .all()
        )

        for match in matched_records:
            if self.stop_requested:
                break
            while self.is_paused and not self.stop_requested:
                time.sleep(1)

            job = db.query(JobListing).filter(JobListing.id == match.job_id).first()
            if not job:
                continue

            # Duplicate protection check
            existing_app = (
                db.query(Application)
                .filter(Application.user_id == self.user_id, Application.job_id == job.id)
                .first()
            )
            if existing_app and existing_app.status in {"submitted", "ready_to_submit", "already_applied"}:
                continue

            # Credit check
            if not check_has_sufficient_credits(db, self.user_id):
                self.current_action = "Paused: Credits exhausted. Please add credits to continue."
                notif = Notification(
                    user_id=self.user_id,
                    type="credit_exhausted",
                    title="Application Credits Exhausted",
                    message="Your available application credits have run out. Please purchase credits to resume automation.",
                )
                db.add(notif)
                db.commit()
                break

            self.eligible_applications += 1

            # Create or update application record
            if not existing_app:
                existing_app = Application(
                    user_id=self.user_id,
                    job_id=job.id,
                    resume_id=active_resume.id if active_resume else None,
                    status="application_started",
                    stage="initializing",
                    match_score=match.match_score,
                )
                db.add(existing_app)
                db.commit()
                db.refresh(existing_app)

            # Record event
            event = ApplicationEvent(
                application_id=existing_app.id,
                user_id=self.user_id,
                status="application_started",
                stage="preparing",
                message=f"Agent preparing application for {job.title} at {job.company}",
            )
            db.add(event)
            db.commit()

            # Deduct credit
            try:
                deduct_credit_for_application(db, self.user_id, existing_app.id)
            except Exception as e:
                logger.warning(f"Credit deduction failed: {e}")
                continue

            self.current_action = f"Executing application for {job.title} at {job.company}..."

            # Execute with user-scoped BrowserExecutor
            answers_dict = {}
            if app_profile:
                answers_dict = {
                    "country": "India",
                    "disability": app_profile.disability_status,
                    "notice_period": f"{app_profile.notice_period_days} days",
                    "work_authorization": app_profile.work_authorization,
                    "expected_salary": f"₹{app_profile.expected_salary_lpa} LPA",
                }
                if app_profile.custom_answers:
                    answers_dict.update(app_profile.custom_answers)

            resume_file_path = active_resume.file_path if active_resume else None

            # Prepare Candidate package for executor
            candidate_package = {
                "job": {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "url": job.url,
                    "match_score": match.match_score,
                },
                "candidate": {
                    "name": profile.first_name + " " + profile.last_name if profile else "Candidate",
                    "first_name": profile.first_name if profile else "Candidate",
                    "last_name": profile.last_name if profile else "",
                    "email": user.email,
                    "phone": profile.phone if profile else "",
                    "headline": profile.headline if profile else "",
                    "education": profile.education if profile else "",
                    "notice_period_days": app_profile.notice_period_days if app_profile else 15,
                },
                "matched_skills": match.matched_skills or [],
                "application_pitch": f"I am a skilled engineer with expertise in {', '.join((match.matched_skills or [])[:3])}. I look forward to contributing to {job.company}.",
                "requires_human_review": preferences.require_human_review,
            }

            executor = None
            try:
                # 1. Human review gate check
                if preferences.require_human_review:
                    existing_app.status = "needs_human_review"
                    existing_app.stage = "review_gate"
                    db.add(ApplicationEvent(
                        application_id=existing_app.id,
                        user_id=self.user_id,
                        status="needs_human_review",
                        stage="review_gate",
                        message="Application drafted and held for human review gate per user settings.",
                    ))
                    db.commit()
                    continue

                # 2. Launch real isolated BrowserExecutor
                self.current_action = f"Opening {job.title} at {job.company} in browser..."
                executor = BrowserExecutor(
                    user_id=self.user_id,
                    headless=True,
                    resume_path=resume_file_path,
                    application_answers=answers_dict,
                )
                self.current_executor = executor

                open_res = executor.open_application(job.url)
                if open_res.status in {"failed", "blocked"}:
                    msg_lower = (open_res.message or "").lower()
                    if any(term in msg_lower for term in ("verification", "captcha", "security", "cloudflare", "challenge")):
                        self.verification_required += 1
                        existing_app.status = "verification_required"
                        existing_app.stage = "security_challenge"
                    elif any(term in msg_lower for term in ("login", "sign in", "auth")):
                        self.login_required += 1
                        existing_app.status = "login_required"
                        existing_app.stage = "auth_gate"
                    else:
                        self.failed += 1
                        existing_app.status = "failed"
                    existing_app.error_message = open_res.message
                    db.add(ApplicationEvent(
                        application_id=existing_app.id,
                        user_id=self.user_id,
                        status=existing_app.status,
                        stage=existing_app.stage,
                        message=open_res.message or "Could not open application page.",
                    ))
                    refund_credit_for_application(db, self.user_id, existing_app.id, reason=open_res.message or "Open failed")
                    db.commit()
                    continue

                db.add(ApplicationEvent(
                    application_id=existing_app.id,
                    user_id=self.user_id,
                    status="opened",
                    stage="navigation",
                    message=f"Application page opened: {open_res.message}",
                ))
                db.commit()

                # 3. Fill Form
                self.current_action = f"Filling application fields for {job.company}..."
                fill_res = executor.fill_application(candidate_package)

                # Check for login inputs or filling challenges
                req_inputs = " ".join(fill_res.required_fields_needing_input or []).lower()
                if any(k in req_inputs for k in ("password", "session_key", "session_password", "sign in", "login")):
                    self.login_required += 1
                    existing_app.status = "login_required"
                    existing_app.stage = "auth_gate"
                    existing_app.error_message = "Portal requires user login credentials to proceed."
                    db.add(ApplicationEvent(
                        application_id=existing_app.id,
                        user_id=self.user_id,
                        status="login_required",
                        stage="auth_gate",
                        message="Login wall detected: credentials required for this portal.",
                    ))
                    refund_credit_for_application(db, self.user_id, existing_app.id, reason="Login required")
                    db.commit()
                    continue

                if fill_res.status in {"failed", "blocked"}:
                    msg_lower = (fill_res.message or "").lower()
                    if any(term in msg_lower for term in ("verification", "captcha", "security", "cloudflare")):
                        self.verification_required += 1
                        existing_app.status = "verification_required"
                        existing_app.stage = "security_challenge"
                    elif any(term in msg_lower for term in ("login", "sign in")):
                        self.login_required += 1
                        existing_app.status = "login_required"
                        existing_app.stage = "auth_gate"
                    else:
                        self.failed += 1
                        existing_app.status = "failed"
                    existing_app.error_message = fill_res.message
                    db.add(ApplicationEvent(
                        application_id=existing_app.id,
                        user_id=self.user_id,
                        status=existing_app.status,
                        stage=existing_app.stage,
                        message=fill_res.message or "Form filling challenge encountered.",
                    ))
                    refund_credit_for_application(db, self.user_id, existing_app.id, reason=fill_res.message or "Fill failed")
                    db.commit()
                    continue

                db.add(ApplicationEvent(
                    application_id=existing_app.id,
                    user_id=self.user_id,
                    status="form_filling",
                    stage="filling",
                    message=fill_res.message or "Candidate details, pitch, and questions filled.",
                ))
                if resume_file_path:
                    db.add(ApplicationEvent(
                        application_id=existing_app.id,
                        user_id=self.user_id,
                        status="resume_uploaded",
                        stage="upload",
                        message=f"Uploaded candidate resume: {active_resume.filename if active_resume else 'resume.pdf'}",
                    ))
                db.commit()

                # 4. Submit application
                self.current_action = f"Submitting application to {job.company}..."
                submit_res = executor.submit_application(candidate_package)

                if submit_res.status == "submitted":
                    existing_app.status = "submitted"
                    existing_app.stage = "completed"
                    existing_app.submitted_at = datetime.utcnow()
                    db.add(ApplicationEvent(
                        application_id=existing_app.id,
                        user_id=self.user_id,
                        status="submitted",
                        stage="submission_verified",
                        message="Application successfully submitted and verified in live browser session.",
                    ))
                    db.commit()
                    self.applications_submitted += 1

                    db.add(Notification(
                        user_id=self.user_id,
                        type="application_submitted",
                        title="Application Submitted",
                        message=f"Successfully applied to {job.title} at {job.company}.",
                        metadata_json={"job_id": job.id, "application_id": existing_app.id},
                    ))
                    db.commit()
                else:
                    msg_lower = (submit_res.message or "").lower()
                    if any(term in msg_lower for term in ("verification", "captcha", "security", "cloudflare")):
                        self.verification_required += 1
                        existing_app.status = "verification_required"
                        existing_app.stage = "security_challenge"
                    elif any(term in msg_lower for term in ("login", "sign in")):
                        self.login_required += 1
                        existing_app.status = "login_required"
                        existing_app.stage = "auth_gate"
                    else:
                        self.failed += 1
                        existing_app.status = "failed"
                    existing_app.error_message = submit_res.message
                    db.add(ApplicationEvent(
                        application_id=existing_app.id,
                        user_id=self.user_id,
                        status=existing_app.status,
                        stage=existing_app.stage,
                        message=submit_res.message or "Submission halted.",
                    ))
                    refund_credit_for_application(db, self.user_id, existing_app.id, reason=submit_res.message or "Submission failed")
                    db.commit()

            except Exception as app_err:
                logger.error(f"Application error for job {job.id}: {app_err}", exc_info=True)
                self.failed += 1
                existing_app.status = "failed"
                existing_app.error_message = str(app_err)
                db.add(ApplicationEvent(
                    application_id=existing_app.id,
                    user_id=self.user_id,
                    status="failed",
                    stage="execution_error",
                    message=f"Execution error: {app_err}",
                ))
                refund_credit_for_application(db, self.user_id, existing_app.id, reason=str(app_err))
                db.commit()
            finally:
                if executor:
                    try:
                        executor.close()
                    except Exception:
                        pass
                self.current_executor = None

            time.sleep(0.5)


class AutomationManager:
    _instance: Optional[AutomationManager] = None
    _controllers: Dict[int, UserAutomationController] = {}
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> AutomationManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = AutomationManager()
        return cls._instance

    def get_controller(self, user_id: int) -> UserAutomationController:
        with self._lock:
            if user_id not in self._controllers:
                self._controllers[user_id] = UserAutomationController(user_id)
            return self._controllers[user_id]

    def start_user_automation(self, user_id: int) -> Dict[str, Any]:
        ctrl = self.get_controller(user_id)
        ctrl.start()
        return self.get_user_status(user_id)

    def pause_user_automation(self, user_id: int) -> Dict[str, Any]:
        ctrl = self.get_controller(user_id)
        ctrl.pause()
        return self.get_user_status(user_id)

    def resume_user_automation(self, user_id: int) -> Dict[str, Any]:
        ctrl = self.get_controller(user_id)
        ctrl.resume()
        return self.get_user_status(user_id)

    def stop_user_automation(self, user_id: int) -> Dict[str, Any]:
        ctrl = self.get_controller(user_id)
        ctrl.stop()
        return self.get_user_status(user_id)

    def get_user_status(self, user_id: int) -> Dict[str, Any]:
        ctrl = self.get_controller(user_id)
        db = SessionLocal()
        credits_rem = 0
        try:
            cb = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
            if cb:
                credits_rem = cb.balance
        finally:
            db.close()

        status_str = "running" if ctrl.is_running and not ctrl.is_paused else ("paused" if ctrl.is_paused else "stopped")

        return {
            "is_running": ctrl.is_running,
            "status": status_str,
            "current_action": ctrl.current_action,
            "jobs_discovered": ctrl.jobs_discovered,
            "jobs_analyzed": ctrl.jobs_analyzed,
            "jobs_matched": ctrl.jobs_matched,
            "eligible_applications": ctrl.eligible_applications,
            "applications_submitted": ctrl.applications_submitted,
            "verification_required": ctrl.verification_required,
            "login_required": ctrl.login_required,
            "failed": ctrl.failed,
            "credits_remaining": credits_rem,
            "active_tasks": 1 if ctrl.is_running else 0,
        }
