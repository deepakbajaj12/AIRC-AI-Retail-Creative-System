from __future__ import annotations

from typing import Dict, Tuple, List


def intersects_safe_zone(bbox: Tuple[int, int, int, int], image_width: int, image_height: int, safe_zone_height: int = 250) -> bool:
    x, y, w, h = bbox
    bbox_bottom = y + h
    safe_zone_top = image_height - safe_zone_height
    return bbox_bottom > safe_zone_top


def check_layout_safezone(element_bboxes: Dict[str, Tuple[int, int, int, int]], image_width: int, image_height: int, safe_zone_height: int = 250) -> List[dict]:
    violations = []
    for name, bbox in element_bboxes.items():
        if intersects_safe_zone(bbox, image_width, image_height, safe_zone_height):
            violations.append({"element": name, "rule": "safe_zone", "msg": "Element overlaps bottom safe zone", "bbox": bbox})
    return violations
