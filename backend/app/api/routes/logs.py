from fastapi import APIRouter, Depends

from app.core.dependencies import get_log_service
from app.schemas.logs import LogsResponse
from app.services.log_service import LogService

router = APIRouter()


@router.get("/logs", response_model=LogsResponse)
def list_logs(
    limit: int = 500,
    q: str | None = None,
    level: str | None = None,
    category: str | None = None,
    service: LogService = Depends(get_log_service),
) -> LogsResponse:
    return service.list_logs(limit=limit, query=q, level=level, category=category)
