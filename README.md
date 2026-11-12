Indus Vision
A Multimodal AI-Based Industrial Quality Inspection and Defect Explanation System
Indus Vision is a web-based industrial quality inspection prototype that
combines computer vision and multimodal Generative AI to help users
inspect product images, identify visible defects, understand detection
results, and prepare inspection reports.

The system separates three responsibilities:
- Computer vision: detects and localizes visible defects.
- Severity assessment: applies configurable rules to classify
  inspection risk.
- Generative AI: turns image context and detection metadata into a
  readable explanation, possible causes, and recommended next actions.
Project status: Academic/demo prototype. Results depend on the
model checkpoint, dataset, and configuration. Generated explanations
are decision-support text, not certified engineering conclusions.

Table of Contents
- Features
- Architecture
- Technology Stack
- Datasets
- Project Structure
- Prerequisites
- Installation
- Environment Configuration
- Run the Application
- Using the Application
- API Documentation
- Training and Evaluation
- Testing
- Troubleshooting
- Limitations
- Future Enhancements
- Contributing
- License
Features
- Upload industrial/product images for inspection.
- Detect and localize visible defects using a compatible YOLOv8 model.
- Display defect labels, confidence scores, bounding boxes, and
  annotated images.
- Classify severity using configurable rules (LOW, MEDIUM, HIGH,
  CRITICAL).
- Support inspection dispositions such as PASS, FAIL, or MANUAL_REVIEW
  according to configured rules.
- Generate multimodal defect explanations using the configured Google
  Gemini integration.
- Provide a rule-based fallback explanation when supported and when
  Gemini is unavailable.
- Support dataset preparation/integration workflows for NEU-DET,
  GC10-DET, and MVTec AD.
- Review inspection history and analytics.
- Generate PDF inspection reports and export tabular data where
  enabled.
- Run frontend and backend independently in separate terminals.
Architecture
                 USER / INSPECTOR
                        |
                        v
          REACT + TYPESCRIPT FRONTEND
       Dashboard | Upload | Results | Reports
                        |
                    REST API
                        |
                        v
                 FASTAPI BACKEND
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
  YOLOv8 Detector  Severity Rules   Gemini VLM
       |                |          / Rule Fallback
       +----------------+----------------+
                        |
                        v
              SQLALCHEMY DATABASE
                        |
                        v
                PDF / CSV REPORTS
Inspection workflow
1. Upload an industrial image through the frontend.
2. The frontend sends the image to the FastAPI backend.
3. The backend validates the file and invokes the configured detector.
4. The detector returns defect classes, confidence scores, and
   bounding-box coordinates.
5. The severity engine applies configured inspection rules.
6. The multimodal component generates an explanation from the image and
   detection metadata, when configured.
7. The backend stores inspection information and returns the result.
8. The user reviews the annotated image, explanation, severity, and
   decision.
Technology Stack
  Layer                   Technologies            Purpose
  Frontend                React, TypeScript, Vite Web interface

  Styling                 Tailwind CSS            Responsive UI

  Charts                  Recharts                Analytics
visualizations

  API client              Axios                   HTTP communication

  Backend                 Python, FastAPI,        REST API and
Uvicorn                 application logic

  Computer vision         Ultralytics YOLOv8,     Detection and image
OpenCV, Pillow          processing

  Deep learning           PyTorch                 Model
execution/training

  Generative AI           Google Gemini API       Multimodal explanations

  Database                SQLAlchemy, SQLite;     Persistent records
PostgreSQL-compatible
configuration           

  Reporting               ReportLab               PDF generation

  Testing                 Pytest                  Backend tests
Version control         Git, GitHub             Source management
Datasets
The project documentation identifies these industrial benchmark
datasets:
  Dataset                 Description             Annotation / task
  NEU-DET             Steel surface defects,  Bounding-box detection;
including crazing,      Pascal VOC XML
inclusion, patches,     annotations can be
pitted surface,         converted to YOLO
rolled-in scale, and    format.
scratches.              

  GC10-DET            Metallic surface defect Bounding-box detection
dataset with ten defect using its source
categories.             annotations and class
mapping.
MVTec AD            Industrial anomaly      Image-level and
dataset with normal and pixel-level anomaly
anomalous samples       evaluation using
across object and       ground-truth masks; not
texture categories.     a standard YOLO
bounding-box dataset.
Dataset notes
- Download data from official or authorized sources and follow their
  terms of use.
- Dataset files may not be included in this Git repository; use the
  preparation scripts and instructions available in the codebase.
- Validate downloaded images and annotations before training.
- Keep MVTec AD masks in their task-appropriate representation unless
  a specific conversion method is implemented.
- Report only metrics measured on an actual, documented test split.
Project Structure
The application keeps frontend and backend code in separate directories.
Indus-Vision/
├── backend/
│   ├── app/                 # FastAPI application and backend modules
│   ├── tests/               # Backend tests, if included
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Example configuration, if included
├── frontend/
│   ├── src/                 # React application source
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies and scripts
│   └── vite.config.ts       # Vite configuration
└── README.md
This is a high-level guide. Exact files and subfolders can differ
between repository versions. Check the actual directories before
running commands that refer to a particular file.

Prerequisites
- Git
- Python version supported by the backend dependencies
- Node.js and npm
- A modern web browser
- Optional: Google Gemini API key for cloud-based multimodal
  explanations
- Optional: compatible NVIDIA GPU/CUDA setup for faster model training
  or inference
CPU execution may be slower, especially for model training and
inference.
Installation
1. Clone the repository
git clone https://github.com/ruchika172005-creator/Indus-Vision.git
cd Indus-Vision
2. Backend setup --- Terminal 1
From the repository root:
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
If the repository contains .env.example, copy it to .env:
Copy-Item .env.example .env
Edit the local .env values as required. Do not overwrite an existing
.env without backing it up.
3. Frontend setup --- Terminal 2
Open a second terminal at the repository root:
cd frontend
npm install
Environment Configuration
Check backend/.env.example and the backend configuration code for the
exact variable names expected by the current version.

A typical configuration may resemble:
# Example only: use the exact variable names expected by your backend
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./indus_vision.db
- Keep real API keys in the backend .env file.
- Never commit .env, passwords, or credentials to GitHub.
- Keep .env.example limited to safe placeholder values.
- Never expose the Gemini API key in frontend/browser code.
- If Gemini is not configured, use the documented fallback mode if
  available.
Run the Application
Run the backend and frontend in two separate terminals.
Terminal 1 --- Backend
From the repository root:
cd backend
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
Backend base URL: http://127.0.0.1:8000

Swagger API documentation: http://127.0.0.1:8000/docs
Terminal 2 --- Frontend
From the repository root:
cd frontend
npm run dev
Open the local URL printed by Vite. The default is commonly
http://localhost:5173; if Vite selects another port, use the URL shown
in the terminal.
Build the frontend
cd frontend
npm run build
If the backend does not start, verify the virtual environment, installed
dependencies, working directory, and Uvicorn import path. If the
frontend cannot reach the backend, check its API base URL and the
backend CORS configuration.
Using the Application
1. Open the frontend in your browser.
2. Navigate to the image inspection page.
3. Upload a supported product/material image.
4. Select an available model or inspection configuration.
5. Start the inspection.
6. Review the original and annotated images.
7. Examine defect labels, confidence scores, and locations.
8. Review severity and the inspection disposition.
9. Read the generated explanation and recommended actions.
10. Save the inspection or generate a report if those features are
    enabled.
Available pages and controls depend on the current implementation and
backend configuration.
API Documentation
When the backend is running:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
Use the documentation generated by the running backend as the source of
truth for endpoint paths, request fields, and response schemas.
Training and Evaluation
For a meaningful defect-detection result:
1. Obtain the dataset from an authorized source.
2. Prepare it using the matching dataset adapter or preparation script
   in the repository.
3. Validate image-label pairs, class mappings, and bounding-box
   coordinates.
4. Create reproducible training, validation, and test splits.
5. Train or fine-tune the detector using the project's training
   workflow.
6. Evaluate the checkpoint on held-out data.
7. Record the checkpoint, dataset version, split, hardware, and
   training configuration.
Useful object-detection metrics include:
- Precision: proportion of predicted detections that are correct.
- Recall: proportion of ground-truth objects detected.
- mAP@50: mean average precision at IoU 0.50.
- mAP@50--95: mean average precision averaged across IoU
  thresholds 0.50--0.95.
- IoU: overlap between a predicted box and a ground-truth box.
MVTec AD is an anomaly-detection benchmark and should be evaluated with
appropriate image-level and pixel-level anomaly metrics.
No accuracy score is guaranteed by this README. Add only measured
results from your own evaluation run.

Testing
If a backend Pytest suite is present, run it from the backend directory:
cd backend
.venv\Scripts\Activate.ps1
python -m pytest
Check the frontend production build:
cd frontend
npm run build
Use the scripts that actually exist in the current repository. Document
failing tests and known issues honestly.
Troubleshooting
  Problem                             What to check
  uvicorn not recognized            Activate the backend virtual
environment and install
requirements.txt.

  No module named app               Run Uvicorn from backend/ and
verify the application import path.

  Frontend dependency error           Check Node/npm versions, network
access, and the package lock file.

  Frontend cannot reach backend       Confirm the backend is running;
check API URL and CORS settings.

  Gemini explanation unavailable      Check the backend API key, network,
provider configuration, and
fallback behaviour.

  Model/checkpoint not found          Verify the configured model path
and that the checkpoint exists.

  Dataset preparation fails           Check download completeness, folder
paths, annotation format, and disk
space.

  Inference is slow                   Check whether inference is running
on CPU or a supported GPU.
PDF generation fails                Check backend logs,
output-directory permissions, and
inspection record availability.
Limitations
- This is an academic prototype and is not certified for production
  quality control.
- Performance depends on dataset quality, class balance, annotation
  accuracy, camera conditions, and the trained model.
- A model trained on one material or dataset may not generalize to
  another factory, product, or lighting setup.
- A vision-language model can generate incorrect explanations.
  Possible causes must be treated as hypotheses, not confirmed root
  causes.
- Severity and PASS/FAIL rules require calibration and approval by
  qualified quality engineers before operational use.
- The system does not replace non-destructive testing, dimensional
  inspection, laboratory testing, or human quality approval.
- Demo/sample outputs must be clearly distinguished from live model
  predictions.
Future Enhancements
- Real-time inspection using industrial cameras and conveyor-belt
  video.
- Defect segmentation for more precise area measurement.
- Active learning and operator-assisted annotation correction.
- Support for additional product categories and validated datasets.
- Local vision-language models to reduce dependence on external APIs.
- Integration with production systems using approved industrial
  protocols.
- Role-based access, audit trails, and report approval workflows.
Contributing
Suggestions and contributions are welcome.
1. Fork the repository.
2. Create a feature branch.
3. Make a focused change.
4. Run relevant backend tests and the frontend build.
5. Submit a pull request describing the change and how it was tested.
Do not commit API keys, passwords, private datasets, or large model
weights.
License
No license is specified in this README. Unless a license file is added
to the repository, do not assume that the project grants permission for
reuse, modification, or redistribution. Add an appropriate LICENSE
file if you intend to publish it under an open-source license.
Acknowledgements
- Ultralytics for the YOLO framework.
- Google AI for Gemini API documentation and multimodal model access.
- The creators and maintainers of NEU-DET, GC10-DET, and MVTec AD.
- The open-source communities behind React, FastAPI, PyTorch, OpenCV,
  SQLAlchemy, and the other technologies used.
Repository
GitHub: https://github.com/ruchika172005-creator/Indus-Vision
