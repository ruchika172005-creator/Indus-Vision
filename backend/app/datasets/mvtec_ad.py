import os
from pathlib import Path
from typing import Dict, Any, List
from app.datasets.dataset_statistics import dataset_statistics
from app.core.config import settings

MVTEC_SUBSETS = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

class MVTecADManager:
    """
    Manager for MVTec Anomaly Detection (MVTec AD) benchmark.
    Preserves original folder structure:
      mvtec_ad/
        <object_category>/ (e.g., metal_nut)
          train/good/ (.png normal golden samples)
          test/good/ (.png normal test samples)
          test/<defect_type>/ (e.g. scratch, bent, color)
          ground_truth/<defect_type>/ (.png binary defect masks)
    """

    def __init__(self, root_dir: str = None):
        self.root_dir = Path(root_dir) if root_dir else settings.DATASETS_DIR / "mvtec_ad"

    def is_downloaded(self) -> bool:
        if not self.root_dir.exists():
            return False
        # Check if at least one category directory exists with train/good
        for sub in self.root_dir.iterdir():
            if sub.is_dir() and (sub / "train" / "good").exists():
                return True
        return False

    def is_prepared(self) -> bool:
        return self.is_downloaded()

    def get_statistics(self) -> Dict[str, Any]:
        downloaded = self.is_downloaded()
        size_mb = dataset_statistics.get_directory_size_mb(str(self.root_dir))

        total_images = 0
        normal_train = 0
        normal_test = 0
        defective_test = 0
        mask_count = 0
        subsets_found = []

        if self.root_dir.exists():
            for sub in self.root_dir.iterdir():
                if sub.is_dir():
                    train_good = sub / "train" / "good"
                    if train_good.exists():
                        subsets_found.append(sub.name)
                        n_tr = dataset_statistics.count_images_in_dir(str(train_good))
                        normal_train += n_tr

                        test_dir = sub / "test"
                        if test_dir.exists():
                            for d in test_dir.iterdir():
                                if d.is_dir():
                                    count = dataset_statistics.count_images_in_dir(str(d))
                                    if d.name == "good":
                                        normal_test += count
                                    else:
                                        defective_test += count

                        gt_dir = sub / "ground_truth"
                        if gt_dir.exists():
                            mask_count += dataset_statistics.count_images_in_dir(str(gt_dir))

        total_images = normal_train + normal_test + defective_test

        return {
            "name": "mvtec_ad",
            "display_name": "MVTec Anomaly Detection (MVTec AD)",
            "category": "Industrial Anomaly Detection & Segmentation",
            "source_url": "https://www.mvtec.com/company/research/datasets/mvtec-ad",
            "description": "Comprehensive industrial anomaly detection benchmark across 15 categories (10 objects, 5 textures: 5,354 total images with pixel-precise binary ground truth defect masks).",
            "is_downloaded": downloaded,
            "is_prepared": downloaded,
            "total_images": total_images,
            "normal_training_images": normal_train,
            "normal_test_images": normal_test,
            "defective_test_images": defective_test,
            "ground_truth_masks": mask_count,
            "subsets_available": subsets_found,
            "num_classes": 15,
            "classes": MVTEC_SUBSETS,
            "available_classes": subsets_found,
            "annotation_type": "Pixel-Level Binary Anomaly Masks (Ground Truth)",
            "disk_size_mb": size_mb,
            "local_path": str(self.root_dir),
            "yaml_config_path": None # MVTec AD is an unsupervised pixel-level anomaly benchmark, not YOLO bounding boxes
        }

mvtec_ad_manager = MVTecADManager()
