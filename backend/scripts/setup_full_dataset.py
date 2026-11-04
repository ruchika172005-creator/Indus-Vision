"""
Script to automatically detect, extract, and prepare the complete 1,800-image NEU-DET
or 3,570-image GC10-DET dataset downloaded to your laptop.
"""
import os
import sys
import zipfile
import tarfile
import shutil
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.datasets.neu_det import neu_det_manager
from app.datasets.gc10_det import gc10_det_manager
from app.core.logging import logger

def search_for_zip(dataset_name: str) -> list[Path]:
    """Searches user Downloads and datasets folders for dataset zip files."""
    candidates = []
    search_dirs = [
        Path.home() / "Downloads",
        backend_dir / "datasets",
        backend_dir.parent
    ]
    patterns = {
        "neu_det": ["*neu*", "*NEU*", "*surface*defect*"],
        "gc10_det": ["*gc10*", "*GC10*"]
    }
    
    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for pat in patterns.get(dataset_name, []):
            for f in sdir.glob(f"{pat}.zip"):
                if f.is_file():
                    candidates.append(f)
    return list(set(candidates))

def extract_and_organize_neu(zip_path: Path):
    target_dir = backend_dir / "datasets" / "neu_det"
    temp_extract = target_dir / "_temp_extract"
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[1/3] Extracting '{zip_path.name}' to {target_dir}...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(temp_extract)

    # Locate IMAGES and ANNOTATIONS folders recursively
    raw_images = None
    raw_annots = None
    for p in temp_extract.rglob("*"):
        if p.is_dir():
            if p.name.lower() in ["images", "img"]:
                raw_images = p
            elif p.name.lower() in ["annotations", "annotation", "xml"]:
                raw_annots = p

    dest_images = target_dir / "IMAGES"
    dest_annots = target_dir / "ANNOTATIONS"
    dest_images.mkdir(parents=True, exist_ok=True)
    dest_annots.mkdir(parents=True, exist_ok=True)

    if raw_images:
        print("[2/3] Moving image files...")
        for img in raw_images.glob("*.*"):
            if img.suffix.lower() in [".jpg", ".jpeg", ".bmp", ".png"]:
                shutil.copy2(img, dest_images / img.name)
    
    if raw_annots:
        print("[2/3] Moving annotation XML files...")
        for xml in raw_annots.glob("*.xml"):
            shutil.copy2(xml, dest_annots / xml.name)

    # Clean up temp
    shutil.rmtree(temp_extract, ignore_errors=True)

    img_count = len(list(dest_images.glob("*.*")))
    xml_count = len(list(dest_annots.glob("*.xml")))
    print(f"Extracted: {img_count} images, {xml_count} XML annotations.")

    print("\n[3/3] Running automated YOLO split partitioning (70% train / 15% val / 15% test)...")
    stats = neu_det_manager.prepare_yolo_dataset()
    print("\nSUCCESS! Complete NEU-DET is ready:")
    print(f"  Total Images: {stats['total_images']}")
    print(f"  Train:        {stats['train_images']}")
    print(f"  Validation:   {stats['val_images']}")
    print(f"  Test:         {stats['test_images']}")
    print(f"  YAML Config:  {stats['yaml_config_path']}")

def main():
    print("=" * 65)
    print(" Complete Industrial Defect Dataset Installer & YOLO Partitioner")
    print("=" * 65)
    
    zips = search_for_zip("neu_det")
    if zips:
        print(f"Found archive: {zips[0]}")
        extract_and_organize_neu(zips[0])
    else:
        print("\nNo dataset archive (.zip) found automatically in your Downloads folder.")
        print("\nTo install the complete 1,800-image NEU-DET dataset:")
        print("1. Download the zip from Kaggle:")
        print("   https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database")
        print("2. Place the downloaded .zip file into either:")
        print("   - Your 'Downloads' folder, OR")
        print(f"   - '{backend_dir / 'datasets'}'")
        print("3. Re-run this script, or click 'Prepare Splits' in the web dashboard!")

if __name__ == "__main__":
    main()

