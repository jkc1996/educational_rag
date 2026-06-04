from datetime import datetime, timezone

from pydantic import BaseModel, Field


class UsageRecord(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    feature: str
    model_id: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    token_source: str = "legacy"
    cost_source: str = "legacy"
    pricing_snapshot: str | None = None
    openai_response_id: str | None = None
    openai_request_id: str | None = None
    is_estimate: bool = False


class UsageSummary(BaseModel):
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cached_tokens: int
    estimated_cost_usd: float
    records: list[UsageRecord]
