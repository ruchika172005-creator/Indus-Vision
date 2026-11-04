import os
import torch
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import ApplicationSetting
from app.schemas.api_schemas import SystemSettingsResponse, SystemSettingsUpdate
from app.core.config import settings
from app.ml.model_manager import model_manager
from app.genai.explanation_generator import explanation_generator
from app.ml.severity_engine import severity_engine

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=SystemSettingsResponse)
def get_system_settings(db: Session = Depends(get_db)):
    """
    Returns current active configurations, model parameters, and API integration states.
    """
    db_settings = {s.key: s.value for s in db.query(ApplicationSetting).all()}

    gemini_key = db_settings.get("gemini_api_key", settings.GEMINI_API_KEY)
    gemini_model = db_settings.get("gemini_model", settings.GEMINI_MODEL)
    conf_thresh = float(db_settings.get("confidence_threshold", settings.DEFAULT_CONFIDENCE_THRESHOLD))
    iou_thresh = float(db_settings.get("iou_threshold", settings.DEFAULT_IOU_THRESHOLD))
    crit_ratio = float(db_settings.get("critical_area_ratio", settings.CRITICAL_DEFECT_AREA_RATIO))
    high_ratio = float(db_settings.get("high_area_ratio", settings.HIGH_DEFECT_AREA_RATIO))
    med_ratio = float(db_settings.get("medium_area_ratio", settings.MEDIUM_DEFECT_AREA_RATIO))
    active_model = db_settings.get("active_model_name", model_manager.active_model_name)

    cuda_avail = torch.cuda.is_available()
    dev_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU (Standard Host Execution)"

    return SystemSettingsResponse(
        gemini_api_key_configured=bool(gemini_key and len(gemini_key) > 6),
        gemini_model=gemini_model,
        confidence_threshold=conf_thresh,
        iou_threshold=iou_thresh,
        critical_area_ratio=crit_ratio,
        high_area_ratio=high_ratio,
        medium_area_ratio=med_ratio,
        active_model_name=active_model,
        device_name=dev_name,
        cuda_available=cuda_avail,
        version="1.0.0"
    )

@router.put("", response_model=SystemSettingsResponse)
def update_system_settings(payload: SystemSettingsUpdate, db: Session = Depends(get_db)):
    """
    Updates system parameters, thresholds, and reconfigures Gemini API credentials securely.
    """
    updates = {}
    if payload.gemini_api_key is not None and payload.gemini_api_key.strip():
        updates["gemini_api_key"] = payload.gemini_api_key.strip()
        settings.GEMINI_API_KEY = payload.gemini_api_key.strip()
        explanation_generator.update_api_key(payload.gemini_api_key.strip())

    if payload.gemini_model is not None:
        updates["gemini_model"] = payload.gemini_model.strip()
        settings.GEMINI_MODEL = payload.gemini_model.strip()

    if payload.confidence_threshold is not None:
        updates["confidence_threshold"] = str(payload.confidence_threshold)
        settings.DEFAULT_CONFIDENCE_THRESHOLD = payload.confidence_threshold

    if payload.iou_threshold is not None:
        updates["iou_threshold"] = str(payload.iou_threshold)
        settings.DEFAULT_IOU_THRESHOLD = payload.iou_threshold

    if payload.critical_area_ratio is not None:
        updates["critical_area_ratio"] = str(payload.critical_area_ratio)
        severity_engine.critical_area_ratio = payload.critical_area_ratio

    if payload.high_area_ratio is not None:
        updates["high_area_ratio"] = str(payload.high_area_ratio)
        severity_engine.high_area_ratio = payload.high_area_ratio

    if payload.medium_area_ratio is not None:
        updates["medium_area_ratio"] = str(payload.medium_area_ratio)
        severity_engine.medium_area_ratio = payload.medium_area_ratio

    if payload.active_model_name is not None:
        updates["active_model_name"] = payload.active_model_name
        model_manager.set_active_model(payload.active_model_name)

    # Persist in DB
    for k, v in updates.items():
        rec = db.query(ApplicationSetting).filter(ApplicationSetting.key == k).first()
        if rec:
            rec.value = v
        else:
            db.add(ApplicationSetting(key=k, value=v))
    db.commit()

    return get_system_settings(db)
