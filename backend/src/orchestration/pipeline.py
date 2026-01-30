from src.ingestion.chunkers import (
     run_chunking,
    CHUNKING_PAGE_ONLY,
    CHUNKING_PAGE_RECURSIVE,
    CHUNKING_PAGE_RECURSIVE_SEMANTIC
)
from src.ingestion import get_fastembed_embedding
from src.ingestion import create_chroma_vectorstore, load_chroma_vectorstore
from src.generation import get_gemini_llm, get_groq_llm, get_openai_llm, get_ollama_llm
from src.retrieval import get_retriever, FeedbackAwareRetriever  # <-- NEW
from .chain import get_semantic_rag_chain
import logging

def ingest_pdfs_to_chroma(
    pdf_files,
    chroma_persist_dir,
    chunk_size=2000,
    chunk_overlap=100,
    use_llamaparse=False,
    chunking_strategy=CHUNKING_PAGE_ONLY,  # 👈 change the chunking stratagy here
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
        from src.ingestion import load_llamaparse_nodes
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_core.documents import Document
        from hashlib import md5
        import os, re

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        all_semantic_chunks = []

        PAGE_RX = re.compile(r"^\s*=== PAGE (\d+) ===\s*$")  # {pageNumber} = next page

        for pdf in pdf_files:
            nodes = load_llamaparse_nodes(pdf)
            raw_md = "\n".join([n.text for n in nodes]) if nodes else ""

            # Start at page 1; each marker means "next page begins"
            pages = []
            current_page = 1
            current_buf = []

            for line in raw_md.splitlines():
                m = PAGE_RX.match(line)
                if m:
                    # flush the current page BEFORE switching to the next one
                    pages.append((current_page, "\n".join(current_buf).strip()))
                    current_page = int(m.group(1))  # marker already holds *next* page number
                    current_buf = []
                else:
                    current_buf.append(line)

            # flush the last page
            pages.append((current_page, "\n".join(current_buf).strip()))

            base_name = os.path.basename(pdf).replace("\\", "/").split("/")[-1]

            for page_num, page_text in pages:
                if not page_text:
                    continue
                for idx, chunk_text in enumerate(splitter.split_text(page_text)):
                    meta = {
                        "source_pdf": base_name,
                        "page": page_num,          # correct 1-based page number
                        "parsed_by": "llamaparse",
                        "parent_chunk_type": "page_block",
                        "parent_chunk_index": idx,
                    }
                    meta["chunk_uid"] = f"{base_name}_{page_num}_{md5(chunk_text.encode('utf-8')).hexdigest()[:10]}"
                    all_semantic_chunks.append(Document(page_content=chunk_text, metadata=meta))

    else:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        pre_chunker = None
        if chunking_strategy != CHUNKING_PAGE_ONLY:
            pre_chunker = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

        all_chunks = run_chunking(
            files=pdf_files,
            chunking_strategy=chunking_strategy,
            embed_model=embed_model,
            pre_chunker=pre_chunker,
        )

    # Store in Chroma
    vectorstore = create_chroma_vectorstore(
        all_chunks, embed_model, persist_directory=chroma_persist_dir
    )

    logging.info({
        "event": "chroma_ingest_done",
        "chroma_dir": chroma_persist_dir,
        "total_chunks": len(all_chunks)
    })
    return True

def get_rag_chain(
    chroma_persist_dir,
    top_k=5,
    llm_backend="groq",
    enable_feedback_rerank: bool = False
):
    logging.info({...})
    embed_model = get_fastembed_embedding()
    vectorstore = load_chroma_vectorstore(embed_model, persist_directory=chroma_persist_dir)
    retriever = get_retriever(vectorstore, k=top_k)

    # --- Optional feedback-aware rerank wrapper (post-retrieval) ---
    if enable_feedback_rerank:
        try:
            # reuse the in-memory reputation map maintained in app.py
            from src.api.app import CHUNK_REP
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

    elif llm_backend == "openai":
        chat_model = get_openai_llm()
        logging.info({"event": "llm_selected", "llm_type": "openai"})

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
