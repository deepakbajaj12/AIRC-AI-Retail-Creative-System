from fastapi import APIRouter
from ..models.schemas import ExportRequest, ExportResponse
from ..services.exporter import render_canvas

router = APIRouter(prefix="/export", tags=["export"])

@router.post("/image", response_model=ExportResponse)
def export_image(payload: ExportRequest):
    out_path = render_canvas(payload.canvas, payload.output_format)
    url = f"/static/exports/{out_path.name}"
    return ExportResponse(file_path=str(out_path), url=url)
