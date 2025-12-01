from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, Query
from ..config import ASSETS_DIR
from ..utils.image_ops import remove_simple_bg

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/remove_bg")
def remove_bg(url: str = Query(..., description="/static/assets/<name> url")):
    # Expect a url like /static/assets/filename.png
    name = Path(url).name
    src = ASSETS_DIR / name
    if not src.exists():
        return {"error": "not_found"}
    out = ASSETS_DIR / f"bgremoved_{name}"
    try:
        remove_simple_bg(src, out)
    except Exception as e:
        return {"error": "processing_failed", "detail": str(e)}
    return {"url": f"/static/assets/{out.name}", "file_path": str(out)}
