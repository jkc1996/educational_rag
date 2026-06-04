from fastapi import APIRouter, Depends

from app.core.dependencies import get_rag_service
from app.schemas.rag import AskRequest, AskResponse
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/rag/ask", response_model=AskResponse)
def ask_question(request: AskRequest, service: RagService = Depends(get_rag_service)) -> AskResponse:
    return service.ask(request)

