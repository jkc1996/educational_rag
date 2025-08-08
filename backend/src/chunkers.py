# src/chunkers.py

from langchain_experimental.text_splitter import SemanticChunker
from src.utils import final_clean_text
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader
import logging
import os

def run_semantic_chunking(files, pre_chunker, embed_model):
    """
    Accepts a list of PDF or DOCX files, performs semantic chunking, and returns all chunks with proper metadata.
    """
    all_semantic_chunks = []
    semantic_chunker = SemanticChunker(embed_model, breakpoint_threshold_type="percentile")

    for filename in files:
        ext = os.path.splitext(filename)[-1].lower()
        # Pick loader based on extension
        if ext == ".pdf":
            loader = PyPDFLoader(filename)
            file_type = "pdf"
        elif ext in [".docx", ".doc"]:
            loader = Docx2txtLoader(filename)
            file_type = "docx"
        else:
            logging.warning({"event": "unsupported_filetype", "file": filename, "ext": ext})
            continue

        logging.info({"event": "prechunk_start", "file": filename})
        docs = loader.load()
        docs_prechunked = []

        for doc in docs:
            # Pre-chunk this doc/page
            partials = pre_chunker.create_documents([doc.page_content])

            # For PDFs: get page number from metadata (0-based), for Word: single page
            if file_type == "pdf":
                page0 = doc.metadata.get("page", None)
                page_num = (page0 + 1) if page0 is not None else None
            else:
                page_num = 1

            for p in partials:
                p.metadata = getattr(p, "metadata", {})
                basename = os.path.basename(filename)
                p.metadata.update({
                    "source_file": basename,
                    "source_pdf": basename,   # always fill this, for both PDF and Word
                    "page": page_num
                })
            docs_prechunked.extend(partials)

        logging.info({"event": "prechunk_done", "file": filename, "prechunk_count": len(docs_prechunked)})
        logging.info({"event": "semantic_chunking_start", "file": filename})

        # Preserve metadata while semantic-chunking
        chunks = semantic_chunker.create_documents(
            [d.page_content for d in docs_prechunked],
            metadatas=[d.metadata for d in docs_prechunked],
        )

        logging.info({"event": "semantic_chunking_done", "file": filename, "semantic_chunk_count": len(chunks)})
        all_semantic_chunks.extend(chunks)

    logging.info({
        "event": "semantic_chunking_total",
        "total_chunks": len(all_semantic_chunks),
        "num_files": len(files)
    })

    for chunk in all_semantic_chunks:
        chunk.page_content = final_clean_text(chunk.page_content)

    return all_semantic_chunks
