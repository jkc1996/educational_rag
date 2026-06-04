import logging

from app.core.config import Settings
from app.infrastructure.app_logger import app_event, log_context, new_flow_id
from app.infrastructure.document_loader import DocumentLoader
from app.infrastructure.repositories import DocumentRepository
from app.infrastructure.vector_store import ChromaVectorRepository
from app.schemas.documents import DocumentRecord, DocumentStatus
from app.services.summarization_service import SummarizationService


class IngestionService:
    def __init__(
        self,
        *,
        settings: Settings,
        documents: DocumentRepository,
        loader: DocumentLoader,
        vector_repository: ChromaVectorRepository,
        summarizer: SummarizationService,
    ) -> None:
        self.settings = settings
        self.documents = documents
        self.loader = loader
        self.vector_repository = vector_repository
        self.summarizer = summarizer

    def ingest(self, *, document_id: str, model_id: str | None = None, force_summary_refresh: bool = False) -> DocumentRecord:
        flow_id = new_flow_id("ingest")
        record = self.documents.mark_status(document_id, DocumentStatus.processing)
        selected_model = model_id or self.settings.openai_summary_model
        with log_context(flow="ingestion", flow_id=flow_id):
            app_event(
                "document_ingestion_started",
                message=f"Document ingestion started: {record.filename}",
                step="ingest",
                document_id=record.id,
                subject=record.subject,
                filename=record.filename,
                model_id=selected_model,
                force_summary_refresh=force_summary_refresh,
            )
            try:
                pages = self.loader.load(record.stored_file)
                app_event(
                    "document_pages_loaded",
                    message=f"Loaded {len(pages)} pages from {record.filename}",
                    step="load",
                    document_id=record.id,
                    subject=record.subject,
                    filename=record.filename,
                    page_count=len(pages),
                )
                chunks = self.vector_repository.split_documents(pages, document_id=record.id, subject=record.subject)
                app_event(
                    "document_chunks_created",
                    message=f"Created {len(chunks)} chunks for {record.filename}",
                    step="chunk",
                    document_id=record.id,
                    subject=record.subject,
                    filename=record.filename,
                    chunk_count=len(chunks),
                    chunk_size=self.settings.chunk_size,
                    chunk_overlap=self.settings.chunk_overlap,
                )
                self.vector_repository.add_documents(record.subject, chunks)
                app_event(
                    "document_chunks_indexed",
                    message=f"Indexed {len(chunks)} chunks into Chroma",
                    step="index",
                    document_id=record.id,
                    subject=record.subject,
                    filename=record.filename,
                    chunk_count=len(chunks),
                )
                summary = self.summarizer.summarize_document(
                    record=record,
                    chunks=chunks,
                    model_id=selected_model,
                    force_refresh=force_summary_refresh,
                )
                completed = self.documents.mark_status(
                    record.id,
                    DocumentStatus.completed,
                    chunk_count=len(chunks),
                    summary_cache_key=self.summarizer.cache_key_for(record, selected_model),
                )
                app_event(
                    "document_ingestion_completed",
                    message=f"Document ingestion completed: {record.filename}",
                    step="complete",
                    document_id=record.id,
                    subject=record.subject,
                    filename=record.filename,
                    chunk_count=len(chunks),
                    summary_cache_key=completed.summary_cache_key,
                    summary_topics=summary.likely_exam_topics[:8],
                )
                return completed
            except Exception as exc:
                logging.exception({"event": "document_ingestion_failed", "document_id": document_id, "error": str(exc)})
                app_event(
                    "document_ingestion_failed",
                    message=f"Document ingestion failed: {record.filename}",
                    step="error",
                    level=logging.ERROR,
                    document_id=document_id,
                    subject=record.subject,
                    filename=record.filename,
                    error=str(exc),
                )
                return self.documents.mark_status(document_id, DocumentStatus.failed, error=str(exc))
