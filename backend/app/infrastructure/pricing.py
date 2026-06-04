from dataclasses import dataclass


@dataclass(frozen=True)
class CostCalculation:
    amount_usd: float
    source: str
    snapshot: str


@dataclass(frozen=True)
class ModelTokenPricing:
    input_per_million: float
    cached_input_per_million: float
    output_per_million: float


class OpenAIPricingCatalog:
    """
    Pricing is not returned by normal OpenAI model responses.
    This catalog converts OpenAI-returned token counts into a local calculated cost.
    Invoice-grade spend should be read from OpenAI's Costs API or billing dashboard.
    """

    SNAPSHOT = "openai-pricing-2026-06-04"
    SOURCE_URL = "https://openai.com/api/pricing/"
    EMBEDDING_SOURCE_URL = "https://developers.openai.com/api/docs/models/text-embedding-3-large"

    _TOKEN_PRICING_PER_MILLION: dict[str, ModelTokenPricing] = {
        "gpt-5.5": ModelTokenPricing(input_per_million=5.0, cached_input_per_million=0.5, output_per_million=30.0),
        "gpt-5.4": ModelTokenPricing(input_per_million=2.5, cached_input_per_million=0.25, output_per_million=15.0),
        "gpt-5.4-mini": ModelTokenPricing(input_per_million=0.75, cached_input_per_million=0.075, output_per_million=4.5),
        "gpt-5.4-nano": ModelTokenPricing(input_per_million=0.20, cached_input_per_million=0.02, output_per_million=1.25),
        "text-embedding-3-large": ModelTokenPricing(input_per_million=0.13, cached_input_per_million=0.0, output_per_million=0.0),
    }

    def calculate(
        self,
        *,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        cached_tokens: int = 0,
    ) -> CostCalculation | None:
        pricing = self._TOKEN_PRICING_PER_MILLION.get(model_id)
        if not pricing:
            return None

        billable_prompt_tokens = max(prompt_tokens - cached_tokens, 0)
        amount = (
            (billable_prompt_tokens / 1_000_000) * pricing.input_per_million
            + (cached_tokens / 1_000_000) * pricing.cached_input_per_million
            + (completion_tokens / 1_000_000) * pricing.output_per_million
        )
        return CostCalculation(
            amount_usd=round(amount, 6),
            source=self.source_for(model_id),
            snapshot=self.SNAPSHOT,
        )

    def source_for(self, model_id: str) -> str:
        if model_id.startswith("text-embedding"):
            return self.EMBEDDING_SOURCE_URL
        return self.SOURCE_URL
