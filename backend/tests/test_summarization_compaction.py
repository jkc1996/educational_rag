from pathlib import Path
from uuid import uuid4

from langchain_core.documents import Document

from app.core.config import Settings
from app.schemas.summaries import DocumentSummary
from app.services.summarization_service import SummarizationService


def test_document_summary_compacts_oversized_payloads():
    summary = DocumentSummary.model_validate(
        {
            "document_id": "doc-1",
            "subject": "Machine Learning",
            "filename": "ml.pdf",
            "prompt_version": "old",
            "model_id": "gpt-5.4-mini",
            "chunk_count": 24,
            "concepts": [f"Concept {index}" for index in range(40)],
            "definitions": [f"Definition {index} " + ("x" * 300) for index in range(40)],
            "formulas": [f"Formula {index}" for index in range(20)],
            "examples": [f"Example {index}" for index in range(20)],
            "learning_objectives": [f"Objective {index}" for index in range(40)],
            "likely_exam_topics": [f"Topic {index}" for index in range(40)],
            "source_coverage": [f"Page {index}" for index in range(30)],
            "executive_summary": "x" * 3000,
            "chunk_summaries": [],
        }
    )

    assert len(summary.concepts) == 20
    assert len(summary.definitions) == 16
    assert len(summary.likely_exam_topics) == 20
    assert len(summary.source_coverage) == 12
    assert len(summary.executive_summary) <= 1400
    assert not hasattr(summary, "chunk_summaries")


def test_summary_chunk_selection_spreads_across_document():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir, max_summary_chunks_per_document=4)
    service = SummarizationService(
        settings=settings,
        model_factory=None,
        prompt_registry=None,
        summary_repository=None,
    )
    chunks = [Document(page_content=f"chunk {index}", metadata={"chunk_index": index}) for index in range(10)]

    selected = service._select_chunks_for_summary(chunks)

    assert len(selected) == 4
    assert selected[0].metadata["chunk_index"] == 0
    assert selected[-1].metadata["chunk_index"] == 9
