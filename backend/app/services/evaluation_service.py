import json

from app.core.config import Settings
from app.infrastructure.app_logger import app_event, log_context, new_flow_id, text_preview
from app.infrastructure.openai_factory import OpenAIModelFactory
from app.infrastructure.usage import OpenAIUsageTracker
from app.schemas.evaluations import EvaluationSetInfo, EvaluationSetsResponse, RagasEvaluationRequest, RagasEvaluationResponse
from app.schemas.rag import AskRequest
from app.services.rag_service import RagService


class RagasEvaluationService:
    _DEFAULT_EVAL_ROWS: list[dict] = [
        {
            "id": 1,
            "subject": "Machine Learning",
            "question": "What is machine learning?",
            "reference": "Machine learning is a subfield of artificial intelligence where algorithms learn patterns from data and improve task performance without being explicitly programmed for every individual case.",
        },
        {
            "id": 2,
            "subject": "Machine Learning",
            "question": "What is the difference between supervised and unsupervised learning?",
            "reference": "Supervised learning trains on labeled examples with known outputs, while unsupervised learning discovers patterns or structure in unlabeled data.",
        },
        {
            "id": 3,
            "subject": "Machine Learning",
            "question": "What is overfitting in machine learning?",
            "reference": "Overfitting occurs when a model learns training data too closely, including noise or accidental patterns, so it performs poorly on unseen data.",
        },
        {
            "id": 4,
            "subject": "Machine Learning",
            "question": "What is a support vector machine?",
            "reference": "A support vector machine is a supervised learning model that classifies data by finding a decision boundary with a maximum margin between classes.",
        },
        {
            "id": 5,
            "subject": "Machine Learning",
            "question": "What is the kernel trick in SVMs?",
            "reference": "The kernel trick lets SVMs work with nonlinear patterns by computing similarity through a kernel function instead of explicitly mapping data into a higher-dimensional feature space.",
        },
    ]

    def __init__(
        self,
        *,
        settings: Settings,
        rag_service: RagService,
        usage_tracker: OpenAIUsageTracker,
        model_factory: OpenAIModelFactory,
    ) -> None:
        self.settings = settings
        self.rag_service = rag_service
        self.usage_tracker = usage_tracker
        self.model_factory = model_factory

    def list_eval_sets(self) -> EvaluationSetsResponse:
        self._ensure_default_eval_set()
        items = []
        for path in sorted(self.settings.eval_sets_dir.glob("*.json")):
            try:
                rows = self._read_eval_rows(path)
            except Exception:
                continue
            items.append(
                EvaluationSetInfo(
                    name=path.stem,
                    row_count=len(rows),
                    sample_questions=[str(row.get("question") or row.get("user_input") or "") for row in rows[:3]],
                )
            )
        return EvaluationSetsResponse(items=items)

    def run(self, request: RagasEvaluationRequest) -> RagasEvaluationResponse:
        flow_id = new_flow_id("eval")
        model_ids = request.model_ids or [self.settings.openai_default_chat_model]
        for model_id in model_ids:
            self.settings.validate_model_id(model_id)

        with log_context(flow="evaluation", flow_id=flow_id):
            app_event(
                "ragas_evaluation_started",
                message=f"RAGAS evaluation started: {request.eval_set}",
                step="request",
                subject=request.subject,
                eval_set=request.eval_set,
                model_ids=model_ids,
                metrics=request.metrics,
                requested_limit=request.limit,
            )
            rows = self._load_eval_rows(request.eval_set, subject=request.subject)
            if request.limit:
                rows = rows[: min(request.limit, self.settings.max_ragas_questions)]
            else:
                rows = rows[: self.settings.max_ragas_questions]
            if not rows:
                raise ValueError(f"Evaluation set '{request.eval_set}' has no rows for subject '{request.subject}'.")
            app_event(
                "ragas_eval_rows_loaded",
                message=f"Loaded {len(rows)} evaluation rows",
                step="load",
                subject=request.subject,
                eval_set=request.eval_set,
                row_count=len(rows),
                sample_questions=[text_preview(row.get("question", ""), limit=220) for row in rows[:5]],
            )

            results: dict[str, list[dict]] = {}
            for model_id in model_ids:
                app_event(
                    "ragas_model_evaluation_started",
                    message=f"Answer generation started for evaluation model {model_id}",
                    step="answer_generation",
                    subject=request.subject,
                    eval_set=request.eval_set,
                    model_id=model_id,
                    row_count=len(rows),
                )
                answered = []
                for index, row in enumerate(rows, start=1):
                    response = self.rag_service.ask(
                        AskRequest(
                            subject=request.subject,
                            question=self._row_question(row),
                            model_id=model_id,
                            include_context=True,
                        )
                    )
                    answered.append(
                        {
                            "id": row.get("id", index),
                            "question": self._row_question(row),
                            "answer": response.answer,
                            "reference": self._row_reference(row),
                            "contexts": [source.preview for source in response.sources if source.preview],
                        }
                    )
                results[model_id] = self._evaluate_rows(answered, request.metrics)
                app_event(
                    "ragas_model_evaluation_completed",
                    message=f"RAGAS metrics completed for {model_id}",
                    step="metrics",
                    subject=request.subject,
                    eval_set=request.eval_set,
                    model_id=model_id,
                    result_count=len(results[model_id]),
                    metrics=request.metrics,
                )
            app_event(
                "ragas_evaluation_completed",
                message=f"RAGAS evaluation completed: {request.eval_set}",
                step="complete",
                subject=request.subject,
                eval_set=request.eval_set,
                model_ids=model_ids,
            )
            return RagasEvaluationResponse(status="success", results=results)

    def _load_eval_rows(self, eval_set: str, *, subject: str | None = None) -> list[dict]:
        if eval_set == "default":
            self._ensure_default_eval_set()
        path = self.settings.eval_sets_dir / f"{eval_set}.json"
        if not path.exists():
            available = ", ".join(item.name for item in self.list_eval_sets().items) or "none"
            raise FileNotFoundError(f"Evaluation set '{eval_set}' was not found. Available eval sets: {available}.")
        rows = self._read_eval_rows(path)
        if not isinstance(rows, list):
            raise ValueError("Evaluation set must be a JSON array.")
        if subject:
            rows = [row for row in rows if not row.get("subject") or str(row.get("subject")).lower() == subject.lower()]
        return rows

    def _evaluate_rows(self, rows: list[dict], metric_names: list[str]) -> list[dict]:
        if not rows:
            return []
        try:
            from datasets import Dataset
            from ragas import evaluate
            from ragas.embeddings import LangchainEmbeddingsWrapper
            from ragas.llms import LangchainLLMWrapper
            from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

            metric_map = {
                "context_precision": context_precision,
                "context_recall": context_recall,
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
            }
            metrics = [metric_map[name] for name in metric_names if name in metric_map]
            if not metrics:
                return rows

            dataset = Dataset.from_list(
                [
                    {
                        "user_input": row["question"],
                        "response": row["answer"],
                        "retrieved_contexts": row.get("contexts", []),
                        "reference": row.get("reference", ""),
                    }
                    for row in rows
                ]
            )
            evaluator_llm = LangchainLLMWrapper(
                self.model_factory.chat_model(self.settings.openai_utility_model, feature="ragas_metrics")
            )
            evaluator_embeddings = LangchainEmbeddingsWrapper(self.model_factory.embeddings())
            result = evaluate(
                dataset,
                metrics=metrics,
                llm=evaluator_llm,
                embeddings=evaluator_embeddings,
                raise_exceptions=False,
                show_progress=False,
            )
            scores = result.to_pandas().to_dict(orient="records")
            return [{**row, **score} for row, score in zip(rows, scores)]
        except Exception as exc:
            return [{**row, "evaluation_error": str(exc)} for row in rows]

    def _ensure_default_eval_set(self) -> None:
        self.settings.ensure_storage()
        path = self.settings.eval_sets_dir / "default.json"
        if path.exists():
            return
        path.write_text(json.dumps(self._DEFAULT_EVAL_ROWS, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_eval_rows(self, path) -> list[dict]:
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"Evaluation set must be a JSON array: {path.name}")
        return rows

    def _row_question(self, row: dict) -> str:
        question = row.get("question") or row.get("user_input")
        if not question:
            raise ValueError("Each evaluation row must include 'question' or 'user_input'.")
        return str(question)

    def _row_reference(self, row: dict) -> str:
        return str(row.get("reference") or row.get("ground_truth") or row.get("answer") or "")
