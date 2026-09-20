def normalize_field_text(value: str) -> str:
    return " ".join(value.lower().split()).strip()


SAFE_FIELD_ALIASES = {
    "name": {
        "name",
        "full name",
        "full_name",
        "candidate name",
        "candidate_name",
        "your name",
    },
    "first_name": {
        "first name",
        "first_name",
        "given name",
        "given_name",
        "firstname",
    },
    "last_name": {
        "last name",
        "last_name",
        "family name",
        "family_name",
        "lastname",
        "surname",
    },
    "email": {
        "email",
        "email address",
        "email_address",
        "e-mail",
        "contact email",
        "contact_email",
    },
    "phone": {
        "phone",
        "phone number",
        "mobile",
        "mobile number",
        "telephone",
        "contact number",
        "cell",
        "cell phone",
    },
    "linkedin": {
        "linkedin",
        "linkedin url",
        "linkedin profile",
        "linkedin_url",
        "linkedin_profile",
    },
    "github": {
        "github",
        "github url",
        "github profile",
        "github_url",
    },
    "portfolio": {
        "portfolio",
        "portfolio url",
        "website",
        "personal website",
        "personal site",
        "blog",
        "url",
    },
    "city": {
        "city",
        "current city",
        "location",
        "current location",
    },
    "state": {
        "state",
        "province",
        "region",
    },
    "country": {
        "country",
        "current country",
        "nationality",
    },
    "address": {
        "address",
        "street address",
        "street",
        "residential address",
    },
    "pincode": {
        "pincode",
        "pin code",
        "postal code",
        "zip",
        "zip code",
    },
    "headline": {
        "headline",
        "title",
        "current title",
        "job title",
    },
    "current_company": {
        "current company",
        "company",
        "employer",
        "current employer",
        "organization",
    },
    "experience": {
        "experience",
        "years of experience",
        "total experience",
        "relevant experience",
        "experience years",
    },
    "notice_period": {
        "notice period",
        "availability",
        "how soon can you start",
        "earliest start date",
    },
    "current_salary": {
        "current salary",
        "current ctc",
        "current compensation",
    },
    "expected_salary": {
        "expected salary",
        "expected ctc",
        "desired compensation",
        "salary expectations",
    },
    "education": {
        "education",
        "degree",
        "highest degree",
        "qualification",
    },
    "university": {
        "university",
        "college",
        "school",
        "institution",
    },
    "work_authorization": {
        "work authorization",
        "authorized to work",
        "legally authorized",
        "work permit",
    },
    "sponsorship": {
        "sponsorship",
        "require sponsorship",
        "visa sponsorship",
    },
    "relocation": {
        "relocate",
        "willing to relocate",
        "relocation",
    },
    "cover_letter": {
        "cover letter",
        "cover_letter",
        "coverletter",
        "application message",
        "application_message",
        "cover letter/message",
        "pitch",
        "why work here",
        "summary",
        "about yourself",
    },
}


def map_field_to_candidate_data(field: dict) -> str | None:
    candidates = [
        field.get("name", ""),
        field.get("id", ""),
        field.get("placeholder", ""),
        field.get("aria_label", ""),
        field.get("label", ""),
    ]

    for value in candidates:
        if not value:
            continue
        normalized = normalize_field_text(value)

        for canonical_name, aliases in SAFE_FIELD_ALIASES.items():
            if normalized in aliases or any(alias in normalized for alias in aliases):
                return canonical_name

    return None
