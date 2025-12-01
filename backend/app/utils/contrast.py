from __future__ import annotations

from typing import Tuple


def _linearize_channel(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 * 255 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    r, g, b = rgb
    R = _linearize_channel(r)
    G = _linearize_channel(g)
    B = _linearize_channel(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def contrast_ratio(fg: Tuple[int, int, int], bg: Tuple[int, int, int]) -> float:
    L1 = relative_luminance(fg)
    L2 = relative_luminance(bg)
    lighter = max(L1, L2)
    darker = min(L1, L2)
    return (lighter + 0.05) / (darker + 0.05)


def passes_wcag_aa(fg: Tuple[int, int, int], bg: Tuple[int, int, int], large_text: bool) -> bool:
    ratio = contrast_ratio(fg, bg)
    return ratio >= (3.0 if large_text else 4.5)
