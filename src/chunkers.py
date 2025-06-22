# src/chunkers.py

from langchain_experimental.text_splitter import SemanticChunker
from src.utils import final_clean_text
from src.logger import get_logger

logger = get_logger()

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
        logger.info(f"🔵 Pre-chunking: {filename}")
        loader = PyPDFLoader(filename)
        docs = loader.load()
        docs_prechunked = []
        for doc in docs:
            # Pre-chunk using the provided pre_chunker (e.g., RecursiveCharacterTextSplitter)
            docs_prechunked.extend(pre_chunker.create_documents([doc.page_content]))
        logger.info(f"...{len(docs_prechunked)} pre-chunks created.")

        logger.info(f"Semantic chunking: {filename}")
        chunks = semantic_chunker.create_documents([d.page_content for d in docs_prechunked])

        # Add metadata to each chunk
        for chunk in chunks:
            chunk.metadata = getattr(chunk, 'metadata', {})
            chunk.metadata["source_pdf"] = filename

        logger.info(f"...{len(chunks)} semantic chunks created for {filename}")
        all_semantic_chunks.extend(chunks)

    logger.info(f"Total semantic chunks across all PDFs: {len(all_semantic_chunks)}")

    # Final clean-up (remove artifacts from all semantic chunks)
    for chunk in all_semantic_chunks:
        chunk.page_content = final_clean_text(chunk.page_content)

    return all_semantic_chunks
