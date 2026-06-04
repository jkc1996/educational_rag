from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.services.evaluation_service import RagasEvaluationService


def _service(settings: Settings) -> RagasEvaluationService:
    return RagasEvaluationService(
        settings=settings,
        rag_service=None,
        usage_tracker=None,
        model_factory=None,
    )


def test_eval_sets_seed_default_when_missing():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)

    response = _service(settings).list_eval_sets()

    assert response.items
    assert response.items[0].name == "default"
    assert response.items[0].row_count >= 1
    assert (settings.eval_sets_dir / "default.json").exists()


def test_load_eval_rows_filters_by_subject():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    service = _service(settings)

    rows = service._load_eval_rows("default", subject="Machine Learning")

    assert rows
    assert all(row.get("subject") == "Machine Learning" for row in rows)


def test_row_helpers_accept_legacy_and_current_columns():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    service = _service(settings)

    assert service._row_question({"user_input": "What is RAG?"}) == "What is RAG?"
    assert service._row_reference({"ground_truth": "A retrieval workflow."}) == "A retrieval workflow."
