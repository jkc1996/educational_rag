import json

from app.core.config import Settings
from app.infrastructure.app_logger import app_event, log_context, new_flow_id, text_preview
from app.infrastructure.openai_factory import OpenAIModelFactory
from app.infrastructure.repositories import DocumentRepository, SummaryRepository
from app.prompts.registry import PromptRegistry
from app.schemas.question_papers import QuestionPaper, QuestionPaperRequest, QuestionPaperResponse
from app.schemas.summaries import DocumentSummary, QuestionBlueprint


class QuestionPaperService:
    def __init__(
        self,
        *,
        settings: Settings,
        documents: DocumentRepository,
        summaries: SummaryRepository,
        model_factory: OpenAIModelFactory,
        prompt_registry: PromptRegistry,
    ) -> None:
        self.settings = settings
        self.documents = documents
        self.summaries = summaries
        self.model_factory = model_factory
        self.prompt_registry = prompt_registry

    def generate(self, request: QuestionPaperRequest) -> QuestionPaperResponse:
        if request.total_questions > self.settings.max_questions_per_paper:
            raise ValueError(f"Question limit exceeded. Max allowed: {self.settings.max_questions_per_paper}")
        model_id = self.settings.validate_model_id(request.model_id)
        flow_id = new_flow_id("paper")
        with log_context(flow="question_paper", flow_id=flow_id):
            app_event(
                "question_paper_started",
                message=f"Question paper generation started for {request.subject}",
                step="request",
                subject=request.subject,
                model_id=model_id,
                summary_model_id=self.settings.openai_summary_model,
                document_ids=request.document_ids,
                total_questions=request.total_questions,
                difficulty=request.difficulty,
                distribution=request.distribution,
                extra_context_preview=text_preview(request.extra_context, limit=500),
            )
            summaries = []
            documents = []
            for document_id in request.document_ids:
                record = self.documents.get(document_id)
                if not record.summary_cache_key:
                    raise ValueError(f"Document has no cached summary yet: {record.filename}")
                documents.append(
                    {
                        "document_id": record.id,
                        "filename": record.filename,
                        "subject": record.subject,
                        "summary_cache_key": record.summary_cache_key,
                    }
                )
                summaries.append(self.summaries.load(record.summary_cache_key))
            app_event(
                "question_paper_summaries_loaded",
                message=f"Loaded {len(summaries)} cached summaries for question paper",
                step="summaries",
                subject=request.subject,
                documents=documents,
            )

            summary_payload = self._render_blueprint_summary_payload(summaries)
            blueprint_prompt = self.prompt_registry.render(
                "question_blueprint_prompt",
                subject=request.subject,
                difficulty=request.difficulty,
                distribution=json.dumps(request.distribution, ensure_ascii=False),
                extra_context=request.extra_context,
                summaries=summary_payload,
            )
            blueprint = self.model_factory.invoke_structured(
                model_id=self.settings.openai_summary_model,
                prompt=blueprint_prompt,
                schema=QuestionBlueprint,
                feature="question_blueprint",
            )
            app_event(
                "question_blueprint_completed",
                message="Question paper blueprint generated",
                step="blueprint",
                subject=request.subject,
                focus_areas=blueprint.focus_areas,
                learning_objectives=blueprint.learning_objectives,
                distribution_guidance=blueprint.distribution_guidance,
                source_coverage=blueprint.source_coverage,
            )

            paper_prompt = self.prompt_registry.render(
                "question_paper_generation_prompt",
                subject=request.subject,
                total_questions=request.total_questions,
                difficulty=request.difficulty,
                distribution=json.dumps(request.distribution, ensure_ascii=False),
                blueprint=blueprint.model_dump_json(),
            )
            paper = self.model_factory.invoke_structured(
                model_id=model_id,
                prompt=paper_prompt,
                schema=QuestionPaper,
                feature="question_paper",
            )
            app_event(
                "question_paper_completed",
                message=f"Generated {len(paper.questions)} questions",
                step="complete",
                subject=request.subject,
                model_id=model_id,
                total_questions=len(paper.questions),
                question_type_counts=self._question_type_counts(paper),
                sample_questions=[
                    {
                        "type": question.type,
                        "question": text_preview(question.question, limit=220),
                        "answer": text_preview(question.answer, limit=220),
                    }
                    for question in paper.questions[:5]
                ],
            )
            return QuestionPaperResponse(model_id=model_id, blueprint=blueprint.model_dump(), question_paper=paper)

    def _render_blueprint_summary_payload(self, summaries: list[DocumentSummary]) -> str:
        payloads = []
        for summary in summaries:
            payloads.append(
                {
                    "document_id": summary.document_id,
                    "filename": summary.filename,
                    "subject": summary.subject,
                    "chunk_count": summary.chunk_count,
                    "executive_summary": summary.executive_summary,
                    "concepts": summary.concepts,
                    "definitions": summary.definitions,
                    "formulas": summary.formulas,
                    "examples": summary.examples,
                    "learning_objectives": summary.learning_objectives,
                    "likely_exam_topics": summary.likely_exam_topics,
                    "source_coverage": summary.source_coverage,
                }
            )
        return "\n\n".join(json.dumps(payload, ensure_ascii=False) for payload in payloads)

    def _question_type_counts(self, paper: QuestionPaper) -> dict[str, int]:
        counts: dict[str, int] = {}
        for question in paper.questions:
            counts[question.type] = counts.get(question.type, 0) + 1
        return counts
