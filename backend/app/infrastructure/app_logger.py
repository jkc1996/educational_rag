import logging
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator


_flow_id: ContextVar[str | None] = ContextVar("app_log_flow_id", default=None)
_flow: ContextVar[str | None] = ContextVar("app_log_flow", default=None)


def new_flow_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4()}"


def current_flow_id() -> str | None:
    return _flow_id.get()


def current_flow() -> str | None:
    return _flow.get()


@contextmanager
def log_context(*, flow: str, flow_id: str) -> Iterator[None]:
    flow_token = _flow.set(flow)
    flow_id_token = _flow_id.set(flow_id)
    try:
        yield
    finally:
        _flow.reset(flow_token)
        _flow_id.reset(flow_id_token)


def app_event(
    event: str,
    *,
    message: str,
    category: str | None = None,
    flow: str | None = None,
    flow_id: str | None = None,
    step: str | None = None,
    level: int = logging.INFO,
    **details: Any,
) -> None:
    active_flow = flow or current_flow()
    payload = {
        "event": event,
        "message": message,
        "category": category or active_flow or "application",
        "flow": active_flow,
        "flow_id": flow_id or current_flow_id(),
        "step": step,
        **_clean(details),
    }
    logging.getLogger("educational_rag.app").log(level, payload)


@contextmanager
def timed_step(event: str, *, message: str, step: str, **details: Any) -> Iterator[None]:
    started = time.perf_counter()
    app_event(f"{event}_started", message=message, step=step, **details)
    try:
        yield
    except Exception as exc:
        app_event(
            f"{event}_failed",
            message=f"{message} failed",
            step=step,
            level=logging.ERROR,
            error=str(exc),
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            **details,
        )
        raise
    app_event(
        f"{event}_completed",
        message=f"{message} completed",
        step=step,
        duration_ms=round((time.perf_counter() - started) * 1000, 2),
        **details,
    )


def text_preview(value: str | None, *, limit: int = 1200) -> str:
    if not value:
        return ""
    normalized = " ".join(str(value).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _clean(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value
