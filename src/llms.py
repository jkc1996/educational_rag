# from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_ollama import ChatOllama
# from src.config import GROQ_API_KEY, GEMINI_API_KEY, OLLAMA_BASE_URL

# def get_groq_llm():
#     return ChatGroq(model_name="llama3-8b-8192", api_key=GROQ_API_KEY)

# def get_gemini_llm():
#     return ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=GEMINI_API_KEY)

# def get_ollama_llm():
#     return ChatOllama(model="edusage", base_url=OLLAMA_BASE_URL)


# src/llms.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from src.config import GEMINI_API_KEY, GROQ_API_KEY
from src.logger import get_logger

logger = get_logger()

def get_gemini_llm(model_name="gemini-1.5-flash-latest"):
    """
    Returns a Gemini chat model for answering queries.
    """
    logger.info(f"Loading Gemini chat model: {model_name}")
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GEMINI_API_KEY
    )
    logger.info("Gemini chat model loaded.")
    return llm

def get_groq_llm(model_name="llama3-8b-8192"):
    """
    Returns a Groq chat model for answering queries.
    """
    logger.info(f"Loading Groq chat model: {model_name}")
    llm = ChatGroq(
        model_name=model_name,
        api_key=GROQ_API_KEY
    )
    logger.info("Groq chat model loaded.")
    return llm