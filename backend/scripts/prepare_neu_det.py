import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.datasets.neu_det import neu_det_manager
from app.core.logging import logger

def main():
    logger.info("Starting NEU-DET dataset preparation pipeline...")
    try:
        stats = neu_det_manager.prepare_yolo_dataset()
        print("\nNEU-DET Preparation Summary:")
        print(f"Total Images: {stats['total_images']}")
        print(f"Train Split:  {stats['train_images']}")
        print(f"Val Split:    {stats['val_images']}")
        print(f"Test Split:   {stats['test_images']}")
        print(f"Dataset YAML: {stats['yaml_config_path']}")
        print("\nClasses:")
        for cls_name, count in stats["class_distribution"].items():
            print(f"  - {cls_name}: {count} instances")
    except Exception as e:
        logger.error(f"Preparation failed: {e}")
        print("\nInstructions:")
        print("Please ensure raw NEU-DET dataset is placed in 'backend/datasets/neu_det/'")
        print("with 'IMAGES/' and 'ANNOTATIONS/' folders.")

if __name__ == "__main__":
    main()
