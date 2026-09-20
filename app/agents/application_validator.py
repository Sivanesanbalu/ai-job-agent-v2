from app.config import REQUIRE_HUMAN_REVIEW

def validate_application_package(package: dict) -> tuple[bool, list[str]]:
    errors = []

    job = package.get("job", {})
    candidate = package.get("candidate", {})

    required_job_fields = [
        "title",
        "company",
        "url",
        "match_score",
    ]

    required_candidate_fields = [
        "name",
        "headline",
        "education",
    ]

    for field in required_job_fields:
        if not job.get(field):
            errors.append(f"Missing job field: {field}")

    for field in required_candidate_fields:
        if not candidate.get(field):
            errors.append(f"Missing candidate field: {field}")

    if not package.get("matched_skills"):
        errors.append("No matched skills found")

    if not package.get("application_pitch"):
        errors.append("Missing application pitch")

    if package.get("requires_human_review") != REQUIRE_HUMAN_REVIEW:
        errors.append(
            "Human review setting does not match application configuration"
        )

    return len(errors) == 0, errors
