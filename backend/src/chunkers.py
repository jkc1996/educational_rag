# src/chunkers.py

from langchain_experimental.text_splitter import SemanticChunker
from src.utils import final_clean_text
from langchain.document_loaders import PyPDFLoader
import logging
import os

def run_semantic_chunking(pdf_files, pre_chunker, embed_model):
    all_semantic_chunks = []

    semantic_chunker = SemanticChunker(embed_model, breakpoint_threshold_type="percentile")

    for filename in pdf_files:
        logging.info({"event": "prechunk_start", "file": filename})
        loader = PyPDFLoader(filename)
        docs = loader.load()  # each doc has metadata like {'source': path, 'page': 0-based int}
        docs_prechunked = []

        for doc in docs:
            # pre-chunk this single page
            partials = pre_chunker.create_documents([doc.page_content])
            page0 = doc.metadata.get("page", None)

            # attach metadata to each prechunk
            for p in partials:
                p.metadata = getattr(p, "metadata", {})
                p.metadata.update({
                    "source_pdf": os.path.basename(filename),
                    "page": (page0 + 1) if page0 is not None else None,  # make it 1-based
                })
            docs_prechunked.extend(partials)

        logging.info({"event": "prechunk_done", "file": filename, "prechunk_count": len(docs_prechunked)})
        logging.info({"event": "semantic_chunking_start", "file": filename})

        # preserve metadata while semantic-chunking
        chunks = semantic_chunker.create_documents(
            [d.page_content for d in docs_prechunked],
            metadatas=[d.metadata for d in docs_prechunked],
        )

        logging.info({"event": "semantic_chunking_done", "file": filename, "semantic_chunk_count": len(chunks)})
        all_semantic_chunks.extend(chunks)

    logging.info({"event": "semantic_chunking_total", "total_chunks": len(all_semantic_chunks), "num_pdfs": len(pdf_files)})

    for chunk in all_semantic_chunks:
        chunk.page_content = final_clean_text(chunk.page_content)

    return all_semantic_chunks
