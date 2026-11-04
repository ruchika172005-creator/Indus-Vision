import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image

def generate_base_steel_texture(width=640, height=640, base_val=170) -> np.ndarray:
    """Generates brushed steel plate texture with realistic lighting gradient and grain."""
    # Gradient across rolling direction
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xv, yv = np.meshgrid(x, y)
    gradient = (xv * 15 + yv * 10).astype(np.float32)

    # Base gray texture
    img = np.full((height, width), base_val, dtype=np.float32) + gradient

    # Brushed grain streaks along horizontal axis
    grain = np.random.normal(0, 6, (height, width)).astype(np.float32)
    grain = cv2.GaussianBlur(grain, (1, 15), 0)
    img += grain

    # High frequency metal noise
    noise = np.random.normal(0, 3, (height, width)).astype(np.float32)
    img += noise

    img = np.clip(img, 40, 245).astype(np.uint8)
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def create_demo_clean_steel(out_path: str):
    img = generate_base_steel_texture()
    cv2.imwrite(out_path, img)

def create_demo_scratches(out_path: str):
    img = generate_base_steel_texture()
    # Draw longitudinal scratch tracks
    h, w = img.shape[:2]
    # Primary deep scratch
    pts = np.array([[int(w * 0.12), int(h * 0.35)], [int(w * 0.45), int(h * 0.38)], [int(w * 0.88), int(h * 0.40)]], np.int32)
    cv2.polylines(img, [pts], False, (70, 70, 70), 3, cv2.LINE_AA)
    # Bright highlight scratch reflection
    cv2.polylines(img, [pts + [0, 2]], False, (230, 230, 230), 1, cv2.LINE_AA)

    # Secondary parallel scratches
    pts2 = np.array([[int(w * 0.20), int(h * 0.44)], [int(w * 0.65), int(h * 0.46)]], np.int32)
    cv2.polylines(img, [pts2], False, (85, 85, 85), 2, cv2.LINE_AA)
    cv2.imwrite(out_path, img)

def create_demo_crazing(out_path: str):
    img = generate_base_steel_texture()
    h, w = img.shape[:2]
    # Spiderweb network of micro cracks in center-upper area
    np.random.seed(42)
    cx, cy = int(w * 0.45), int(h * 0.45)
    for _ in range(35):
        x1 = np.random.randint(cx - 150, cx + 150)
        y1 = np.random.randint(cy - 120, cy + 120)
        x2 = x1 + np.random.randint(-35, 35)
        y2 = y1 + np.random.randint(-35, 35)
        cv2.line(img, (x1, y1), (x2, y2), (75, 75, 80), 1, cv2.LINE_AA)
    cv2.imwrite(out_path, img)

def create_demo_inclusion(out_path: str):
    img = generate_base_steel_texture()
    h, w = img.shape[:2]
    # Dark slag particle with surrounding stress halo
    cx, cy = int(w * 0.52), int(h * 0.48)
    cv2.circle(img, (cx, cy), 32, (130, 130, 135), -1) # Diffuse halo
    cv2.circle(img, (cx, cy), 18, (45, 45, 50), -1)    # Dense particle
    cv2.circle(img, (cx + 12, cy - 8), 8, (35, 35, 40), -1) # Second bead
    cv2.imwrite(out_path, img)

def create_demo_patches(out_path: str):
    img = generate_base_steel_texture()
    h, w = img.shape[:2]
    # Irregular dark oxidation patch
    patch_pts = np.array([
        [int(w * 0.20), int(h * 0.25)],
        [int(w * 0.48), int(h * 0.22)],
        [int(w * 0.52), int(h * 0.45)],
        [int(w * 0.38), int(h * 0.52)],
        [int(w * 0.18), int(h * 0.40)]
    ], np.int32)
    cv2.fillPoly(img, [patch_pts], (90, 90, 95))
    cv2.imwrite(out_path, img)

def create_demo_pitted_surface(out_path: str):
    img = generate_base_steel_texture()
    h, w = img.shape[:2]
    np.random.seed(101)
    # Dense scatter of small pitting craters
    for _ in range(80):
        px = np.random.randint(int(w * 0.32), int(w * 0.78))
        py = np.random.randint(int(h * 0.42), int(h * 0.82))
        rad = np.random.randint(2, 6)
        cv2.circle(img, (px, py), rad, (60, 60, 65), -1)
        cv2.circle(img, (px + 1, py + 1), max(1, rad - 1), (220, 220, 225), 1) # Crater rim highlight
    cv2.imwrite(out_path, img)

def create_demo_rolled_in_scale(out_path: str):
    img = generate_base_steel_texture()
    h, w = img.shape[:2]
    # Elongated scale band pressed into surface
    scale_pts = np.array([
        [int(w * 0.28), int(h * 0.20)],
        [int(w * 0.68), int(h * 0.22)],
        [int(w * 0.65), int(h * 0.38)],
        [int(w * 0.32), int(h * 0.35)]
    ], np.int32)
    cv2.fillPoly(img, [scale_pts], (75, 80, 85))
    # Texture inside scale
    for _ in range(25):
        sx = np.random.randint(int(w * 0.30), int(w * 0.65))
        sy = np.random.randint(int(h * 0.22), int(h * 0.35))
        cv2.circle(img, (sx, sy), 2, (50, 50, 55), -1)
    cv2.imwrite(out_path, img)

def generate_all_demo_images(target_dir: str):
    path = Path(target_dir)
    path.mkdir(parents=True, exist_ok=True)

    samples = {
        "demo_sample_clean_steel.jpg": create_demo_clean_steel,
        "demo_sample_scratches.jpg": create_demo_scratches,
        "demo_sample_crazing.jpg": create_demo_crazing,
        "demo_sample_inclusion.jpg": create_demo_inclusion,
        "demo_sample_patches.jpg": create_demo_patches,
        "demo_sample_pitted_surface.jpg": create_demo_pitted_surface,
        "demo_sample_rolled_in_scale.jpg": create_demo_rolled_in_scale,
    }

    created = []
    for filename, fn in samples.items():
        file_path = str(path / filename)
        fn(file_path)
        created.append(file_path)
    return created

if __name__ == "__main__":
    from app.core.config import settings
    dest = settings.DATASETS_DIR / "demo"
    print(f"Generating realistic demo industrial defect images in {dest}...")
    files = generate_all_demo_images(str(dest))
    print(f"Successfully generated {len(files)} demo images.")
