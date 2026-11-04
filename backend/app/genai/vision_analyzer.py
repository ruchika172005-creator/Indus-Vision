from typing import List, Dict, Any, Tuple
from pathlib import Path
from PIL import Image

class VisionAnalyzer:
    """
    Extracts spatial metadata, image quadrant localization,
    and visual attributes to feed into defect explanations.
    """

    @staticmethod
    def determine_quadrant(bbox: List[float], img_w: int, img_h: int) -> str:
        """
        Calculates human-readable engineering location (e.g., 'Upper-right region').
        """
        if not bbox or len(bbox) < 4:
            return "Center region"
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        horiz = "Center"
        if cx < img_w * 0.35:
            horiz = "Left"
        elif cx > img_w * 0.65:
            horiz = "Right"

        vert = "middle"
        if cy < img_h * 0.35:
            vert = "Upper"
        elif cy > img_h * 0.65:
            vert = "Lower"

        if horiz == "Center" and vert == "middle":
            return "Central surface area"
        elif vert == "middle":
            return f"Mid-{horiz.lower()} edge"
        else:
            return f"{vert}-{horiz.lower()} region"

    @staticmethod
    def crop_defect_region(image_path: str, bbox: List[float], output_path: str) -> str:
        with Image.open(image_path) as img:
            x1, y1, x2, y2 = [int(round(c)) for c in bbox]
            w, h = img.size
            # Add 10% context padding around bbox
            pad_x = int((x2 - x1) * 0.10)
            pad_y = int((y2 - y1) * 0.10)
            box = (
                max(0, x1 - pad_x),
                max(0, y1 - pad_y),
                min(w, x2 + pad_x),
                min(h, y2 + pad_y)
            )
            crop = img.crop(box)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            crop.save(output_path)
            return output_path

vision_analyzer = VisionAnalyzer()
