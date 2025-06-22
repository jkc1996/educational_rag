# src/prompts.py

from langchain_core.prompts import ChatPromptTemplate

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
    return ChatPromptTemplate.from_template(rag_template)
