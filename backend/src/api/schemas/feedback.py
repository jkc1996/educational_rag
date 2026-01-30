from pydantic import BaseModel

class FeedbackIn(BaseModel):
    qa_session_id: str
    helpful: bool
    comment: str | None = None
    llm_backend: str | None = None