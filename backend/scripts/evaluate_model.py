import argparse
import sys
from pathlib import Path
import torch

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.logging import logger

def evaluate(weights_path: str, dataset_yaml: str):
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("Ultralytics package is not installed.")
        sys.exit(1)

    if not Path(weights_path).exists():
        logger.error(f"Weights file not found at: {weights_path}")
        sys.exit(1)

    if not Path(dataset_yaml).exists():
        logger.error(f"Dataset YAML not found at: {dataset_yaml}")
        sys.exit(1)

    logger.info(f"Evaluating model {weights_path} on {dataset_yaml}...")
    model = YOLO(weights_path)
    metrics = model.val(data=dataset_yaml, split="val")

    precision = float(metrics.box.mp)
    recall = float(metrics.box.mr)
    map50 = float(metrics.box.map50)
    map50_95 = float(metrics.box.map)

    print("\n--- Verified Benchmark Validation Metrics ---")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"mAP@50:    {map50:.4f}")
    print(f"mAP@50-95: {map50_95:.4f}")

    import json
    weights_p = Path(weights_path)
    metrics_file = weights_p.parent / f"{weights_p.stem}_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump({
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "map50": round(map50, 4),
            "map50_95": round(map50_95, 4),
            "weights": str(weights_path),
            "data": str(dataset_yaml)
        }, f, indent=2)

    try:
        from app.database.connection import SessionLocal
        from app.models.db_models import TrainedModel
        db = SessionLocal()
        record = db.query(TrainedModel).filter(
            (TrainedModel.weights_path == str(weights_p.resolve())) |
            (TrainedModel.weights_path == str(weights_path)) |
            (TrainedModel.name.ilike(f"%{weights_p.stem}%"))
        ).first()
        if record:
            record.precision = precision
            record.recall = recall
            record.map50 = map50
            record.map50_95 = map50_95
            record.file_exists = True
            db.commit()
        db.close()
    except Exception as e:
        logger.warning(f"Could not update db record: {e}")

    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate YOLOv8 Defect Model")
    parser.add_argument("--weights", type=str, required=True)
    parser.add_argument("--data", type=str, required=True)
    args = parser.parse_args()

    evaluate(args.weights, args.data)
