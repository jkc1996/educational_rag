import streamlit as st
from src.pipeline import run_rag_pipeline
from src.postprocess import spacy_polish

st.set_page_config(page_title="Educational RAG QA", page_icon="📚")
st.title("📚 Educational RAG Question Answering")

PDF_FILES = ["data/[01] Introduction.pdf"]  # <-- Change to your file(s)

# Pipeline ONCE per session
if "semantic_rag_chain" not in st.session_state:
    with st.spinner("Setting up the RAG pipeline..."):
        st.session_state.semantic_rag_chain = run_rag_pipeline(PDF_FILES)
    st.success("RAG pipeline is ready! Ask your questions below.")

# Always use a key and control value via session_state
if "user_question" not in st.session_state:
    st.session_state.user_question = ""

def clear_question():
    st.session_state.user_question = ""

st.write("Ask a question about your PDF(s):")

question = st.text_input(
    "Your question",
    value=st.session_state.user_question,
    key="user_question",
)

col1, col2 = st.columns([2, 1])
answer = None

with col1:
    ask = st.button("Get Answer")
with col2:
    clear = st.button("Clear Input", on_click=clear_question)

if ask and st.session_state.user_question.strip():
    with st.spinner("Retrieving answer..."):
        raw_answer = st.session_state.semantic_rag_chain.invoke(st.session_state.user_question)
        answer = spacy_polish(raw_answer)
        st.markdown("**Answer:**")
        st.success(answer)

# No rerun needed—input box will clear, and the value is always from session_state

st.markdown("---")
st.caption("Powered by Educational RAG · LangChain · Gemini · Streamlit")
