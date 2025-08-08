import os
import hashlib
import pickle
import json
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.vectorstore import load_chroma_vectorstore
from src.embeddings import get_fastembed_embedding
from src.llms import get_groq_llm, get_gemini_llm, get_ollama_llm

from langchain_core.prompts import ChatPromptTemplate
from src.question_schema import QuestionPaper  # Pydantic schema for strict JSON
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

# ======================================
# ChromaDB Chunk Fetching (by filenames)
# ======================================
def get_chunks_by_filenames(vectorstore, filenames):
    """
    Returns raw document strings whose metadata source_pdf basename matches any of `filenames`.
    """
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
# Token Budget Helpers (rough but safe, model-agnostic)
# ======================================================
def estimate_tokens(text: str) -> int:
    # Conservative heuristic: max of 4 chars/token and 0.8 tokens/word
    return max(len(text) // 4, int(len(text.split()) * 0.8))

def clip_to_token_budget(text: str, max_input_tokens: int) -> str:
    # Fast clipping by chars (~4 chars per token)
    max_chars = max_input_tokens * 4
    if len(text) > max_chars:
        return text[:max_chars]
    return text

# Per‑model input token budgets (tune as needed)
MAX_INPUT_TOKENS_MAP = {
    "groq": 5000,    # llama3-8b-8192 (leave headroom)
    "gemini": 12000, # generous, Gemini usually allows more
    "ollama": 3500,  # conservative default for local models
}

def _pick_budget(llm_choice: str) -> int:
    return MAX_INPUT_TOKENS_MAP.get(llm_choice, 5000)

# ======================================================
# Retry helper (exponential backoff + jitter)
# ======================================================
def _with_retries(callable_fn, *, retries=3, base_sleep=1.5, jitter=0.6):
    """
    Exponential backoff + jitter for transient API/network hiccups.
    Raises after final attempt.
    """
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
# LLM Summarization (safe prompt + clipping)
# =========================================
def llm_summarize_func(text, llm_choice="groq", max_input_tokens=None):
    """
    Summarize `text` with a hard cap on input size and retry on transient failures.
    """
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

    # Reserve ~600 tokens for system/overhead/formatting.
    total_budget = max_input_tokens - 600
    # Budget for user's content inside the wrapper
    content_budget = total_budget - estimate_tokens(prompt_header + prompt_footer)
    content_budget = max(content_budget, 800)  # never drop too low

    safe_text = clip_to_token_budget(text, content_budget)
    prompt = f"{prompt_header}{safe_text}{prompt_footer}"

    # Diagnostics
    print(f"DEBUG: llm_summarize_func -> est tokens (prompt+content): {estimate_tokens(prompt)}; model={llm_choice}")

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
    # Remove any blocks that look like exam questions sections
    blocks = summary.split("\n\n")
    filtered_blocks = [b for b in blocks if not re.search(r"\bexam(ination)? questions\b", b, re.IGNORECASE)]
    return "\n\n".join(filtered_blocks)

# ====================================================
# Recursive Summarization with conservative parallelism
# ====================================================
def deep_summarize_content(
    long_text,
    llm_summarize_func_ref,
    llm_choice="groq",
    max_chunk_words=900,     # smaller default blocks for safety
    recursion_level=1,
    max_recursion=2,
    parallelize=True
):
    if not (long_text and long_text.strip()):
        return ""

    start_time = time.time()
    total_words = len(long_text.split())
    print(f"DEBUG: Summarizing at level {recursion_level}, total words: {total_words}")

    def split_text_blocks(text, max_words):
        words = text.split()
        return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

    blocks = split_text_blocks(long_text, max_chunk_words)
    print(f"DEBUG: {len(blocks)} blocks at level {recursion_level}")

    summaries = [None] * len(blocks)

    def summarize_block(idx, block):
        if block.strip():
            print(f"DEBUG: Summarizing block {idx + 1}/{len(blocks)} ({len(block.split())} words)")
            out = llm_summarize_func_ref(block, llm_choice=llm_choice).strip()
            # tiny cooldown for Groq to avoid spikes
            if llm_choice == "groq":
                time.sleep(0.7)
            return out
        return ""

    # For Groq, be conservative: avoid parallel spikes
    if llm_choice == "groq":
        parallelize = False

    if parallelize and len(blocks) > 1:
        with ThreadPoolExecutor(max_workers=min(2, len(blocks))) as executor:
            futures = {executor.submit(summarize_block, idx, block): idx for idx, block in enumerate(blocks)}
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    summaries[idx] = future.result()
                except Exception as e:
                    print(f"Error in summarizing block {idx + 1}: {e}")
                    summaries[idx] = ""
    else:
        for idx, block in enumerate(blocks):
            try:
                summaries[idx] = summarize_block(idx, block)
            except Exception as e:
                print(f"Error in summarizing block {idx + 1}: {e}")
                summaries[idx] = ""

    # If all failed, fallback to truncated input instead of empty
    if not any(summaries) or not "\n".join([s or "" for s in summaries]).strip():
        print("DEBUG: All blocks failed at this level; returning truncated input to avoid empty summary.")
        words = long_text.split()
        combined = " ".join(words[:max_chunk_words])
    else:
        combined = "\n".join(summaries)

    elapsed = int(time.time() - start_time)
    print(f"DEBUG: After level {recursion_level}, summary words: {len(combined.split())}, time: {elapsed}s")

    # Recurse if still large
    if recursion_level < max_recursion and len(combined.split()) > max_chunk_words:
        print(f"DEBUG: Recursing to summarization level {recursion_level + 1}")
        return deep_summarize_content(
            combined,
            llm_summarize_func_ref,
            llm_choice=llm_choice,
            max_chunk_words=max_chunk_words,
            recursion_level=recursion_level + 1,
            max_recursion=max_recursion,
            parallelize=parallelize
        )
    return combined

# =====================================================
# Main Orchestration (with cache + safe final compression)
# =====================================================
def summarize_selected_pdfs(subject, selected_filenames, llm_choice="groq", extra_context=""):
    """
    Full pipeline: Fetch chunks, deep summarize with token-safe calls, cache result.
    Ensures the final summary is <= max_final_words (by re-summarizing safely).
    """
    cache_key = make_summary_cache_key(subject, selected_filenames, llm_choice, extra_context)
    cached = cache_summary_load(cache_key)
    if cached:
        return cached

    long_text = fetch_chunks_for_question_generation(subject, selected_filenames)
    if not (long_text and long_text.strip()):
        print("DEBUG: No chunks found for the selected files; returning empty summary.")
        return ""

    # First pass summary
    summary = deep_summarize_content(
        long_text,
        llm_summarize_func,
        llm_choice=llm_choice,
        max_chunk_words=900,   # smaller blocks for Groq safety
        recursion_level=1,
        max_recursion=2
    )
    summary = filter_summary(summary)

    # === FINAL COMPRESSION (MUST BE < 1800 WORDS for QA LLM!) ===
    max_final_words = 1800
    if len(summary.split()) > max_final_words:
        print(f"DEBUG: Final summary too long ({len(summary.split())} words). Compressing safely...")
        compressed = deep_summarize_content(
            summary,
            llm_summarize_func,
            llm_choice=llm_choice,
            max_chunk_words=800,    # a bit smaller for the last pass
            recursion_level=1,
            max_recursion=2
        )
        # If compression failed (all connection errors), preserve previous summary (trim)
        if not compressed.strip():
            print("DEBUG: Compression failed; falling back to trimmed previous summary.")
            words = summary.split()
            summary = " ".join(words[:max_final_words])
        else:
            words = compressed.split()
            summary = " ".join(words[:max_final_words])

    if summary and summary.strip():
        cache_summary_save(cache_key, summary)
    else:
        print("Did NOT cache empty summary.")

    return summary

# ======================================
# Question Generation (strict JSON output)
# ======================================
def generate_question_paper(summary, config, llm_choice="groq", extra_context=""):
    system_message = """
You are an expert academic exam generator.
Your task is to generate a set of exam questions and answers based only on the following summary. 
Return ONLY a JSON object that strictly matches the provided schema. Do not add any extra text or explanation.

Schema:
{{
  "questions": [
    {{
      "type": "one_liner" | "true_false" | "fill_blank" | "multiple_choice" | "descriptive",
      "question": string,
      "options": string[] | null,
      "answer": string
    }}
  ]
}}

Notes:
- All fields must be filled.
- For "answer", always provide the answer as a **string** (e.g. "True", "False", "23", "Gradient Descent").
- Never return answer as a boolean (true/false); always as a string.
"""
    user_prompt = f"""Generate {config['total_questions']} questions. Difficulty: {config.get('difficulty', 'medium')}
Distribute as:
- One-liner: {config.get('distribution', {}).get('one_liner', 0)}
- True/False: {config.get('distribution', {}).get('true_false', 0)}
- Fill-in-the-blank: {config.get('distribution', {}).get('fill_blank', 0)}
- Multiple choice: {config.get('distribution', {}).get('multiple_choice', 0)}
- Descriptive: {config.get('distribution', {}).get('descriptive', 0)}

{"Additional instructions: " + extra_context if extra_context else ""}

[SUMMARY]
{summary}
"""

    if llm_choice == "groq":
        # LangChain structured output to Pydantic
        llm = get_groq_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}")
        ])
        structured_llm = llm.with_structured_output(QuestionPaper, method="json_mode")
        full_chain = prompt | structured_llm

        try:
            result = full_chain.invoke({"input": user_prompt})
            print("Strict validated JSON (Groq):", result.model_dump_json(indent=2))
            return result.model_dump_json(indent=2)
        except Exception as e:
            print(f"Groq LLM failed to produce valid JSON: {e}")
            return json.dumps({"error": "Groq LLM did not produce valid structured output. " + str(e)})

    elif llm_choice == "gemini":
        # Google Gemini native SDK with schema enforcement
        client = genai.Client()  # Ensure authentication is configured
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",  # or "gemini-1.5-pro"
                contents=user_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": QuestionPaper,
                }
            )
            print("Strict validated JSON (Gemini):", response.text)
            return response.text
        except Exception as e:
            print(f"Gemini LLM failed to produce valid JSON: {e}")
            return json.dumps({"error": "Gemini LLM did not produce valid structured output. " + str(e)})

    else:
        raise ValueError("Invalid LLM choice: must be 'groq' or 'gemini'.")
