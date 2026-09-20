from app.services.application_field_values import (
    get_candidate_field_value,
)


def validate_resume_input(
    package: dict,
    human_input: dict[str, str],
) -> list[str]:
    """
    Validate explicitly supplied human input.

    Returns field names that are still missing.
    """

    updated_package = dict(package)

    candidate = dict(
        package.get("candidate", {})
    )

    updated_package["candidate"] = candidate

    for field_name, value in human_input.items():
        if value is not None and str(value).strip():
            candidate[field_name] = value

    required_fields = [
        "email",
    ]

    missing = []

    for field_name in required_fields:
        value = get_candidate_field_value(
            field_name,
            updated_package,
        )

        if value is None or not str(value).strip():
            missing.append(field_name)

    return missing
