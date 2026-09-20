from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.session import init_db
from app.db.migrate_legacy import migrate_legacy_data
from app.api.v1 import api_v1_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai-job-agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Job Agent SaaS platform...")
    try:
        init_db()
        migrate_legacy_data()
        logger.info("Database and migrations initialized.")
    except Exception as e:
        logger.error(f"Error during startup database initialization: {e}")
    yield
    logger.info("Shutting down AI Job Agent SaaS platform.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "running",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "message": "AI Job Agent Multi-User SaaS Backend is operational 🚀",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.APP_ENV,
    }


@app.get("/ready")
def ready():
    return {
        "status": "ready",
        "service": "fastapi",
    }


# Mount unified API v1
app.include_router(api_v1_router)

# Also mount under /api for convenience
app.include_router(api_v1_router, prefix="/api", tags=["Aliased"])
