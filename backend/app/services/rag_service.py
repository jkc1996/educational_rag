from app.core.config import Settings
from app.infrastructure.app_logger import app_event, current_flow, current_flow_id, log_context, new_flow_id, text_preview
from app.infrastructure.openai_factory import OpenAIModelFactory
from app.infrastructure.repositories import DocumentRepository
from app.infrastructure.vector_store import ChromaVectorRepository
from app.prompts.registry import PromptRegistry
from app.schemas.rag import AskRequest, AskResponse, SourceSnippet


class RagService:
    def __init__(
        self,
        *,
        settings: Settings,
        documents: DocumentRepository,
        vector_repository: ChromaVectorRepository,
        model_factory: OpenAIModelFactory,
        prompt_registry: PromptRegistry,
    ) -> None:
        self.settings = settings
        self.documents = documents
        self.vector_repository = vector_repository
        self.model_factory = model_factory
        self.prompt_registry = prompt_registry
        self._qa_cache: dict[str, dict] = {}

    def ask(self, request: AskRequest) -> AskResponse:
        model_id = self.settings.validate_model_id(request.model_id)
        qa_session_id = new_flow_id("qa")
        parent_flow = current_flow()
        parent_flow_id = current_flow_id()
        top_k = request.top_k or self.settings.retrieval_top_k
        with log_context(flow="qa", flow_id=qa_session_id):
            app_event(
                "qa_started",
                message=f"QA started for {request.subject}",
                step="request",
                subject=request.subject,
                model_id=model_id,
                top_k=top_k,
                include_context=request.include_context,
                question=request.question,
                question_preview=text_preview(request.question, limit=500),
                parent_flow=parent_flow,
                parent_flow_id=parent_flow_id,
            )
            retriever = self.vector_repository.retriever(request.subject, top_k=top_k)
            docs = retriever.invoke(request.question)
            sources = self._source_snippets(docs, include_preview=True)
            app_event(
                "qa_retrieval_completed",
                message=f"Retrieved {len(docs)} context chunks for QA",
                step="retrieval",
                subject=request.subject,
                top_k=top_k,
                source_count=len(sources),
                sources=[self._source_log_payload(source) for source in sources],
            )
            context = self._format_context(docs)
            prompt = self.prompt_registry.render("rag_answer_prompt", question=request.question, context=context)
            answer = self.model_factory.invoke_text(model_id=model_id, prompt=prompt, feature="rag_answer")
            app_event(
                "qa_answer_completed",
                message="QA answer generated",
                step="answer",
                subject=request.subject,
                model_id=model_id,
                question=request.question,
                answer_preview=text_preview(answer, limit=1800),
                answer_chars=len(answer),
                source_count=len(sources),
            )
            response_sources = self._trim_sources(sources, include_preview=request.include_context)
        self._qa_cache[qa_session_id] = {
            "query": request.question,
            "answer_excerpt": answer[:600],
            "retrieval_snapshot": [source.model_dump() for source in response_sources],
        }
        return AskResponse(answer=answer, model_id=model_id, qa_session_id=qa_session_id, sources=response_sources)

    def cached_session(self, qa_session_id: str) -> dict:
        return self._qa_cache.get(qa_session_id, {})

    def _format_context(self, docs: list) -> str:
        blocks = []
        for index, doc in enumerate(docs, start=1):
            metadata = getattr(doc, "metadata", {}) or {}
            source = metadata.get("source_file") or metadata.get("source") or "unknown"
            page = metadata.get("page")
            label = f"[{index}] {source}" + (f", page {page}" if page else "")
            blocks.append(f"{label}\n{doc.page_content}")
        return "\n\n".join(blocks)

    def _source_snippets(self, docs: list, *, include_preview: bool) -> list[SourceSnippet]:
        snippets: list[SourceSnippet] = []
        for index, doc in enumerate(docs, start=1):
            metadata = getattr(doc, "metadata", {}) or {}
            content = getattr(doc, "page_content", "") or ""
            snippets.append(
                SourceSnippet(
                    chunk_uid=metadata.get("chunk_uid"),
                    source_file=metadata.get("source_file") or metadata.get("source"),
                    page=metadata.get("page"),
                    rank=index,
                    preview=(content[:500] if include_preview else ""),
                )
            )
        return snippets

    def _trim_sources(self, sources: list[SourceSnippet], *, include_preview: bool) -> list[SourceSnippet]:
        if include_preview:
            return sources
        return [source.model_copy(update={"preview": ""}) for source in sources]

    def _source_log_payload(self, source: SourceSnippet) -> dict:
        return {
            "rank": source.rank,
            "source_file": source.source_file,
            "page": source.page,
            "chunk_uid": source.chunk_uid,
            "preview": text_preview(source.preview, limit=280),
        }
