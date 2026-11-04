import os
from pathlib import Path
from app.reports.pdf_generator import PDFReportGenerator
from app.core.config import settings

def test_pdf_report_generation():
    generator = PDFReportGenerator()
    test_pdf_path = str(settings.REPORTS_DIR / "test_audit_report.pdf")

    sample_data = {
        "inspection_code": "TEST-QA-101",
        "timestamp": "2026-10-30T10:00:00",
        "product_name": "Test Coil Steel",
        "product_category": "Coil Sheet",
        "model_name": "YOLOv8n-NEU-DET",
        "inference_time_ms": 15.2,
        "total_defects": 1,
        "max_severity": "MEDIUM",
        "overall_decision": "MANUAL_REVIEW",
        "inference_source": "YOLO Model Inference",
        "annotated_image_path": None,
        "original_image_path": None,
        "defects": [
            {
                "defect_name": "Scratches",
                "confidence": 0.91,
                "bbox": [50.0, 100.0, 400.0, 150.0],
                "area_ratio": 0.045,
                "severity_level": "MEDIUM"
            }
        ],
        "explanation": {
            "defect_name": "Scratches",
            "description": "Longitudinal scratch abrasion mark.",
            "location": "Upper-central region",
            "severity": "MEDIUM",
            "possible_causes": ["Guide roller misalignment"],
            "recommended_actions": ["Polish contact roller"],
            "quality_summary": "Passed with secondary inspection required.",
            "provider_used": "Test Rule Engine"
        }
    }

    out_path = generator.generate_inspection_report(sample_data, test_pdf_path)
    assert Path(out_path).exists()
    assert os.path.getsize(out_path) > 1000 # Valid non-empty PDF
    # Cleanup
    try:
        os.remove(out_path)
    except OSError:
        pass
