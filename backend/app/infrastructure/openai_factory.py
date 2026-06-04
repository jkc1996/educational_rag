from typing import TypeVar

from langchain_core.embeddings import Embeddings
from pydantic import BaseModel

from app.core.config import Settings
from app.infrastructure.app_logger import app_event, text_preview
from app.infrastructure.usage import OpenAIUsageTracker

T = TypeVar("T", bound=BaseModel)


class OpenAIModelFactory:
    def __init__(self, settings: Settings, usage_tracker: OpenAIUsageTracker) -> None:
        self.settings = settings
        self.usage_tracker = usage_tracker

    def chat_model(self, model_id: str | None = None, *, feature: str = "general"):
        from langchain_openai import ChatOpenAI

        selected = self.settings.validate_model_id(model_id)
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI-backed generation.")
        app_event(
            "openai_chat_model_create",
            message=f"OpenAI model prepared for {feature}: {selected}",
            category="llm",
            step=feature,
            model_id=selected,
            feature=feature,
        )
        return ChatOpenAI(
            model=selected,
            api_key=self.settings.openai_api_key,
            timeout=90,
            max_retries=2,
        )

    def embeddings(self):
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI embeddings.")
        return UsageTrackedOpenAIEmbeddings(
            model=self.settings.openai_embedding_model,
            api_key=self.settings.openai_api_key,
            usage_tracker=self.usage_tracker,
        )

    def invoke_text(self, *, model_id: str, prompt: str, feature: str) -> str:
        model = self.chat_model(model_id, feature=feature)
        app_event(
            "llm_call_started",
            message=f"OpenAI text call started for {feature}",
            category="llm",
            step=feature,
            model_id=model_id,
            feature=feature,
            prompt_chars=len(prompt),
        )
        response = model.invoke(prompt)
        content = getattr(response, "content", str(response))
        usage = self.usage_tracker.track_langchain_response(feature, model_id, response, prompt=prompt, output=content)
        app_event(
            "llm_call_completed",
            message=f"OpenAI text response received for {feature}",
            category="llm",
            step=feature,
            model_id=model_id,
            feature=feature,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            calculated_cost_usd=usage.estimated_cost_usd,
            token_source=usage.token_source,
            openai_response_id=usage.openai_response_id,
            response_preview=text_preview(content, limit=1600),
            response_chars=len(content),
        )
        return content

    def invoke_structured(self, *, model_id: str, prompt: str, schema: type[T], feature: str) -> T:
        model = self.chat_model(model_id, feature=feature)
        app_event(
            "llm_structured_call_started",
            message=f"OpenAI structured call started for {feature}",
            category="llm",
            step=feature,
            model_id=model_id,
            feature=feature,
            schema=schema.__name__,
            prompt_chars=len(prompt),
        )
        try:
            structured_model = model.with_structured_output(schema, include_raw=True)
        except TypeError:
            structured_model = model.with_structured_output(schema)

        response = structured_model.invoke(prompt)
        raw_response = response.get("raw") if isinstance(response, dict) else response
        parsed_response = response.get("parsed") if isinstance(response, dict) else response
        parsing_error = response.get("parsing_error") if isinstance(response, dict) else None

        if parsing_error:
            raise parsing_error

        if isinstance(parsed_response, schema):
            parsed = parsed_response
        elif isinstance(parsed_response, dict):
            parsed = schema.model_validate(parsed_response)
        else:
            parsed = schema.model_validate_json(str(parsed_response))

        usage = self.usage_tracker.track_langchain_response(
            feature,
            model_id,
            raw_response,
            prompt=prompt,
            output=parsed.model_dump_json(),
        )
        app_event(
            "llm_structured_call_completed",
            message=f"OpenAI structured response received for {feature}",
            category="llm",
            step=feature,
            model_id=model_id,
            feature=feature,
            schema=schema.__name__,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            calculated_cost_usd=usage.estimated_cost_usd,
            token_source=usage.token_source,
            openai_response_id=usage.openai_response_id,
            response_preview=text_preview(parsed.model_dump_json(), limit=1600),
        )
        return parsed


class UsageTrackedOpenAIEmbeddings(Embeddings):
    def __init__(self, *, model: str, api_key: str, usage_tracker: OpenAIUsageTracker) -> None:
        from openai import OpenAI

        self.model = model
        self.usage_tracker = usage_tracker
        self.client = OpenAI(api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for batch in self._batches(texts, size=256):
            response = self.client.embeddings.create(model=self.model, input=batch, encoding_format="float")
            usage = self.usage_tracker.track_embedding_response("embedding", self.model, response)
            app_event(
                "embedding_call_completed",
                message=f"OpenAI embeddings stored for {len(batch)} chunks",
                category="llm",
                step="embedding",
                model_id=self.model,
                input_count=len(batch),
                prompt_tokens=usage.prompt_tokens,
                total_tokens=usage.total_tokens,
                calculated_cost_usd=usage.estimated_cost_usd,
                token_source=usage.token_source,
                openai_response_id=usage.openai_response_id,
            )
            embeddings.extend(item.embedding for item in sorted(response.data, key=lambda item: item.index))
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model, input=text, encoding_format="float")
        usage = self.usage_tracker.track_embedding_response("embedding_query", self.model, response)
        app_event(
            "embedding_query_completed",
            message="OpenAI query embedding completed",
            category="llm",
            step="embedding_query",
            model_id=self.model,
            query_preview=text_preview(text, limit=500),
            prompt_tokens=usage.prompt_tokens,
            total_tokens=usage.total_tokens,
            calculated_cost_usd=usage.estimated_cost_usd,
            token_source=usage.token_source,
            openai_response_id=usage.openai_response_id,
        )
        return response.data[0].embedding

    def _batches(self, values: list[str], *, size: int) -> list[list[str]]:
        return [values[index : index + size] for index in range(0, len(values), size)]
