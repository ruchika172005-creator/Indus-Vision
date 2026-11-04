import os
import json
import datetime
import shutil
from pathlib import Path

from app.database.connection import engine, SessionLocal, Base
from app.models.db_models import (
    Inspection, DetectedDefect, DatasetRecord, TrainedModel, ApplicationSetting
)
from app.core.config import settings
from app.core.logging import logger
from app.ml.image_processor import image_processor
from scripts.generate_demo_data import generate_all_demo_images

def init_db():
    """
    Creates all tables automatically and seeds initial datasets, models,
    configuration settings, and demo inspection history.
    """
    logger.info("Initializing SQLite database and verifying tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Datasets
        if db.query(DatasetRecord).count() == 0:
            logger.info("Seeding initial dataset catalog...")
            neu = DatasetRecord(
                name="neu_det",
                display_name="NEU-DET Steel Surface Defect Dataset",
                category="Steel Surface Defects",
                source_url="http://faculty.neu.edu.cn/yunhyan/NEU_surface_defect_database.html",
                description="Northeastern University hot-rolled steel surface defect benchmark (~1,800 images across 6 classes).",
                is_downloaded=False,
                is_prepared=False,
                total_images=0,
                num_classes=6,
                classes_json=json.dumps(["crazing", "inclusion", "patches", "pitted surface", "rolled-in scale", "scratches"]),
                local_path=str(settings.DATASETS_DIR / "neu_det")
            )
            gc10 = DatasetRecord(
                name="gc10_det",
                display_name="GC10-DET Metallic Surface Defect Dataset",
                category="Metallic Surface Defects",
                source_url="https://github.com/Spider-Man-Graph/GC10-DET-Dataset",
                description="Comprehensive benchmark covering 10 industrial metallic sheet defect categories (~3,570 images).",
                is_downloaded=False,
                is_prepared=False,
                total_images=0,
                num_classes=10,
                classes_json=json.dumps([
                    "punching hole", "welding line", "crescent gap", "water spot", "oil spot",
                    "silk spot", "inclusion", "rolled-in scale", "scratches", "waist folding"
                ]),
                local_path=str(settings.DATASETS_DIR / "gc10_det")
            )
            mvtec = DatasetRecord(
                name="mvtec_ad",
                display_name="MVTec Anomaly Detection (MVTec AD)",
                category="Industrial Anomaly Detection & Segmentation",
                source_url="https://www.mvtec.com/company/research/datasets/mvtec-ad",
                description="Comprehensive industrial anomaly detection benchmark with 15 object/texture categories and pixel-level ground truth masks.",
                is_downloaded=False,
                is_prepared=False,
                total_images=0,
                num_classes=15,
                classes_json=json.dumps(["metal_nut", "screw", "bottle", "cable", "tile", "etc."]),
                local_path=str(settings.DATASETS_DIR / "mvtec_ad")
            )
            db.add_all([neu, gc10, mvtec])
            db.commit()

        # 2. Seed Registered Models
        if db.query(TrainedModel).count() == 0:
            logger.info("Seeding registered model catalog...")
            m1 = TrainedModel(
                name="YOLOv8n-NEU-DET",
                model_type="YOLOv8n",
                dataset_name="neu_det",
                weights_path=str(settings.WEIGHTS_DIR / "yolov8n_neu_det.pt"),
                file_exists=False,
                precision=0.0,
                recall=0.0,
                map50=0.0,
                map50_95=0.0,
                device_used="cpu",
                is_active=True
            )
            m2 = TrainedModel(
                name="YOLOv8n-GC10-DET",
                model_type="YOLOv8n",
                dataset_name="gc10_det",
                weights_path=str(settings.WEIGHTS_DIR / "yolov8n_gc10_det.pt"),
                file_exists=False,
                precision=0.0,
                recall=0.0,
                map50=0.0,
                map50_95=0.0,
                device_used="cpu",
                is_active=False
            )
            m3 = TrainedModel(
                name="YOLOv8n-Base",
                model_type="YOLOv8n",
                dataset_name="generic",
                weights_path=str(settings.WEIGHTS_DIR / "yolov8n.pt"),
                file_exists=False,
                precision=0.0,
                recall=0.0,
                map50=0.0,
                map50_95=0.0,
                device_used="cpu",
                is_active=False
            )
            db.add_all([m1, m2, m3])
            db.commit()
        else:
            # Sync existing models against actual file existence on disk
            for m in db.query(TrainedModel).all():
                actual_exists = Path(m.weights_path).exists() if m.weights_path else False
                m.file_exists = actual_exists
                if not actual_exists:
                    m.precision = 0.0
                    m.recall = 0.0
                    m.map50 = 0.0
                    m.map50_95 = 0.0
            # Remove any fabricated models that do not have weights on disk
            fake_models = db.query(TrainedModel).filter(TrainedModel.name == "diagnostic_yolo").all()
            for fm in fake_models:
                db.delete(fm)
            db.commit()

        # 3. Seed Default Application Settings
        default_settings = {
            "gemini_api_key": settings.GEMINI_API_KEY,
            "gemini_model": settings.GEMINI_MODEL,
            "confidence_threshold": str(settings.DEFAULT_CONFIDENCE_THRESHOLD),
            "iou_threshold": str(settings.DEFAULT_IOU_THRESHOLD),
            "critical_area_ratio": str(settings.CRITICAL_DEFECT_AREA_RATIO),
            "high_area_ratio": str(settings.HIGH_DEFECT_AREA_RATIO),
            "medium_area_ratio": str(settings.MEDIUM_DEFECT_AREA_RATIO),
            "active_model_name": "YOLOv8n-NEU-DET"
        }
        for k, v in default_settings.items():
            if not db.query(ApplicationSetting).filter(ApplicationSetting.key == k).first():
                db.add(ApplicationSetting(key=k, value=str(v)))
        db.commit()

        # 4. Generate Demo Sample Images if needed
        demo_dir = settings.DATASETS_DIR / "demo"
        uploads_demo = settings.UPLOAD_DIR / "demo"
        uploads_demo.mkdir(parents=True, exist_ok=True)
        demo_files = list(demo_dir.glob("*.jpg")) if demo_dir.exists() else []

        if not demo_files or len(demo_files) < 6:
            logger.info("Generating demo industrial metal surface sample images...")
            generated = generate_all_demo_images(str(demo_dir))
            for f in generated:
                shutil.copy2(f, uploads_demo / Path(f).name)
        else:
            for f in demo_files:
                target = uploads_demo / f.name
                if not target.exists():
                    shutil.copy2(f, target)

        # 5. Seed Demo Inspection History if inspections is empty
        if db.query(Inspection).count() == 0:
            logger.info("Seeding initial realistic inspection history records for analytics...")
            _seed_demo_inspections(db, uploads_demo)

    finally:
        db.close()
    logger.info("Database initialization and auto-seeding complete.")

def _seed_demo_inspections(db, demo_dir: Path):
    now = datetime.datetime.now(datetime.timezone.utc)

    demo_data_records = [
        {
            "code": "QA-2026-901",
            "delta_hours": 140,
            "product": "Hot-Rolled Structural Coil #104",
            "cat": "Coil Steel",
            "img_file": "demo_sample_clean_steel.jpg",
            "defects": [],
            "decision": "PASS",
            "max_sev": "LOW",
            "desc": "Surface exhibits uniform finish without detectable structural or cosmetic anomalies.",
            "loc": "Full surface area",
            "causes": ["Nominal rolling parameters maintained", "Optimal roll lubrication and cooling"],
            "actions": ["Pass to packaging bay", "Continue standard in-line monitoring"],
            "summary": "Product complies fully with ISO surface quality specifications."
        },
        {
            "code": "QA-2026-902",
            "delta_hours": 120,
            "product": "Cold Rolled Sheet Lot #22",
            "cat": "Sheet Metal",
            "img_file": "demo_sample_scratches.jpg",
            "defects": [
                {"name": "Scratches", "conf": 0.94, "bbox": [64.0, 192.0, 576.0, 288.0], "area_ratio": 0.057, "sev": "MEDIUM"}
            ],
            "decision": "MANUAL_REVIEW",
            "max_sev": "MEDIUM",
            "desc": "Continuous longitudinal surface abrasion grooves aligned parallel to the rolling pass direction.",
            "loc": "Mid-center horizontal stripe",
            "causes": ["Mechanical rubbing against worn guide plates or pinch rollers", "Debris lodged in bridle roller"],
            "actions": ["Inspect table guides and dressing stone contact surfaces", "Verify strip tension on bridle roll"],
            "summary": "Superficial scratches detected. Manual inspection required before electro-galvanizing."
        },
        {
            "code": "QA-2026-903",
            "delta_hours": 96,
            "product": "High-Strength Alloy Plate #518",
            "cat": "Alloy Plate",
            "img_file": "demo_sample_crazing.jpg",
            "defects": [
                {"name": "Crazing", "conf": 0.88, "bbox": [128.0, 160.0, 480.0, 448.0], "area_ratio": 0.098, "sev": "HIGH"}
            ],
            "decision": "MANUAL_REVIEW",
            "max_sev": "HIGH",
            "desc": "Network of fine, interconnected micro-fissures resembling spiderweb cracking across the rolled steel surface.",
            "loc": "Central surface area",
            "causes": ["Severe thermal fatigue caused by improper work roll cooling water spray patterns", "Excessive tensile strain during reduction"],
            "actions": ["Inspect descaling roll cooling nozzles", "Perform ultrasonic depth measurement"],
            "summary": "High-severity crazing micro-cracks present. Reject if structural fatigue threshold exceeded."
        },
        {
            "code": "QA-2026-904",
            "delta_hours": 72,
            "product": "Galvanized Strip Substrate #31",
            "cat": "Strip Substrate",
            "img_file": "demo_sample_inclusion.jpg",
            "defects": [
                {"name": "Inclusion", "conf": 0.92, "bbox": [256.0, 224.0, 416.0, 384.0], "area_ratio": 0.062, "sev": "CRITICAL"}
            ],
            "decision": "FAIL",
            "max_sev": "CRITICAL",
            "desc": "Embedded non-metallic foreign particles (slag or refractory inclusion) entrapped in the steel matrix.",
            "loc": "Center region",
            "causes": ["Ladle shroud or tundish refractory erosion during continuous casting", "Incomplete deoxidation slag flotation"],
            "actions": ["Quarantine batch immediately", "Review ladle temperature and argon bubbling logs"],
            "summary": "Critical inclusion defect detected. Component rejected due to high stress concentration risk."
        },
        {
            "code": "QA-2026-905",
            "delta_hours": 48,
            "product": "Automotive Body Panel Steel #89",
            "cat": "Auto Sheet",
            "img_file": "demo_sample_patches.jpg",
            "defects": [
                {"name": "Patches", "conf": 0.85, "bbox": [96.0, 115.0, 352.0, 332.0], "area_ratio": 0.086, "sev": "HIGH"}
            ],
            "decision": "MANUAL_REVIEW",
            "max_sev": "HIGH",
            "desc": "Irregular dark scaly surface patches caused by localized oxidation and unremoved high-temperature scale.",
            "loc": "Upper-left quadrant",
            "causes": ["Descaling header water pressure drop below standard 180 bar", "Uneven reheating furnace atmosphere"],
            "actions": ["Recalibrate descaling pump pressure transducers", "Inspect furnace Zone 2 oxygen burners"],
            "summary": "High surface patch oxidation detected. Reroute for cosmetic buffing or secondary pickling."
        },
        {
            "code": "QA-2026-906",
            "delta_hours": 24,
            "product": "Pickled and Oiled Coil #772",
            "cat": "Coil Steel",
            "img_file": "demo_sample_pitted_surface.jpg",
            "defects": [
                {"name": "Pitted Surface", "conf": 0.89, "bbox": [192.0, 256.0, 512.0, 544.0], "area_ratio": 0.112, "sev": "HIGH"}
            ],
            "decision": "FAIL",
            "max_sev": "HIGH",
            "desc": "Localized microscopic crater-like depressions and surface porosity distributed across the metal face.",
            "loc": "Lower-right quadrant",
            "causes": ["Over-pickling in hydrochloric acid bath resulting in intergranular acid attack", "Pitted roll surface transfer"],
            "actions": ["Check acid bath concentration and inhibitor dosing schedule", "Schedule work roll polishing"],
            "summary": "Severe pitting exceeds allowable roughness specification. Reject coil section."
        },
        {
            "code": "QA-2026-907",
            "delta_hours": 6,
            "product": "Structural Section Flange #91",
            "cat": "Structural Steel",
            "img_file": "demo_sample_rolled_in_scale.jpg",
            "defects": [
                {"name": "Rolled-in Scale", "conf": 0.87, "bbox": [160.0, 96.0, 448.0, 288.0], "area_ratio": 0.078, "sev": "HIGH"}
            ],
            "decision": "MANUAL_REVIEW",
            "max_sev": "HIGH",
            "desc": "Iron oxide mill scale embedded flush or depressed into the steel substrate under high rolling pressure.",
            "loc": "Upper-center edge",
            "causes": ["Delayed primary descaling before entry into roughing mill", "Clogged descaler spray nozzles"],
            "actions": ["Perform acid washing test on sample coupon", "Clean descaler manifold spray header"],
            "summary": "Rolled-in scale requires supervisor review before hot-dip coating."
        },
        {
            "code": "QA-2026-908",
            "delta_hours": 2,
            "product": "Cold Rolled Strip #904",
            "cat": "Strip Substrate",
            "img_file": "demo_sample_clean_steel.jpg",
            "defects": [],
            "decision": "PASS",
            "max_sev": "LOW",
            "desc": "Uniform, flawless metallic grain finish with no observable defects.",
            "loc": "Full surface area",
            "causes": ["Optimal continuous annealing and temper rolling parameters"],
            "actions": ["Authorize for direct dispatch"],
            "summary": "Certified compliant with visual inspection parameters."
        }
    ]

    for rec in demo_data_records:
        orig_path = demo_dir / rec["img_file"]
        if not orig_path.exists():
            continue

        annotated_path = demo_dir / f"annotated_{rec['img_file']}"
        # Generate annotated image
        try:
            image_processor.annotate_image(
                image_path=str(orig_path),
                defects=rec["defects"],
                output_path=str(annotated_path)
            )
        except Exception:
            annotated_path = orig_path

        t_stamp = now - datetime.timedelta(hours=rec["delta_hours"])
        insp = Inspection(
            inspection_code=rec["code"],
            timestamp=t_stamp,
            product_name=rec["product"],
            product_category=rec["cat"],
            original_image_path=str(orig_path),
            annotated_image_path=str(annotated_path),
            total_defects=len(rec["defects"]),
            max_severity=rec["max_sev"],
            overall_decision=rec["decision"],
            confidence_avg=round(rec["defects"][0]["conf"], 3) if rec["defects"] else 0.99,
            inference_time_ms=18.4,
            model_name="YOLOv8n-NEU-DET",
            is_demo=True,
            inference_source="demo_precomputed",
            genai_defect_name=rec["defects"][0]["name"] if rec["defects"] else "None",
            genai_description=rec["desc"],
            genai_location=rec["loc"],
            genai_severity=rec["max_sev"],
            genai_possible_causes=json.dumps(rec["causes"]),
            genai_recommended_actions=json.dumps(rec["actions"]),
            genai_quality_summary=rec["summary"],
            genai_provider_used="Rule-Based Industrial Expert Engine",
            notes="Initial calibration and baseline verification inspection."
        )
        db.add(insp)
        db.flush()

        for d in rec["defects"]:
            defect_obj = DetectedDefect(
                inspection_id=insp.id,
                defect_name=d["name"],
                class_id=0,
                confidence=d["conf"],
                bbox_x1=d["bbox"][0],
                bbox_y1=d["bbox"][1],
                bbox_x2=d["bbox"][2],
                bbox_y2=d["bbox"][3],
                area_pixels=round((d["bbox"][2] - d["bbox"][0]) * (d["bbox"][3] - d["bbox"][1]), 1),
                area_ratio=d["area_ratio"],
                severity_level=d["sev"],
                visual_description=rec["desc"]
            )
            db.add(defect_obj)

    db.commit()
    logger.info("Successfully seeded demo inspections.")
