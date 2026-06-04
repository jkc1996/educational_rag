import json
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.services.log_service import LogService


def test_log_service_normalizes_and_summarizes_events():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    settings.ensure_storage()
    settings.app_log_path.write_text(
        "\n".join(
            [
                json.dumps({"timestamp": "2026-06-04 10:00:00", "level": "INFO", "event": "openai_chat_model_create", "model_id": "gpt-5.4", "feature": "rag_answer"}),
                json.dumps({"timestamp": "2026-06-04 10:01:00", "level": "ERROR", "event": "document_ingestion_failed", "document_id": "doc-1", "error": "bad pdf"}),
            ]
        ),
        encoding="utf-8",
    )

    response = LogService(settings).list_logs(limit=100)

    assert response.summary.total == 2
    assert response.summary.errors == 1
    assert response.summary.openai_events == 1
    assert response.summary.llm_events == 1
    assert response.summary.ingestion_events == 1
    assert response.items[1].message == "OpenAI model prepared for rag_answer: gpt-5.4"
    assert response.items[0].category == "ingestion"


def test_log_service_filters_by_category_and_query():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    settings.ensure_storage()
    settings.app_log_path.write_text(
        "\n".join(
            [
                json.dumps({"timestamp": "2026-06-04 10:00:00", "level": "INFO", "event": "openai_chat_model_create", "model_id": "gpt-5.4", "feature": "rag_answer"}),
                json.dumps({"timestamp": "2026-06-04 10:01:00", "level": "INFO", "event": "HTTP Request: %s %s"}),
            ]
        ),
        encoding="utf-8",
    )

    response = LogService(settings).list_logs(limit=100, category="llm", query="rag")

    assert len(response.items) == 1
    assert response.items[0].category == "llm"
    assert response.items[0].details["feature"] == "rag_answer"


def test_log_service_preserves_application_flow_fields():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    settings.ensure_storage()
    settings.app_log_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-06-04 10:00:00",
                "level": "INFO",
                "category": "qa",
                "flow": "qa",
                "flow_id": "qa_123",
                "step": "answer",
                "event": "qa_answer_completed",
                "message": "QA answer generated",
                "question": "What is SVM?",
                "answer_preview": "SVM stands for Support Vector Machine.",
            }
        ),
        encoding="utf-8",
    )

    response = LogService(settings).list_logs(limit=100)

    assert response.summary.qa_events == 1
    assert response.items[0].flow == "qa"
    assert response.items[0].flow_id == "qa_123"
    assert response.items[0].step == "answer"
    assert response.items[0].details["question"] == "What is SVM?"
