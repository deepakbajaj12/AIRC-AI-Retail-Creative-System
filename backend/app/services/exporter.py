from __future__ import annotations

from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
from ..models.schemas import Canvas, TextElement, ImageElement
from ..config import EXPORTS_DIR


def _rgb_tuple(rgba) -> Tuple[int, int, int]:
    return (rgba.r, rgba.g, rgba.b)


def _load_font(name: str, size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def render_canvas(canvas: Canvas, output_format: str = "PNG") -> Path:
    img = Image.new("RGBA", (canvas.width, canvas.height), (*_rgb_tuple(canvas.background_color), int(canvas.background_color.a * 255)))
    draw = ImageDraw.Draw(img)

    for el in sorted(canvas.elements, key=lambda e: e.z):
        if isinstance(el, ImageElement):
            try:
                src_path = Path(el.src)
                if not src_path.exists():
                    continue
                pic = Image.open(src_path).convert("RGBA")
                pic = pic.resize((el.bounds.width, el.bounds.height), Image.LANCZOS)
                img.alpha_composite(pic, (el.bounds.x, el.bounds.y))
            except Exception:
                continue
        elif isinstance(el, TextElement):
            font = _load_font(el.font_family, el.font_size)
            tx = el.bounds.x
            ty = el.bounds.y
            tw = el.bounds.width
            th = el.bounds.height
            if el.background is not None:
                draw.rectangle([tx, ty, tx + tw, ty + th], fill=_rgb_tuple(el.background))
            # simple vertical centering baseline
            w, h = draw.textlength(el.text, font=font), el.font_size
            x = tx + (tw - w) / 2 if el.align == "center" else (tx if el.align == "left" else tx + tw - w)
            y = ty + (th - h) / 2
            draw.text((x, y), el.text, font=font, fill=_rgb_tuple(el.color))

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EXPORTS_DIR / f"export_{canvas.format}.{output_format.lower()}"
    if output_format.upper() == "JPG":
        rgb = img.convert("RGB")
        rgb.save(out_path, format="JPEG", quality=85, optimize=True)
    else:
        img.save(out_path, format="PNG", optimize=True)
    return out_path
