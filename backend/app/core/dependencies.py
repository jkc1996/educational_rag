from functools import lru_cache

from app.core.config import Settings, get_settings
from app.infrastructure.document_loader import DocumentLoader
from app.infrastructure.openai_factory import OpenAIModelFactory
from app.infrastructure.repositories import (
    DocumentRepository,
    FeedbackRepository,
    SummaryRepository,
)
from app.infrastructure.usage import OpenAIUsageTracker
from app.infrastructure.vector_store import ChromaVectorRepository
from app.prompts.registry import PromptRegistry
from app.services.document_service import DocumentService
from app.services.evaluation_service import RagasEvaluationService
from app.services.feedback_service import FeedbackService
from app.services.ingestion_service import IngestionService
from app.services.log_service import LogService
from app.services.question_paper_service import QuestionPaperService
from app.services.rag_service import RagService
from app.services.summarization_service import SummarizationService
from app.services.usage_service import UsageService


@lru_cache
def get_prompt_registry() -> PromptRegistry:
    return PromptRegistry()


@lru_cache
def get_usage_tracker() -> OpenAIUsageTracker:
    return OpenAIUsageTracker(get_settings())


@lru_cache
def get_model_factory() -> OpenAIModelFactory:
    return OpenAIModelFactory(get_settings(), get_usage_tracker())


@lru_cache
def get_document_repository() -> DocumentRepository:
    return DocumentRepository(get_settings())


@lru_cache
def get_summary_repository() -> SummaryRepository:
    return SummaryRepository(get_settings())


@lru_cache
def get_feedback_repository() -> FeedbackRepository:
    return FeedbackRepository(get_settings())


@lru_cache
def get_vector_repository() -> ChromaVectorRepository:
    return ChromaVectorRepository(get_settings(), get_model_factory())


@lru_cache
def get_document_loader() -> DocumentLoader:
    return DocumentLoader()


@lru_cache
def get_document_service() -> DocumentService:
    return DocumentService(get_settings(), get_document_repository())


@lru_cache
def get_summarization_service() -> SummarizationService:
    return SummarizationService(
        settings=get_settings(),
        model_factory=get_model_factory(),
        prompt_registry=get_prompt_registry(),
        summary_repository=get_summary_repository(),
    )


@lru_cache
def get_ingestion_service() -> IngestionService:
    return IngestionService(
        settings=get_settings(),
        documents=get_document_repository(),
        loader=get_document_loader(),
        vector_repository=get_vector_repository(),
        summarizer=get_summarization_service(),
    )


@lru_cache
def get_rag_service() -> RagService:
    return RagService(
        settings=get_settings(),
        documents=get_document_repository(),
        vector_repository=get_vector_repository(),
        model_factory=get_model_factory(),
        prompt_registry=get_prompt_registry(),
    )


@lru_cache
def get_question_paper_service() -> QuestionPaperService:
    return QuestionPaperService(
        settings=get_settings(),
        documents=get_document_repository(),
        summaries=get_summary_repository(),
        model_factory=get_model_factory(),
        prompt_registry=get_prompt_registry(),
    )


@lru_cache
def get_evaluation_service() -> RagasEvaluationService:
    return RagasEvaluationService(
        settings=get_settings(),
        rag_service=get_rag_service(),
        usage_tracker=get_usage_tracker(),
        model_factory=get_model_factory(),
    )


@lru_cache
def get_feedback_service() -> FeedbackService:
    return FeedbackService(get_feedback_repository())


@lru_cache
def get_log_service() -> LogService:
    return LogService(get_settings())


@lru_cache
def get_usage_service() -> UsageService:
    return UsageService(get_usage_tracker())


def settings_dependency() -> Settings:
    return get_settings()
