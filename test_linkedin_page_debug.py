from playwright.sync_api import sync_playwright

URL = "https://in.linkedin.com/jobs/view/ai-engineer-genai-agentic-ai-and-mlops-at-navasys-technologies-4442345026"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        viewport={
            "width": 1440,
            "height": 900,
        }
    )

    page = context.new_page()
    page.set_default_timeout(5000)

    print("=" * 70)
    print("OPENING LINKEDIN JOB")
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

    print("\nURL:")
    print(page.url)

    print("\nTITLE:")
    print(page.title())

    # ---------------------------------------------------------
    # Body text
    # ---------------------------------------------------------

    body = page.locator("body").inner_text()

    print("\nBODY LENGTH:")
    print(len(body))

    print("\nBODY FIRST 4000 CHARS:")
    print(body[:4000])

    # ---------------------------------------------------------
    # Password inputs
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("PASSWORD INPUTS")
    print("=" * 70)

    password_inputs = page.locator(
        "input[type='password']"
    )

    print("Count:", password_inputs.count())

    for i in range(password_inputs.count()):
        try:
            el = password_inputs.nth(i)

            print(
                f"[{i}] "
                f"visible={el.is_visible()} "
                f"placeholder={el.get_attribute('placeholder')} "
                f"name={el.get_attribute('name')} "
                f"id={el.get_attribute('id')}"
            )
        except Exception as e:
            print("ERROR:", e)

    # ---------------------------------------------------------
    # Google buttons/links
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("GOOGLE AUTH ELEMENTS")
    print("=" * 70)

    google_elements = page.locator(
        "text=/google/i"
    )

    print("Count:", google_elements.count())

    for i in range(
        min(google_elements.count(), 20)
    ):
        try:
            el = google_elements.nth(i)

            if el.is_visible():
                print(
                    f"[{i}] "
                    f"{el.inner_text(timeout=1000)[:300]!r}"
                )
        except Exception:
            pass

    # ---------------------------------------------------------
    # Dialogs
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("DIALOGS")
    print("=" * 70)

    dialogs = page.locator(
        "[role='dialog'], [aria-modal='true']"
    )

    print("Count:", dialogs.count())

    for i in range(
        min(dialogs.count(), 10)
    ):
        try:
            el = dialogs.nth(i)

            print(
                f"\nDIALOG [{i}] "
                f"visible={el.is_visible()}"
            )

            if el.is_visible():
                print(
                    el.inner_text(timeout=1500)[:2000]
                )

        except Exception as e:
            print("ERROR:", e)

    # ---------------------------------------------------------
    # Forms
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("FORMS")
    print("=" * 70)

    forms = page.locator("form")

    print("Count:", forms.count())

    for i in range(
        min(forms.count(), 10)
    ):
        try:
            form = forms.nth(i)

            if not form.is_visible():
                continue

            print(
                f"\nFORM [{i}]"
            )

            print(
                form.inner_text(timeout=1500)[:2000]
            )

        except Exception:
            pass

    # ---------------------------------------------------------
    # Important login phrases
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("AUTH PHRASE CHECK")
    print("=" * 70)

    lower = body.lower()

    phrases = [
        "sign in with google",
        "continue with google",
        "google account",
        "choose an account",
        "sign in",
        "log in",
        "login",
        "password",
        "email",
        "join linkedin",
        "skip to main content",
        "apply",
        "job details",
        "responsibilities",
        "qualifications",
        "requirements",
    ]

    for phrase in phrases:
        print(
            f"{phrase:30} -> "
            f"{phrase in lower}"
        )

    print("\n" + "=" * 70)
    print("KEEPING BROWSER OPEN FOR 10 SECONDS")
    print("=" * 70)

    page.wait_for_timeout(10000)

    browser.close()
