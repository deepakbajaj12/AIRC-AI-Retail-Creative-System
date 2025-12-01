from pathlib import Path
from typing import Optional
from PIL import Image
import numpy as np


def remove_simple_bg(input_path: Path, output_path: Path, threshold: int = 240) -> Path:
    """
    Naive background removal for near-solid (white) backgrounds.
    Creates transparency where pixels are near white.
    """
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)
    r, g, b, a = data.T
    near_white = (r > threshold) & (g > threshold) & (b > threshold)
    data[..., 3][near_white.T] = 0
    out = Image.fromarray(data)
    out.save(output_path)
    return output_path


def resize_fit(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    img = img.copy()
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return img
