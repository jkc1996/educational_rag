from fastapi import APIRouter, Depends

from app.core.config import Settings
from app.core.dependencies import settings_dependency
from app.schemas.models import ModelInfo, ModelsResponse

router = APIRouter()


@router.get("/models", response_model=ModelsResponse)
def list_models(settings: Settings = Depends(settings_dependency)) -> ModelsResponse:
    models = [
        ModelInfo(
            id=model_id,
            label=model_id,
            role=_role_for(settings, model_id),
            default=model_id == settings.openai_default_chat_model,
        )
        for model_id in settings.openai_allowed_chat_models
    ]
    return ModelsResponse(models=models, embedding_model=settings.openai_embedding_model)


def _role_for(settings: Settings, model_id: str) -> str:
    if model_id == settings.openai_summary_model:
        return "summarization"
    if model_id == settings.openai_utility_model:
        return "utility"
    if model_id == settings.openai_default_chat_model:
        return "qa-default"
    return "high-quality"

