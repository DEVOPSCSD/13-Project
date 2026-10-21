"""Application configuration. Values can be overridden with environment variables."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent      # .../backend
PROJECT_ROOT = BASE_DIR.parent                  # project root


class Config:
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DEBUG = os.environ.get("APP_DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "data" / "students.db"))
    FRONTEND_DIR = os.environ.get("FRONTEND_DIR", str(PROJECT_ROOT / "frontend"))
    SEED_DEMO_DATA = os.environ.get("SEED_DEMO_DATA", "true").lower() == "true"
