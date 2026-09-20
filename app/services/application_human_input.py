from copy import deepcopy


def merge_human_input(
    package: dict,
    human_input: dict[str, str],
) -> dict:
    """
    Merge explicitly supplied human values into an
    application package.

    Only fields already represented in the candidate
    section can be updated.
    """

    updated = deepcopy(package)

    candidate = updated.setdefault(
        "candidate",
        {},
    )

    allowed_fields = {
        "name",
        "email",
        "phone",
        "headline",
        "education",
        "notice_period_days",
    }

    for field_name, value in human_input.items():
        if field_name not in allowed_fields:
            continue

        if value is None:
            continue

        candidate[field_name] = value

    return updated
