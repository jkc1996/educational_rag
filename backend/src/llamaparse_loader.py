import os
from dotenv import load_dotenv
from llama_parse import LlamaParse, ResultType

load_dotenv()  # Loads from .env file

def load_llamaparse_nodes(pdf_path, parsing_instruction=None, result_type="markdown"):
    api_key = os.getenv("LLAMA_PARSE_API_KEY")
    if not api_key:
        raise RuntimeError("LLAMA_PARSE_API_KEY not found in environment or .env")
    parsingInstructionUber10k = """The provided document is a quarterly report filed by Uber Technologies,
        Inc. with the Securities and Exchange Commission (SEC).
        This form provides detailed financial information about the company's performance for a specific quarter.
        It includes unaudited financial statements, management discussion and analysis, and other relevant disclosures required by the SEC.
        It contains many tables.
        Try to be precise while answering the questions"""
    parser = LlamaParse(
        api_key=api_key,
        result_type=ResultType.TXT if result_type == "txt" else ResultType.MD,
        parsing_instruction=parsingInstructionUber10k,
        max_timeout=5000,
        verbose=True,
    )
    return parser.load_data(pdf_path)  # returns list of Node objects

def save_llamaparse_cache(nodes, cache_file):
    import joblib
    joblib.dump(nodes, cache_file)

def load_llamaparse_cache(cache_file):
    import joblib
    return joblib.load(cache_file)
