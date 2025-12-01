from fastapi import APIRouter
from ..models.schemas import LayoutSuggestRequest, LayoutSuggestResponse
from ..services.layout_engine import suggest_layouts

router = APIRouter(prefix="/layout", tags=["layout"])

@router.post("/suggest", response_model=LayoutSuggestResponse)
def layout_suggest(payload: LayoutSuggestRequest):
    candidates = suggest_layouts(
        payload.format,
        payload.headline,
        payload.subhead,
        payload.value_text,
        payload.logo,
        payload.packshots,
    )
    return LayoutSuggestResponse(candidates=candidates)
