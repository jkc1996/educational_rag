# src/pipeline.py

from src.loaders import load_pdf_pages
from src.chunkers import run_semantic_chunking
from src.embeddings import get_fastembed_embedding
from src.vectorstore import create_chroma_vectorstore
from src.llms import get_gemini_llm
from src.retriever import get_retriever
from src.chain import get_semantic_rag_chain
from src.postprocess import spacy_polish
from src.logger import get_logger

logger = get_logger()

def run_rag_pipeline(
    pdf_files,
    chroma_persist_dir="outputs/chroma_semantic_allpdfs_v2",
    chunk_size=2000,
    chunk_overlap=50,
    top_k=5
):
    # 1. Embedding model
    embed_model = get_fastembed_embedding()

    # 2. Pre-chunker
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    pre_chunker = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # 3. Semantic chunking (pre-chunking & semantic chunking)
    all_semantic_chunks = run_semantic_chunking(pdf_files, pre_chunker, embed_model)

    # 4. Vectorstore
    vectorstore = create_chroma_vectorstore(all_semantic_chunks, embed_model, persist_directory=chroma_persist_dir)

    # 5. Retriever
    retriever = get_retriever(vectorstore, k=top_k)

    # 6. Gemini LLM
    chat_model = get_gemini_llm()

    # 7. Semantic RAG Chain
    semantic_rag_chain = get_semantic_rag_chain(retriever, chat_model)

    logger.info("RAG pipeline fully initialized.")

    return semantic_rag_chain
