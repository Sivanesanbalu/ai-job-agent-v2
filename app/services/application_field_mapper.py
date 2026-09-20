def normalize_field_text(value: str) -> str:
    return " ".join(value.lower().split()).strip()


SAFE_FIELD_ALIASES = {
    "name": {
        "name",
        "full name",
        "full_name",
        "candidate name",
        "candidate_name",
    },
    "first_name": {
        "first name",
        "first_name",
        "given name",
        "given_name",
    },
    "last_name": {
        "last name",
        "last_name",
        "family name",
        "family_name",
    },
    "email": {
        "email",
        "email address",
        "email_address",
        "e-mail",
        "contact email",
        "contact_email",
    },
    "cover_letter": {
        "cover letter",
        "cover_letter",
        "coverletter",
        "application message",
        "application_message",
        "cover letter/message",
    },
}


def map_field_to_candidate_data(field: dict) -> str | None:
    candidates = [
        field.get("name", ""),
        field.get("id", ""),
        field.get("placeholder", ""),
        field.get("aria_label", ""),
    ]

    for value in candidates:
        normalized = normalize_field_text(value)

        for canonical_name, aliases in SAFE_FIELD_ALIASES.items():
            if normalized in aliases:
                return canonical_name

    return None
