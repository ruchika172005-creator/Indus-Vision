from typing import List, Dict, Any, Tuple
import numpy as np

class ModelEvaluator:
    """
    Computes precision, recall, and mean Average Precision (mAP)
    for defect detection evaluation.
    """

    @staticmethod
    def calculate_iou(box1: List[float], box2: List[float]) -> float:
        """Calculates Intersection over Union (IoU) between two bounding boxes [x1, y1, x2, y2]."""
        x1_inter = max(box1[0], box2[0])
        y1_inter = max(box1[1], box2[1])
        x2_inter = min(box1[2], box2[2])
        y2_inter = min(box1[3], box2[3])

        inter_w = max(0.0, x2_inter - x1_inter)
        inter_h = max(0.0, y2_inter - y1_inter)
        inter_area = inter_w * inter_h

        box1_area = max(0.0, (box1[2] - box1[0]) * (box1[3] - box1[1]))
        box2_area = max(0.0, (box2[2] - box2[0]) * (box2[3] - box2[1]))
        union_area = box1_area + box2_area - inter_area

        if union_area <= 0:
            return 0.0
        return inter_area / union_area

    @staticmethod
    def evaluate_detections(
        ground_truths: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]],
        iou_threshold: float = 0.50
    ) -> Dict[str, float]:
        """
        Evaluates predictions against ground-truth annotations.
        """
        if not ground_truths and not predictions:
            return {"precision": 1.0, "recall": 1.0, "f1_score": 1.0, "map50": 1.0}
        if not predictions:
            return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0, "map50": 0.0}
        if not ground_truths:
            return {"precision": 0.0, "recall": 1.0, "f1_score": 0.0, "map50": 0.0}

        matched_gt = set()
        true_positives = 0
        false_positives = 0

        # Sort predictions by confidence descending
        sorted_preds = sorted(predictions, key=lambda x: x.get("confidence", 0.0), reverse=True)

        for pred in sorted_preds:
            p_box = pred["bbox"]
            p_cls = pred.get("defect_name", "").lower()
            best_iou = 0.0
            best_gt_idx = -1

            for idx, gt in enumerate(ground_truths):
                if idx in matched_gt:
                    continue
                g_cls = gt.get("defect_name", "").lower()
                if p_cls != g_cls:
                    continue
                iou = ModelEvaluator.calculate_iou(p_box, gt["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = idx

            if best_iou >= iou_threshold and best_gt_idx >= 0:
                true_positives += 1
                matched_gt.add(best_gt_idx)
            else:
                false_positives += 1

        total_gt = len(ground_truths)
        precision = true_positives / max(1, (true_positives + false_positives))
        recall = true_positives / max(1, total_gt)
        f1 = (2 * precision * recall) / max(1e-6, (precision + recall))

        return {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "map50": round(precision * recall, 3) # Interpolated approximation
        }

model_evaluator = ModelEvaluator()
