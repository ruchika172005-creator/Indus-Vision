import pytest
from app.ml.severity_engine import SeverityEngine

def test_clean_part_pass():
    engine = SeverityEngine()
    decision, max_sev, meta = engine.evaluate_inspection([], 640, 640)
    assert decision == "PASS"
    assert max_sev == "LOW"

def test_critical_defect_fail():
    engine = SeverityEngine()
    # Large inclusion occupying significant area
    defect = engine.evaluate_defect(
        defect_name="inclusion",
        bbox=[100, 100, 450, 450], # Large area
        image_width=640,
        image_height=640,
        confidence=0.95
    )
    assert defect["severity_level"] in ["HIGH", "CRITICAL"]

    decision, max_sev, _ = engine.evaluate_inspection([defect], 640, 640)
    assert decision in ["FAIL", "MANUAL_REVIEW"]

def test_minor_scratch_advisory():
    engine = SeverityEngine()
    defect = engine.evaluate_defect(
        defect_name="scratches",
        bbox=[10, 10, 50, 30], # Tiny area
        image_width=640,
        image_height=640,
        confidence=0.60
    )
    assert defect["severity_level"] == "LOW"
    decision, max_sev, _ = engine.evaluate_inspection([defect], 640, 640)
    assert decision == "PASS"
