import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

class MVTecAnomalyDetector:
    """
    Unsupervised / Reference-based optical anomaly detector for MVTec AD dataset.
    Compares industrial test components against normal golden-sample profiles.
    """

    def __init__(self, blur_kernel: int = 15, anomaly_threshold: float = 35.0):
        self.blur_kernel = blur_kernel
        self.anomaly_threshold = anomaly_threshold

    def evaluate_sample(
        self,
        image_path: str,
        normal_reference_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates structural deviations against reference or structural gradient.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        if normal_reference_path and Path(normal_reference_path).exists():
            ref = cv2.imread(normal_reference_path, cv2.IMREAD_GRAYSCALE)
            ref_resized = cv2.resize(ref, (w, h))
            diff = cv2.absdiff(gray, ref_resized)
        else:
            # Self-reference structural deviation using morphological background subtraction
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.blur_kernel, self.blur_kernel))
            background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            diff = cv2.absdiff(gray, background)

        _, mask = cv2.threshold(diff, self.anomaly_threshold, 255, cv2.THRESH_BINARY)
        anomaly_pixels = int(np.count_nonzero(mask))
        total_pixels = h * w
        anomaly_ratio = float(anomaly_pixels) / float(total_pixels)
        anomaly_score = float(np.mean(diff[mask > 0])) if anomaly_pixels > 0 else 0.0

        is_defective = anomaly_ratio > 0.015 or anomaly_score > 40.0

        return {
            "image_path": image_path,
            "anomaly_score": round(anomaly_score, 2),
            "anomaly_area_ratio": round(anomaly_ratio, 4),
            "anomaly_pixel_count": anomaly_pixels,
            "is_anomalous": is_defective,
            "classification": "DEFECTIVE" if is_defective else "NORMAL"
        }

mvtec_anomaly_detector = MVTecAnomalyDetector()
