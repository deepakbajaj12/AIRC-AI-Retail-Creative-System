from fastapi import APIRouter
from ..models.schemas import ExportRequest, ExportResponse, LayoutSuggestRequest, LayoutSuggestResponse, Format
from ..services.exporter import render_canvas
from ..services.layout_engine import suggest_layouts
from ..services.compliance_engine import check_compliance
from ..services.autofix import apply_autofixes
from ..config import FORMATS

router = APIRouter(prefix="/export", tags=["export"])

@router.post("/image", response_model=ExportResponse)
def export_image(payload: ExportRequest):
    out_path = render_canvas(payload.canvas, payload.output_format)
    url = f"/static/exports/{out_path.name}"
    return ExportResponse(file_path=str(out_path), url=url)

@router.post("/batch")
def export_batch(payload: LayoutSuggestRequest):
    results = {}
    for fmt in FORMATS.keys():
        candidates = suggest_layouts(fmt, payload.headline, payload.subhead, payload.value_text, payload.logo, payload.packshots)
        if not candidates:
            continue
        c = candidates[0]
        issues = check_compliance(c)
        if issues:
            c = apply_autofixes(c, issues)
        out_path = render_canvas(c, "PNG")
        results[fmt] = {"url": f"/static/exports/{out_path.name}", "file_path": str(out_path)}
    return results
