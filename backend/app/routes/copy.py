from fastapi import APIRouter
from pydantic import BaseModel
from ..services.llm_service import generate_ad_copy

router = APIRouter(prefix="/copy", tags=["copy"])

class CopyRequest(BaseModel):
    product_name: str
    topic: str = "general"

@router.post("/generate")
def generate_copy_endpoint(req: CopyRequest):
    return generate_ad_copy(req.product_name, req.topic)
