# src/retriever.py

from src.logger import get_logger

logger = get_logger()

def get_retriever(vectorstore, k=5):
    """
    Returns a retriever object from a vectorstore, for RAG-style context retrieval.
    """
    logger.info(f"Creating retriever with top {k} results...")
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    logger.info("Retriever created.")
    return retriever
