import argparse
import sys
from pathlib import Path
import torch

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.logging import logger

def train(
    dataset_name: str = "neu_det",
    base_model: str = "yolov8n.pt",
    epochs: int = 50,
    batch_size: int = 16,
    img_size: int = 640,
    device: str = "auto"
):
    """Fine-tunes YOLOv8 on prepared industrial defect dataset."""
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("Ultralytics package is not installed. Please run: pip install ultralytics")
        sys.exit(1)

    yaml_path = settings.DATASETS_DIR / dataset_name / "dataset.yaml"
    if not yaml_path.exists():
        yaml_path = settings.DATASETS_DIR / dataset_name / "yolo" / "dataset.yaml"

    if not yaml_path.exists():
        logger.error(f"Dataset YAML config not found at: {yaml_path}")
        logger.error(f"Run python scripts/prepare_{dataset_name}.py first!")
        sys.exit(1)

    if device == "auto":
        device = "0" if torch.cuda.is_available() else "cpu"

    logger.info(f"Loading base YOLO architecture: {base_model}...")
    model = YOLO(base_model)

    run_name = f"yolov8n_{dataset_name}"
    logger.info(f"Starting training on {dataset_name} for {epochs} epochs on device: {device}...")
    results = model.train(
        data=str(yaml_path),
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        device=device,
        project=str(settings.WEIGHTS_DIR),
        name=run_name,
        exist_ok=True,
        save=True
    )

    logger.info("Evaluating fine-tuned weights on validation set...")
    val_metrics = model.val(data=str(yaml_path), split="val")

    best_pt = Path(results.save_dir) / "weights" / "best.pt"
    dest_pt = settings.WEIGHTS_DIR / f"{run_name}.pt"
    import shutil
    import json
    if best_pt.exists():
        shutil.copy2(best_pt, dest_pt)

    metrics_dict = {
        "precision": float(val_metrics.box.mp),
        "recall": float(val_metrics.box.mr),
        "map50": float(val_metrics.box.map50),
        "map50_95": float(val_metrics.box.map),
        "dataset": dataset_name,
        "epochs": epochs
    }
    metrics_file = settings.WEIGHTS_DIR / f"{run_name}_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_dict, f, indent=2)

    # Update database record if exists
    try:
        from app.database.connection import SessionLocal
        from app.models.db_models import TrainedModel
        db = SessionLocal()
        display_name = f"YOLOv8n-{dataset_name.upper().replace('_', '-')}"
        record = db.query(TrainedModel).filter(
            (TrainedModel.name == display_name) | (TrainedModel.name == run_name)
        ).first()
        if record:
            record.weights_path = str(dest_pt)
            record.file_exists = True
            record.precision = metrics_dict["precision"]
            record.recall = metrics_dict["recall"]
            record.map50 = metrics_dict["map50"]
            record.map50_95 = metrics_dict["map50_95"]
            record.device_used = device
            db.commit()
        db.close()
    except Exception as e:
        logger.warning(f"Could not update database record: {e}")

    logger.info(f"Training completed successfully! Saved verified weights to: {dest_pt}")
    logger.info(f"Validation Metrics: Precision={metrics_dict['precision']:.4f}, Recall={metrics_dict['recall']:.4f}, mAP@50={metrics_dict['map50']:.4f}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune YOLOv8 on Industrial Defect Datasets")
    parser.add_argument("--dataset", type=str, default="neu_det", choices=["neu_det", "gc10_det"])
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", type=str, default="auto")
    args = parser.parse_args()

    train(
        dataset_name=args.dataset,
        epochs=args.epochs,
        batch_size=args.batch,
        img_size=args.imgsz,
        device=args.device
    )
