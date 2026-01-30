from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from src.core import GEMINI_API_KEY, GROQ_API_KEY, OPENAI_API_KEY, OLLAMA_BASE_URL
import logging

def get_gemini_llm(model_name="models/gemini-2.5-flash"):
    """
    Returns a Gemini chat model for answering queries.
    """
    logging.info({
        "event": "llm_load_start",
        "llm_type": "gemini",
        "model_name": model_name
    })
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=GEMINI_API_KEY
    )
    logging.info({
        "event": "llm_load_done",
        "llm_type": "gemini",
        "model_name": model_name
    })
    return llm

def get_groq_llm(model_name="llama-3.1-8b-instant"):
    """
    Returns a Groq chat model for answering queries.
    """
    logging.info({
        "event": "llm_load_start",
        "llm_type": "groq",
        "model_name": model_name
    })
    llm = ChatGroq(
        model_name=model_name,
        api_key=GROQ_API_KEY
    )
    logging.info({
        "event": "llm_load_done",
        "llm_type": "groq",
        "model_name": model_name
    })
    return llm

def get_ollama_llm(model_name="edusage"):
    """
    Returns an Ollama chat model for answering queries.
    """
    logging.info({
        "event": "llm_load_start",
        "llm_type": "ollama",
        "model_name": model_name
    })
    llm = ChatOllama(
        model=model_name,
        base_url=OLLAMA_BASE_URL
    )
    logging.info({
        "event": "llm_load_done",
        "llm_type": "ollama",
        "model_name": model_name
    })
    return llm

def get_openai_llm(model_name="gpt-4o-mini"):
    """
    Returns an OpenAI chat model for answering queries.
    """
    logging.info({
        "event": "llm_load_start",
        "llm_type": "openai",
        "model_name": model_name
    })

    llm = ChatOpenAI(
        model=model_name,
        api_key=OPENAI_API_KEY,
        temperature=0
    )

    logging.info({
        "event": "llm_load_done",
        "llm_type": "openai",
        "model_name": model_name
    })
    return llm

