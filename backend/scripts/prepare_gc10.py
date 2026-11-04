import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.datasets.gc10_det import gc10_det_manager
from app.core.logging import logger

def main():
    logger.info("Starting GC10-DET metallic dataset preparation...")
    try:
        stats = gc10_det_manager.prepare_yolo_dataset()
        print("\nGC10-DET Preparation Summary:")
        print(f"Total Images: {stats['total_images']}")
        print(f"Train Split:  {stats['train_images']}")
        print(f"Val Split:    {stats['val_images']}")
        print(f"Test Split:   {stats['test_images']}")
        print(f"Dataset YAML: {stats['yaml_config_path']}")
    except Exception as e:
        logger.error(f"Preparation failed: {e}")
        print("\nInstructions:")
        print("Please ensure raw GC10-DET dataset is placed in 'backend/datasets/gc10_det/'")
        print("with 'images/' and 'labelxml/' folders.")

if __name__ == "__main__":
    main()
