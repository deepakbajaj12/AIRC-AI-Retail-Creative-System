from __future__ import annotations

from typing import List
from ..models.schemas import Canvas, TextElement, ImageElement, BaseElement, Rect, RGBA, Format
from ..config import FORMATS, SAFE_ZONES


def suggest_layouts(
    format: Format,
    headline: str | None,
    subhead: str | None,
    value_text: str | None,
    logo: str | None,
    packshots: list[str],
) -> List[Canvas]:
    w, h = FORMATS[format]
    t, r, b, l = SAFE_ZONES[format]

    elements: List[BaseElement] = []
    z = 1

    if logo:
        elements.append(
            ImageElement(
                id="logo",
                type="logo",
                src=logo,
                bounds=Rect(x=l, y=t, width=200, height=120),
                z=z,
            )
        )
        z += 1

    if headline:
        elements.append(
            TextElement(
                id="headline",
                type="text",
                text=headline,
                font_family="Arial",
                font_size=64,
                font_weight="bold",
                color=RGBA(r=0, g=0, b=0, a=1),
                align="center",
                bounds=Rect(x= int(w*0.1), y=int(h*0.2), width=int(w*0.8), height=150),
                z=z,
            )
        )
        z += 1

    if subhead:
        elements.append(
            TextElement(
                id="subhead",
                type="text",
                text=subhead,
                font_family="Arial",
                font_size=32,
                font_weight="normal",
                color=RGBA(r=0, g=0, b=0, a=1),
                align="center",
                bounds=Rect(x=int(w*0.15), y=int(h*0.32), width=int(w*0.7), height=120),
                z=z,
            )
        )
        z += 1

    # Value tile bottom-left
    if value_text:
        elements.append(
            TextElement(
                id="value",
                type="value_tile",
                text=value_text,
                font_family="Arial",
                font_size=48,
                font_weight="bold",
                color=RGBA(r=255, g=255, b=255, a=1),
                background=RGBA(r=0, g=0, b=0, a=1),
                align="center",
                bounds=Rect(x=l, y=h - b - 140, width=320, height=120),
                z=z,
            )
        )
        z += 1

    # Packshots arranged along bottom-right
    max_ps = min(3, len(packshots))
    if max_ps:
        tile_w = 220
        gap = 20
        total_w = max_ps * tile_w + (max_ps - 1) * gap
        start_x = w - r - total_w
        y = h - b - 260
        for i, src in enumerate(packshots[:max_ps]):
            elements.append(
                ImageElement(
                    id=f"packshot_{i}",
                    type="packshot",
                    src=src,
                    bounds=Rect(x=start_x + i * (tile_w + gap), y=y, width=tile_w, height=240),
                    z=z,
                )
            )
            z += 1

    canvas = Canvas(
        format=format,
        width=w,
        height=h,
        background_color=RGBA(r=255, g=255, b=255, a=1),
        elements=elements,
    )

    # Return a single candidate for now
    return [canvas]
