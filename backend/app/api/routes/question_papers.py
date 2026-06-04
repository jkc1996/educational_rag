from fastapi import APIRouter, Depends

from app.core.dependencies import get_question_paper_service
from app.schemas.question_papers import QuestionPaperRequest, QuestionPaperResponse
from app.services.question_paper_service import QuestionPaperService

router = APIRouter()


@router.post("/question-papers", response_model=QuestionPaperResponse)
def generate_question_paper(
    request: QuestionPaperRequest,
    service: QuestionPaperService = Depends(get_question_paper_service),
) -> QuestionPaperResponse:
    return service.generate(request)

