from app.services.application_field_mapper import (
    map_field_to_candidate_data,
)
from app.services.application_field_values import (
    get_candidate_field_value,
)


def build_application_fill_plan(
    fields: list[dict],
    package: dict,
    supported_fields: list[str] | None = None,
) -> list[dict]:
    """
    Build a safe application fill plan.

    When supported_fields is provided, only fields explicitly
    supported by the selected site adapter can be filled.
    """

    plan = []

    allowed_fields = (
        set(supported_fields)
        if supported_fields is not None
        else None
    )

    for field in fields:
        field_name = map_field_to_candidate_data(field)
        required = bool(field.get("required", False))

        if field_name is None:
            plan.append(
                {
                    "field": field,
                    "mapped_name": None,
                    "value": None,
                    "action": "skip",
                    "required": required,
                    "reason": (
                        "Required field is unknown or unsafe"
                        if required
                        else "Unknown or unsafe field"
                    ),
                }
            )
            continue

        if (
            allowed_fields is not None
            and field_name not in allowed_fields
        ):
            plan.append(
                {
                    "field": field,
                    "mapped_name": field_name,
                    "value": None,
                    "action": "skip",
                    "required": required,
                    "reason": (
                        "Field is not supported by "
                        "the selected site adapter"
                    ),
                }
            )
            continue

        value = get_candidate_field_value(
            field_name,
            package,
        )

        if value is None:
            plan.append(
                {
                    "field": field,
                    "mapped_name": field_name,
                    "value": None,
                    "action": "skip",
                    "required": required,
                    "reason": (
                        "Required field has no candidate value"
                        if required
                        else "Candidate value unavailable"
                    ),
                }
            )
            continue

        plan.append(
            {
                "field": field,
                "mapped_name": field_name,
                "value": value,
                "action": "fill",
                "required": required,
                "reason": (
                    "Safe field supported by adapter "
                    "with available candidate value"
                ),
            }
        )

    return plan
