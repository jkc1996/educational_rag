from app.prompts.registry import PromptRegistry


def test_prompt_registry_renders_variables():
    registry = PromptRegistry()
    rendered = registry.render("rag_answer_prompt", question="What is RAG?", context="[1] notes")
    assert "What is RAG?" in rendered
    assert "[1] notes" in rendered


def test_prompt_versions_are_available():
    registry = PromptRegistry()
    assert registry.version("chunk_summary_prompt")

