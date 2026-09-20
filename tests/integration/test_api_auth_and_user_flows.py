import io
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

def create_dummy_pdf_bytes(content: str = "Test Candidate Resume. Skills: Python, FastAPI, React.") -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    # PyPDF blank page is valid PDF
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()

def test_full_user_lifecycle_via_api(client: TestClient):
    import time
    ts = int(time.time() * 1000)
    email = f"flow_user_{ts}@production-test.com"
    password = "StrongPassword2026!"

    # 1. Register User
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert reg_res.status_code in [200, 201], reg_res.text
    data = reg_res.json()
    assert "access_token" in data
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify 5 Free Credits Granted Automatically
    cred_res = client.get("/api/v1/credits", headers=headers)
    assert cred_res.status_code == 200
    cred_data = cred_res.json()
    assert cred_data["balance"] == 5
    assert cred_data["total_included"] == 5

    # 3. Get and Update Profile
    prof_res = client.get("/api/v1/profile", headers=headers)
    assert prof_res.status_code == 200
    patch_prof = client.patch(
        "/api/v1/profile",
        headers=headers,
        json={
            "first_name": "Jordan",
            "last_name": "Smith",
            "phone": "+1-555-898-0000",
            "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
            "experience_years": 4.5,
        },
    )
    assert patch_prof.status_code == 200
    assert patch_prof.json()["first_name"] == "Jordan"
    assert "FastAPI" in patch_prof.json()["skills"]

    # 4. Get and Update Preferences
    patch_pref = client.patch(
        "/api/v1/preferences",
        headers=headers,
        json={
            "preferred_roles": ["Full Stack Engineer", "Backend Developer"],
            "preferred_locations": ["Remote", "Bengaluru"],
            "remote_friendly": True,
            "min_salary_lpa": 18.0,
            "min_match_score": 75,
            "auto_submit": False,
        },
    )
    assert patch_pref.status_code == 200
    assert patch_pref.json()["remote_friendly"] is True

    # 5. Get and Update Application Profile
    patch_app_prof = client.patch(
        "/api/v1/application-profile",
        headers=headers,
        json={
            "notice_period_days": 15,
            "work_authorization": "Citizen",
            "expected_salary_lpa": 24.0,
            "custom_answers": {
                "Are you willing to undergo a background check?": "Yes"
            },
        },
    )
    assert patch_app_prof.status_code == 200
    assert patch_app_prof.json()["notice_period_days"] == 15

    # 6. Upload Valid Resume
    pdf_bytes = create_dummy_pdf_bytes()
    upload_res = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": ("jordan_resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_res.status_code in [200, 201], upload_res.text
    resume_id = upload_res.json()["id"]
    assert upload_res.json()["is_active"] is True

    # 7. List Resumes
    list_res = client.get("/api/v1/resumes", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 8. List Jobs
    jobs_res = client.get("/api/v1/jobs", headers=headers)
    assert jobs_res.status_code == 200
    jobs = jobs_res.json()

    if jobs:
        test_job_id = jobs[0]["id"]
        # Trigger Job Match
        match_res = client.post(f"/api/v1/jobs/{test_job_id}/match", headers=headers)
        assert match_res.status_code == 200
        match_data = match_res.json()
        assert "match_score" in match_data
        assert "apply_decision" in match_data

    # 9. Check Automation Status
    auto_status = client.get("/api/v1/automation/status", headers=headers)
    assert auto_status.status_code == 200
    assert "is_running" in auto_status.json()
    assert auto_status.json()["credits_remaining"] == 5
