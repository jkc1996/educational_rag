from pydantic import BaseModel, Field


def _clip(value: str, max_chars: int) -> str:
    value = " ".join(str(value).split())
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def _compact_items(items: list[str], *, limit: int, max_chars: int) -> list[str]:
    compacted: list[str] = []
    seen: set[str] = set()
    for item in items:
        clipped = _clip(item, max_chars)
        key = clipped.lower()
        if clipped and key not in seen:
            compacted.append(clipped)
            seen.add(key)
        if len(compacted) >= limit:
            break
    return compacted


class SourcePage(BaseModel):
    source_file: str
    page: int | None = None


class ChunkSummary(BaseModel):
    source: SourcePage
    concepts: list[str] = Field(default_factory=list, description="Up to 6 concise concept names.")
    definitions: list[str] = Field(default_factory=list, description="Up to 4 one-sentence definitions.")
    formulas: list[str] = Field(default_factory=list, description="Up to 4 formulas or symbolic rules.")
    examples: list[str] = Field(default_factory=list, description="Up to 3 short examples.")
    learning_objectives: list[str] = Field(default_factory=list, description="Up to 4 learning objectives.")
    likely_exam_topics: list[str] = Field(default_factory=list, description="Up to 4 likely exam topics.")
    summary: str

    def model_post_init(self, __context: object) -> None:
        self.concepts = _compact_items(self.concepts, limit=6, max_chars=90)
        self.definitions = _compact_items(self.definitions, limit=4, max_chars=220)
        self.formulas = _compact_items(self.formulas, limit=4, max_chars=180)
        self.examples = _compact_items(self.examples, limit=3, max_chars=180)
        self.learning_objectives = _compact_items(self.learning_objectives, limit=4, max_chars=160)
        self.likely_exam_topics = _compact_items(self.likely_exam_topics, limit=4, max_chars=160)
        self.summary = _clip(self.summary, 700)


class DocumentSummary(BaseModel):
    document_id: str
    subject: str
    filename: str
    prompt_version: str
    model_id: str
    chunk_count: int
    concepts: list[str] = Field(default_factory=list, description="Up to 20 high-signal concept names.")
    definitions: list[str] = Field(default_factory=list, description="Up to 16 core definitions.")
    formulas: list[str] = Field(default_factory=list, description="Up to 12 formulas or symbolic rules.")
    examples: list[str] = Field(default_factory=list, description="Up to 12 representative examples.")
    learning_objectives: list[str] = Field(default_factory=list, description="Up to 16 exam-relevant learning objectives.")
    likely_exam_topics: list[str] = Field(default_factory=list, description="Up to 20 likely exam topics.")
    source_coverage: list[str] = Field(default_factory=list, description="Up to 12 source page or section coverage notes.")
    executive_summary: str

    def model_post_init(self, __context: object) -> None:
        self.concepts = _compact_items(self.concepts, limit=20, max_chars=90)
        self.definitions = _compact_items(self.definitions, limit=16, max_chars=220)
        self.formulas = _compact_items(self.formulas, limit=12, max_chars=180)
        self.examples = _compact_items(self.examples, limit=12, max_chars=180)
        self.learning_objectives = _compact_items(self.learning_objectives, limit=16, max_chars=160)
        self.likely_exam_topics = _compact_items(self.likely_exam_topics, limit=20, max_chars=160)
        self.source_coverage = _compact_items(self.source_coverage, limit=12, max_chars=160)
        self.executive_summary = _clip(self.executive_summary, 1400)


class QuestionBlueprint(BaseModel):
    subject: str
    focus_areas: list[str] = Field(default_factory=list)
    learning_objectives: list[str] = Field(default_factory=list)
    difficulty_notes: str
    distribution_guidance: list[str] = Field(default_factory=list)
    source_coverage: list[str] = Field(default_factory=list)
