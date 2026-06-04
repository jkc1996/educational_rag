from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Educational RAG"
    api_prefix: str = "/api/v1"
    cors_origins_raw: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    storage_dir: Path = BACKEND_DIR / "storage"
    uploads_dir_name: str = "uploads"
    chroma_dir_name: str = "chroma"
    summaries_dir_name: str = "summaries"
    eval_sets_dir_name: str = "eval_sets"
    eval_results_dir_name: str = "eval_results"
    logs_dir_name: str = "logs"

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_allowed_chat_models_raw: str = Field(
        default="gpt-5.5,gpt-5.4,gpt-5.4-mini,gpt-5.4-nano",
        alias="OPENAI_ALLOWED_CHAT_MODELS",
    )
    openai_default_chat_model: str = Field(default="gpt-5.4", alias="OPENAI_DEFAULT_CHAT_MODEL")
    openai_summary_model: str = Field(default="gpt-5.4-mini", alias="OPENAI_SUMMARY_MODEL")
    openai_utility_model: str = Field(default="gpt-5.4-nano", alias="OPENAI_UTILITY_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-large", alias="OPENAI_EMBEDDING_MODEL")

    chunk_size: int = 1800
    chunk_overlap: int = 180
    retrieval_top_k: int = 5
    max_summary_chunks_per_document: int = 18
    max_questions_per_paper: int = 50
    max_ragas_questions: int = 25
    daily_soft_budget_usd: float = 5.0

    @property
    def cors_origins(self) -> list[str]:
        return self._csv(self.cors_origins_raw)

    @property
    def openai_allowed_chat_models(self) -> list[str]:
        return self._csv(self.openai_allowed_chat_models_raw)

    def _csv(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def uploads_dir(self) -> Path:
        return self.storage_dir / self.uploads_dir_name

    @property
    def chroma_dir(self) -> Path:
        return self.storage_dir / self.chroma_dir_name

    @property
    def summaries_dir(self) -> Path:
        return self.storage_dir / self.summaries_dir_name

    @property
    def eval_sets_dir(self) -> Path:
        return self.storage_dir / self.eval_sets_dir_name

    @property
    def eval_results_dir(self) -> Path:
        return self.storage_dir / self.eval_results_dir_name

    @property
    def logs_dir(self) -> Path:
        return self.storage_dir / self.logs_dir_name

    @property
    def documents_index_path(self) -> Path:
        return self.storage_dir / "documents.json"

    @property
    def feedback_log_path(self) -> Path:
        return self.storage_dir / "feedback.jsonl"

    @property
    def usage_log_path(self) -> Path:
        return self.storage_dir / "usage.jsonl"

    @property
    def app_log_path(self) -> Path:
        return self.logs_dir / "app.jsonl"

    def ensure_storage(self) -> None:
        for path in [
            self.storage_dir,
            self.uploads_dir,
            self.chroma_dir,
            self.summaries_dir,
            self.eval_sets_dir,
            self.eval_results_dir,
            self.logs_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def validate_model_id(self, model_id: str | None) -> str:
        selected = model_id or self.openai_default_chat_model
        if selected not in self.openai_allowed_chat_models:
            allowed = ", ".join(self.openai_allowed_chat_models)
            raise ValueError(f"Unsupported OpenAI model '{selected}'. Allowed models: {allowed}")
        return selected


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_storage()
    return settings
