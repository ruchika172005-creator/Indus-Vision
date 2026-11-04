import os
import uuid
import json
import datetime
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.db_models import Inspection, DetectedDefect
from app.schemas.api_schemas import (
    InspectionResponse, DefectItem, GenAIExplanation
)
from app.ml.inference import inspection_pipeline
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/inspection", tags=["Inspection"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
MAX_FILE_SIZE = 25 * 1024 * 1024 # 25 MB

def _format_inspection_response(insp: Inspection) -> InspectionResponse:
    defects_list = []
    for d in insp.defects:
        defects_list.append(DefectItem(
            id=d.id,
            defect_name=d.defect_name,
            class_id=d.class_id,
            confidence=d.confidence,
            bbox=[d.bbox_x1, d.bbox_y1, d.bbox_x2, d.bbox_y2],
            area_pixels=d.area_pixels,
            area_ratio=d.area_ratio,
            severity_level=d.severity_level,
            visual_description=d.visual_description
        ))

    causes = []
    actions = []
    try:
        if insp.genai_possible_causes:
            causes = json.loads(insp.genai_possible_causes)
    except Exception:
        causes = [insp.genai_possible_causes] if insp.genai_possible_causes else []

    try:
        if insp.genai_recommended_actions:
            actions = json.loads(insp.genai_recommended_actions)
    except Exception:
        actions = [insp.genai_recommended_actions] if insp.genai_recommended_actions else []

    explanation = GenAIExplanation(
        defect_name=insp.genai_defect_name or "None",
        description=insp.genai_description or "",
        location=insp.genai_location or "Full surface",
        severity=insp.genai_severity or insp.max_severity,
        possible_causes=causes,
        recommended_actions=actions,
        inspection_decision=insp.overall_decision,
        quality_summary=insp.genai_quality_summary,
        provider_used=insp.genai_provider_used or "Rule-Based Fallback"
    )

    # Convert local absolute paths to relative static URLs
    orig_url = f"/uploads/{Path(insp.original_image_path).name}"
    annot_url = f"/uploads/{Path(insp.annotated_image_path).name}" if insp.annotated_image_path else None

    return InspectionResponse(
        id=insp.id,
        inspection_code=insp.inspection_code,
        timestamp=insp.timestamp,
        product_name=insp.product_name,
        product_category=insp.product_category,
        original_image_url=orig_url,
        annotated_image_url=annot_url,
        total_defects=insp.total_defects,
        max_severity=insp.max_severity,
        overall_decision=insp.overall_decision,
        confidence_avg=insp.confidence_avg,
        inference_time_ms=insp.inference_time_ms,
        model_name=insp.model_name,
        is_demo=insp.is_demo,
        inference_source=insp.inference_source,
        defects=defects_list,
        explanation=explanation,
        notes=insp.notes
    )

@router.get("/samples")
def get_sample_images():
    """
    Returns available demo defect sample images for instant 1-click inspection testing.
    """
    demo_dir = settings.UPLOAD_DIR / "demo"
    if not demo_dir.exists():
        demo_dir = settings.DATASETS_DIR / "demo"

    samples = [
        {"id": "clean", "name": "Defect-Free Clean Steel Plate", "defect_type": "Clean Surface", "filename": "demo_sample_clean_steel.jpg", "category": "Cold Rolled Sheet"},
        {"id": "scratches", "name": "Longitudinal Surface Scratches", "defect_type": "Scratches", "filename": "demo_sample_scratches.jpg", "category": "Coil Strip"},
        {"id": "crazing", "name": "Thermal Fatigue Crazing Cracks", "defect_type": "Crazing", "filename": "demo_sample_crazing.jpg", "category": "Heavy Plate"},
        {"id": "inclusion", "name": "Refractory Slag Inclusion Cluster", "defect_type": "Inclusion", "filename": "demo_sample_inclusion.jpg", "category": "Structural Flange"},
        {"id": "patches", "name": "High-Temp Scale Oxidation Patches", "defect_type": "Patches", "filename": "demo_sample_patches.jpg", "category": "Hot-Rolled Sheet"},
        {"id": "pitted", "name": "Acid Intergranular Pitted Surface", "defect_type": "Pitted Surface", "filename": "demo_sample_pitted_surface.jpg", "category": "Pickled Steel"},
        {"id": "rolled_scale", "name": "Pressed Rolled-in Mill Scale", "defect_type": "Rolled-in Scale", "filename": "demo_sample_rolled_in_scale.jpg", "category": "Rolled Strip"}
    ]

    for s in samples:
        s["url"] = f"/uploads/demo/{s['filename']}"

    return {"samples": samples}

@router.get("/dataset-images")
def get_dataset_images(
    dataset_name: str = Query("neu_det"),
    split: str = Query("all"),
    limit: int = Query(60, ge=1, le=300)
):
    """
    Loads verified dataset images from local disk (NEU-DET, GC10-DET, or Demo Samples)
    enabling dynamic dataset selection, browsing, and instant optical inspection.
    """
    d_name = dataset_name.lower().replace("-", "_")
    images_list = []
    recommended_model = "YOLOv8n-NEU-DET"
    display_title = "NEU-DET Steel Surface Defect Dataset"
    classes = []

    if d_name == "neu_det":
        display_title = "NEU-DET Steel Surface Defect Dataset"
        recommended_model = "YOLOv8n-NEU-DET"
        classes = ["crazing", "inclusion", "patches", "pitted surface", "rolled-in scale", "scratches"]
        root = settings.DATASETS_DIR / "neu_det"

        target_dirs = []
        if split in ["train", "val", "test"]:
            p = root / "yolo" / "images" / split
            if p.exists():
                target_dirs.append((p, split))
        else:
            if (root / "yolo" / "images" / "test").exists():
                target_dirs.append((root / "yolo" / "images" / "test", "test"))
            if (root / "yolo" / "images" / "val").exists():
                target_dirs.append((root / "yolo" / "images" / "val", "val"))
            if (root / "yolo" / "images" / "train").exists():
                target_dirs.append((root / "yolo" / "images" / "train", "train"))
            if (root / "IMAGES").exists():
                target_dirs.append((root / "IMAGES", "raw"))

        seen = set()
        for sdir, split_tag in target_dirs:
            for f in sorted(sdir.glob("*.*")):
                if f.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS and f.name not in seen:
                    seen.add(f.name)
                    name_parts = f.stem.split("_")
                    defect_label = name_parts[0].capitalize()
                    if len(name_parts) > 2:
                        defect_label = " ".join(name_parts[:-1]).title()

                    rel_path = f.relative_to(settings.DATASETS_DIR).as_posix()
                    xml_candidate = root / "ANNOTATIONS" / f"{f.stem}.xml"

                    images_list.append({
                        "id": f"neu_{f.stem}",
                        "filename": f.name,
                        "relative_path": rel_path,
                        "defect_type": defect_label,
                        "category": "Steel Plate",
                        "split": split_tag,
                        "url": f"/datasets-static/{rel_path}",
                        "has_annotation": xml_candidate.exists()
                    })
                    if len(images_list) >= limit:
                        break
            if len(images_list) >= limit:
                break

    elif d_name == "gc10_det":
        display_title = "GC10-DET Metallic Sheet Defect Dataset"
        recommended_model = "YOLOv8n-GC10-DET"
        classes = ["punching hole", "welding line", "crescent gap", "water spot", "oil spot", "silk spot", "inclusion", "rolled-in scale", "scratches", "waist folding"]
        root = settings.DATASETS_DIR / "gc10_det"

        target_dirs = []
        if split in ["train", "val", "test"]:
            p = root / "yolo" / "images" / split
            if p.exists():
                target_dirs.append((p, split))
        else:
            if (root / "yolo" / "images" / "test").exists():
                target_dirs.append((root / "yolo" / "images" / "test", "test"))
            if (root / "yolo" / "images" / "val").exists():
                target_dirs.append((root / "yolo" / "images" / "val", "val"))
            if (root / "yolo" / "images" / "train").exists():
                target_dirs.append((root / "yolo" / "images" / "train", "train"))
            if (root / "images").exists():
                target_dirs.append((root / "images", "raw"))

        seen = set()
        for sdir, split_tag in target_dirs:
            for f in sorted(sdir.glob("*.*")):
                if f.suffix.lower() in ALLOWED_IMAGE_EXTENSIONS and f.name not in seen:
                    seen.add(f.name)
                    name_parts = f.stem.split("_")
                    defect_label = " ".join(name_parts[:-1]).title() if len(name_parts) > 1 else f.stem.title()
                    rel_path = f.relative_to(settings.DATASETS_DIR).as_posix()
                    xml_candidate = root / "labelxml" / f"{f.stem}.xml"

                    images_list.append({
                        "id": f"gc10_{f.stem}",
                        "filename": f.name,
                        "relative_path": rel_path,
                        "defect_type": defect_label,
                        "category": "Metallic Sheet",
                        "split": split_tag,
                        "url": f"/datasets-static/{rel_path}",
                        "has_annotation": xml_candidate.exists()
                    })
                    if len(images_list) >= limit:
                        break
            if len(images_list) >= limit:
                break

    else:
        # Fallback to calibration demo samples
        display_title = "Factory Demonstration Calibration Samples"
        recommended_model = "YOLOv8n-NEU-DET"
        classes = ["Clean Surface", "Scratches", "Crazing", "Inclusion", "Patches", "Pitted Surface", "Rolled-in Scale"]
        demo_dir = settings.DATASETS_DIR / "demo"
        if demo_dir.exists():
            for f in sorted(demo_dir.glob("*.jpg")):
                clean_type = f.stem.replace("demo_sample_", "").replace("_", " ").title()
                images_list.append({
                    "id": f.stem,
                    "filename": f.name,
                    "relative_path": f"demo/{f.name}",
                    "defect_type": clean_type,
                    "category": "Industrial Cold Rolled Plate",
                    "split": "demo",
                    "url": f"/datasets-static/demo/{f.name}",
                    "has_annotation": True
                })

    return {
        "dataset_name": d_name,
        "display_name": display_title,
        "total_images": len(images_list),
        "classes": classes,
        "recommended_model": recommended_model,
        "images": images_list
    }

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Uploads an industrial product image for inspection.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    # Save to uploads
    unique_filename = f"upload_{uuid.uuid4().hex[:10]}{ext}"
    dest_path = settings.UPLOAD_DIR / unique_filename

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum 25 MB limit.")

    with open(dest_path, "wb") as f:
        f.write(content)

    return {
        "filename": unique_filename,
        "file_path": str(dest_path),
        "file_url": f"/uploads/{unique_filename}",
        "size_bytes": len(content)
    }

@router.post("/analyze", response_model=InspectionResponse)
async def analyze_inspection(
    image_path: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    sample_filename: Optional[str] = Form(None),
    product_name: str = Form("Steel Plate Component"),
    product_category: str = Form("Cold Rolled Steel"),
    model_name: Optional[str] = Form(None),
    conf_threshold: float = Form(0.35),
    iou_threshold: float = Form(0.45),
    db: Session = Depends(get_db)
):
    """
    Runs computer vision defect detection, severity assessment, and GenAI defect explanation.
    Persists inspection records in the database.
    """
    target_path = None

    if sample_filename:
        # Search demo directory first
        for cand in [
            settings.UPLOAD_DIR / "demo" / sample_filename,
            settings.DATASETS_DIR / "demo" / sample_filename,
            settings.DATASETS_DIR / "neu_det" / "IMAGES" / sample_filename,
            settings.DATASETS_DIR / "neu_det" / "yolo" / "images" / "test" / sample_filename,
            settings.DATASETS_DIR / "gc10_det" / "images" / sample_filename,
            settings.DATASETS_DIR / "gc10_det" / "yolo" / "images" / "test" / sample_filename,
        ]:
            if cand.exists():
                target_path = str(cand)
                break

        if not target_path:
            # Recursive search in datasets directory
            matches = list(settings.DATASETS_DIR.rglob(sample_filename))
            if matches:
                target_path = str(matches[0])

    if not target_path and file:
        ext = Path(file.filename).suffix.lower()
        unique_filename = f"inspect_{uuid.uuid4().hex[:10]}{ext}"
        dest_path = settings.UPLOAD_DIR / unique_filename
        content = await file.read()
        with open(dest_path, "wb") as f:
            f.write(content)
        target_path = str(dest_path)

    if not target_path and image_path:
        # Clean static prefixes if passed from frontend URL
        clean_img_path = image_path.replace("/datasets-static/", "").replace("\\datasets-static\\", "")
        clean_img_path = clean_img_path.replace("/uploads/", "").replace("\\uploads\\", "")

        candidates = [
            Path(image_path),
            settings.DATASETS_DIR / clean_img_path,
            settings.UPLOAD_DIR / clean_img_path,
            settings.UPLOAD_DIR / Path(image_path).name,
            settings.DATASETS_DIR / "neu_det" / "IMAGES" / Path(image_path).name,
            settings.DATASETS_DIR / "gc10_det" / "images" / Path(image_path).name,
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                target_path = str(c)
                break

        if not target_path:
            matches = list(settings.DATASETS_DIR.rglob(Path(image_path).name))
            if matches:
                target_path = str(matches[0])

    if not target_path or not Path(target_path).exists():
        raise HTTPException(status_code=400, detail="Valid image file or sample must be provided.")

    try:
        result = await inspection_pipeline.run_inspection(
            image_path=target_path,
            product_name=product_name,
            product_category=product_category,
            model_name=model_name,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold
        )
    except Exception as e:
        logger.error(f"Inference pipeline execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Inspection pipeline failure: {str(e)}")

    # Persist in DB
    code = f"QA-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    expl = result.get("explanation", {})

    inspection_record = Inspection(
        inspection_code=code,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        product_name=result["product_name"],
        product_category=result["product_category"],
        original_image_path=result["original_image_path"],
        annotated_image_path=result["annotated_image_path"],
        total_defects=result["total_defects"],
        max_severity=result["max_severity"],
        overall_decision=result["overall_decision"],
        confidence_avg=result["confidence_avg"],
        inference_time_ms=result["inference_time_ms"],
        model_name=result["model_name"],
        is_demo=result["is_demo"],
        inference_source=result["inference_source"],
        genai_defect_name=expl.get("defect_name"),
        genai_description=expl.get("description"),
        genai_location=expl.get("location"),
        genai_severity=expl.get("severity"),
        genai_possible_causes=json.dumps(expl.get("possible_causes", [])),
        genai_recommended_actions=json.dumps(expl.get("recommended_actions", [])),
        genai_quality_summary=expl.get("quality_summary"),
        genai_provider_used=expl.get("provider_used")
    )
    db.add(inspection_record)
    db.flush()

    for d in result["defects"]:
        defect_obj = DetectedDefect(
            inspection_id=inspection_record.id,
            defect_name=d["defect_name"],
            class_id=d.get("class_id", 0),
            confidence=d["confidence"],
            bbox_x1=d["bbox"][0],
            bbox_y1=d["bbox"][1],
            bbox_x2=d["bbox"][2],
            bbox_y2=d["bbox"][3],
            area_pixels=d.get("area_pixels", 0.0),
            area_ratio=d.get("area_ratio", 0.0),
            severity_level=d.get("severity_level", "LOW"),
            visual_description=d.get("evaluation_reason")
        )
        db.add(defect_obj)

    db.commit()
    db.refresh(inspection_record)

    return _format_inspection_response(inspection_record)

@router.get("/history", response_model=List[InspectionResponse])
def get_inspection_history(
    search: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns filtered and paginated inspection history.
    """
    q = db.query(Inspection)

    if search:
        search_filter = f"%{search}%"
        q = q.filter(
            (Inspection.product_name.ilike(search_filter)) |
            (Inspection.inspection_code.ilike(search_filter)) |
            (Inspection.genai_defect_name.ilike(search_filter))
        )

    if severity and severity.upper() != "ALL":
        q = q.filter(Inspection.max_severity == severity.upper())

    if decision and decision.upper() != "ALL":
        q = q.filter(Inspection.overall_decision == decision.upper())

    items = q.order_by(Inspection.timestamp.desc()).offset(offset).limit(limit).all()
    return [_format_inspection_response(item) for item in items]

@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection_by_id(inspection_id: int, db: Session = Depends(get_db)):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection record not found")
    return _format_inspection_response(insp)

@router.delete("/{inspection_id}")
def delete_inspection(inspection_id: int, db: Session = Depends(get_db)):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection record not found")

    db.delete(insp)
    db.commit()
    return {"success": True, "message": f"Inspection #{inspection_id} deleted."}
