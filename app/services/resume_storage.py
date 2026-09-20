from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/octet-stream",  # often sent by browsers for docx
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_resume_file(file: UploadFile, content: bytes) -> Tuple[str, str]:
    filename = file.filename or "resume.pdf"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension '{ext}'. Only PDF and DOCX files are permitted.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed size of 10MB.",
        )

    # Magic byte verification
    if ext == ".pdf" and not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file format.",
        )

    if ext == ".docx" and not content.startswith(b"PK"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid DOCX file format.",
        )

    mime_type = "application/pdf" if ext == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return filename, mime_type


def save_user_resume_file(user_id: int, original_filename: str, content: bytes) -> Path:
    user_dir = settings.RESUME_STORAGE_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex[:12]}_{Path(original_filename).stem[:30]}{ext}"
    dest_path = user_dir / unique_name

    with open(dest_path, "wb") as f:
        f.write(content)

    return dest_path


def delete_resume_file(file_path: str) -> None:
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
    except Exception:
        pass
