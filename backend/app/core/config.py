import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "IndusVision — Industrial Quality Inspector"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'app.db'}"

    # Storage Paths
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    WEIGHTS_DIR: Path = BASE_DIR / "weights"
    REPORTS_DIR: Path = BASE_DIR / "reports"

    # Multimodal GenAI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GENAI_TIMEOUT_SECONDS: int = 30

    # Detection & Severity
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.35
    DEFAULT_IOU_THRESHOLD: float = 0.45
    CRITICAL_DEFECT_AREA_RATIO: float = 0.15
    HIGH_DEFECT_AREA_RATIO: float = 0.08
    MEDIUM_DEFECT_AREA_RATIO: float = 0.03

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DATASETS_DIR.mkdir(parents=True, exist_ok=True)
settings.WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
