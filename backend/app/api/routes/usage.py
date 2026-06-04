from fastapi import APIRouter, Depends

from app.core.dependencies import get_usage_service
from app.schemas.usage import UsageSummary
from app.services.usage_service import UsageService

router = APIRouter()


@router.get("/usage", response_model=UsageSummary)
def usage_summary(limit: int = 500, service: UsageService = Depends(get_usage_service)) -> UsageSummary:
    return service.summary(limit)

