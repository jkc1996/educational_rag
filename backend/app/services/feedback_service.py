from app.infrastructure.app_logger import app_event, log_context, new_flow_id, text_preview
from app.infrastructure.repositories import FeedbackRepository
from app.schemas.feedback import FeedbackRequest, FeedbackResponse


class FeedbackService:
    def __init__(self, feedback_repository: FeedbackRepository) -> None:
        self.feedback_repository = feedback_repository

    def submit(self, request: FeedbackRequest, session_snapshot: dict | None = None) -> FeedbackResponse:
        flow_id = new_flow_id("feedback")
        with log_context(flow="feedback", flow_id=flow_id):
            payload = request.model_dump()
            payload.update(session_snapshot or {})
            self.feedback_repository.append(payload)
            app_event(
                "feedback_submitted",
                message="Feedback submitted for QA answer",
                step="feedback",
                qa_session_id=request.qa_session_id,
                helpful=request.helpful,
                model_id=request.model_id,
                comment_preview=text_preview(request.comment, limit=500),
                question_preview=text_preview((session_snapshot or {}).get("query"), limit=500),
                answer_preview=text_preview((session_snapshot or {}).get("answer_excerpt"), limit=700),
            )
            return FeedbackResponse(ok=True)
