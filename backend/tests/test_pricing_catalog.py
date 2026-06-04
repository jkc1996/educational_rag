from app.infrastructure.pricing import OpenAIPricingCatalog


def test_pricing_catalog_calculates_from_token_counts():
    catalog = OpenAIPricingCatalog()

    calculation = catalog.calculate(
        model_id="gpt-5.4-mini",
        prompt_tokens=1000,
        cached_tokens=200,
        completion_tokens=500,
    )

    assert calculation is not None
    assert calculation.amount_usd > 0
    assert calculation.source == "https://openai.com/api/pricing/"
    assert calculation.snapshot == "openai-pricing-2026-06-04"


def test_pricing_catalog_returns_none_for_unknown_models():
    catalog = OpenAIPricingCatalog()

    assert catalog.calculate(model_id="unknown-model", prompt_tokens=1000, completion_tokens=500) is None
