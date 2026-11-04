import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_samples():
    response = client.get("/api/inspection/samples")
    assert response.status_code == 200
    data = response.json()
    assert "samples" in data
    assert len(data["samples"]) >= 6

def test_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert data["metrics"]["total_inspections"] >= 8
    assert "defect_distribution" in data
    assert "inspection_trends" in data

def test_list_datasets():
    response = client.get("/api/datasets")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) == 3
    names = [d["name"] for d in datasets]
    assert "neu_det" in names
    assert "gc10_det" in names
    assert "mvtec_ad" in names

def test_list_models():
    response = client.get("/api/models")
    assert response.status_code == 200
    models = response.json()
    assert len(models) >= 2
    assert any(m["name"] == "YOLOv8n-NEU-DET" for m in models)

def test_analyze_sample_image():
    # Test analyze with clean steel sample
    response = client.post(
        "/api/inspection/analyze",
        data={
            "sample_filename": "demo_sample_clean_steel.jpg",
            "product_name": "Test Plate",
            "product_category": "Sheet Metal"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["overall_decision"] == "PASS"
    assert result["total_defects"] == 0
    assert "explanation" in result
    assert result["explanation"]["inspection_decision"] == "PASS"
