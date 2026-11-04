import io
import time
import httpx
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================")
    print(" Running Full End-to-End API Diagnostic Test Suite")
    print("==================================================")
    
    passed = 0
    failed = 0
    client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    def test(name, fn):
        nonlocal passed, failed
        try:
            fn()
            print(f" [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f" [FAIL] {name}: {e}")
            failed += 1

    # 1. Root & Health
    def t_root():
        r = client.get("/")
        assert r.status_code == 200, f"Status: {r.status_code}"
        assert r.json().get("status") == "online"
    test("GET / (Root endpoint)", t_root)

    def t_health():
        r = client.get("/api/health")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert data["database_connected"] is True
        assert data["status"] in ["healthy", "degraded"]
    test("GET /api/health (System diagnostic)", t_health)

    # 2. Dashboard
    def t_dashboard():
        r = client.get("/api/dashboard/summary")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert "metrics" in data
        assert "recent_inspections" in data
        assert "defect_distribution" in data
        assert "inspection_trends" in data
    test("GET /api/dashboard/summary", t_dashboard)

    # 3. Samples
    def t_samples():
        r = client.get("/api/inspection/samples")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert "samples" in data
        assert len(data["samples"]) >= 6
    test("GET /api/inspection/samples", t_samples)

    # 4. Image Upload (valid and invalid)
    uploaded_filename = None
    def t_upload_valid():
        nonlocal uploaded_filename
        # Create a small in-memory JPEG
        img = Image.new("RGB", (100, 100), color=(180, 180, 180))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        files = {"file": ("test_part.jpg", buf, "image/jpeg")}
        r = client.post("/api/inspection/upload", files=files)
        assert r.status_code == 200, f"Status: {r.status_code}: {r.text}"
        data = r.json()
        assert "filename" in data
        uploaded_filename = data["filename"]
    test("POST /api/inspection/upload (Valid image)", t_upload_valid)

    def t_upload_invalid():
        files = {"file": ("malicious.exe", io.BytesIO(b"binary"), "application/octet-stream")}
        r = client.post("/api/inspection/upload", files=files)
        assert r.status_code == 400, f"Expected 400, got: {r.status_code}"
    test("POST /api/inspection/upload (Rejection of invalid format)", t_upload_invalid)

    # 5. Inspection Analysis
    created_inspection_id = None
    def t_analyze_sample():
        nonlocal created_inspection_id
        r = client.post(
            "/api/inspection/analyze",
            data={
                "sample_filename": "demo_sample_scratches.jpg",
                "product_name": "API Test Coil",
                "product_category": "Coil Steel",
                "conf_threshold": "0.35"
            }
        )
        assert r.status_code == 200, f"Status: {r.status_code}: {r.text}"
        data = r.json()
        assert data["id"] > 0
        assert data["overall_decision"] in ["PASS", "FAIL", "MANUAL_REVIEW"]
        assert "explanation" in data
        assert len(data["explanation"]["possible_causes"]) > 0
        created_inspection_id = data["id"]
    test("POST /api/inspection/analyze (Demo sample trigger)", t_analyze_sample)

    def t_analyze_upload():
        if not uploaded_filename:
            return
        r = client.post(
            "/api/inspection/analyze",
            data={
                "image_path": uploaded_filename,
                "product_name": "API Uploaded Test",
                "product_category": "Steel Plate"
            }
        )
        assert r.status_code == 200, f"Status: {r.status_code}: {r.text}"
    test("POST /api/inspection/analyze (Uploaded image trigger)", t_analyze_upload)

    def t_analyze_missing():
        r = client.post("/api/inspection/analyze", data={})
        assert r.status_code == 400, f"Expected 400, got: {r.status_code}"
    test("POST /api/inspection/analyze (Missing image rejection)", t_analyze_missing)

    # 6. Inspection History & Single Read
    def t_history():
        r = client.get("/api/inspection/history?limit=10")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0
    test("GET /api/inspection/history", t_history)

    def t_history_filters():
        r = client.get("/api/inspection/history?severity=HIGH&decision=MANUAL_REVIEW")
        assert r.status_code == 200, f"Status: {r.status_code}"
    test("GET /api/inspection/history (Filters)", t_history_filters)

    def t_get_inspection():
        assert created_inspection_id is not None
        r = client.get(f"/api/inspection/{created_inspection_id}")
        assert r.status_code == 200, f"Status: {r.status_code}"
        assert r.json()["id"] == created_inspection_id
    test(f"GET /api/inspection/{{id}}", t_get_inspection)

    # 7. Datasets
    def t_datasets():
        r = client.get("/api/datasets")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert len(data) == 3
        names = [d["name"] for d in data]
        assert "neu_det" in names
        assert "gc10_det" in names
        assert "mvtec_ad" in names
    test("GET /api/datasets", t_datasets)

    def t_dataset_stats():
        r = client.get("/api/datasets/neu_det/statistics")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert data["name"] == "neu_det"
        assert "classes" in data
    test("GET /api/datasets/{name}/statistics", t_dataset_stats)

    def t_dataset_download():
        r = client.post("/api/datasets/neu_det/download")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert data["success"] is True
        assert "data" in data
    test("POST /api/datasets/{name}/download", t_dataset_download)

    # 8. Models
    def t_models():
        r = client.get("/api/models")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert len(data) >= 3
    test("GET /api/models", t_models)

    def t_select_active_model():
        r = client.post("/api/models/select-active?model_name=YOLOv8n-NEU-DET")
        assert r.status_code == 200, f"Status: {r.status_code}"
        assert r.json()["active_model"] == "YOLOv8n-NEU-DET"
    test("POST /api/models/select-active", t_select_active_model)

    training_job_id = None
    def t_train_model():
        nonlocal training_job_id
        r = client.post(
            "/api/models/train",
            json={
                "model_name": "diagnostic_yolo",
                "dataset_name": "neu_det",
                "epochs": 10,
                "batch_size": 8,
                "img_size": 640,
                "device": "cpu"
            }
        )
        assert r.status_code == 200, f"Status: {r.status_code}: {r.text}"
        data = r.json()
        assert "job_id" in data
        training_job_id = data["job_id"]
    test("POST /api/models/train (Background job launch)", t_train_model)

    def t_training_status():
        assert training_job_id is not None
        time.sleep(0.5)
        r = client.get(f"/api/models/training-status/{training_job_id}")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert data["job_id"] == training_job_id
    test("GET /api/models/training-status/{job_id}", t_training_status)

    # 9. Reports
    generated_pdf_filename = None
    def t_generate_pdf():
        nonlocal generated_pdf_filename
        assert created_inspection_id is not None
        r = client.post(f"/api/reports/{created_inspection_id}/pdf")
        assert r.status_code == 200, f"Status: {r.status_code}: {r.text}"
        data = r.json()
        assert data["success"] is True
        assert "filename" in data
        generated_pdf_filename = data["filename"]
    test("POST /api/reports/{id}/pdf (ReportLab PDF compiler)", t_generate_pdf)

    def t_download_pdf():
        assert generated_pdf_filename is not None
        r = client.get(f"/api/reports/download/{generated_pdf_filename}")
        assert r.status_code == 200, f"Status: {r.status_code}"
        assert r.headers.get("content-type") == "application/pdf"
        assert len(r.content) > 1000
    test("GET /api/reports/download/{filename}", t_download_pdf)

    def t_export_csv():
        r = client.get("/api/reports/export-csv")
        assert r.status_code == 200, f"Status: {r.status_code}"
        assert "text/csv" in r.headers.get("content-type", "")
        assert b"Inspection ID" in r.content
    test("GET /api/reports/export-csv", t_export_csv)

    def t_list_reports():
        r = client.get("/api/reports")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert isinstance(data, list)
    test("GET /api/reports", t_list_reports)

    # 10. Analytics
    def t_analytics_defects():
        r = client.get("/api/analytics/defects")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert "by_category" in data
        assert "by_severity" in data
    test("GET /api/analytics/defects", t_analytics_defects)

    def t_analytics_trends():
        r = client.get("/api/analytics/trends?days=7")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert "trends" in data
        assert len(data["trends"]) == 7
    test("GET /api/analytics/trends", t_analytics_trends)

    # 11. Settings
    def t_get_settings():
        r = client.get("/api/settings")
        assert r.status_code == 200, f"Status: {r.status_code}"
        data = r.json()
        assert "confidence_threshold" in data
        assert "gemini_model" in data
    test("GET /api/settings", t_get_settings)

    def t_put_settings():
        r = client.put(
            "/api/settings",
            json={
                "confidence_threshold": 0.38,
                "gemini_model": "gemini-1.5-flash"
            }
        )
        assert r.status_code == 200, f"Status: {r.status_code}"
        assert r.json()["confidence_threshold"] == 0.38
    test("PUT /api/settings", t_put_settings)

    # 12. Delete
    def t_delete():
        assert created_inspection_id is not None
        r = client.delete(f"/api/inspection/{created_inspection_id}")
        assert r.status_code == 200, f"Status: {r.status_code}"
    test(f"DELETE /api/inspection/{{id}}", t_delete)

    print("==================================================")
    print(f" Diagnostic Summary: {passed} PASSED, {failed} FAILED")
    print("==================================================")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
