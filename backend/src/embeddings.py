# src/embeddings.py

from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from src.logger import get_logger

logger = get_logger()

def get_fastembed_embedding(model_name="BAAI/bge-base-en-v1.5"):
    """
    Loads and returns a FastEmbedEmbeddings model.
    """
    logger.info(f"Loading FastEmbedEmbeddings model: {model_name}")
    embed_model = FastEmbedEmbeddings(model_name=model_name)
    logger.info("Embedding model loaded.")
    return embed_model
