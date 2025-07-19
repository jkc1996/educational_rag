from langchain_community.vectorstores import Chroma
import logging

def create_chroma_vectorstore(
    all_semantic_chunks,
    embed_model,
    persist_directory="outputs/chroma_semantic_allpdfs_v2"
):
    """
    Stores chunks in ChromaDB vectorstore and persists it to disk.
    """
    logging.info({
        "event": "chroma_index_start",
        "chunk_count": len(all_semantic_chunks),
        "chroma_dir": persist_directory
    })
    vectorstore = Chroma.from_documents(
        all_semantic_chunks,
        embedding=embed_model,
        persist_directory=persist_directory
    )
    logging.info({
        "event": "chroma_index_done",
        "chroma_dir": persist_directory,
        "chunk_count": len(all_semantic_chunks)
    })
    return vectorstore

def load_chroma_vectorstore(
    embed_model,
    persist_directory="outputs/chroma_semantic_allpdfs_v2"
):
    """
    Loads an existing ChromaDB vectorstore from disk for retrieval.
    """
    logging.info({
        "event": "chroma_load_start",
        "chroma_dir": persist_directory
    })
    vectorstore = Chroma(
        embedding_function=embed_model,
        persist_directory=persist_directory
    )
    logging.info({
        "event": "chroma_load_done",
        "chroma_dir": persist_directory
    })
    return vectorstore
