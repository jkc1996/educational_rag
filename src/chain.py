# src/chain.py

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.prompts import get_rag_prompt
from src.logger import get_logger

logger = get_logger()

def get_semantic_rag_chain(retriever, chat_model):
    rag_prompt = get_rag_prompt()
    logger.info("Building semantic RAG chain...")
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | chat_model
        | StrOutputParser()
    )
    logger.info("Semantic RAG chain built.")
    return chain
