import os
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

class ModelManager:
    """
    Manages detection models, registered weights, device discovery,
    and active model switching.
    """

    def __init__(self):
        self.weights_dir = settings.WEIGHTS_DIR
        self.active_model_name = "YOLOv8n-NEU-DET"

    def get_device_info(self) -> Dict[str, Any]:
        cuda_avail = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU (Standard Host)"
        return {
            "device": "cuda" if cuda_avail else "cpu",
            "cuda_available": cuda_avail,
            "device_name": device_name,
            "pytorch_version": torch.__version__
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Returns list of registered models with verified file existence and benchmark metrics.
        """
        from app.database.connection import SessionLocal
        from app.models.db_models import TrainedModel
        db = SessionLocal()
        try:
            records = db.query(TrainedModel).all()
            if records:
                results = []
                for r in records:
                    p = Path(r.weights_path) if r.weights_path else None
                    if p and not p.exists():
                        fallback_p = settings.WEIGHTS_DIR / p.name
                        if fallback_p.exists():
                            p = fallback_p
                        elif not p.is_absolute():
                            candidate = settings.BASE_DIR / p
                            if candidate.exists():
                                p = candidate
                    actual_exists = p.exists() if p else False
                    results.append({
                        "id": r.id,
                        "name": r.name,
                        "model_type": r.model_type,
                        "dataset_name": r.dataset_name,
                        "weights_path": str(p) if p else r.weights_path,
                        "file_exists": actual_exists,
                        "precision": r.precision if actual_exists else 0.0,
                        "recall": r.recall if actual_exists else 0.0,
                        "map50": r.map50 if actual_exists else 0.0,
                        "map50_95": r.map50_95 if actual_exists else 0.0,
                        "device_used": r.device_used,
                        "is_active": (self.active_model_name == r.name)
                    })
                return results
        except Exception as e:
            logger.warning(f"Error querying trained_models: {e}")
        finally:
            db.close()

        neu_weights = self.weights_dir / "yolov8n_neu_det.pt"
        gc10_weights = self.weights_dir / "yolov8n_gc10_det.pt"
        base_weights = self.weights_dir / "yolov8n.pt"

        return [
            {
                "id": 1,
                "name": "YOLOv8n-NEU-DET",
                "model_type": "YOLOv8n",
                "dataset_name": "neu_det",
                "weights_path": str(neu_weights),
                "file_exists": neu_weights.exists(),
                "precision": 0.0,
                "recall": 0.0,
                "map50": 0.0,
                "map50_95": 0.0,
                "device_used": "cuda" if torch.cuda.is_available() else "cpu",
                "is_active": (self.active_model_name == "YOLOv8n-NEU-DET")
            },
            {
                "id": 2,
                "name": "YOLOv8n-GC10-DET",
                "model_type": "YOLOv8n",
                "dataset_name": "gc10_det",
                "weights_path": str(gc10_weights),
                "file_exists": gc10_weights.exists(),
                "precision": 0.0,
                "recall": 0.0,
                "map50": 0.0,
                "map50_95": 0.0,
                "device_used": "cuda" if torch.cuda.is_available() else "cpu",
                "is_active": (self.active_model_name == "YOLOv8n-GC10-DET")
            },
            {
                "id": 3,
                "name": "YOLOv8n-Base",
                "model_type": "YOLOv8n",
                "dataset_name": "generic",
                "weights_path": str(base_weights),
                "file_exists": base_weights.exists(),
                "precision": 0.0,
                "recall": 0.0,
                "map50": 0.0,
                "map50_95": 0.0,
                "device_used": "cuda" if torch.cuda.is_available() else "cpu",
                "is_active": (self.active_model_name == "YOLOv8n-Base")
            }
        ]

    def set_active_model(self, model_name: str) -> bool:
        self.active_model_name = model_name
        logger.info(f"Active model switched to: {model_name}")
        return True

    def get_model_path(self, model_name: Optional[str] = None) -> Optional[str]:
        target = model_name or self.active_model_name
        for m in self.list_models():
            if m["name"] == target and m["file_exists"]:
                return m["weights_path"]
        return None

    def get_active_model_path(self) -> Optional[str]:
        return self.get_model_path(self.active_model_name)

model_manager = ModelManager()
