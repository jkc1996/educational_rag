# src/chain.py

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.prompts import get_rag_prompt

import logging

def get_semantic_rag_chain(retriever, chat_model):
    rag_prompt = get_rag_prompt()

    logging.info({
        "event": "rag_chain_build_start",
        "details": {
            "retriever_type": str(type(retriever)),
            "model_type": str(type(chat_model)),
        }
    })

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | chat_model
        | StrOutputParser()
    )

    logging.info({
        "event": "rag_chain_build_done",
        "details": {
            "retriever_type": str(type(retriever)),
            "model_type": str(type(chat_model)),
        }
    })

    return chain
