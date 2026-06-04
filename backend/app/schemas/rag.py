from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    subject: str
    question: str = Field(min_length=1)
    model_id: str | None = None
    include_context: bool = False
    top_k: int | None = None


class SourceSnippet(BaseModel):
    chunk_uid: str | None = None
    source_file: str | None = None
    page: int | None = None
    rank: int
    preview: str


class AskResponse(BaseModel):
    answer: str
    model_id: str
    qa_session_id: str
    sources: list[SourceSnippet] = Field(default_factory=list)

