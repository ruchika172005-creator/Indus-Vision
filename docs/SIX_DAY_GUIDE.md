# 📅 Six-Day Development & Final Demonstration Guide
## Multimodal AI-Based Industrial Quality Inspection and Defect Explanation System

---

## 🎯 Demonstration Objective
This guide outlines the systematic walkthrough for presenting this Final-Year B.Tech project to academic evaluators, university project committees, and industrial reviewers.

---

### 🗓️ Day 1: Problem Statement, Architectural Defense & System Initialization

#### 1. Presentation Talking Points
- **The Core Industrial Problem:** Traditional automated optical inspection (AOI) identifies that a flaw exists, but leaves the machine operator guessing *why* it occurred, *how severe* it is structurally, and *what corrective machine actions* must be taken.
- **The Solution:** Combining YOLOv8 computer vision detection with Multimodal Vision-Language Models (Google Gemini) and an Explainable Severity Assessment Engine.

#### 2. Demonstration Steps
1. Open PowerShell Terminal 1:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --port 8000
   ```
2. Open PowerShell Terminal 2:
   ```powershell
   cd frontend
   npm run dev
   ```
3. Open browser at `http://localhost:5173`.
4. Showcase the dark navy enterprise sidebar, system connectivity indicator, and clean light dashboard.
5. Open Swagger docs at `http://localhost:8000/docs` to demonstrate standard OpenAPI 3.0 REST endpoints.

---

### 🗓️ Day 2: Industrial Defect Datasets & Annotation Conversion Pipeline

#### 1. Presentation Talking Points
- Demonstrate support for three major industrial defect benchmarks:
  - **NEU-DET:** 6 steel surface defect categories (~1,800 images).
  - **GC10-DET:** 10 metallic surface defect categories (~3,570 images).
  - **MVTec AD:** Industrial anomaly detection benchmark with pixel-level ground truth masks.
- **Academic Rigor:** Highlight that the project never fabricates fake dataset downloads. The UI reflects genuine on-disk file counts.

#### 2. Demonstration Steps
1. Navigate to **Dataset Management** in the left sidebar.
2. Review the three dataset cards showing real image counts and download status.
3. Click **"Download Guide"** on NEU-DET to reveal official Northeastern University source links and folder structure requirements.
4. Explain how `annotation_converter.py` converts raw Pascal VOC XML (`<bndbox><xmin>...`) into normalized YOLO coordinates (`class_id x_center y_center width height`).

---

### 🗓️ Day 3: Computer Vision & Model Management

#### 1. Presentation Talking Points
- Explain Ultralytics YOLOv8 architecture for single-stage defect localization.
- Auto-hardware discovery: Automatically detects whether NVIDIA CUDA GPU or CPU is available.
- Model registry tracks file existence, Precision, Recall, mAP@50, and mAP@50-95.

#### 2. Demonstration Steps
1. Navigate to **Model Management** page.
2. Showcase the registered checkpoints: `YOLOv8n-NEU-DET`, `YOLOv8n-GC10-DET`, and `YOLOv8n-Base`.
3. Submit a background fine-tuning job using the form:
   - Select Dataset: `NEU-DET`
   - Set Epochs: `25`
   - Click **"Launch Background Training Job"**.
4. Point out that the REST API does not freeze; the job runs asynchronously, updating progress, loss convergence, and epoch numbers in real-time.

---

### 🗓️ Day 4: Multimodal Generative AI & Prompt Engineering

#### 1. Presentation Talking Points
- Explain why Generative AI is the critical differentiator: It bridges optical pixels to metallurgical engineering decisions.
- **Safety & Grounding Rules:**
  - Bounding boxes and confidence originate *strictly* from the computer vision model, never hallucinated by the LLM.
  - The VLM is instructed to distinguish between **observed physical facts** (surface appearance) and **hypotheses** (root causes).
- **Rule-Based Fallback:** If the Gemini API key is missing or offline, the system seamlessly activates the internal metallurgical knowledge base, ensuring zero downtime.

#### 2. Demonstration Steps
1. Navigate to **System Settings**.
2. Show that Gemini API key can be updated dynamically without restarting the server.
3. Show the active prompt template in `backend/app/genai/prompt_templates.py`.

---

### 🗓️ Day 5: Explainable Severity Engine & Quality Decision Rules

#### 1. Presentation Talking Points
- Explain the transparent severity formula:
  $$Score = \left(0.45 \cdot \frac{AreaRatio}{CriticalAreaRatio} + 0.35 \cdot CatWeight + 0.20 \cdot Confidence\right) \times 100$$
- Defect categories have inherent metallurgical risk factors (e.g., Crazing = 0.85, Inclusion = 0.90, Superficial Scratch = 0.50).
- Explainable dispositions:
  - **PASS:** 0 defects or isolated low-severity cosmetic deviation.
  - **FAIL:** Presence of critical flaws (Inclusions/Cracks) or $> 4$ total defects.
  - **MANUAL REVIEW:** Moderate severity requiring supervisor optical signoff.

#### 2. Demonstration Steps
1. In **Settings**, adjust the Critical Area Ratio slider and save.
2. Walk evaluators through the logic in `backend/app/ml/severity_engine.py`.

---

### 🗓️ Day 6: Live Inspection Walkthrough, PDF Reports & Examiner Q&A

#### 1. Live Inspection Demonstration
1. Navigate to **Live Inspection**.
2. Click **"Crazing"** in the Quick Sample Picker.
3. Click **"Start Quality Inspection"**.
4. Observe:
   - Scanning animation.
   - Dual-tab image display: Toggle between Original and Annotated image with corner brackets and crosshairs.
   - Detected defect coordinates table: `[x1, y1, x2, y2]`, Confidence %, Area %.
   - High-severity badge and **MANUAL REVIEW** decision.
   - Multimodal AI explanation detailing thermal fatigue causes and cooling nozzle adjustments.
5. Click **"Live Webcam Snapshot"** to demonstrate hardware camera capture with crosshair viewfinder.
6. Click **"Download Official PDF Report"**: Open the generated ReportLab PDF showing company headers, embedded annotated imagery, and signoff blocks.
7. Open **Quality Analytics** to showcase Recharts Pareto charts and defect trends.

---

## 🎓 Viva / Examiner Q&A Preparation

**Q1: Why not use an End-to-End Multimodal LLM to detect bounding boxes directly?**
*Answer:* Current Vision-Language Models have high localization jitter and latency (2-5 seconds), making them unsuitable for high-speed industrial conveyor lines. Our hybrid architecture uses YOLOv8 for sub-30ms millisecond-level precision localization, and leverages the VLM where it excels: domain reasoning, causal diagnosis, and corrective action synthesis.

**Q2: What happens if the manufacturing plant has no internet connection?**
*Answer:* The system features an automatic Rule-Based Industrial Expert Engine fallback that provides full metallurgical explanations, causes, and corrective actions completely offline.

**Q3: How are false positives mitigated?**
*Answer:* Operators can tune confidence thresholds and NMS IoU overlap sliders directly from the UI, and isolated low-severity deviations trigger a manual review disposition rather than an outright line stoppage.
