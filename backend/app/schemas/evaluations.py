from pydantic import BaseModel, Field


class RagasEvaluationRequest(BaseModel):
    subject: str
    model_ids: list[str] = Field(default_factory=list)
    eval_set: str = "default"
    metrics: list[str] = Field(default_factory=lambda: ["context_precision", "context_recall", "faithfulness", "answer_relevancy"])
    limit: int | None = None


class RagasEvaluationResponse(BaseModel):
    status: str
    results: dict[str, list[dict]]
    message: str | None = None


class EvaluationSetInfo(BaseModel):
    name: str
    row_count: int
    sample_questions: list[str] = Field(default_factory=list)


class EvaluationSetsResponse(BaseModel):
    items: list[EvaluationSetInfo]
