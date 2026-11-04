import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from app.ml.detector import DefectDetector
from app.ml.severity_engine import severity_engine
from app.ml.image_processor import image_processor
from app.ml.model_manager import model_manager
from app.genai.explanation_generator import explanation_generator
from app.core.config import settings
from app.core.logging import logger

class InspectionPipeline:
    """
    Unified end-to-end inference orchestrator:
    Loads Image -> Detects Bounding Boxes -> Assesses Defect Severity ->
    Generates Annotated Visualization -> Synthesizes Multimodal GenAI Explanation.
    """

    def __init__(self):
        pass

    async def run_inspection(
        self,
        image_path: str,
        product_name: str = "Steel Component",
        product_category: str = "Steel Plate",
        model_name: Optional[str] = None,
        conf_threshold: float = 0.35,
        iou_threshold: float = 0.45
    ) -> Dict[str, Any]:
        """
        Executes complete quality inspection pipeline.
        """
        selected_model = model_name or model_manager.active_model_name
        weights_path = model_manager.get_model_path(selected_model)
        dataset_key = "gc10_det" if "GC10" in selected_model else "neu_det"

        # 1. Initialize detector
        detector = DefectDetector(model_path=weights_path, dataset_name=dataset_key)

        # 2. Get image dimensions
        with Image.open(image_path) as img:
            img_w, img_h = img.size

        # 3. Computer Vision Detection
        raw_defects, inference_time_ms, inference_source = detector.predict(
            image_path=image_path,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold
        )

        # 4. Severity Assessment Engine
        processed_defects = []
        for d in raw_defects:
            evaluated = severity_engine.evaluate_defect(
                defect_name=d["defect_name"],
                bbox=d["bbox"],
                image_width=img_w,
                image_height=img_h,
                confidence=d["confidence"]
            )
            evaluated["class_id"] = d.get("class_id", 0)
            processed_defects.append(evaluated)

        overall_decision, max_severity, decision_meta = severity_engine.evaluate_inspection(
            defects=processed_defects,
            image_width=img_w,
            image_height=img_h
        )

        # 5. Generate Annotated Image
        annotated_filename = f"annotated_{uuid.uuid4().hex[:8]}_{Path(image_path).name}"
        annotated_path = str(settings.UPLOAD_DIR / annotated_filename)
        image_processor.annotate_image(
            image_path=image_path,
            defects=processed_defects,
            output_path=annotated_path
        )

        # 6. Multimodal GenAI Defect Explanation
        is_demo = (inference_source != "real_yolo_model")
        genai_result = await explanation_generator.generate(
            image_path=image_path,
            defects=processed_defects,
            product_category=product_category,
            detection_metadata=decision_meta,
            image_width=img_w,
            image_height=img_h
        )

        # Average confidence
        conf_avg = 0.0
        if processed_defects:
            conf_avg = round(sum(d["confidence"] for d in processed_defects) / len(processed_defects), 3)

        return {
            "product_name": product_name,
            "product_category": product_category,
            "original_image_path": str(image_path),
            "annotated_image_path": str(annotated_path),
            "total_defects": len(processed_defects),
            "max_severity": max_severity,
            "overall_decision": overall_decision,
            "confidence_avg": conf_avg,
            "inference_time_ms": inference_time_ms,
            "model_name": selected_model,
            "is_demo": is_demo,
            "inference_source": inference_source,
            "defects": processed_defects,
            "explanation": genai_result,
            "decision_metadata": decision_meta
        }

inspection_pipeline = InspectionPipeline()
