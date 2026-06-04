from app.schemas.question_papers import Question, QuestionPaper


def test_question_paper_schema_validates_questions():
    paper = QuestionPaper(questions=[Question(type="one_liner", question="Define RAG.", answer="Retrieval augmented generation.")])
    assert paper.questions[0].type == "one_liner"

