import json
import re
from collections import Counter
from typing import Any

from app.core.config import Settings
from app.schemas.logs import LogEntry, LogsResponse, LogSummary


class LogService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def list_logs(
        self,
        *,
        limit: int = 500,
        query: str | None = None,
        level: str | None = None,
        category: str | None = None,
    ) -> LogsResponse:
        if not self.settings.app_log_path.exists():
            return LogsResponse(items=[], summary=self._summary([]), levels=[], categories=[])

        rows: list[LogEntry] = []
        for line in self.settings.app_log_path.read_text(encoding="utf-8").splitlines()[-limit:]:
            try:
                rows.append(self._normalize(json.loads(line)))
            except Exception:
                continue
        rows = list(reversed(rows))

        levels = sorted({row.level for row in rows})
        categories = sorted({row.category for row in rows})
        filtered = self._filter(rows, query=query, level=level, category=category)

        return LogsResponse(
            items=filtered,
            summary=self._summary(filtered),
            levels=levels,
            categories=categories,
        )

    def _normalize(self, row: dict[str, Any]) -> LogEntry:
        event = str(row.get("event") or "log_event")
        level = str(row.get("level") or "INFO").upper()
        known = {"timestamp", "level", "event", "message", "category", "flow", "flow_id", "step"}
        details = {key: value for key, value in row.items() if key not in known}
        category = str(row.get("category") or self._category(event, details))
        message = str(row.get("message") or self._message(event, details))
        details_preview = self._details_preview(details)

        return LogEntry(
            timestamp=str(row.get("timestamp") or ""),
            level=level,
            category=category,
            flow=row.get("flow"),
            flow_id=row.get("flow_id"),
            step=row.get("step"),
            event=event,
            message=message,
            details=details,
            details_preview=details_preview,
            logger=details.get("logger"),
            fingerprint=self._fingerprint(event),
            is_noise=self._is_noise(event, category),
        )

    def _category(self, event: str, details: dict[str, Any]) -> str:
        event_l = event.lower()
        if event_l.startswith("qa_"):
            return "qa"
        if event_l.startswith("question_"):
            return "question_paper"
        if event_l.startswith("ragas_"):
            return "evaluation"
        if event_l.startswith("feedback_"):
            return "feedback"
        if event_l.startswith("llm_") or event_l.startswith("embedding_"):
            return "llm"
        if event_l.startswith("openai_") or details.get("model_id"):
            return "llm"
        if "ingestion" in event_l or details.get("document_id"):
            return "ingestion"
        if event_l.startswith("http request"):
            return "http"
        if "backing off" in event_l or "retry" in event_l:
            return "retry"
        if "chroma" in event_l or "telemetry" in event_l:
            return "vector_store"
        if "error" in details or "exception" in details:
            return "error"
        return "system"

    def _message(self, event: str, details: dict[str, Any]) -> str:
        if event == "openai_chat_model_create":
            model = details.get("model_id", "unknown model")
            feature = details.get("feature", "general")
            return f"OpenAI model prepared for {feature}: {model}"
        if event == "document_ingestion_failed":
            return f"Document ingestion failed: {details.get('error', 'unknown error')}"
        if event.startswith("HTTP Request"):
            return "HTTP client request"
        if "Anonymized telemetry enabled" in event:
            return "Chroma telemetry notice"
        if event.startswith("Backing off"):
            return "Retry backoff started"
        return event.replace("_", " ").strip().capitalize()

    def _details_preview(self, details: dict[str, Any]) -> str:
        preferred = [
            "question_preview",
            "answer_preview",
            "response_preview",
            "feature",
            "model_id",
            "document_id",
            "subject",
            "filename",
            "source_count",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "calculated_cost_usd",
            "error",
        ]
        parts = [f"{key}: {details[key]}" for key in preferred if details.get(key) is not None]
        if parts:
            return " · ".join(parts)
        compact = {key: value for key, value in details.items() if key not in {"exception"}}
        if not compact:
            return ""
        return json.dumps(compact, ensure_ascii=False, separators=(",", ":"))[:220]

    def _fingerprint(self, event: str) -> str:
        cleaned = re.sub(r"\s+", " ", event.lower()).strip()
        cleaned = re.sub(r"[^a-z0-9_ -]+", "", cleaned)
        return cleaned[:96] or "log_event"

    def _is_noise(self, event: str, category: str) -> bool:
        return category in {"http", "vector_store"} or event.startswith("Backing off")

    def _filter(
        self,
        rows: list[LogEntry],
        *,
        query: str | None,
        level: str | None,
        category: str | None,
    ) -> list[LogEntry]:
        filtered = rows
        if level:
            filtered = [row for row in filtered if row.level == level.upper()]
        if category:
            filtered = [row for row in filtered if row.category == category]
        if query:
            needle = query.lower()
            filtered = [
                row
                for row in filtered
                if needle in row.message.lower()
                or needle in row.event.lower()
                or needle in row.details_preview.lower()
                or needle in json.dumps(row.details, ensure_ascii=False).lower()
            ]
        return filtered

    def _summary(self, rows: list[LogEntry]) -> LogSummary:
        categories = Counter(row.category for row in rows)
        return LogSummary(
            total=len(rows),
            errors=sum(1 for row in rows if row.level in {"ERROR", "CRITICAL"}),
            warnings=sum(1 for row in rows if row.level == "WARNING"),
            qa_events=categories["qa"],
            llm_events=categories["llm"],
            openai_events=categories["openai"] + categories["llm"],
            ingestion_events=categories["ingestion"],
            noisy_events=sum(1 for row in rows if row.is_noise),
        )
