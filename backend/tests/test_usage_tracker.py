from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from app.core.config import Settings
from app.infrastructure.usage import OpenAIUsageTracker


def test_usage_tracker_estimates_and_persists():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    settings.ensure_storage()
    tracker = OpenAIUsageTracker(settings)
    record = tracker.record(feature="test", model_id="gpt-5.4-mini", prompt_tokens=1000, completion_tokens=500)
    assert record.estimated_cost_usd > 0
    assert record.token_source == "manual"
    assert tracker.summary().total_prompt_tokens == 1000


def test_usage_tracker_uses_openai_response_metadata_without_estimate():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    settings.ensure_storage()
    tracker = OpenAIUsageTracker(settings)
    response = SimpleNamespace(
        usage_metadata={
            "input_tokens": 1000,
            "output_tokens": 500,
            "total_tokens": 1500,
            "input_token_details": {"cache_read": 200},
        },
        response_metadata={"id": "chatcmpl_test", "request_id": "req_test"},
    )

    record = tracker.track_langchain_response(
        "chunk_summary",
        "gpt-5.4-mini",
        response,
    )

    assert record.prompt_tokens == 1000
    assert record.completion_tokens == 500
    assert record.cached_tokens == 200
    assert record.total_tokens == 1500
    assert record.token_source == "openai_response_metadata"
    assert record.openai_response_id == "chatcmpl_test"
    assert record.openai_request_id == "req_test"
    assert record.is_estimate is False
    assert record.estimated_cost_usd > 0


def test_usage_tracker_does_not_estimate_missing_metadata():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    settings.ensure_storage()
    tracker = OpenAIUsageTracker(settings)

    record = tracker.track_langchain_response("chunk_summary", "gpt-5.4-mini", SimpleNamespace())

    assert record.prompt_tokens == 0
    assert record.completion_tokens == 0
    assert record.estimated_cost_usd == 0
    assert record.token_source == "missing_openai_usage_metadata"
    assert record.cost_source == "not_calculated"
    assert record.is_estimate is False


def test_usage_tracker_uses_openai_embedding_usage():
    storage_dir = Path("storage") / "tests" / str(uuid4())
    settings = Settings(storage_dir=storage_dir)
    settings.ensure_storage()
    tracker = OpenAIUsageTracker(settings)
    response = SimpleNamespace(usage=SimpleNamespace(prompt_tokens=8, total_tokens=8), id="emb_test")

    record = tracker.track_embedding_response("embedding", "text-embedding-3-large", response)

    assert record.prompt_tokens == 8
    assert record.total_tokens == 8
    assert record.token_source == "openai_embedding_response_usage"
    assert record.openai_response_id == "emb_test"
    assert record.is_estimate is False
