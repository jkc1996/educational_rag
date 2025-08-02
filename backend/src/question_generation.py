import os
import hashlib
import pickle
from src.vectorstore import load_chroma_vectorstore
from src.embeddings import get_fastembed_embedding
from src.llms import get_groq_llm, get_gemini_llm, get_ollama_llm
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import json
from langchain_core.prompts import ChatPromptTemplate
from .question_schema import QuestionPaper
from google import genai

# ---- Simple File Cache for Summaries (cache/summary_*.pkl) ----
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def make_summary_cache_key(subject, filenames, llm_choice, extra_context):
    hasher = hashlib.sha256()
    hasher.update(subject.encode("utf-8"))
    for fname in sorted(filenames):
        hasher.update(fname.encode("utf-8"))
    hasher.update(llm_choice.encode("utf-8"))
    hasher.update(extra_context.strip().encode("utf-8"))
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

# --------------------- ChromaDB Chunk Fetching --------------------------
def get_chunks_by_filenames(vectorstore, filenames):
    all_docs = vectorstore._collection.get(include=['documents', 'metadatas'])
    matched_chunks = []
    filenames_set = set(os.path.basename(f) for f in filenames)
    print("DEBUG: Normalized Filenames to match:", filenames_set)
    for doc, meta in zip(all_docs['documents'], all_docs['metadatas']):
        source_pdf = meta.get('source_pdf')
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

# --------------------- LLM Summarization Logic --------------------------
def deep_summarize_content(long_text, llm_summarize_func, llm_choice="groq", max_chunk_words=1200, recursion_level=1, max_recursion=2):
    import time
    start_time = time.time()
    print(f"DEBUG: Summarizing at level {recursion_level}, total words: {len(long_text.split())}")

    def split_text_blocks(text, max_words):
        words = text.split()
        blocks = []
        for i in range(0, len(words), max_words):
            blocks.append(' '.join(words[i:i+max_words]))
        return blocks

    blocks = split_text_blocks(long_text, max_chunk_words)
    print(f"DEBUG: {len(blocks)} blocks at level {recursion_level}")

    # --- Parallelize block summarization ---
    summaries = [None] * len(blocks)
    def summarize_block(idx, block):
        if block.strip():
            print(f"DEBUG: Summarizing block {idx+1}/{len(blocks)} ({len(block.split())} words)")
            return llm_summarize_func(block, llm_choice=llm_choice).strip()
        return ""

    with ThreadPoolExecutor(max_workers=min(2, len(blocks))) as executor:
        futures = {executor.submit(summarize_block, idx, block): idx for idx, block in enumerate(blocks)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                summaries[idx] = future.result()
            except Exception as e:
                print(f"Error in summarizing block {idx+1}: {e}")
                summaries[idx] = ""

    combined = "\n".join(summaries)
    print(f"DEBUG: After level {recursion_level}, summary words: {len(combined.split())}, time: {int(time.time()-start_time)}s")

    if recursion_level < max_recursion and len(combined.split()) > max_chunk_words:
        print(f"DEBUG: Recursing to summarization level {recursion_level+1}")
        return deep_summarize_content(combined, llm_summarize_func, llm_choice=llm_choice,
                                      max_chunk_words=max_chunk_words, recursion_level=recursion_level+1, max_recursion=max_recursion)
    return combined

# --------- LLM Summarization Prompt (User-Selectable LLM) ----------
def llm_summarize_func(text, llm_choice="groq"):
    prompt = f"""
Carefully read the following academic content and produce a **deep, comprehensive summary**:
- Capture all key concepts, definitions, and explanations.
- Organize using headings if the content contains chapters or sections.
- The summary should be detailed enough that a professor could create exam questions from it.
- Do NOT include any section or block named "Exam Questions", "Examination Questions", or similar. Omit any list of exam questions found in the text.

[START CONTENT]
{text}
[END CONTENT]
"""
    if llm_choice == "groq":
        llm = get_groq_llm()
    elif llm_choice == "gemini":
        llm = get_gemini_llm()
    elif llm_choice == "ollama":
        llm = get_ollama_llm()
    else:
        llm = get_groq_llm()  # fallback default

    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)

def filter_summary(summary):
    import re
    blocks = summary.split("\n\n")
    filtered_blocks = [b for b in blocks if not re.search(r'\bexam(ination)? questions\b', b, re.IGNORECASE)]
    return "\n\n".join(filtered_blocks)

# --------------------- Main Orchestration Function (with caching) --------------------------

def summarize_selected_pdfs(subject, selected_filenames, llm_choice="groq", extra_context=""):
    """
    Full pipeline: Fetches chunks, returns a deep summary.
    Uses cache for speed, and always ensures summary < max_final_words.
    """
    cache_key = make_summary_cache_key(subject, selected_filenames, llm_choice, extra_context)
    cached = cache_summary_load(cache_key)
    if cached:
        return cached

    long_text = fetch_chunks_for_question_generation(subject, selected_filenames)
    summary = deep_summarize_content(long_text, llm_summarize_func, llm_choice=llm_choice, max_chunk_words=1200)
    summary = filter_summary(summary)

    # === FINAL COMPRESSION (MUST BE < 1800 WORDS for QA LLM!) ===
    max_final_words = 1800
    if len(summary.split()) > max_final_words:
        print(f"DEBUG: Final summary still too long ({len(summary.split())} words), compressing one more time")
        summary = llm_summarize_func(' '.join(summary.split()[:max_final_words*2]), llm_choice=llm_choice)[:max_final_words*8]  # truncate string after summarizing

    if summary and summary.strip():
        cache_summary_save(cache_key, summary)
    else:
        print("Did NOT cache empty summary.")
    return summary

# --------------------- Question Generation Step -------------------

from langchain_core.prompts import ChatPromptTemplate
from src.question_schema import QuestionPaper  # your Pydantic schema
import json

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
"""
    user_prompt = f"""Generate {config['total_questions']} questions. Difficulty: {config.get('difficulty', 'medium')}
Distribute as:
- One-liner: {config.get('distribution', {}).get('one_liner',0)}
- True/False: {config.get('distribution', {}).get('true_false',0)}
- Fill-in-the-blank: {config.get('distribution', {}).get('fill_blank',0)}
- Multiple choice: {config.get('distribution', {}).get('multiple_choice',0)}
- Descriptive: {config.get('distribution', {}).get('descriptive',0)}

{"Additional instructions: " + extra_context if extra_context else ""}

[SUMMARY]
{summary}
"""
    if llm_choice == "groq":
        llm = get_groq_llm()
        # Strict structured output via LangChain and Pydantic
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
        # Use Google Gemini native SDK for strict schema-based output
        client = genai.Client()  # Ensure you have already authenticated
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",  # or "gemini-1.5-pro"
                contents=user_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": QuestionPaper,
                }
            )
            # Print JSON string and also return it (for frontend)
            print("Strict validated JSON (Gemini):", response.text)
            return response.text
        except Exception as e:
            print(f"Gemini LLM failed to produce valid JSON: {e}")
            return json.dumps({"error": "Gemini LLM did not produce valid structured output. " + str(e)})

    else:
        raise ValueError("Invalid LLM choice: must be 'groq' or 'gemini'.")

