from __future__ import annotations

from pathlib import Path
from typing import List
from fastapi import APIRouter
from ..models.schemas import Canvas
from ..config import DATA_DIR
import json

PROJECTS_DIR = DATA_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("")
def list_projects():
    items = []
    for p in PROJECTS_DIR.glob("*.json"):
        items.append({"id": p.stem, "file": str(p)})
    return {"projects": items}

@router.get("/{project_id}")
def get_project(project_id: str):
    path = PROJECTS_DIR / f"{project_id}.json"
    if not path.exists():
        return {"error": "not_found"}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@router.post("/{project_id}")
def save_project(project_id: str, canvas: Canvas):
    path = PROJECTS_DIR / f"{project_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(canvas.model_dump(), f, ensure_ascii=False, indent=2)
    return {"id": project_id, "file": str(path)}
