from pathlib import Path
from typing import Dict, Any
from app.core.config import settings

DATASET_SOURCES = {
    "neu_det": {
        "title": "NEU-DET Steel Surface Defect Database",
        "official_url": "http://faculty.neu.edu.cn/yunhyan/NEU_surface_defect_database.html",
        "kaggle_mirror": "https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database",
        "instructions": (
            "1. Download 'NEU-DET.zip' from official or verified Kaggle repository.\n"
            "2. Extract into 'backend/datasets/neu_det/'.\n"
            "3. Ensure the folder contains 'IMAGES/' and 'ANNOTATIONS/' directories.\n"
            "4. Click 'Prepare YOLO Splits' in the dashboard or run 'python scripts/prepare_neu_det.py'."
        ),
        "license": "Academic research use only (Northeastern University)",
        "expected_images": 1800,
        "classes": ["crazing", "inclusion", "patches", "pitted surface", "rolled-in scale", "scratches"]
    },
    "gc10_det": {
        "title": "GC10-DET Metallic Surface Defect Benchmark",
        "official_url": "https://github.com/Spider-Man-Graph/GC10-DET-Dataset",
        "instructions": (
            "1. Clone or download GC10-DET repository.\n"
            "2. Place image files into 'backend/datasets/gc10_det/images/'.\n"
            "3. Place XML annotations into 'backend/datasets/gc10_det/labelxml/'.\n"
            "4. Click 'Prepare YOLO Splits' in the dashboard or run 'python scripts/prepare_gc10.py'."
        ),
        "license": "Open research dataset",
        "expected_images": 3570,
        "classes": [
            "punching hole", "welding line", "crescent gap", "water spot", "oil spot",
            "silk spot", "inclusion", "rolled-in scale", "scratches", "waist folding"
        ]
    },
    "mvtec_ad": {
        "title": "MVTec Anomaly Detection (MVTec AD)",
        "official_url": "https://www.mvtec.com/company/research/datasets/mvtec-ad",
        "instructions": (
            "1. Register at MVTec website and download object categories (e.g., metal_nut.tar.xz).\n"
            "2. Extract into 'backend/datasets/mvtec_ad/metal_nut/'.\n"
            "3. Keep original folder structure (train/good, test, ground_truth).\n"
            "4. The system automatically detects and evaluates anomaly masks."
        ),
        "license": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)",
        "expected_images": 5354,
        "classes": [
            "bottle", "cable", "capsule", "carpet", "grid",
            "hazelnut", "leather", "metal_nut", "pill", "screw",
            "tile", "toothbrush", "transistor", "wood", "zipper"
        ]
    }
}

class DownloadManager:
    @staticmethod
    def get_download_guide(dataset_name: str) -> Dict[str, Any]:
        info = DATASET_SOURCES.get(dataset_name.lower())
        if not info:
            raise KeyError(f"Unknown dataset '{dataset_name}'")
        return info

download_manager = DownloadManager()
