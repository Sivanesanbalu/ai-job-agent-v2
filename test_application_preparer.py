from app.agents.application_preparer import prepare_application
from app.services.job_queries import get_approved_jobs


jobs = get_approved_jobs()

print("Approved jobs:", len(jobs))

for job in jobs:
    application = prepare_application(job)

    print("\nAPPLICATION PACKAGE")
    print("-------------------")
    for key, value in application.items():
        print(f"{key}: {value}")
