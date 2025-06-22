# src/vectorstore.py

from langchain_community.vectorstores import Chroma
from src.logger import get_logger

logger = get_logger()

def create_chroma_vectorstore(
    all_semantic_chunks,
    embed_model,
    persist_directory="outputs/chroma_semantic_allpdfs_v2"
):
    """
    Stores chunks in ChromaDB vectorstore and persists it to disk.
    """
    logger.info(f"Indexing {len(all_semantic_chunks)} semantic chunks in Chroma at '{persist_directory}' ...")
    vectorstore = Chroma.from_documents(
        all_semantic_chunks,
        embedding=embed_model,
        persist_directory=persist_directory
    )
    logger.info("Done! All PDFs indexed with semantic chunking.")
    return vectorstore
