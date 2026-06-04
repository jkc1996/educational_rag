import pytest

from app.core.config import Settings


def test_model_allowlist_validation_accepts_default():
    settings = Settings()
    assert settings.validate_model_id(None) == "gpt-5.4"


def test_model_allowlist_validation_rejects_unknown():
    settings = Settings()
    with pytest.raises(ValueError):
        settings.validate_model_id("not-a-model")
