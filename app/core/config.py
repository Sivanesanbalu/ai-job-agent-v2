from __future__ import annotations

import getpass
import os
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "AI Job Agent SaaS"
    APP_ENV: str = "development"
    DEBUG: bool = True
    VERSION: str = "2.0.0"

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            f"postgresql://{getpass.getuser()}@localhost:5432/ai_job_agent",
        )
    )
    SQLITE_FALLBACK_URL: str = f"sqlite:///{BASE_DIR}/jobs_v2.db"

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Security
    SECRET_KEY: str = Field(
        default="development-super-secret-key-change-in-production-2026-secure-jwt"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Storage
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    RESUME_STORAGE_DIR: Path = BASE_DIR / "data" / "resumes"
    BROWSER_DATA_DIR: Path = BASE_DIR / "data" / "browser_sessions"

    # AI / Ollama
    OLLAMA_BASE_URL: str = Field(default="http://127.0.0.1:11434")
    OLLAMA_MODEL: str = Field(default="")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Application Defaults & Limits
    FREE_SIGNUP_CREDITS: int = 100
    CREDIT_PRICE_PER_100_INR: int = 100

    def init_storage(self) -> None:
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.BROWSER_DATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.init_storage()
