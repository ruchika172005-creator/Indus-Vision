import pytest
from app.genai.response_validator import ResponseValidator
from app.genai.explanation_generator import ExplanationGenerator

def test_response_validator_valid_json():
    raw_json = """
    ```json
    {
      "defect_name": "Surface Scratch",
      "description": "Continuous abrasion groove.",
      "location": "Upper-right region",
      "severity": "Medium",
      "possible_causes": ["Mechanical roller rubbing"],
      "recommended_actions": ["Polish guide plates"],
      "inspection_decision": "MANUAL_REVIEW"
    }
    ```
    """
    parsed = ResponseValidator.parse_and_validate(raw_json)
    assert parsed["defect_name"] == "Surface Scratch"
    assert parsed["severity"] == "MEDIUM"
    assert len(parsed["possible_causes"]) == 1
    assert parsed["inspection_decision"] == "MANUAL_REVIEW"

def test_rule_based_fallback_explanation():
    gen = ExplanationGenerator()
    defects = [{
        "defect_name": "Crazing",
        "confidence": 0.88,
        "bbox": [100.0, 100.0, 400.0, 400.0],
        "severity_level": "HIGH"
    }]
    result = gen._generate_rule_based(
        defects=defects,
        product_category="Steel Plate",
        detection_metadata={"decision": "MANUAL_REVIEW", "max_severity": "HIGH"},
        img_w=640,
        img_h=640
    )
    assert result["defect_name"] == "Crazing"
    assert "crack" in result["description"].lower() or "fissure" in result["description"].lower()
    assert len(result["possible_causes"]) >= 2
    assert len(result["recommended_actions"]) >= 2
    assert "Rule-Based" in result["provider_used"]
