# src/retriever.py

import logging

def get_retriever(vectorstore, k=5):
    """
    Returns a retriever object from a vectorstore, for RAG-style context retrieval.
    """
    logging.info({
        "event": "retriever_create_start",
        "top_k": k,
        "vectorstore_type": str(type(vectorstore))
    })
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    logging.info({
        "event": "retriever_created",
        "top_k": k,
        "retriever_type": str(type(retriever))
    })
    return retriever
