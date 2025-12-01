from __future__ import annotations

from typing import List
from ..models.schemas import Canvas, ComplianceIssue, TextElement


def apply_autofixes(canvas: Canvas, issues: List[ComplianceIssue]) -> Canvas:
    updated = canvas.model_copy(deep=True)
    for issue in issues:
        fx = issue.autofix or {}
        action = fx.get("action")
        if action == "nudge_inside":
            el = next((e for e in updated.elements if e.id == fx.get("id")), None)
            if not el:
                continue
            min_x = fx.get("min_x", el.bounds.x)
            min_y = fx.get("min_y", el.bounds.y)
            max_x = fx.get("max_x", el.bounds.x)
            max_y = fx.get("max_y", el.bounds.y)
            el.bounds.x = int(max(min_x, min(el.bounds.x, max_x)))
            el.bounds.y = int(max(min_y, min(el.bounds.y, max_y)))
        elif action == "set_font_size":
            el = next((e for e in updated.elements if e.id == fx.get("id")), None)
            if not el or not isinstance(el, TextElement):
                continue
            size = fx.get("size")
            if size:
                el.font_size = int(size)
        elif action == "move_to":
            el = next((e for e in updated.elements if e.id == fx.get("id")), None)
            if not el:
                continue
            if "x" in fx:
                el.bounds.x = int(fx["x"])
            if "y" in fx:
                el.bounds.y = int(fx["y"])
        elif action == "limit_packshots":
            keep = int(fx.get("keep", 3))
            kept = 0
            new_elements = []
            for e in updated.elements:
                if getattr(e, "type", None) == "packshot":
                    if kept < keep:
                        new_elements.append(e)
                        kept += 1
                else:
                    new_elements.append(e)
            updated.elements = new_elements
        elif action == "increase_contrast":
            el = next((e for e in updated.elements if e.id == fx.get("id")), None)
            if not el or not isinstance(el, TextElement):
                continue
            el.background = type(el).model_fields['background'].annotation(r=0, g=0, b=0, a=1) if hasattr(type(el), 'model_fields') else None
            # If RGBA class available, set explicit values
            try:
                from ..models.schemas import RGBA
                el.background = RGBA(r=0, g=0, b=0, a=1)
                el.color = RGBA(r=255, g=255, b=255, a=1)
            except Exception:
                pass
        else:
            continue
    return updated
