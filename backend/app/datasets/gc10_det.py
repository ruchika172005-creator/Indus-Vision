import os
import shutil
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import yaml

from app.datasets.annotation_converter import annotation_converter
from app.datasets.dataset_statistics import dataset_statistics
from app.core.config import settings
from app.core.logging import logger

GC10_CLASSES = [
    "punching hole",
    "welding line",
    "crescent gap",
    "water spot",
    "oil spot",
    "silk spot",
    "inclusion",
    "rolled-in scale",
    "scratches",
    "waist folding"
]

GC10_CLASS_MAPPING = {
    # 0: Punching hole
    "1_chongkong": 0, "chongkong": 0, "punching hole": 0, "punching_hole": 0, "punching-hole": 0,
    # 1: Welding line
    "2_hanfeng": 1, "hanfeng": 1, "welding line": 1, "welding_line": 1, "welding-line": 1,
    # 2: Crescent gap
    "3_yueyawan": 2, "yueyawan": 2, "crescent gap": 2, "crescent_gap": 2, "crescent-gap": 2,
    # 3: Water spot
    "4_shuiban": 3, "shuiban": 3, "water spot": 3, "water_spot": 3, "water-spot": 3,
    # 4: Oil spot
    "5_youban": 4, "youban": 4, "oil spot": 4, "oil_spot": 4, "oil-spot": 4,
    # 5: Silk spot
    "6_siban": 5, "siban": 5, "silk spot": 5, "silk_spot": 5, "silk-spot": 5,
    # 6: Inclusion
    "7_yabing": 6, "yabing": 6, "inclusion": 6,
    # 7: Rolled-in scale
    "8_daopian": 7, "daopian": 7, "rolled-in scale": 7, "rolled-in_scale": 7, "rolled_in_scale": 7, "rolled in scale": 7,
    # 8: Scratches
    "9_huashen": 8, "huashen": 8, "scratches": 8, "scratch": 8,
    # 9: Waist folding
    "10_yaozhe": 9, "yaozhe": 9, "waist folding": 9, "waist_folding": 9, "waist-folding": 9
}

class GC10DETManager:
    """
    Manager for the GC10-DET (10-class metallic surface defect dataset, Lv et al., 2020).
    Expected structure:
      gc10_det/
        images/ (.jpg files, 3,570 images across 10 defect modes)
        labelxml/ (.xml Pascal VOC annotations)
    """

    def __init__(self, root_dir: str = None):
        self.root_dir = Path(root_dir) if root_dir else settings.DATASETS_DIR / "gc10_det"
        self.yolo_dir = self.root_dir / "yolo"
        self.yaml_path = self.root_dir / "dataset.yaml"
        self.yolo_yaml_path = self.yolo_dir / "dataset.yaml"

    def _find_raw_dirs(self) -> Tuple[Optional[Path], Optional[Path]]:
        """Dynamically locates images and XML annotations directories."""
        images_dir = None
        for cand in ["images", "IMAGES", "img"]:
            p = self.root_dir / cand
            if p.exists() and p.is_dir():
                images_dir = p
                break

        annotations_dir = None
        for cand in ["labelxml", "xml", "annotations", "ANNOTATIONS"]:
            p = self.root_dir / cand
            if p.exists() and p.is_dir():
                annotations_dir = p
                break

        return images_dir, annotations_dir

    def is_downloaded(self) -> bool:
        images_dir, _ = self._find_raw_dirs()
        if not images_dir:
            return False
        return dataset_statistics.count_images_in_dir(str(images_dir)) >= 1

    def is_prepared(self) -> bool:
        has_yaml = self.yaml_path.exists() or self.yolo_yaml_path.exists()
        has_train = (self.yolo_dir / "images" / "train").exists()
        return bool(has_yaml and has_train)

    def get_statistics(self) -> Dict[str, Any]:
        downloaded = self.is_downloaded()
        prepared = self.is_prepared()
        size_mb = dataset_statistics.get_directory_size_mb(str(self.root_dir))

        if prepared:
            stats = dataset_statistics.compute_yolo_dataset_stats(str(self.yolo_dir), GC10_CLASSES)
        else:
            images_dir, _ = self._find_raw_dirs()
            raw_img_count = dataset_statistics.count_images_in_dir(str(images_dir)) if images_dir else 0
            stats = {
                "total_images": raw_img_count,
                "train_images": 0,
                "val_images": 0,
                "test_images": 0,
                "class_distribution": {c: 0 for c in GC10_CLASSES},
                "disk_size_mb": size_mb,
                "is_prepared": False
            }

        return {
            "name": "gc10_det",
            "display_name": "GC10-DET Metallic Surface Defect Dataset",
            "category": "Metallic Surface Defects",
            "source_url": "https://github.com/Spider-Man-Graph/GC10-DET-Dataset",
            "description": "Comprehensive benchmark covering 10 industrial metallic sheet defect categories (exactly 3,570 images across 10 classes).",
            "is_downloaded": downloaded,
            "is_prepared": prepared,
            "classes": GC10_CLASSES,
            "num_classes": len(GC10_CLASSES),
            "annotation_type": "XML Annotations -> YOLO Format",
            "local_path": str(self.root_dir),
            "yaml_config_path": str(self.yaml_path) if prepared else None,
            **stats
        }

    def prepare_yolo_dataset(self, train_ratio=0.70, val_ratio=0.15, seed=42) -> Dict[str, Any]:
        raw_images, raw_annotations = self._find_raw_dirs()

        if not raw_images or not raw_annotations:
            raise FileNotFoundError(
                f"Cannot prepare GC10-DET: images or labelxml directory not found in {self.root_dir}."
            )

        for split in ["train", "val", "test"]:
            (self.yolo_dir / "images" / split).mkdir(parents=True, exist_ok=True)
            (self.yolo_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

        image_files = sorted([f for f in raw_images.glob("*.*") if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]])
        if not image_files:
            raise ValueError(f"No image files found in {raw_images}")

        random.seed(seed)
        shuffled = image_files.copy()
        random.shuffle(shuffled)

        n = len(shuffled)
        if n >= 3:
            n_train = max(1, int(n * train_ratio))
            n_val = max(1, int(n * val_ratio))
            if n_train + n_val >= n:
                n_train = max(1, n - 2)
                n_val = 1
        else:
            n_train = n
            n_val = 0

        splits = {
            "train": shuffled[:n_train],
            "val": shuffled[n_train:n_train + n_val],
            "test": shuffled[n_train + n_val:]
        }

        processed = 0
        for split_name, files in splits.items():
            for img_path in files:
                xml_path = raw_annotations / f"{img_path.stem}.xml"
                if not xml_path.exists():
                    continue

                dest_img = self.yolo_dir / "images" / split_name / img_path.name
                shutil.copy2(img_path, dest_img)

                try:
                    records = annotation_converter.voc_xml_to_yolo(
                        str(xml_path), GC10_CLASS_MAPPING, image_path=str(img_path)
                    )
                    dest_txt = self.yolo_dir / "labels" / split_name / f"{img_path.stem}.txt"
                    annotation_converter.save_yolo_annotation(records, str(dest_txt))
                    processed += 1
                except Exception as e:
                    logger.warning(f"Error converting GC10 annotation for {img_path.name}: {e}")

        yaml_content = {
            "path": str(self.yolo_dir.resolve()),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "names": {i: name for i, name in enumerate(GC10_CLASSES)}
        }

        # Save to both root_dir and yolo_dir
        with open(self.yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_content, f, sort_keys=False)
        with open(self.yolo_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_content, f, sort_keys=False)

        logger.info(f"GC10-DET preparation completed: {processed} images processed.")
        return self.get_statistics()

    def initialize_demo_subset(self) -> Dict[str, Any]:
        """
        Populates a demonstration subset for GC10-DET with Pascal VOC XML annotations.
        """
        raw_images = self.root_dir / "images"
        raw_annotations = self.root_dir / "labelxml"
        raw_images.mkdir(parents=True, exist_ok=True)
        raw_annotations.mkdir(parents=True, exist_ok=True)

        demo_src_dir = settings.DATASETS_DIR / "demo"
        if not demo_src_dir.exists():
            raise FileNotFoundError("Demo sample source images directory not found.")

        from PIL import Image

        # Map available defect templates to GC10 defect modes
        class_configs = {
            "punching hole": ("demo_sample_pitted_surface.jpg", (200, 200, 440, 440)),
            "welding line": ("demo_sample_scratches.jpg", (80, 280, 560, 360)),
            "crescent gap": ("demo_sample_patches.jpg", (90, 110, 500, 480)),
            "water spot": ("demo_sample_crazing.jpg", (100, 100, 540, 540)),
            "oil spot": ("demo_sample_patches.jpg", (120, 120, 480, 480)),
            "silk spot": ("demo_sample_crazing.jpg", (70, 90, 520, 510)),
            "inclusion": ("demo_sample_inclusion.jpg", (120, 150, 480, 490)),
            "rolled-in scale": ("demo_sample_rolled_in_scale.jpg", (100, 120, 530, 500)),
            "scratches": ("demo_sample_scratches.jpg", (80, 90, 560, 540)),
            "waist folding": ("demo_sample_rolled_in_scale.jpg", (50, 200, 590, 440))
        }

        created = 0
        for cls_name, (sample_file, (xmin, ymin, xmax, ymax)) in class_configs.items():
            src_file = demo_src_dir / sample_file
            if not src_file.exists():
                continue

            with Image.open(src_file) as base_im:
                w, h = base_im.size
                safe_name = cls_name.replace(" ", "_")
                # Variation 1: Original
                fn1 = f"{safe_name}_1.jpg"
                base_im.save(raw_images / fn1, quality=95)
                self._write_voc_xml(raw_annotations / f"{safe_name}_1.xml", fn1, cls_name, w, h, xmin, ymin, xmax, ymax)
                created += 1

                # Variation 2: Flipped
                fn2 = f"{safe_name}_2.jpg"
                im_flip = base_im.transpose(Image.FLIP_LEFT_RIGHT)
                im_flip.save(raw_images / fn2, quality=95)
                self._write_voc_xml(raw_annotations / f"{safe_name}_2.xml", fn2, cls_name, w, h, w - xmax, ymin, w - xmin, ymax)
                created += 1

        logger.info(f"Initialized demonstration subset for GC10-DET with {created} images.")
        return self.get_statistics()

    def _write_voc_xml(self, xml_path: Path, filename: str, class_name: str, width: int, height: int, xmin: int, ymin: int, xmax: int, ymax: int):
        xml_content = f"""<annotation>
    <folder>images</folder>
    <filename>{filename}</filename>
    <size>
        <width>{width}</width>
        <height>{height}</height>
        <depth>3</depth>
    </size>
    <object>
        <name>{class_name}</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>{max(1, int(xmin))}</xmin>
            <ymin>{max(1, int(ymin))}</ymin>
            <xmax>{min(width - 1, int(xmax))}</xmax>
            <ymax>{min(height - 1, int(ymax))}</ymax>
        </bndbox>
    </object>
</annotation>"""
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content.strip())

gc10_det_manager = GC10DETManager()
