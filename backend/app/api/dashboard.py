import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.db_models import Inspection, DetectedDefect
from app.schemas.api_schemas import (
    DashboardSummaryResponse, MetricSummary, DefectDistributionItem, TrendItem
)
from app.ml.model_manager import model_manager
from app.datasets.dataset_manager import dataset_manager
from app.core.config import settings

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Computes enterprise dashboard statistics, trend telemetry,
    defect distribution, and system readiness.
    """
    total = db.query(Inspection).count()
    defective = db.query(Inspection).filter(Inspection.total_defects > 0).count()
    defect_free = total - defective
    defect_rate = round((defective / max(1, total)) * 100.0, 1)

    high_crit = db.query(Inspection).filter(
        Inspection.max_severity.in_(["HIGH", "CRITICAL"])
    ).count()

    metrics = MetricSummary(
        total_inspections=total,
        defective_products=defective,
        defect_free_products=defect_free,
        defect_rate=defect_rate,
        high_critical_defects=high_crit
    )

    # Recent 6 inspections
    recent_objs = (
        db.query(Inspection)
        .order_by(Inspection.timestamp.desc())
        .limit(6)
        .all()
    )
    recent = []
    for r in recent_objs:
        recent.append({
            "id": r.id,
            "inspection_code": r.inspection_code,
            "timestamp": r.timestamp.isoformat(),
            "product_name": r.product_name,
            "product_category": r.product_category,
            "defect_name": r.genai_defect_name or "None",
            "total_defects": r.total_defects,
            "max_severity": r.max_severity,
            "overall_decision": r.overall_decision,
            "confidence_avg": r.confidence_avg,
            "is_demo": r.is_demo
        })

    # Defect Distribution
    defect_rows = (
        db.query(DetectedDefect.defect_name, func.count(DetectedDefect.id))
        .group_by(DetectedDefect.defect_name)
        .all()
    )
    total_defects_count = sum(cnt for _, cnt in defect_rows) or 1
    distribution = [
        DefectDistributionItem(
            name=name,
            count=cnt,
            percentage=round((cnt / total_defects_count) * 100.0, 1)
        )
        for name, cnt in defect_rows
    ]

    # Inspection Trends (Last 7 Days)
    today = datetime.datetime.now(datetime.timezone.utc).date()
    trends = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_start = datetime.datetime.combine(day, datetime.time.min)
        day_end = datetime.datetime.combine(day, datetime.time.max)

        day_total = (
            db.query(Inspection)
            .filter(Inspection.timestamp >= day_start, Inspection.timestamp <= day_end)
            .count()
        )
        day_defective = (
            db.query(Inspection)
            .filter(
                Inspection.timestamp >= day_start,
                Inspection.timestamp <= day_end,
                Inspection.total_defects > 0
            )
            .count()
        )
        trends.append(
            TrendItem(
                date=day.strftime("%b %d"),
                total=day_total,
                defective=day_defective,
                defect_free=max(0, day_total - day_defective)
            )
        )

    # Active hardware device info
    device_info = model_manager.get_device_info()
    dataset_catalog = dataset_manager.list_all()

    return DashboardSummaryResponse(
        metrics=metrics,
        recent_inspections=recent,
        defect_distribution=distribution,
        inspection_trends=trends,
        active_model=model_manager.active_model_name,
        device_info=f"{device_info['device'].upper()} ({device_info['device_name']})",
        gemini_status=bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5),
        dataset_status={
            d["name"]: {"downloaded": d["is_downloaded"], "images": d["total_images"]}
            for d in dataset_catalog
        }
    )
