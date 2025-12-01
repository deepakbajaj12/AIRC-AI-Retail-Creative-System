from __future__ import annotations

import re
from typing import List, Tuple
from ..models.schemas import Canvas, ComplianceIssue, TextElement, ImageElement, BaseElement
from ..config import SAFE_ZONES, BANNED_COPY_PATTERNS, MIN_FONT_SIZES, DRINKAWARE_TEXT
from ..utils.contrast import passes_wcag_aa
from ..compliance.ocr_check import ocr_text_from_bytes


def _rgb_tuple(rgba) -> Tuple[int, int, int]:
    return (rgba.r, rgba.g, rgba.b)


def _elements_by_type(canvas: Canvas):
    texts: List[TextElement] = []
    images: List[ImageElement] = []
    for el in canvas.elements:
        if isinstance(el, TextElement):
            texts.append(el)
        elif isinstance(el, ImageElement):
            images.append(el)
    return texts, images


def check_compliance(canvas: Canvas) -> List[ComplianceIssue]:
    issues: List[ComplianceIssue] = []
    t, r, b, l = SAFE_ZONES[canvas.format]

    texts, images = _elements_by_type(canvas)

    # 1. Safe zones: ensure no element intersects the margin area
    def in_safe_zone(el) -> bool:
        x, y, w, h = el.bounds.x, el.bounds.y, el.bounds.width, el.bounds.height
        if x < l or y < t or x + w > canvas.width - r or y + h > canvas.height - b:
            return False
        return True

    for el in canvas.elements:
        if not in_safe_zone(el):
            issues.append(
                ComplianceIssue(
                    code="SAFE_ZONE",
                    message=f"Element {el.id} violates safe zone.",
                    severity="error",
                    autofix={
                        "action": "nudge_inside",
                        "id": el.id,
                        "min_x": l,
                        "min_y": t,
                        "max_x": canvas.width - r - el.bounds.width,
                        "max_y": canvas.height - b - el.bounds.height,
                    },
                )
            )

    # 2. Packshot limit <= 3
    packshots = [el for el in images if el.type == "packshot"]
    if len(packshots) > 3:
        issues.append(
            ComplianceIssue(
                code="PACKSHOT_LIMIT",
                message=f"Packshots exceed 3 (found {len(packshots)}).",
                severity="error",
                autofix={"action": "limit_packshots", "keep": 3},
            )
        )

    # 3. Banned copy in any text elements
    pattern = re.compile("|".join(BANNED_COPY_PATTERNS), flags=re.IGNORECASE)
    for te in texts:
        if te.text and pattern.search(te.text):
            issues.append(
                ComplianceIssue(
                    code="BANNED_COPY",
                    message=f"Banned copy detected in {te.id}.",
                    severity="error",
                    autofix={"action": "highlight_text", "id": te.id},
                )
            )

    # 3b. OCR banned copy inside images (packshots/logos)
    for img_el in images:
        try:
            from pathlib import Path
            p = Path(img_el.src)
            if not p.exists():
                continue
            with open(p, 'rb') as f:
                text = ocr_text_from_bytes(f.read())
            if text and pattern.search(text):
                issues.append(
                    ComplianceIssue(
                        code="BANNED_COPY_OCR",
                        message=f"Banned text detected in image {img_el.id} via OCR.",
                        severity="error",
                        autofix={"action": "highlight_image", "id": img_el.id},
                    )
                )
        except Exception:
            continue

    # 4. Contrast checker AA: assume large text if font_size >= 24
    bg_rgb = (255, 255, 255)
    if canvas.background_color:
        bg_rgb = _rgb_tuple(canvas.background_color)
    for te in texts:
        fg = _rgb_tuple(te.color)
        bg = bg_rgb
        if te.background is not None:
            bg = _rgb_tuple(te.background)
        large = te.font_size >= 24
        if not passes_wcag_aa(fg, bg, large):
            issues.append(
                ComplianceIssue(
                    code="CONTRAST",
                    message=f"Contrast fails WCAG AA for {te.id}.",
                    severity="error",
                    autofix={"action": "increase_contrast", "id": te.id},
                )
            )

    # 5. Drinkaware rule: if drinkaware text present, enforce min font size and bottom placement
    drinkaware_elems = [te for te in texts if DRINKAWARE_TEXT.lower() in (te.text or "").lower()]
    for te in drinkaware_elems:
        if te.font_size < MIN_FONT_SIZES["drinkaware"]:
            issues.append(
                ComplianceIssue(
                    code="DRINKAWARE_SIZE",
                    message="Drinkaware font size too small.",
                    severity="error",
                    autofix={"action": "set_font_size", "id": te.id, "size": MIN_FONT_SIZES["drinkaware"]},
                )
            )
        # bottom placement: within last 15% of canvas height
        if te.bounds.y < int(canvas.height * 0.85):
            issues.append(
                ComplianceIssue(
                    code="DRINKAWARE_POSITION",
                    message="Drinkaware must be at the bottom area.",
                    severity="error",
                    autofix={
                        "action": "move_to",
                        "id": te.id,
                        "x": te.bounds.x,
                        "y": int(canvas.height * 0.88),
                    },
                )
            )

    # 6. Minimal font sizes for text types if IDs are standard
    id_to_min = {"headline": MIN_FONT_SIZES["headline"], "subhead": MIN_FONT_SIZES["subhead"], "value": MIN_FONT_SIZES["value"]}
    for te in texts:
        if te.id in id_to_min and te.font_size < id_to_min[te.id]:
            issues.append(
                ComplianceIssue(
                    code="MIN_FONT_SIZE",
                    message=f"{te.id} font size below minimum.",
                    severity="error",
                    autofix={"action": "set_font_size", "id": te.id, "size": id_to_min[te.id]},
                )
            )

    return issues
