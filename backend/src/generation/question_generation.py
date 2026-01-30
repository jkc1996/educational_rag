import os
import hashlib
import pickle
import json
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.generation.schema.question import QuestionPaper
from src.ingestion import load_chroma_vectorstore
from src.ingestion import get_fastembed_embedding
from src.generation import get_groq_llm, get_gemini_llm, get_ollama_llm

from langchain_core.prompts import ChatPromptTemplate
from google import genai

# ======================================================
# Simple File Cache for Summaries (cache/summary_*.pkl)
# ======================================================
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def make_summary_cache_key(subject, filenames, llm_choice, extra_context):
    hasher = hashlib.sha256()
    hasher.update(subject.encode("utf-8"))
    for fname in sorted(filenames):
        hasher.update(fname.encode("utf-8"))
    hasher.update(llm_choice.encode("utf-8"))
    hasher.update((extra_context or "").strip().encode("utf-8"))
    return hasher.hexdigest()

def cache_summary_load(cache_key):
    path = os.path.join(CACHE_DIR, f"summary_{cache_key}.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            print(f"Loaded summary from cache: {path}")
            return pickle.load(f)
    return None

def cache_summary_save(cache_key, summary):
    path = os.path.join(CACHE_DIR, f"summary_{cache_key}.pkl")
    with open(path, "wb") as f:
        pickle.dump(summary, f)
    print(f"Saved summary to cache: {path}")

# ======================================================
# NEW: Gemini per-recursion call budget (ONLY ADDITION)
# ======================================================
class GeminiRecursionBudget:
    def __init__(self, limits):
        """
        limits example: {1: 5, 2: 5}
        """
        self.limits = limits
        self.used = {lvl: 0 for lvl in limits}

    def can_call(self, level):
        return self.used.get(level, 0) < self.limits.get(level, 0)

    def record_call(self, level):
        self.used[level] += 1

    def has_level(self, level):
        return level in self.limits

# ======================================
# ChromaDB Chunk Fetching (by filenames)
# ======================================
def get_chunks_by_filenames(vectorstore, filenames):
    all_docs = vectorstore._collection.get(include=["documents", "metadatas"])
    matched_chunks = []
    filenames_set = set(os.path.basename(f) for f in filenames)
    print("DEBUG: Normalized Filenames to match:", filenames_set)

    for doc, meta in zip(all_docs.get("documents", []), all_docs.get("metadatas", [])):
        source_pdf = meta.get("source_pdf")
        if source_pdf:
            base_source = os.path.basename(source_pdf)
            if base_source in filenames_set:
                matched_chunks.append(doc)

    print("DEBUG: Matched chunks:", len(matched_chunks))
    return matched_chunks

def fetch_chunks_for_question_generation(subject, selected_filenames):
    chroma_dir = f"outputs/chroma_{subject.replace(' ', '_').lower()}"
    embed_model = get_fastembed_embedding()
    vectorstore = load_chroma_vectorstore(embed_model, persist_directory=chroma_dir)
    chunks = get_chunks_by_filenames(vectorstore, selected_filenames)
    return "\n".join(chunks)

# ======================================================
# Token Budget Helpers
# ======================================================
def estimate_tokens(text: str) -> int:
    return max(len(text) // 4, int(len(text.split()) * 0.8))

def clip_to_token_budget(text: str, max_input_tokens: int) -> str:
    max_chars = max_input_tokens * 4
    return text[:max_chars] if len(text) > max_chars else text

MAX_INPUT_TOKENS_MAP = {
    "groq": 5000,
    "gemini": 12000,
    "ollama": 3500,
}

def _pick_budget(llm_choice: str) -> int:
    return MAX_INPUT_TOKENS_MAP.get(llm_choice, 5000)

# ======================================================
# Retry helper
# ======================================================
def _with_retries(callable_fn, *, retries=3, base_sleep=1.5, jitter=0.6):
    for attempt in range(1, retries + 1):
        try:
            return callable_fn()
        except Exception as e:
            if attempt == retries:
                raise
            sleep = base_sleep * (2 ** (attempt - 1)) + random.uniform(0, jitter)
            print(f"Retry {attempt}/{retries} after error: {e}. Sleeping {sleep:.1f}s")
            time.sleep(sleep)

# =========================================
# LLM Summarization (UNCHANGED)
# =========================================
def llm_summarize_func(text, llm_choice="groq", max_input_tokens=None):
    max_input_tokens = max_input_tokens or _pick_budget(llm_choice)

    prompt_header = (
        "Carefully read the following academic content and produce a **deep, comprehensive summary**:\n"
        "- Capture all key concepts, definitions, and explanations.\n"
        "- Organize using headings if the content contains chapters or sections.\n"
        "- The summary should be detailed enough that a professor could create exam questions from it.\n"
        "- Do NOT include any section or block named \"Exam Questions\", \"Examination Questions\", or similar. "
        "Omit any list of exam questions found in the text.\n\n"
        "[START CONTENT]\n"
    )
    prompt_footer = "\n[END CONTENT]\n"

    total_budget = max_input_tokens - 600
    content_budget = total_budget - estimate_tokens(prompt_header + prompt_footer)
    content_budget = max(content_budget, 800)

    safe_text = clip_to_token_budget(text, content_budget)
    prompt = f"{prompt_header}{safe_text}{prompt_footer}"

    print(f"DEBUG: llm_summarize_func -> est tokens: {estimate_tokens(prompt)}; model={llm_choice}")

    if llm_choice == "groq":
        llm = get_groq_llm()
        retries = 4
    elif llm_choice == "gemini":
        llm = get_gemini_llm()
        retries = 3
    elif llm_choice == "ollama":
        llm = get_ollama_llm()
        retries = 3
    else:
        llm = get_groq_llm()
        retries = 4

    def _invoke():
        return llm.invoke(prompt)

    resp = _with_retries(_invoke, retries=retries)
    return resp.content if hasattr(resp, "content") else str(resp)

def filter_summary(summary: str) -> str:
    blocks = summary.split("\n\n")
    filtered_blocks = [b for b in blocks if not re.search(r"\bexam(ination)? questions\b", b, re.IGNORECASE)]
    return "\n\n".join(filtered_blocks)

# ====================================================
# Recursive Summarization 
# ====================================================
def deep_summarize_content(
    long_text,
    llm_summarize_func_ref,
    llm_choice="groq",
    max_chunk_words=900,
    recursion_level=1,
    max_recursion=2,
    parallelize=True,
    gemini_budget: GeminiRecursionBudget | None = None
):
    if not (long_text and long_text.strip()):
        return ""

    print(f"DEBUG: Summarizing at level {recursion_level}")

    words = long_text.split()
    blocks = [' '.join(words[i:i + max_chunk_words]) for i in range(0, len(words), max_chunk_words)]
    summaries = [None] * len(blocks)

    def summarize_block(idx, block):
        if block.strip():
            print(f"DEBUG: Summarizing block {idx + 1}/{len(blocks)}")

            # Gemini call limit 
            if llm_choice == "gemini" and gemini_budget:
                if not gemini_budget.can_call(recursion_level):
                    print(f"INFO: Gemini budget exhausted at level {recursion_level}")
                    return " ".join(block.split()[:150])
                gemini_budget.record_call(recursion_level)

            out = llm_summarize_func_ref(block, llm_choice=llm_choice).strip()

            if llm_choice == "groq":
                time.sleep(0.7)
            return out
        return ""

    if llm_choice == "groq":
        parallelize = False

    if parallelize and len(blocks) > 1:
        with ThreadPoolExecutor(max_workers=min(2, len(blocks))) as executor:
            futures = {executor.submit(summarize_block, i, b): i for i, b in enumerate(blocks)}
            for future in as_completed(futures):
                i = futures[future]
                try:
                    summaries[i] = future.result()
                except Exception:
                    summaries[i] = ""
    else:
        for i, b in enumerate(blocks):
            try:
                summaries[i] = summarize_block(i, b)
            except Exception:
                summaries[i] = ""

    combined = "\n".join(summaries)

    # Stop Gemini recursion beyond level 2
    if llm_choice == "gemini" and gemini_budget and not gemini_budget.has_level(recursion_level + 1):
        return combined

    if recursion_level < max_recursion and len(combined.split()) > max_chunk_words:
        return deep_summarize_content(
            combined,
            llm_summarize_func_ref,
            llm_choice=llm_choice,
            max_chunk_words=max_chunk_words,
            recursion_level=recursion_level + 1,
            max_recursion=max_recursion,
            parallelize=parallelize,
            gemini_budget=gemini_budget
        )

    return combined

# =====================================================
# Main Orchestration
# =====================================================
def summarize_selected_pdfs(subject, selected_filenames, llm_choice="groq", extra_context=""):
    cache_key = make_summary_cache_key(subject, selected_filenames, llm_choice, extra_context)
    cached = cache_summary_load(cache_key)
    if cached:
        return cached

    long_text = fetch_chunks_for_question_generation(subject, selected_filenames)
    if not long_text.strip():
        return ""

    gemini_budget = None
    if llm_choice == "gemini":
        gemini_budget = GeminiRecursionBudget({1: 5, 2: 5})

    summary = deep_summarize_content(
        long_text,
        llm_summarize_func,
        llm_choice=llm_choice,
        max_chunk_words=900,
        recursion_level=1,
        max_recursion=2,
        gemini_budget=gemini_budget
    )

    summary = filter_summary(summary)

    if summary.strip():
        cache_summary_save(cache_key, summary)

    return summary

# ======================================
# Question Generation (UNCHANGED)
# ======================================
def generate_question_paper(summary, config, llm_choice="groq", extra_context=""):
    system_message = """
You are an expert academic exam generator.
Your task is to generate a set of exam questions and answers based only on the following summary. 
Return ONLY a JSON object that strictly matches the provided schema. Do not add any extra text or explanation.
"""
    user_prompt = f"""Generate {config['total_questions']} questions. Difficulty: {config.get('difficulty', 'medium')}
[SUMMARY]
{summary}
"""

    if llm_choice == "groq":
        llm = get_groq_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}")
        ])
        structured_llm = llm.with_structured_output(QuestionPaper, method="json_mode")
        return (prompt | structured_llm).invoke({"input": user_prompt}).model_dump_json(indent=2)

    elif llm_choice == "gemini":
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": QuestionPaper,
            }
        )
        return response.text

    else:
        raise ValueError("Invalid LLM choice")
