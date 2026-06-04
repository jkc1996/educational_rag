from fastapi import APIRouter, Depends

from app.core.dependencies import get_feedback_service, get_rag_service
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import FeedbackService
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    request: FeedbackRequest,
    feedback: FeedbackService = Depends(get_feedback_service),
    rag: RagService = Depends(get_rag_service),
) -> FeedbackResponse:
    return feedback.submit(request, rag.cached_session(request.qa_session_id))

