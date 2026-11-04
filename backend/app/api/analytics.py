import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.db_models import Inspection, DetectedDefect

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/defects")
def get_defect_analytics(db: Session = Depends(get_db)):
    """
    Computes statistical distribution across defect categories, severity levels,
    and identifies the top root defect modes.
    """
    total_inspections = db.query(Inspection).count()
    defective_inspections = db.query(Inspection).filter(Inspection.total_defects > 0).count()
    defect_rate = round((defective_inspections / max(1, total_inspections)) * 100.0, 1)

    # By category
    cat_rows = (
        db.query(DetectedDefect.defect_name, func.count(DetectedDefect.id))
        .group_by(DetectedDefect.defect_name)
        .order_by(func.count(DetectedDefect.id).desc())
        .all()
    )
    total_defects = sum(c for _, c in cat_rows) or 1
    by_category = [
        {"name": name, "count": count, "percentage": round((count / total_defects) * 100.0, 1)}
        for name, count in cat_rows
    ]

    # By severity
    sev_rows = (
        db.query(DetectedDefect.severity_level, func.count(DetectedDefect.id))
        .group_by(DetectedDefect.severity_level)
        .all()
    )
    by_severity = [
        {"severity": sev, "count": count, "percentage": round((count / total_defects) * 100.0, 1)}
        for sev, count in sev_rows
    ]

    # Most frequent (top 5)
    most_frequent = by_category[:5]

    return {
        "total_analyzed": total_inspections,
        "total_defects_found": sum(c for _, c in cat_rows),
        "defect_rate_overall": defect_rate,
        "by_category": by_category,
        "by_severity": by_severity,
        "most_frequent": most_frequent
    }

@router.get("/trends")
def get_trend_analytics(days: int = 14, db: Session = Depends(get_db)):
    """
    Returns daily inspection throughput, defect frequencies, and pass/fail disposition trends.
    """
    today = datetime.datetime.now(datetime.timezone.utc).date()
    daily_trends = []

    for i in range(days - 1, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_start = datetime.datetime.combine(day, datetime.time.min)
        day_end = datetime.datetime.combine(day, datetime.time.max)

        day_total = (
            db.query(Inspection)
            .filter(Inspection.timestamp >= day_start, Inspection.timestamp <= day_end)
            .count()
        )
        day_pass = (
            db.query(Inspection)
            .filter(
                Inspection.timestamp >= day_start,
                Inspection.timestamp <= day_end,
                Inspection.overall_decision == "PASS"
            )
            .count()
        )
        day_fail = (
            db.query(Inspection)
            .filter(
                Inspection.timestamp >= day_start,
                Inspection.timestamp <= day_end,
                Inspection.overall_decision == "FAIL"
            )
            .count()
        )
        day_review = (
            db.query(Inspection)
            .filter(
                Inspection.timestamp >= day_start,
                Inspection.timestamp <= day_end,
                Inspection.overall_decision == "MANUAL_REVIEW"
            )
            .count()
        )

        daily_trends.append({
            "date": day.strftime("%b %d"),
            "total": day_total,
            "pass": day_pass,
            "fail": day_fail,
            "review": day_review,
            "defect_rate": round((day_fail + day_review) / max(1, day_total) * 100.0, 1) if day_total > 0 else 0.0
        })

    return {"trends": daily_trends}
