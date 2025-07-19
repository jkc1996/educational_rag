from src.loaders import load_pdf_pages
from src.chunkers import run_semantic_chunking
from src.embeddings import get_fastembed_embedding
from src.vectorstore import create_chroma_vectorstore, load_chroma_vectorstore
from src.llms import get_gemini_llm, get_groq_llm, get_ollama_llm
from src.retriever import get_retriever
from src.chain import get_semantic_rag_chain
import logging

def ingest_pdfs_to_chroma(
    pdf_files,
    chroma_persist_dir,
    chunk_size=2000,
    chunk_overlap=50,
):
    """
    Step 1: Chunk, embed, and store PDFs in ChromaDB.
    Does NOT load LLM or retriever.
    """
    logging.info({
        "event": "chroma_ingest_start",
        "pdf_files": pdf_files,
        "chroma_dir": chroma_persist_dir,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap
    })

    embed_model = get_fastembed_embedding()

    from langchain.text_splitter import RecursiveCharacterTextSplitter
    pre_chunker = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    all_semantic_chunks = run_semantic_chunking(pdf_files, pre_chunker, embed_model)

    # Store in Chroma
    vectorstore = create_chroma_vectorstore(
        all_semantic_chunks, embed_model, persist_directory=chroma_persist_dir
    )

    logging.info({
        "event": "chroma_ingest_done",
        "chroma_dir": chroma_persist_dir,
        "total_chunks": len(all_semantic_chunks)
    })
    return True

def get_rag_chain(
    chroma_persist_dir,
    top_k=5,
    llm_backend="groq"
):
    """
    Step 2: For a given subject, load embeddings from Chroma,
    create retriever and LLM chain, return ready to answer.
    """
    logging.info({
        "event": "rag_chain_init_start",
        "chroma_dir": chroma_persist_dir,
        "llm_backend": llm_backend,
        "top_k": top_k
    })

    embed_model = get_fastembed_embedding()
    vectorstore = load_chroma_vectorstore(embed_model, persist_directory=chroma_persist_dir)
    retriever = get_retriever(vectorstore, k=top_k)

    if llm_backend == "groq":
        chat_model = get_groq_llm()
        logging.info({
            "event": "llm_selected",
            "llm_type": "groq"
        })
    elif llm_backend == "ollama":
        chat_model = get_ollama_llm()
        logging.info({
            "event": "llm_selected",
            "llm_type": "ollama"
        })
    else:
        chat_model = get_gemini_llm()
        logging.info({
            "event": "llm_selected",
            "llm_type": "gemini"
        })

    semantic_rag_chain = get_semantic_rag_chain(retriever, chat_model)
    logging.info({
        "event": "rag_chain_ready",
        "chroma_dir": chroma_persist_dir,
        "llm_backend": llm_backend
    })

    return semantic_rag_chain
