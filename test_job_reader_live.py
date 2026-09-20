from playwright.sync_api import sync_playwright

from app.services.job_page_reader import JobPageReader


URL = (
    "https://in.linkedin.com/jobs/view/"
    "ai-engineer-genai-agentic-ai-and-mlops-at-"
    "navasys-technologies-4442345026"
)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        viewport={
            "width": 1440,
            "height": 900,
        }
    )

    page = context.new_page()

    page.set_default_timeout(8000)

    print("=" * 70)
    print("LIVE JOB READER TEST")
    print("=" * 70)

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=30000,
    )

    try:
        page.wait_for_load_state(
            "networkidle",
            timeout=8000,
        )
    except Exception:
        pass

    reader = JobPageReader(page)

    print("")
    print("Authentication:")
    print(
        reader.detect_authentication()
    )

    print("")
    print("Security:")
    print(
        reader.detect_security_challenge()
    )

    print("")
    print("Invalid shell:")
    print(
        reader.detect_invalid_job_shell()
    )

    result = reader.read()

    print("")
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    print("success              :", result.success)
    print("blocked              :", result.blocked)
    print("verification_required:", result.verification_required)
    print("reason               :", result.reason)
    print("title                :", result.title)
    print("company              :", result.company)
    print("location             :", result.location)
    print("salary               :", result.salary)
    print("experience           :", result.experience)
    print("seniority            :", result.seniority_signal)
    print("description chars    :", len(result.description))

    print("")
    print("DESCRIPTION PREVIEW:")
    print(result.description[:1500])

    print("")
    print("=" * 70)

    page.wait_for_timeout(3000)

    browser.close()
