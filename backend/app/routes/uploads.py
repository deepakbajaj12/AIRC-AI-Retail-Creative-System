from typing import List
from fastapi import APIRouter, UploadFile, File
from ..config import ASSETS_DIR
from ..models.schemas import UploadResponse

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/assets", response_model=UploadResponse)
async def upload_assets(files: List[UploadFile] = File(...)):
    saved: List[str] = []
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        target = ASSETS_DIR / f.filename
        # Ensure unique by appending a number if exists
        stem = target.stem
        suffix = target.suffix
        i = 1
        while target.exists():
            target = ASSETS_DIR / f"{stem}_{i}{suffix}"
            i += 1
        with open(target, "wb") as out:
            out.write(await f.read())
        saved.append(f"/static/assets/{target.name}")
    return UploadResponse(files=saved)
