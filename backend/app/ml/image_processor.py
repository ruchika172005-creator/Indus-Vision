import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image

# High-contrast BGR colors for industrial inspection visualization
SEVERITY_COLORS_BGR = {
    "LOW": (94, 197, 34),       # Industrial Green
    "MEDIUM": (11, 158, 245),    # Vibrant Amber
    "HIGH": (22, 115, 249),      # Safety Orange
    "CRITICAL": (68, 68, 239)    # Alert Red
}

class ImageProcessor:
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """Loads an image via OpenCV, preserving 3-channel BGR."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found at {image_path}")
        img = cv2.imread(str(path))
        if img is None:
            raise ValueError(f"Failed to decode image from {image_path}")
        return img

    @staticmethod
    def get_image_dimensions(image_path: str) -> Tuple[int, int]:
        with Image.open(image_path) as img:
            return img.width, img.height

    @staticmethod
    def annotate_image(
        image_path: str,
        defects: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        Draws industrial-grade bounding boxes, corner indicators,
        semi-transparent highlight fills, and defect badge labels.
        """
        img = ImageProcessor.load_image(image_path)
        overlay = img.copy()
        h, w = img.shape[:2]

        for defect in defects:
            bbox = defect["bbox"]
            x1, y1, x2, y2 = [int(round(coord)) for coord in bbox]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)

            severity = defect.get("severity_level", "LOW")
            color = SEVERITY_COLORS_BGR.get(severity, (94, 197, 34))

            # 1. Semi-transparent fill
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

            # 2. Main bounding box line
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            # 3. Precision corner brackets (industrial crosshair feel)
            corner_len = min(16, max(6, (x2 - x1) // 4, (y2 - y1) // 4))
            # Top-left
            cv2.line(img, (x1, y1), (x1 + corner_len, y1), color, 3)
            cv2.line(img, (x1, y1), (x1, y1 + corner_len), color, 3)
            # Top-right
            cv2.line(img, (x2, y1), (x2 - corner_len, y1), color, 3)
            cv2.line(img, (x2, y1), (x2, y1 + corner_len), color, 3)
            # Bottom-left
            cv2.line(img, (x1, y2), (x1 + corner_len, y2), color, 3)
            cv2.line(img, (x1, y2), (x1, y2 - corner_len), color, 3)
            # Bottom-right
            cv2.line(img, (x2, y2), (x2 - corner_len, y2), color, 3)
            cv2.line(img, (x2, y2), (x2 - corner_len, y2), color, 3)

            # 4. High-contrast text label badge
            name = defect.get("defect_name", "Defect")
            conf = defect.get("confidence", 0.0)
            label = f"{name} {int(conf * 100)}% [{severity}]"

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.45
            thickness = 1
            (tw, th), baseline = cv2.getTextSize(label, font, font_scale, thickness)

            badge_y1 = max(0, y1 - th - 8)
            badge_y2 = y1
            badge_x1 = x1
            badge_x2 = min(w, x1 + tw + 10)

            # Badge background
            cv2.rectangle(img, (badge_x1, badge_y1), (badge_x2, badge_y2), (15, 23, 42), -1) # Dark Slate
            cv2.rectangle(img, (badge_x1, badge_y1), (badge_x2, badge_y2), color, 1)

            # Badge text (White)
            cv2.putText(
                img,
                label,
                (badge_x1 + 4, badge_y2 - 4),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )

        # Blend overlay (20% opacity on defect regions)
        alpha = 0.20
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        # Save annotated image
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, img)
        return output_path

image_processor = ImageProcessor()
