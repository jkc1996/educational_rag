# src/chunkers.py

from langchain_experimental.text_splitter import SemanticChunker
from src.utils import final_clean_text
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
import logging
import os
import hashlib

CHUNKING_PAGE_ONLY = "page_only"
CHUNKING_PAGE_RECURSIVE = "page_recursive"
CHUNKING_PAGE_RECURSIVE_SEMANTIC = "page_recursive_semantic"

# This function alone already gives page-wise chunking.
def load_pages_as_documents(files):
    """
    Loads PDFs/DOCX as page-level Documents with metadata.
    Each Document == one page.
    """
    all_docs = []

    for filename in files:
        ext = os.path.splitext(filename)[-1].lower()

        if ext == ".pdf":
            loader = PyPDFLoader(filename)
            file_type = "pdf"
        elif ext in [".docx", ".doc"]:
            loader = Docx2txtLoader(filename)
            file_type = "docx"
        else:
            logging.warning({"event": "unsupported_filetype", "file": filename, "ext": ext})
            continue

        docs = loader.load()
        basename = os.path.basename(filename)

        for doc in docs:
            if file_type == "pdf":
                page0 = doc.metadata.get("page")
                page_num = (page0 + 1) if page0 is not None else None
            else:
                page_num = 1

            all_docs.append(
                Document(
                    page_content=doc.page_content,
                    metadata={
                        "source_file": basename,
                        "source_pdf": basename,
                        "page": page_num,
                    },
                )
            )

    return all_docs

def run_chunking(
    files,
    chunking_strategy,
    embed_model,
    pre_chunker=None,
):
    """
    Main chunking dispatcher supporting:
    - page_only
    - page_recursive
    - page_recursive_semantic
    """
    logging.info({
        "event": "chunking_start",
        "strategy": chunking_strategy,
        "num_files": len(files),
    })

    # 1️⃣ Load page-level documents (common for all)
    page_docs = load_pages_as_documents(files)

    # -----------------------------
    # STRATEGY 1: PAGE ONLY
    # -----------------------------
    if chunking_strategy == CHUNKING_PAGE_ONLY:
        final_docs = page_docs

    # -----------------------------
    # STRATEGY 2: PAGE → RECURSIVE
    # -----------------------------
    elif chunking_strategy == CHUNKING_PAGE_RECURSIVE:
        if pre_chunker is None:
            raise ValueError("pre_chunker required for page_recursive")

        final_docs = []
        for doc in page_docs:
            splits = pre_chunker.create_documents([doc.page_content])
            for s in splits:
                s.metadata = dict(doc.metadata)
                final_docs.append(s)

    # -----------------------------
    # STRATEGY 3: PAGE → RECURSIVE → SEMANTIC
    # -----------------------------
    elif chunking_strategy == CHUNKING_PAGE_RECURSIVE_SEMANTIC:
        if pre_chunker is None:
            raise ValueError("pre_chunker required for semantic chunking")

        semantic_chunker = SemanticChunker(
            embed_model, breakpoint_threshold_type="percentile"
        )

        pre_docs = []
        for doc in page_docs:
            splits = pre_chunker.create_documents([doc.page_content])
            for s in splits:
                s.metadata = dict(doc.metadata)
                pre_docs.append(s)

        final_docs = semantic_chunker.create_documents(
            [d.page_content for d in pre_docs],
            metadatas=[d.metadata for d in pre_docs],
        )

    else:
        raise ValueError(f"Unknown chunking strategy: {chunking_strategy}")

    # -----------------------------
    # CLEAN + UID (common)
    # -----------------------------
    for d in final_docs:
        d.page_content = final_clean_text(d.page_content)
        m = d.metadata or {}
        if "chunk_uid" not in m:
            m["chunk_uid"] = _make_chunk_uid(d.page_content, m)
        d.metadata = m

    logging.info({
        "event": "chunking_done",
        "strategy": chunking_strategy,
        "total_chunks": len(final_docs),
    })

    return final_docs



def _make_chunk_uid(text: str, meta: dict) -> str:
    base = f"{meta.get('source_pdf','')}_{meta.get('page','')}_{hashlib.md5(text.encode('utf-8')).hexdigest()[:10]}"
    return base

def run_semantic_chunking(files, pre_chunker, embed_model):
    return run_chunking(
        files=files,
        chunking_strategy=CHUNKING_PAGE_RECURSIVE_SEMANTIC,
        embed_model=embed_model,
        pre_chunker=pre_chunker,
    )
