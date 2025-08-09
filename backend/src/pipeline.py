from src.loaders import load_pdf_pages
from src.chunkers import run_semantic_chunking
from src.embeddings import get_fastembed_embedding
from src.vectorstore import create_chroma_vectorstore, load_chroma_vectorstore
from src.llms import get_gemini_llm, get_groq_llm, get_ollama_llm
from src.retriever import get_retriever, FeedbackAwareRetriever  # <-- NEW
from src.chain import get_semantic_rag_chain
import logging

def ingest_pdfs_to_chroma(
    pdf_files,
    chroma_persist_dir,
    chunk_size=2000,
    chunk_overlap=100,
    use_llamaparse=False,
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
        "chunk_overlap": chunk_overlap,
        "use_llamaparse": use_llamaparse
    })

    embed_model = get_fastembed_embedding()

    if use_llamaparse:
        from src.llamaparse_loader import load_llamaparse_nodes
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document
        from hashlib import md5

        all_semantic_chunks = []
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        for pdf in pdf_files:
            nodes = load_llamaparse_nodes(pdf)
            for node in nodes:
                subchunks = splitter.split_text(node.text)
                for idx, chunk_text in enumerate(subchunks):
                    # build a fresh metadata dict (so we don't mutate node.metadata)
                    meta = {
                        **(getattr(node, "metadata", {}) or {}),
                        "source_pdf": pdf,
                        "parsed_by": "llamaparse",
                        "parent_chunk_type": getattr(node, "type", ""),
                        "parent_chunk_index": idx,
                    }
                    # optional: ensure "page" exists if llamaparse didn't include it
                    meta.setdefault("page", meta.get("page_number") or meta.get("page") or None)

                    # stable ID for feedback & analytics
                    meta["chunk_uid"] = f"{meta.get('source_pdf','')}_{meta.get('page','')}_{md5(chunk_text.encode('utf-8')).hexdigest()[:10]}"

                    doc = Document(page_content=chunk_text, metadata=meta)
                    all_semantic_chunks.append(doc)

    else:
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
    llm_backend="groq",
    enable_feedback_rerank: bool = False  # <-- NEW (default OFF)
):
    logging.info({...})
    embed_model = get_fastembed_embedding()
    vectorstore = load_chroma_vectorstore(embed_model, persist_directory=chroma_persist_dir)
    retriever = get_retriever(vectorstore, k=top_k)

    # --- Optional feedback-aware rerank wrapper (post-retrieval) ---
    if enable_feedback_rerank:
        try:
            # reuse the in-memory reputation map maintained in app.py
            from app import CHUNK_REP
            def rep_lookup(uid: str):
                return CHUNK_REP.get(uid, {"up": 0, "down": 0})
            retriever = FeedbackAwareRetriever(retriever, rep_lookup, beta=0.2)
            logging.info({"event": "feedback_rerank_enabled", "beta": 0.2})
        except Exception as e:
            logging.warning({"event": "feedback_rerank_bind_failed", "error": str(e)})

    if llm_backend == "groq":
        chat_model = get_groq_llm()
        logging.info({"event": "llm_selected", "llm_type": "groq"})
    elif llm_backend == "ollama":
        chat_model = get_ollama_llm()
        logging.info({"event": "llm_selected", "llm_type": "ollama"})
    else:
        chat_model = get_gemini_llm()
        logging.info({"event": "llm_selected", "llm_type": "gemini"})

    semantic_rag_chain = get_semantic_rag_chain(retriever, chat_model)
    logging.info({
        "event": "rag_chain_ready",
        "chroma_dir": chroma_persist_dir,
        "llm_backend": llm_backend,
        "rerank": enable_feedback_rerank
    })
    return semantic_rag_chain
