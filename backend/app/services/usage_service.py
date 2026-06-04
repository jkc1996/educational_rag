from app.infrastructure.usage import OpenAIUsageTracker
from app.schemas.usage import UsageSummary


class UsageService:
    def __init__(self, usage_tracker: OpenAIUsageTracker) -> None:
        self.usage_tracker = usage_tracker

    def summary(self, limit: int = 500) -> UsageSummary:
        return self.usage_tracker.summary(limit)

