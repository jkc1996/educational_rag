# src/embeddings.py

from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import logging

def get_fastembed_embedding(model_name="BAAI/bge-base-en-v1.5"):
    """
    Loads and returns a FastEmbedEmbeddings model.
    """
    logging.info({
        "event": "embedding_model_load_start",
        "model_name": model_name
    })
    embed_model = FastEmbedEmbeddings(model_name=model_name)
    logging.info({
        "event": "embedding_model_load_done",
        "model_name": model_name
    })
    return embed_model
