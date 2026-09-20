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
        # Seed default plans if not present
        if not session.query(Plan).first():
            free_plan = Plan(
                name="Free Starter",
                slug="free",
                price_inr=0,
                included_applications=100,
                extra_application_cost_inr=1,
                features=[
                    "100 Included Applications",
                    "LinkedIn, Indeed, Naukri Discovery",
                    "AI Resume Matching",
                    "Real-Time Automation Tracking",
                ],
                is_active=True,
            )
            pro_plan = Plan(
                name="Pro Booster",
                slug="pro-booster",
                price_inr=100,
                included_applications=100,
                extra_application_cost_inr=1,
                features=[
                    "Additional 100 Auto Applications",
                    "Priority Browser Queue",
                    "Advanced Multi-step Form Auto-filling",
                    "Dedicated Support",
                ],
                is_active=True,
            )
            session.add_all([free_plan, pro_plan])
            session.commit()
            logger.info("Default plans seeded successfully.")

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
