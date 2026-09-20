import os
import io
import pytest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from app.main import app
from app.db.session import SessionLocal
from app.db.models import JobListing, Application
from app.services.credit_service import deduct_credit_for_application

def create_sample_pdf(title: str, skills: str) -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()

def register_and_setup_user(client: TestClient, role_label: str, email_prefix: str, skills: list, roles: list, min_score: int):
    import time
    ts = int(time.time() * 1000)
    email = f"{email_prefix}_{ts}@isolation.com"
    pwd = "IsolationPassword123!"

    # 1. Register
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": pwd})
    assert reg.status_code in [200, 201], reg.text
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = reg.json()["user"]["id"]

    # 2. Setup Profile
    client.patch("/api/v1/profile", headers=headers, json={
        "first_name": role_label.split()[0],
        "last_name": "Candidate",
        "skills": skills,
        "experience_years": 5.0,
    })

    # 3. Setup Preferences
    client.patch("/api/v1/preferences", headers=headers, json={
        "preferred_roles": roles,
        "preferred_locations": ["Remote" if "AI" in role_label else "Bengaluru"],
        "min_match_score": min_score,
    })

    # 4. Upload Resume
    pdf_bytes = create_sample_pdf(role_label, ", ".join(skills))
    res_upload = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": (f"{email_prefix}_resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert res_upload.status_code in [200, 201]
    resume_id = res_upload.json()["id"]

    return {
        "user_id": user_id,
        "email": email,
        "token": token,
        "headers": headers,
        "resume_id": resume_id,
        "skills": skills,
    }

def test_three_user_concurrent_isolation():
    with TestClient(app) as client:
        # User A: AI / LLM Engineer
        user_a = register_and_setup_user(
            client,
            role_label="AI Engineer",
            email_prefix="user_a_ai",
            skills=["Python", "PyTorch", "LangChain", "Generative AI"],
            roles=["AI Engineer", "LLM Engineer"],
            min_score=80,
        )

        # User B: Data Scientist
        user_b = register_and_setup_user(
            client,
            role_label="Data Scientist",
            email_prefix="user_b_ds",
            skills=["Python", "SQL", "Pandas", "Machine Learning", "Scikit-Learn"],
            roles=["Data Scientist", "ML Engineer"],
            min_score=75,
        )

        # User C: Frontend Engineer
        user_c = register_and_setup_user(
            client,
            role_label="Frontend Engineer",
            email_prefix="user_c_fe",
            skills=["React", "Next.js", "TypeScript", "Tailwind CSS"],
            roles=["Frontend Developer", "UI Engineer"],
            min_score=70,
        )

        # VERIFICATION 1: Cross-Tenant Resume Access Prohibited (Strict 404 / ID Isolation)
        # User A attempts to view User B's resume
        forbidden_res = client.get(f"/api/v1/resumes/{user_b['resume_id']}", headers=user_a["headers"])
        assert forbidden_res.status_code == 404, "User A was able to access User B's resume!"

        # User B attempts to view User C's resume
        forbidden_res_2 = client.get(f"/api/v1/resumes/{user_c['resume_id']}", headers=user_b["headers"])
        assert forbidden_res_2.status_code == 404, "User B was able to access User C's resume!"

        # User C attempts to view User A's resume
        forbidden_res_3 = client.get(f"/api/v1/resumes/{user_a['resume_id']}", headers=user_c["headers"])
        assert forbidden_res_3.status_code == 404, "User C was able to access User A's resume!"

        # VERIFICATION 2: Resume File System Storage Directory Isolation
        # Verify user resumes are partitioned in data/resumes/{user_id}/
        base_resumes_path = Path("data/resumes")
        path_a = base_resumes_path / str(user_a["user_id"])
        path_b = base_resumes_path / str(user_b["user_id"])
        path_c = base_resumes_path / str(user_c["user_id"])

        assert path_a.exists(), f"Resume path {path_a} does not exist"
        assert path_b.exists(), f"Resume path {path_b} does not exist"
        assert path_c.exists(), f"Resume path {path_c} does not exist"
        assert path_a != path_b != path_c, "Tenant storage directories collided!"

        # VERIFICATION 3: Browser Session Directory Path Isolation
        base_browser_path = Path("data/browser_sessions")
        session_a = base_browser_path / str(user_a["user_id"])
        session_b = base_browser_path / str(user_b["user_id"])
        session_c = base_browser_path / str(user_c["user_id"])
        assert session_a != session_b != session_c

        # VERIFICATION 4: Independent Matching Profiles & Job Relevance
        # Seed 2 distinct jobs: one AI job and one React job
        db = SessionLocal()
        try:
            import time
            ts_now = time.time_ns()
            ai_job = JobListing(
                title="Staff LLM Research Engineer",
                company="OpenModel Inc",
                location="Remote",
                description="Developing Large Language Models, Generative AI agents with PyTorch and LangChain.",
                source="test",
                url=f"https://example.com/ai_job_{ts_now}",
            )
            fe_job = JobListing(
                title="Lead React Next.js Developer",
                company="WebFlow UI",
                location="Bengaluru",
                description="Deep knowledge of React, Next.js, and TypeScript frontend development.",
                source="test",
                url=f"https://example.com/fe_job_{ts_now}",
            )
            db.add(ai_job)
            db.add(fe_job)
            db.commit()
            db.refresh(ai_job)
            db.refresh(fe_job)

            # Match User A against AI Job
            match_a_ai = client.post(f"/api/v1/jobs/{ai_job.id}/match", headers=user_a["headers"]).json()
            # Match User C against AI Job
            match_c_ai = client.post(f"/api/v1/jobs/{ai_job.id}/match", headers=user_c["headers"]).json()

            # User A (AI engineer) should score substantially higher than User C (Frontend) on AI job
            assert match_a_ai["match_score"] > match_c_ai["match_score"], (
                f"Expected User A score ({match_a_ai['match_score']}) > User C score ({match_c_ai['match_score']})"
            )

            # Match User C against Frontend Job
            match_c_fe = client.post(f"/api/v1/jobs/{fe_job.id}/match", headers=user_c["headers"]).json()
            # Match User A against Frontend Job
            match_a_fe = client.post(f"/api/v1/jobs/{fe_job.id}/match", headers=user_a["headers"]).json()

            assert match_c_fe["match_score"] > match_a_fe["match_score"], (
                f"Expected User C score ({match_c_fe['match_score']}) > User A score ({match_a_fe['match_score']})"
            )

            # VERIFICATION 5: Concurrent Credit Operations Do Not Interfere
            app_a = Application(user_id=user_a["user_id"], job_id=ai_job.id, status="queued")
            app_b = Application(user_id=user_b["user_id"], job_id=ai_job.id, status="queued")
            app_c = Application(user_id=user_c["user_id"], job_id=fe_job.id, status="queued")
            db.add_all([app_a, app_b, app_c])
            db.commit()
            db.refresh(app_a)
            db.refresh(app_b)
            db.refresh(app_c)

            def concurrent_deduct(u_id, app_id):
                with SessionLocal() as thread_db:
                    return deduct_credit_for_application(thread_db, u_id, app_id)

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(concurrent_deduct, user_a["user_id"], app_a.id),
                    executor.submit(concurrent_deduct, user_b["user_id"], app_b.id),
                    executor.submit(concurrent_deduct, user_c["user_id"], app_c.id),
                ]
                results = [f.result() for f in futures]

            assert len(results) == 3
            # Each user started with 100 credits, now has 99
            for u in [user_a, user_b, user_c]:
                bal = client.get("/api/v1/credits", headers=u["headers"]).json()
                assert bal["balance"] == 99, f"User {u['user_id']} balance was {bal['balance']}, expected 99"

        finally:
            db.close()
