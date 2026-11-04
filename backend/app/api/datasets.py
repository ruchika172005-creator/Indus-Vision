from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import DatasetRecord
from app.schemas.api_schemas import (
    DatasetItem, DatasetActionResponse
)
from app.datasets.dataset_manager import dataset_manager

router = APIRouter(prefix="/datasets", tags=["Dataset Management"])

@router.get("", response_model=List[DatasetItem])
def list_datasets(db: Session = Depends(get_db)):
    """
    Returns live on-disk status for NEU-DET, GC10-DET, and MVTec AD datasets.
    """
    stats_list = dataset_manager.list_all()
    results = []

    for idx, s in enumerate(stats_list, start=1):
        # Sync with DB if record exists
        rec = db.query(DatasetRecord).filter(DatasetRecord.name == s["name"]).first()
        if rec:
            rec.is_downloaded = s["is_downloaded"]
            rec.is_prepared = s["is_prepared"]
            rec.total_images = s["total_images"]
            rec.train_count = s.get("train_images", 0)
            rec.val_count = s.get("val_images", 0)
            rec.test_count = s.get("test_images", 0)
            rec.disk_size_mb = s["disk_size_mb"]
            db.commit()

        results.append(DatasetItem(
            id=idx,
            name=s["name"],
            display_name=s["display_name"],
            category=s["category"],
            source_url=s.get("source_url"),
            description=s.get("description"),
            is_downloaded=s["is_downloaded"],
            is_prepared=s["is_prepared"],
            total_images=s["total_images"],
            train_count=s.get("train_images", 0),
            val_count=s.get("val_images", 0),
            test_count=s.get("test_images", 0),
            num_classes=s["num_classes"],
            classes=s["classes"],
            disk_size_mb=s["disk_size_mb"],
            local_path=s.get("local_path"),
            yaml_config_path=s.get("yaml_config_path")
        ))
    return results

@router.get("/{dataset_name}/statistics")
def get_dataset_statistics(dataset_name: str):
    """
    Returns class distribution, file counts, and folder sizes for the specified dataset.
    """
    try:
        return dataset_manager.get_dataset(dataset_name)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{dataset_name}/init-demo", response_model=DatasetActionResponse)
def init_demo_dataset(dataset_name: str, db: Session = Depends(get_db)):
    """
    Initializes an authentic demonstration subset with Pascal VOC XML annotations.
    Allows testing split preparation and YOLO training without a 500MB download.
    """
    try:
        stats = dataset_manager.init_demo_subset(dataset_name)
        
        # Sync with DB record
        rec = db.query(DatasetRecord).filter(DatasetRecord.name == stats["name"]).first()
        if rec:
            rec.is_downloaded = stats["is_downloaded"]
            rec.total_images = stats["total_images"]
            rec.disk_size_mb = stats["disk_size_mb"]
            db.commit()

        return DatasetActionResponse(
            success=True,
            message=f"Demonstration subset initialized for '{dataset_name}' ({stats['total_images']} verified samples with Pascal VOC annotations).",
            dataset_name=dataset_name,
            data=stats
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize demo subset: {str(e)}")

@router.post("/{dataset_name}/prepare", response_model=DatasetActionResponse)
def prepare_dataset(dataset_name: str):
    """
    Parses Pascal VOC XML annotations, converts to normalized YOLO format,
    creates train/val/test splits, and writes dataset.yaml.
    """
    try:
        stats = dataset_manager.prepare_dataset(dataset_name)
        return DatasetActionResponse(
            success=True,
            message=f"Dataset '{dataset_name}' successfully converted to YOLO format with splits.",
            dataset_name=dataset_name,
            data=stats
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to prepare dataset: {str(e)}")

@router.post("/{dataset_name}/download", response_model=DatasetActionResponse)
def get_dataset_download_instructions(dataset_name: str):
    """
    Returns official download source URLs, step-by-step instructions, and licensing terms.
    """
    try:
        guide = dataset_manager.get_download_instructions(dataset_name)
        return DatasetActionResponse(
            success=True,
            message="Verified download guide and instructions retrieved.",
            dataset_name=dataset_name,
            data=guide
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
