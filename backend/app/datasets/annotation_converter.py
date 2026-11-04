import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class AnnotationConverter:
    """
    Parses Pascal VOC XML annotations and converts them to standard YOLO format:
    <class_index> <x_center> <y_center> <width> <height> (normalized 0.0 to 1.0)
    """

    @staticmethod
    def voc_xml_to_yolo(
        xml_path: str,
        class_mapping: Dict[str, int],
        image_path: Optional[str] = None
    ) -> List[Tuple[int, float, float, float, float]]:
        """
        Reads Pascal VOC XML and returns list of (class_id, x_center, y_center, w, h).
        If image dimensions are missing or invalid in XML, attempts to read from image_path.
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()

        img_w = 0.0
        img_h = 0.0

        size_el = root.find("size")
        if size_el is not None:
            w_el = size_el.find("width")
            h_el = size_el.find("height")
            if w_el is not None and w_el.text:
                try:
                    img_w = float(w_el.text)
                except ValueError:
                    img_w = 0.0
            if h_el is not None and h_el.text:
                try:
                    img_h = float(h_el.text)
                except ValueError:
                    img_h = 0.0

        # Fallback to actual image file if dimensions in XML are missing or non-positive
        if img_w <= 0 or img_h <= 0:
            candidate_img = image_path
            if not candidate_img:
                filename_el = root.find("filename")
                if filename_el is not None and filename_el.text:
                    fn = filename_el.text.strip()
                    xml_p = Path(xml_path)
                    for parent_cand in [xml_p.parent, xml_p.parent.parent / "images", xml_p.parent.parent / "IMAGES"]:
                        if (parent_cand / fn).exists():
                            candidate_img = str(parent_cand / fn)
                            break
            if candidate_img and Path(candidate_img).exists():
                try:
                    from PIL import Image
                    with Image.open(candidate_img) as im:
                        img_w, img_h = float(im.width), float(im.height)
                except Exception:
                    pass

        if img_w <= 0 or img_h <= 0:
            raise ValueError(f"Invalid image dimensions ({img_w}x{img_h}) in {xml_path}")

        yolo_records = []
        for obj in root.findall("object"):
            name_el = obj.find("name")
            if name_el is None or not name_el.text:
                continue
            name = name_el.text.strip()
            # Match normalized variations
            clean_name = name.lower()
            clean_under = clean_name.replace(" ", "_").replace("-", "_")
            clean_space = clean_name.replace("_", " ").replace("-", " ")
            class_id = class_mapping.get(clean_name, 
                       class_mapping.get(clean_under, 
                       class_mapping.get(clean_space, 
                       class_mapping.get(name, -1))))
            if class_id == -1:
                continue

            bndbox = obj.find("bndbox")
            if bndbox is None:
                continue

            try:
                raw_xmin = float(bndbox.find("xmin").text)
                raw_ymin = float(bndbox.find("ymin").text)
                raw_xmax = float(bndbox.find("xmax").text)
                raw_ymax = float(bndbox.find("ymax").text)
            except (ValueError, AttributeError):
                continue

            # Ensure proper ordering and clip to [0, dimension]
            xmin = max(0.0, min(float(img_w), min(raw_xmin, raw_xmax)))
            xmax = max(0.0, min(float(img_w), max(raw_xmin, raw_xmax)))
            ymin = max(0.0, min(float(img_h), min(raw_ymin, raw_ymax)))
            ymax = max(0.0, min(float(img_h), max(raw_ymin, raw_ymax)))

            bw = xmax - xmin
            bh = ymax - ymin
            if bw <= 0.0 or bh <= 0.0:
                continue

            cx = xmin + bw / 2.0
            cy = ymin + bh / 2.0

            norm_cx = max(0.0, min(1.0, cx / img_w))
            norm_cy = max(0.0, min(1.0, cy / img_h))
            norm_w = max(0.0, min(1.0, bw / img_w))
            norm_h = max(0.0, min(1.0, bh / img_h))

            yolo_records.append((class_id, norm_cx, norm_cy, norm_w, norm_h))

        return yolo_records

    @staticmethod
    def save_yolo_annotation(records: List[Tuple[int, float, float, float, float]], output_txt_path: str):
        """Writes YOLO format txt file."""
        lines = [f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}" for cls_id, cx, cy, w, h in records]
        Path(output_txt_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))

    @staticmethod
    def read_yolo_annotation(txt_path: str, img_w: int, img_h: int) -> List[Dict[str, Any]]:
        """Reads YOLO format txt file and converts to pixel bboxes."""
        path = Path(txt_path)
        if not path.exists():
            return []

        boxes = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    cx, cy, w, h = [float(p) for p in parts[1:5]]
                    x1 = (cx - w / 2.0) * img_w
                    y1 = (cy - h / 2.0) * img_h
                    x2 = (cx + w / 2.0) * img_w
                    y2 = (cy + h / 2.0) * img_h
                    boxes.append({
                        "class_id": cls_id,
                        "bbox": [x1, y1, x2, y2]
                    })
        return boxes

annotation_converter = AnnotationConverter()
