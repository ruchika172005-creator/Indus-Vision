# Industrial Quality Inspection & Defect Explanation System — Backend

High-performance FastAPI service integrating **Ultralytics YOLOv8** computer vision, **Google Gemini Multimodal Vision-Language** explanation, transparent **Defect Severity Assessment Engine**, and **ReportLab PDF report generation**.

---

## 🏗️ Backend Architecture

- **Web Framework:** FastAPI 0.110+ & Uvicorn (ASGI)
- **Object Detection:** Ultralytics YOLOv8 (CPU/CUDA auto-discovery)
- **Multimodal AI:** Google Gemini API (gemini-1.5-flash / gemini-1.5-pro) with expert Rule-Based Fallback
- **Database:** SQLite (default) / PostgreSQL compatible via SQLAlchemy 2.0 ORM
- **Inspection Reporting:** ReportLab PDF Generation & CSV Streaming
- **Image Processing:** OpenCV & Pillow

---

## 🚀 Getting Started (Windows PowerShell)

```powershell
cd backend

# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Launch backend API server
python -m uvicorn app.main:app --reload --port 8000
```

- **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🧪 Automated Testing

Run the automated pytest test suite:

```powershell
python -m pytest tests/ -v
```

Tests verify:
- Health check & database connection
- Explainable severity assessment calculation
- GenAI JSON response validation & rule-based fallback
- ReportLab PDF generation
- End-to-end sample inspection pipeline

---

## 📦 Dataset Preparation & Model Training

```powershell
# Prepare NEU-DET (steel surface defect dataset)
python scripts/prepare_neu_det.py

# Prepare GC10-DET (metallic sheet defect dataset)
python scripts/prepare_gc10.py

# Fine-tune YOLOv8 on prepared dataset
python scripts/train_yolo.py --dataset neu_det --epochs 50 --batch 16 --imgsz 640

# Benchmark model evaluation
python scripts/evaluate_model.py --weights weights/yolov8n_neu_det.pt --data datasets/neu_det/dataset.yaml
```
