from src.loaders import load_pdf_pages
from src.chunkers import run_semantic_chunking
from src.embeddings import get_fastembed_embedding
from src.vectorstore import create_chroma_vectorstore, load_chroma_vectorstore
from src.llms import get_gemini_llm, get_groq_llm, get_ollama_llm
from src.retriever import get_retriever
from src.chain import get_semantic_rag_chain
from src.logger import get_logger

logger = get_logger()

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
    embed_model = get_fastembed_embedding()

    from langchain.text_splitter import RecursiveCharacterTextSplitter
    pre_chunker = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    all_semantic_chunks = run_semantic_chunking(pdf_files, pre_chunker, embed_model)

    # Store in Chroma
    vectorstore = create_chroma_vectorstore(
        all_semantic_chunks, embed_model, persist_directory=chroma_persist_dir
    )

    logger.info(f"Done! All PDFs indexed in Chroma at {chroma_persist_dir}")
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
    embed_model = get_fastembed_embedding()

    # Load Chroma vectorstore (must exist)
    vectorstore = load_chroma_vectorstore(embed_model, persist_directory=chroma_persist_dir)

    retriever = get_retriever(vectorstore, k=top_k)

    # LLM selection
    if llm_backend == "groq":
        chat_model = get_groq_llm()
        logger.info("Using Groq LLM for answering.")

    elif llm_backend == "ollama":
        chat_model = get_ollama_llm()
        logger.info("Using Ollama LLM for answering.")

    else:
        chat_model = get_gemini_llm()
        logger.info("Using Gemini LLM for answering.")

    semantic_rag_chain = get_semantic_rag_chain(retriever, chat_model)
    logger.info("RAG chain ready for answering.")

    return semantic_rag_chain
