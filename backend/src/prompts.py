from langchain_core.prompts import ChatPromptTemplate
import logging

def get_rag_prompt():
    rag_template = """\
Use the following context to answer the user's query. If you cannot answer, please respond with 'I don't know'.

User's Query:
{question}

Context:
{context}

Instructions:
- Avoid unnecessary line breaks, slashes, or bullet points unless specifically required.
"""
    logging.debug({
        "event": "rag_prompt_created",
        "template_preview": rag_template[:60]  # Log the first 60 chars
    })
    return ChatPromptTemplate.from_template(rag_template)
