from pydantic import BaseModel, Field


class Question(BaseModel):
    type: str = Field(description="one_liner, true_false, fill_blank, multiple_choice, or descriptive")
    question: str
    options: list[str] | None = None
    answer: str
    source_hint: str | None = None


class QuestionPaper(BaseModel):
    questions: list[Question]


class QuestionPaperRequest(BaseModel):
    subject: str
    document_ids: list[str]
    model_id: str | None = None
    total_questions: int = Field(default=10, ge=1)
    difficulty: str = "medium"
    distribution: dict[str, int] = Field(default_factory=dict)
    extra_context: str = ""


class QuestionPaperResponse(BaseModel):
    model_id: str
    blueprint: dict
    question_paper: QuestionPaper

