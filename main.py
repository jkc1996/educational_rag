# from src.llms import get_groq_llm, get_gemini_llm, get_ollama_llm

# print("Testing Groq...")
# groq_llm = get_groq_llm()
# print(groq_llm.invoke("Say hello!").content)

# print("Testing Gemini...")
# gemini_llm = get_gemini_llm()
# print(gemini_llm.invoke("Say hello!").content)

# print("Testing Ollama (requires ollama server running)...")
# ollama_llm = get_ollama_llm()
# print(ollama_llm.invoke("Say hello!").content)

# main.py

from src.pipeline import run_rag_pipeline
from src.postprocess import spacy_polish
from src.logger import get_logger

logger = get_logger()

def main():
    # List your PDF files here (relative path from project root)
    pdf_files = [
        "data/[01] Introduction.pdf"  # <-- Replace with your actual PDF filename(s)
    ]

    logger.info("Starting RAG pipeline setup...")
    semantic_rag_chain = run_rag_pipeline(pdf_files)

    # Ask your question here:
    question = "In the context of the Turing test, what was Alan Turing's primary argument for using language as the basis for determining machine intelligence, and what did he aim to avoid?"
    logger.info(f"User question: {question}")

    # Run the RAG chain
    raw_answer = semantic_rag_chain.invoke(question)
    logger.info(f"Raw LLM answer: {raw_answer}")

    # Polish the answer for clean formatting
    polished_answer = spacy_polish(raw_answer)
    logger.info(f"Polished answer: {polished_answer}")

    print("\n===== FINAL ANSWER =====\n")
    print(polished_answer)

if __name__ == "__main__":
    main()

