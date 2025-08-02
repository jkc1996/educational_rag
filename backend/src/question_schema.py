from pydantic import BaseModel, Field
from typing import List, Optional

class Question(BaseModel):
    type: str = Field(..., description="Question type, e.g. one_liner, true_false, fill_blank, multiple_choice, descriptive.")
    question: str = Field(..., description="The exam question text.")
    options: Optional[List[str]] = Field(None, description="List of options for multiple choice questions (if applicable).")
    answer: str = Field(..., description="The answer to the question.")

class QuestionPaper(BaseModel):
    questions: List[Question]
