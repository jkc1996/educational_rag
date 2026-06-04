import hashlib
import json

from langchain_core.documents import Document

from app.core.config import Settings
from app.infrastructure.app_logger import app_event
from app.infrastructure.openai_factory import OpenAIModelFactory
from app.infrastructure.repositories import SummaryRepository
from app.prompts.registry import PromptRegistry
from app.schemas.documents import DocumentRecord
from app.schemas.summaries import ChunkSummary, DocumentSummary


class SummarizationService:
    def __init__(
        self,
        *,
        settings: Settings,
        model_factory: OpenAIModelFactory,
        prompt_registry: PromptRegistry,
        summary_repository: SummaryRepository,
    ) -> None:
        self.settings = settings
        self.model_factory = model_factory
        self.prompt_registry = prompt_registry
        self.summary_repository = summary_repository

    def cache_key_for(self, record: DocumentRecord, model_id: str) -> str:
        payload = {
            "document_id": record.id,
            "sha256": record.sha256,
            "model_id": model_id,
            "prompt_version": self.prompt_registry.version("document_summary_reduce_prompt"),
            "chunk_size": self.settings.chunk_size,
            "chunk_overlap": self.settings.chunk_overlap,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def summarize_document(
        self,
        *,
        record: DocumentRecord,
        chunks: list[Document],
        model_id: str,
        force_refresh: bool = False,
    ) -> DocumentSummary:
        cache_key = self.cache_key_for(record, model_id)
        if not force_refresh and self.summary_repository.exists(cache_key):
            app_event(
                "document_summary_cache_hit",
                message=f"Loaded cached summary for {record.filename}",
                step="summary_cache",
                document_id=record.id,
                subject=record.subject,
                filename=record.filename,
                model_id=model_id,
                summary_cache_key=cache_key,
            )
            return self.summary_repository.load(cache_key)

        app_event(
            "document_summary_started",
            message=f"Document summary generation started: {record.filename}",
            step="summary",
            document_id=record.id,
            subject=record.subject,
            filename=record.filename,
            model_id=model_id,
            available_chunks=len(chunks),
            max_summary_chunks=self.settings.max_summary_chunks_per_document,
            force_refresh=force_refresh,
        )
        chunk_summaries = self._summarize_chunks(record, chunks, model_id)
        if not chunk_summaries:
            raise ValueError("No document content was available for summarization.")
        app_event(
            "chunk_summaries_completed",
            message=f"Generated {len(chunk_summaries)} chunk summaries",
            step="chunk_summary",
            document_id=record.id,
            subject=record.subject,
            filename=record.filename,
            model_id=model_id,
            selected_chunk_count=len(chunk_summaries),
        )
        summary_payload = self._render_compact_chunk_payload(chunk_summaries)
        prompt = self.prompt_registry.render(
            "document_summary_reduce_prompt",
            document_id=record.id,
            subject=record.subject,
            filename=record.filename,
            prompt_version=self.prompt_registry.version("document_summary_reduce_prompt"),
            model_id=model_id,
            chunk_count=len(chunk_summaries),
            chunk_summaries=summary_payload,
        )
        document_summary = self.model_factory.invoke_structured(
            model_id=model_id,
            prompt=prompt,
            schema=DocumentSummary,
            feature="document_summary_reduce",
        )
        document_summary.document_id = record.id
        document_summary.subject = record.subject
        document_summary.filename = record.filename
        document_summary.model_id = model_id
        document_summary.prompt_version = self.prompt_registry.version("document_summary_reduce_prompt")
        document_summary.chunk_count = len(chunk_summaries)
        self.summary_repository.save(cache_key, document_summary)
        app_event(
            "document_summary_completed",
            message=f"Document summary cached for {record.filename}",
            step="summary",
            document_id=record.id,
            subject=record.subject,
            filename=record.filename,
            model_id=model_id,
            summary_cache_key=cache_key,
            chunk_count=len(chunk_summaries),
            concepts=document_summary.concepts[:10],
            likely_exam_topics=document_summary.likely_exam_topics[:10],
            executive_summary_preview=document_summary.executive_summary,
        )
        return document_summary

    def _summarize_chunks(self, record: DocumentRecord, chunks: list[Document], model_id: str) -> list[ChunkSummary]:
        selected = self._select_chunks_for_summary(chunks)
        summaries: list[ChunkSummary] = []
        for chunk in selected:
            prompt = self.prompt_registry.render(
                "chunk_summary_prompt",
                source_file=chunk.metadata.get("source_file", record.filename),
                page=chunk.metadata.get("page", ""),
                content=chunk.page_content,
            )
            summaries.append(
                self.model_factory.invoke_structured(
                    model_id=model_id,
                    prompt=prompt,
                    schema=ChunkSummary,
                    feature="chunk_summary",
                )
            )
        return summaries

    def _select_chunks_for_summary(self, chunks: list[Document]) -> list[Document]:
        limit = max(0, self.settings.max_summary_chunks_per_document)
        if limit == 0 or len(chunks) <= limit:
            return chunks
        if limit == 1:
            return [chunks[0]]

        indexes = {round(index * (len(chunks) - 1) / (limit - 1)) for index in range(limit)}
        selected = [(index, chunk) for index, chunk in enumerate(chunks) if index in indexes]
        if len(selected) < limit:
            selected_indexes = {index for index, _ in selected}
            for index, chunk in enumerate(chunks):
                if index not in selected_indexes:
                    selected.append((index, chunk))
                    selected_indexes.add(index)
                if len(selected) >= limit:
                    break
        return [chunk for _, chunk in sorted(selected[:limit], key=lambda item: item[0])]

    def _render_compact_chunk_payload(self, summaries: list[ChunkSummary]) -> str:
        payloads = []
        for summary in summaries:
            payloads.append(
                {
                    "source": summary.source.model_dump(),
                    "concepts": summary.concepts,
                    "definitions": summary.definitions,
                    "formulas": summary.formulas,
                    "examples": summary.examples,
                    "learning_objectives": summary.learning_objectives,
                    "likely_exam_topics": summary.likely_exam_topics,
                    "summary": summary.summary,
                }
            )
        return "\n".join(json.dumps(payload, ensure_ascii=False) for payload in payloads)
