def get_candidate_field_value(
    field_name: str,
    package: dict,
) -> str | None:
    candidate = package.get("candidate", {})

    if field_name == "name":
        return candidate.get("name")

    if field_name == "first_name":
        full_name = candidate.get("name", "").strip()
        if not full_name:
            return None
        return full_name.split()[0]

    if field_name == "last_name":
        full_name = candidate.get("name", "").strip()
        if not full_name:
            return None
        parts = full_name.split()
        return parts[-1] if len(parts) > 1 else None

    if field_name == "email":
        return candidate.get("email")

    if field_name == "cover_letter":
        return package.get("application_pitch")

    return None
