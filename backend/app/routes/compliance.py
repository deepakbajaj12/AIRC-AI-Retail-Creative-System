from fastapi import APIRouter
from ..models.schemas import ComplianceRequest, ComplianceResponse
from ..services.compliance_engine import check_compliance

router = APIRouter(prefix="/compliance", tags=["compliance"])

@router.post("/check", response_model=ComplianceResponse)
def compliance_check(payload: ComplianceRequest):
    issues = check_compliance(payload.canvas)
    return ComplianceResponse(passed=len(issues) == 0, issues=issues)
