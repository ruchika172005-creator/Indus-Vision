import os
import io
import csv
import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import Inspection, GeneratedReport
from app.reports.pdf_generator import pdf_report_generator
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/{inspection_id}/pdf")
def create_pdf_report(inspection_id: int, db: Session = Depends(get_db)):
    """
    Generates an official QA audit PDF inspection report using ReportLab.
    """
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    filename = f"Inspection_Report_{insp.inspection_code}.pdf"
    pdf_path = str(settings.REPORTS_DIR / filename)

    # Format inspection data
    defects_data = []
    for d in insp.defects:
        defects_data.append({
            "defect_name": d.defect_name,
            "confidence": d.confidence,
            "bbox": [d.bbox_x1, d.bbox_y1, d.bbox_x2, d.bbox_y2],
            "area_ratio": d.area_ratio,
            "severity_level": d.severity_level
        })

    causes = []
    actions = []
    try:
        if insp.genai_possible_causes:
            causes = json.loads(insp.genai_possible_causes)
    except Exception:
        causes = [insp.genai_possible_causes] if insp.genai_possible_causes else []

    try:
        if insp.genai_recommended_actions:
            actions = json.loads(insp.genai_recommended_actions)
    except Exception:
        actions = [insp.genai_recommended_actions] if insp.genai_recommended_actions else []

    payload = {
        "inspection_code": insp.inspection_code,
        "timestamp": insp.timestamp.isoformat(),
        "product_name": insp.product_name,
        "product_category": insp.product_category,
        "model_name": insp.model_name,
        "inference_time_ms": insp.inference_time_ms,
        "total_defects": insp.total_defects,
        "max_severity": insp.max_severity,
        "overall_decision": insp.overall_decision,
        "inference_source": insp.inference_source,
        "annotated_image_path": insp.annotated_image_path,
        "original_image_path": insp.original_image_path,
        "defects": defects_data,
        "explanation": {
            "defect_name": insp.genai_defect_name or "None",
            "description": insp.genai_description or "",
            "location": insp.genai_location or "Full surface",
            "severity": insp.genai_severity or insp.max_severity,
            "possible_causes": causes,
            "recommended_actions": actions,
            "quality_summary": insp.genai_quality_summary,
            "provider_used": insp.genai_provider_used or "Rule-Based Engine"
        }
    }

    try:
        pdf_report_generator.generate_inspection_report(payload, pdf_path)
    except Exception as e:
        logger.error(f"PDF creation failure: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    file_size_kb = round(os.path.getsize(pdf_path) / 1024.0, 1)

    # Record in DB
    report_record = GeneratedReport(
        inspection_id=insp.id,
        report_type="PDF",
        filename=filename,
        file_path=pdf_path,
        file_size_kb=file_size_kb
    )
    db.add(report_record)
    db.commit()

    return {
        "success": True,
        "filename": filename,
        "download_url": f"/api/reports/download/{filename}",
        "file_size_kb": file_size_kb
    }

@router.get("/download/{filename}")
def download_report_file(filename: str):
    """Serves the generated PDF file directly to browser for download."""
    path = settings.REPORTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Requested report file does not exist.")
    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=filename
    )

@router.get("/export-csv")
def export_inspections_csv(db: Session = Depends(get_db)):
    """
    Exports historical inspections as a CSV spreadsheet.
    """
    inspections = db.query(Inspection).order_by(Inspection.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Inspection ID",
        "Inspection Code",
        "Date Time (UTC)",
        "Product Name",
        "Category",
        "Total Defects",
        "Max Severity",
        "Decision",
        "Confidence Avg",
        "Primary Defect",
        "Inference Model",
        "Latency (ms)",
        "Inference Source",
        "AI Engine"
    ])

    for i in inspections:
        writer.writerow([
            i.id,
            i.inspection_code,
            i.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            i.product_name,
            i.product_category,
            i.total_defects,
            i.max_severity,
            i.overall_decision,
            f"{i.confidence_avg:.3f}",
            i.genai_defect_name or "None",
            i.model_name,
            f"{i.inference_time_ms:.1f}",
            i.inference_source,
            i.genai_provider_used or "Rule Engine"
        ])

    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=industrial_inspections_export.csv"
    return response

@router.get("")
def list_generated_reports(db: Session = Depends(get_db)):
    """Returns list of generated reports with file sizes and timestamps."""
    reports = db.query(GeneratedReport).order_by(GeneratedReport.generated_at.desc()).limit(50).all()
    return [
        {
            "id": r.id,
            "inspection_id": r.inspection_id,
            "report_type": r.report_type,
            "filename": r.filename,
            "file_size_kb": r.file_size_kb,
            "download_url": f"/api/reports/download/{r.filename}",
            "generated_at": r.generated_at.isoformat()
        }
        for r in reports
    ]
