from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from app.db.session import SessionLocal
from app.db.models import JobListing, Plan

logger = logging.getLogger(__name__)


def migrate_legacy_data() -> None:
    session = SessionLocal()
    try:
        # Seed or sync Free + Pay-as-you-go credit packs
        desired_packs = [
            {
                "name": "Free",
                "slug": "free",
                "price_inr": 0,
                "included_applications": 5,
                "extra_application_cost_inr": 0,
                "billing_type": "free",
                "tag": "",
                "features": [
                    "5 Applications / month",
                    "Real-Time LinkedIn & Portal Job Discovery",
                    "AI Resume Matching & Scoring",
                    "Autonomous Multi-Step Form Filling",
                    "Candidate Privacy & Zero-Waste Credit Guarantee",
                ],
            },
            {
                "name": "Starter Pack",
                "slug": "starter_pack",
                "price_inr": 149,
                "included_applications": 10,
                "extra_application_cost_inr": 15,
                "billing_type": "pay_as_you_go",
                "tag": "",
                "features": [
                    "10 Guaranteed Application Credits",
                    "Pay-as-you-go (No recurring subscription)",
                    "Priority Browser Queue & Auto-fill",
                    "AI Custom Screening Question Responses",
                    "Credits never expire",
                ],
            },
            {
                "name": "Job Seeker Pack",
                "slug": "job_seeker_pack",
                "price_inr": 299,
                "included_applications": 25,
                "extra_application_cost_inr": 12,
                "billing_type": "pay_as_you_go",
                "tag": "Most Popular",
                "features": [
                    "25 Guaranteed Application Credits",
                    "Pay-as-you-go (No recurring subscription)",
                    "High-Throughput Multi-Step Automation",
                    "Automated Pitch & Cover Letter Synthesis",
                    "Instant Credit Refund on Security Challenges",
                    "Priority Customer Support",
                ],
            },
            {
                "name": "Power Pack",
                "slug": "power_pack",
                "price_inr": 499,
                "included_applications": 50,
                "extra_application_cost_inr": 10,
                "billing_type": "pay_as_you_go",
                "tag": "Best Value",
                "features": [
                    "50 Guaranteed Application Credits",
                    "Pay-as-you-go (No recurring subscription)",
                    "Fastest Execution Queue",
                    "Multi-Portal Live Submissions",
                    "Dedicated AI Agent Pipeline",
                    "Credits never expire",
                ],
            },
        ]

        for p_data in desired_packs:
            existing = session.query(Plan).filter(Plan.slug == p_data["slug"]).first()
            if not existing:
                plan = Plan(
                    name=p_data["name"],
                    slug=p_data["slug"],
                    price_inr=p_data["price_inr"],
                    included_applications=p_data["included_applications"],
                    extra_application_cost_inr=p_data["extra_application_cost_inr"],
                    features=p_data["features"],
                    billing_type=p_data["billing_type"],
                    tag=p_data["tag"],
                    is_active=True,
                )
                session.add(plan)
            else:
                existing.name = p_data["name"]
                existing.price_inr = p_data["price_inr"]
                existing.included_applications = p_data["included_applications"]
                existing.features = p_data["features"]
                existing.billing_type = p_data["billing_type"]
                existing.tag = p_data["tag"]
                existing.is_active = True

        # Deactivate old demo plans if present
        session.query(Plan).filter(Plan.slug.notin_(["free", "starter_pack", "job_seeker_pack", "power_pack"])).update(
            {"is_active": False}, synchronize_session=False
        )
        session.commit()
        logger.info("Monetization credit packs synced successfully.")

        # Migrate jobs from jobs.db if it exists
        legacy_db = Path("jobs.db")
        if legacy_db.exists():
            conn = sqlite3.connect(legacy_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                rows = cursor.execute("SELECT * FROM jobs").fetchall()
                migrated_count = 0
                for row in rows:
                    existing = session.query(JobListing).filter(JobListing.url == row["url"]).first()
                    if not existing:
                        job = JobListing(
                            source=row["source"] or "generic",
                            url=row["url"],
                            title=row["title"] or "Untitled Role",
                            company=row["company"] or "Unknown Company",
                            location=row["location"] or "",
                            description=row["description"] or "",
                            experience_years=row["experience_years"],
                            salary=row["salary"],
                            raw_data={},
                        )
                        session.add(job)
                        migrated_count += 1
                session.commit()
                logger.info(f"Migrated {migrated_count} legacy jobs into PostgreSQL.")
            except Exception as e:
                logger.warning(f"Legacy job migration encountered error: {e}")
            finally:
                conn.close()

    except Exception as e:
        session.rollback()
        logger.error(f"Migration error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    migrate_legacy_data()
