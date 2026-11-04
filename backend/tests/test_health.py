import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data
    assert "device" in data
    assert data["database_connected"] is True

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
