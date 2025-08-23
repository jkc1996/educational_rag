import os
from dotenv import load_dotenv
from llama_parse import LlamaParse, ResultType

load_dotenv()  # Loads from .env file

def load_llamaparse_nodes(pdf_path, parsing_instruction=None, result_type="markdown"):
    api_key = os.getenv("LLAMA_PARSE_API_KEY")
    if not api_key:
        raise RuntimeError("LLAMA_PARSE_API_KEY not found in environment or .env")

    # keep your instruction unchanged
    parsing_instruction = parsing_instruction or """The provided document is a Natural lngage processing topic related.
        It contains tables too.
        Try to be precise while answering the questions"""

    parser = LlamaParse(
        api_key=api_key,
        result_type=ResultType.TXT if result_type == "txt" else ResultType.MD,
        parsing_instruction=parsing_instruction,
        max_timeout=5000,
        verbose=True,
        # IMPORTANT: inject explicit page markers we can parse
        page_separator="\n=== PAGE {pageNumber} ===\n",
        # Optional:
        # hide_headers=True, hide_footers=True,
    )
    return parser.load_data(pdf_path)  # returns list of Node objects

def save_llamaparse_cache(nodes, cache_file):
    import joblib
    joblib.dump(nodes, cache_file)

def load_llamaparse_cache(cache_file):
    import joblib
    return joblib.load(cache_file)
