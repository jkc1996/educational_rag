from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    timestamp: str
    level: str = "INFO"
    category: str = "system"
    flow: str | None = None
    flow_id: str | None = None
    step: str | None = None
    event: str
    message: str
    details: dict = Field(default_factory=dict)
    details_preview: str = ""
    logger: str | None = None
    fingerprint: str
    is_noise: bool = False


class LogSummary(BaseModel):
    total: int
    errors: int
    warnings: int
    qa_events: int
    llm_events: int
    openai_events: int
    ingestion_events: int
    noisy_events: int


class LogsResponse(BaseModel):
    items: list[LogEntry]
    summary: LogSummary
    levels: list[str]
    categories: list[str]
