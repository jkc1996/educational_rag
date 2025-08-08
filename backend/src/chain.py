# wherever get_semantic_rag_chain is defined

from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from src.prompts import get_rag_prompt

def _format_docs_for_prompt(docs):
    # What the LLM sees
    blocks = []
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source_pdf") or d.metadata.get("source") or "unknown_source"
        page = d.metadata.get("page")
        header = f"[{i}] {src}" + (f" — page {page}" if page else "")
        blocks.append(f"{header}\n{d.page_content}")
    return "\n\n".join(blocks)

def get_semantic_rag_chain(retriever, chat_model):
    rag_prompt = get_rag_prompt()

    # pipe: retriever -> format -> prompt -> llm -> string
    formatted_context = retriever | _format_docs_for_prompt

    answer_chain = (
        {"context": formatted_context, "question": RunnablePassthrough()}
        | rag_prompt
        | chat_model
        | StrOutputParser()
    )

    # parallel: return both sources and answer
    combined = RunnableParallel(
        sources=retriever,   # raw Document[] for citations
        answer=answer_chain
    )
    return combined
