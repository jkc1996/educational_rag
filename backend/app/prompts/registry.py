from dataclasses import dataclass, field
from string import Template


@dataclass(frozen=True)
class PromptSpec:
    key: str
    purpose: str
    version: str
    system: str
    template: str
    expected_schema: str | None = None
    regression_examples: list[str] = field(default_factory=list)

    def render(self, **kwargs: object) -> str:
        return Template(self.template).safe_substitute({k: str(v) for k, v in kwargs.items()})


class PromptRegistry:
    def __init__(self) -> None:
        self._prompts = {
            "rag_answer_prompt": PromptSpec(
                key="rag_answer_prompt",
                purpose="Answer a learner question using only retrieved course context.",
                version="2026-06-educational-rag-v1",
                expected_schema=None,
                system=(
                    "You are an academic RAG assistant. Answer with grounded, concise explanations. "
                    "Use only the provided context. If the context is insufficient, say you do not know."
                ),
                template=(
                    "Question:\n$question\n\n"
                    "Retrieved context:\n$context\n\n"
                    "Response rules:\n"
                    "- Cite source labels inline when useful, for example [1].\n"
                    "- Do not invent facts outside the retrieved context.\n"
                    "- Keep formatting readable for a student.\n"
                    "- Use Markdown headings and lists for structure.\n"
                    "- Use single-dollar inline math. For display formulas, put double-dollar delimiters on their own lines.\n"
                    "- Keep formulas compact and do not escape ordinary text outside math delimiters.\n"
                ),
            ),
            "chunk_summary_prompt": PromptSpec(
                key="chunk_summary_prompt",
                purpose="Extract structured academic summary data from one chunk.",
                version="2026-06-summary-v2-compact",
                expected_schema="ChunkSummary",
                system=(
                    "You summarize academic content for later exam generation. "
                    "Extract only information present in the source text. Be selective and compact."
                ),
                template=(
                    "Source file: $source_file\n"
                    "Page: $page\n\n"
                    "Source text:\n$content\n\n"
                    "Return compact structured fields:\n"
                    "- concepts: max 6 short names\n"
                    "- definitions: max 4 one-sentence definitions\n"
                    "- formulas: max 4 formulas or symbolic rules\n"
                    "- examples: max 3 short examples\n"
                    "- learning_objectives: max 4 objectives\n"
                    "- likely_exam_topics: max 4 exam topics\n"
                    "- summary: max 90 words\n\n"
                    "Do not copy long passages. Prefer exam-useful signal over coverage."
                ),
            ),
            "document_summary_reduce_prompt": PromptSpec(
                key="document_summary_reduce_prompt",
                purpose="Reduce chunk summaries into one structured document summary.",
                version="2026-06-summary-v2-compact",
                expected_schema="DocumentSummary",
                system=(
                    "You combine chunk summaries into a compact, exam-ready teaching summary. "
                    "Preserve only high-signal concepts, definitions, formulas, examples, and likely exam topics."
                ),
                template=(
                    "Document id: $document_id\n"
                    "Subject: $subject\n"
                    "Filename: $filename\n"
                    "Prompt version: $prompt_version\n"
                    "Model id: $model_id\n"
                    "Chunk count: $chunk_count\n\n"
                    "Compact chunk evidence:\n$chunk_summaries\n\n"
                    "Return one compact structured document summary:\n"
                    "- concepts: max 20\n"
                    "- definitions: max 16, one sentence each\n"
                    "- formulas: max 12\n"
                    "- examples: max 12\n"
                    "- learning_objectives: max 16\n"
                    "- likely_exam_topics: max 20\n"
                    "- source_coverage: max 12 notes naming pages or sections covered\n"
                    "- executive_summary: max 180 words\n\n"
                    "Merge duplicates. Do not include per-chunk summaries or recreate the full document."
                ),
            ),
            "question_blueprint_prompt": PromptSpec(
                key="question_blueprint_prompt",
                purpose="Create an exam-generation blueprint from selected summaries.",
                version="2026-06-question-paper-v1",
                expected_schema="QuestionBlueprint",
                system=(
                    "You are an academic assessment designer. Build a blueprint before generating questions."
                ),
                template=(
                    "Subject: $subject\n"
                    "Difficulty: $difficulty\n"
                    "Requested distribution: $distribution\n"
                    "Extra instructor guidance: $extra_context\n\n"
                    "Selected compact document summaries:\n$summaries\n\n"
                    "Return a blueprint that balances source coverage and avoids unsupported topics."
                ),
            ),
            "question_paper_generation_prompt": PromptSpec(
                key="question_paper_generation_prompt",
                purpose="Generate a schema-valid question paper from a blueprint.",
                version="2026-06-question-paper-v1",
                expected_schema="QuestionPaper",
                system=(
                    "You generate exam questions and answer keys from an approved blueprint. "
                    "Return only schema-valid structured output."
                ),
                template=(
                    "Subject: $subject\n"
                    "Total questions: $total_questions\n"
                    "Difficulty: $difficulty\n"
                    "Distribution: $distribution\n\n"
                    "Blueprint:\n$blueprint\n\n"
                    "Generate exactly the requested number of questions. Include options only for multiple_choice."
                ),
            ),
            "ragas_answer_generation_prompt": PromptSpec(
                key="ragas_answer_generation_prompt",
                purpose="Generate RAG answers for evaluation rows.",
                version="2026-06-ragas-v1",
                expected_schema=None,
                system="Answer with the same grounded behavior as the production QA flow.",
                template="$question",
            ),
        }

    def get(self, key: str) -> PromptSpec:
        if key not in self._prompts:
            raise KeyError(f"Unknown prompt key: {key}")
        return self._prompts[key]

    def render(self, key: str, **kwargs: object) -> str:
        return self.get(key).render(**kwargs)

    def version(self, key: str) -> str:
        return self.get(key).version

    def list_prompts(self) -> list[PromptSpec]:
        return list(self._prompts.values())
