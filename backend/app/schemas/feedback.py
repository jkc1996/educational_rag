from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    qa_session_id: str
    helpful: bool
    comment: str | None = None
    model_id: str | None = None


class FeedbackResponse(BaseModel):
    ok: bool

