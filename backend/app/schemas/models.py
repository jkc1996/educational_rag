from pydantic import BaseModel


class ModelInfo(BaseModel):
    id: str
    label: str
    role: str
    default: bool = False


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
    embedding_model: str

