import datetime
import torch
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.connection import get_db
from app.schemas.api_schemas import HealthResponse
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("", response_model=HealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    """
    Checks backend connectivity, PyTorch acceleration device,
    database connectivity, and Gemini API key status.
    """
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    cuda_avail = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU (Host Processor)"

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        app_name=settings.APP_NAME,
        version="1.0.0",
        device=device_name,
        cuda_available=cuda_avail,
        gemini_configured=bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5),
        database_connected=db_connected,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
