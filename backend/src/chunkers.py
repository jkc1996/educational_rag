# src/chunkers.py

from langchain_experimental.text_splitter import SemanticChunker
from src.utils import final_clean_text

import logging

def run_semantic_chunking(pdf_files, pre_chunker, embed_model):
    """
    For each PDF:
        - Loads the PDF (expects loader already set up in pipeline)
        - Pre-chunks each doc (page)
        - Semantic chunks pre-chunks
        - Adds source metadata
        - Cleans up final chunk content
    Returns: List of all semantic chunks across all PDFs.
    """
    all_semantic_chunks = []

    from langchain.document_loaders import PyPDFLoader

    semantic_chunker = SemanticChunker(embed_model, breakpoint_threshold_type="percentile")

    for filename in pdf_files:
        logging.info({
            "event": "prechunk_start",
            "file": filename
        })
        loader = PyPDFLoader(filename)
        docs = loader.load()
        docs_prechunked = []
        for doc in docs:
            docs_prechunked.extend(pre_chunker.create_documents([doc.page_content]))
        logging.info({
            "event": "prechunk_done",
            "file": filename,
            "prechunk_count": len(docs_prechunked)
        })

        logging.info({
            "event": "semantic_chunking_start",
            "file": filename
        })
        chunks = semantic_chunker.create_documents([d.page_content for d in docs_prechunked])

        for chunk in chunks:
            chunk.metadata = getattr(chunk, 'metadata', {})
            chunk.metadata["source_pdf"] = filename

        logging.info({
            "event": "semantic_chunking_done",
            "file": filename,
            "semantic_chunk_count": len(chunks)
        })
        all_semantic_chunks.extend(chunks)

    logging.info({
        "event": "semantic_chunking_total",
        "total_chunks": len(all_semantic_chunks),
        "num_pdfs": len(pdf_files)
    })

    for chunk in all_semantic_chunks:
        chunk.page_content = final_clean_text(chunk.page_content)

    return all_semantic_chunks
