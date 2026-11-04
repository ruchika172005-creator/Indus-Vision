import os
from pathlib import Path
from typing import Dict, Any, List

class DatasetStatistics:
    @staticmethod
    def get_directory_size_mb(directory_path: str) -> float:
        """Calculates actual on-disk size of directory in Megabytes."""
        path = Path(directory_path)
        if not path.exists():
            return 0.0
        total_bytes = sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
        return round(total_bytes / (1024 * 1024), 2)

    @staticmethod
    def count_images_in_dir(directory_path: str) -> int:
        """Counts real image files (.jpg, .jpeg, .png, .bmp, .tif)."""
        path = Path(directory_path)
        if not path.exists():
            return 0
        extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
        return sum(1 for f in path.glob("**/*") if f.suffix.lower() in extensions)

    @staticmethod
    def compute_yolo_dataset_stats(dataset_root: str, classes: List[str]) -> Dict[str, Any]:
        """
        Calculates split counts and label statistics for a YOLO formatted dataset.
        """
        root = Path(dataset_root)
        images_dir = root / "images"
        labels_dir = root / "labels"

        train_imgs = DatasetStatistics.count_images_in_dir(str(images_dir / "train"))
        val_imgs = DatasetStatistics.count_images_in_dir(str(images_dir / "val"))
        test_imgs = DatasetStatistics.count_images_in_dir(str(images_dir / "test"))
        total = train_imgs + val_imgs + test_imgs

        # Count defect instances per class from labels
        class_counts = {c: 0 for c in classes}
        if labels_dir.exists():
            for label_file in labels_dir.glob("**/*.txt"):
                with open(label_file, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if parts:
                            cls_id = int(parts[0])
                            if 0 <= cls_id < len(classes):
                                class_counts[classes[cls_id]] += 1

        size_mb = DatasetStatistics.get_directory_size_mb(dataset_root)

        has_yaml = (root / "dataset.yaml").exists() or (root.parent / "dataset.yaml").exists()

        return {
            "total_images": total,
            "train_images": train_imgs,
            "val_images": val_imgs,
            "test_images": test_imgs,
            "class_distribution": class_counts,
            "disk_size_mb": size_mb,
            "is_prepared": total > 0 and has_yaml
        }

dataset_statistics = DatasetStatistics()
