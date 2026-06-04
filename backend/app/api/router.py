from fastapi import APIRouter

from app.api.routes import documents, evaluations, feedback, logs, models, question_papers, rag, usage

api_router = APIRouter()
api_router.include_router(models.router, tags=["models"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(rag.router, tags=["rag"])
api_router.include_router(question_papers.router, tags=["question-papers"])
api_router.include_router(evaluations.router, tags=["evaluations"])
api_router.include_router(feedback.router, tags=["feedback"])
api_router.include_router(logs.router, tags=["logs"])
api_router.include_router(usage.router, tags=["usage"])

