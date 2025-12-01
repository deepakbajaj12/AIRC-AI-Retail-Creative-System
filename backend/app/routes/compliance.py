from fastapi import APIRouter
from ..models.schemas import ComplianceRequest, ComplianceResponse, Canvas
from ..services.compliance_engine import check_compliance
from ..services.autofix import apply_autofixes

router = APIRouter(prefix="/compliance", tags=["compliance"])

@router.post("/check", response_model=ComplianceResponse)
def compliance_check(payload: ComplianceRequest):
    issues = check_compliance(payload.canvas)
    return ComplianceResponse(passed=len(issues) == 0, issues=issues)

@router.post("/autofix", response_model=Canvas)
def compliance_autofix(payload: ComplianceRequest):
    issues = check_compliance(payload.canvas)
    fixed = apply_autofixes(payload.canvas, issues)
    return fixed
