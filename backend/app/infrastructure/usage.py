import json
from datetime import datetime, timezone
from typing import Any

from app.core.config import Settings
from app.infrastructure.pricing import OpenAIPricingCatalog
from app.schemas.usage import UsageRecord, UsageSummary


class OpenAIUsageTracker:
    def __init__(self, settings: Settings, pricing_catalog: OpenAIPricingCatalog | None = None) -> None:
        self.settings = settings
        self.pricing_catalog = pricing_catalog or OpenAIPricingCatalog()
        self.settings.ensure_storage()

    def record(
        self,
        *,
        feature: str,
        model_id: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cached_tokens: int = 0,
        total_tokens: int | None = None,
        token_source: str = "manual",
        cost_source: str | None = None,
        pricing_snapshot: str | None = None,
        openai_response_id: str | None = None,
        openai_request_id: str | None = None,
        is_estimate: bool = False,
    ) -> UsageRecord:
        total = total_tokens if total_tokens is not None else prompt_tokens + completion_tokens
        estimated_cost = 0.0
        selected_cost_source = cost_source or "not_calculated"
        selected_pricing_snapshot = pricing_snapshot
        if cost_source != "not_calculated":
            calculation = self.pricing_catalog.calculate(
                model_id=model_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cached_tokens=cached_tokens,
            )
            if calculation:
                estimated_cost = calculation.amount_usd
                selected_cost_source = calculation.source
                selected_pricing_snapshot = calculation.snapshot
        record = UsageRecord(
            timestamp=datetime.now(timezone.utc),
            feature=feature,
            model_id=model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            total_tokens=total,
            estimated_cost_usd=estimated_cost,
            token_source=token_source,
            cost_source=selected_cost_source,
            pricing_snapshot=selected_pricing_snapshot,
            openai_response_id=openai_response_id,
            openai_request_id=openai_request_id,
            is_estimate=is_estimate,
        )
        with self.settings.usage_log_path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")
        return record

    def track_langchain_response(
        self,
        feature: str,
        model_id: str,
        response: Any,
        *,
        prompt: str | None = None,
        output: str | None = None,
    ) -> UsageRecord:
        usage = self._as_dict(getattr(response, "usage_metadata", None))
        response_metadata = self._as_dict(getattr(response, "response_metadata", None))
        token_usage = self._as_dict(response_metadata.get("token_usage") or response_metadata.get("usage"))

        prompt_tokens = self._first_int(
            usage.get("input_tokens"),
            usage.get("prompt_tokens"),
            token_usage.get("input_tokens"),
            token_usage.get("prompt_tokens"),
        )
        completion_tokens = self._first_int(
            usage.get("output_tokens"),
            usage.get("completion_tokens"),
            token_usage.get("output_tokens"),
            token_usage.get("completion_tokens"),
        )
        total_tokens = self._first_int(usage.get("total_tokens"), token_usage.get("total_tokens"))
        cached_tokens = 0
        input_details = self._as_dict(
            usage.get("input_token_details")
            or usage.get("prompt_tokens_details")
            or token_usage.get("input_tokens_details")
            or token_usage.get("prompt_tokens_details")
        )
        if isinstance(input_details, dict):
            cached_tokens = self._first_int(input_details.get("cache_read"), input_details.get("cached_tokens"))

        has_openai_usage = bool(usage or token_usage)
        if not has_openai_usage:
            return self.record(
                feature=feature,
                model_id=model_id,
                token_source="missing_openai_usage_metadata",
                cost_source="not_calculated",
            )

        return self.record(
            feature=feature,
            model_id=model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            total_tokens=total_tokens or prompt_tokens + completion_tokens,
            token_source="openai_response_metadata",
            openai_response_id=self._first_str(response_metadata.get("id"), getattr(response, "id", None)),
            openai_request_id=self._first_str(response_metadata.get("request_id"), response_metadata.get("x-request-id")),
        )

    def track_embedding_response(self, feature: str, model_id: str, response: Any) -> UsageRecord:
        usage = self._as_dict(getattr(response, "usage", None))
        if not usage:
            return self.record(
                feature=feature,
                model_id=model_id,
                token_source="missing_openai_embedding_usage",
                cost_source="not_calculated",
            )

        prompt_tokens = self._first_int(usage.get("prompt_tokens"), usage.get("input_tokens"))
        total_tokens = self._first_int(usage.get("total_tokens")) or prompt_tokens
        return self.record(
            feature=feature,
            model_id=model_id,
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
            token_source="openai_embedding_response_usage",
            openai_response_id=self._first_str(getattr(response, "id", None)),
        )

    def calculate_cost(self, model_id: str, prompt_tokens: int, completion_tokens: int, cached_tokens: int = 0) -> float:
        calculation = self.pricing_catalog.calculate(
            model_id=model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
        )
        return calculation.amount_usd if calculation else 0.0

    def estimate_cost(self, model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        return self.calculate_cost(model_id, prompt_tokens, completion_tokens)

    def _as_dict(self, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "dict"):
            return value.dict()
        return {
            key: getattr(value, key)
            for key in dir(value)
            if not key.startswith("_") and not callable(getattr(value, key))
        }

    def _first_int(self, *values: Any) -> int:
        for value in values:
            if value is None:
                continue
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
        return 0

    def _first_str(self, *values: Any) -> str | None:
        for value in values:
            if value:
                return str(value)
        return None

    def list_records(self, limit: int = 500) -> list[UsageRecord]:
        if not self.settings.usage_log_path.exists():
            return []
        lines = self.settings.usage_log_path.read_text(encoding="utf-8").splitlines()[-limit:]
        records: list[UsageRecord] = []
        for line in lines:
            try:
                records.append(UsageRecord.model_validate(json.loads(line)))
            except Exception:
                continue
        return records

    def summary(self, limit: int = 500) -> UsageSummary:
        records = self.list_records(limit)
        return UsageSummary(
            total_prompt_tokens=sum(r.prompt_tokens for r in records),
            total_completion_tokens=sum(r.completion_tokens for r in records),
            total_cached_tokens=sum(r.cached_tokens for r in records),
            estimated_cost_usd=round(sum(r.estimated_cost_usd for r in records), 6),
            records=records,
        )
