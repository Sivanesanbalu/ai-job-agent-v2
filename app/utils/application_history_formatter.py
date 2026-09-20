def format_application_history(attempt: dict) -> dict:
    return {
        "id": attempt["id"],
        "status": attempt["status"],
        "message": attempt["message"] or "",
        "created_at": attempt["created_at"],
    }
