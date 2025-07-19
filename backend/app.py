from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
from threading import Lock
from src.pipeline import ingest_pdfs_to_chroma, get_rag_chain
from src.postprocess import spacy_polish

app = FastAPI()

# CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Caching logic ===
rag_chain_cache = {}
cache_lock = Lock()

@app.post("/upload-pdf/")
async def upload_pdf(
    subject: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...)
):
    file_location = f"./uploads/{subject.replace(' ', '_')}_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    print(f"Received PDF: {file.filename}")
    print(f"Subject: {subject}")
    print(f"Description: {description}")

    return {
        "message": "File received and saved",
        "subject": subject,
        "description": description,
        "filename": f"{subject.replace(' ', '_')}_{file.filename}",
    }

@app.post("/ingest/")
async def ingest_pdf(
    subject: str = Form(...),
    filename: str = Form(...)
):
    uploads_dir = "./uploads"
    pdf_path = os.path.join(uploads_dir, filename)
    if not os.path.exists(pdf_path):
        return {"status": "error", "message": "File not found!"}
    try:
        chroma_dir = f"outputs/chroma_{subject.replace(' ', '_').lower()}"
        ingest_pdfs_to_chroma([pdf_path], chroma_persist_dir=chroma_dir)

        # --- Clear cache for this subject (all LLMs) ---
        with cache_lock:
            keys_to_remove = [key for key in rag_chain_cache if key[0] == chroma_dir]
            for key in keys_to_remove:
                del rag_chain_cache[key]

        return {"status": "success", "message": f"Ingested {filename} for {subject}!"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to ingest: {e}"}

@app.post("/ask-question/")
async def ask_question(
    subject: str = Form(...),
    question: str = Form(...),
    llm_choice: str = Form(...)
):
    chroma_dir = f"outputs/chroma_{subject.replace(' ', '_').lower()}"
    cache_key = (chroma_dir, llm_choice)

    # DEBUG: Print the subject, LLM choice, chroma_dir, and current cache keys
    print("="*30)
    print(f"ASK: subject='{subject}', llm_choice='{llm_choice}', chroma_dir='{chroma_dir}'")
    print(f"Current rag_chain_cache keys: {list(rag_chain_cache.keys())}")

    try:
        with cache_lock:
            if cache_key in rag_chain_cache:
                print(f"Cache HIT for {cache_key}")
                rag_chain = rag_chain_cache[cache_key]
            else:
                print(f"Cache MISS for {cache_key}. Building new chain.")
                rag_chain = get_rag_chain(chroma_dir, llm_backend=llm_choice)
                rag_chain_cache[cache_key] = rag_chain

        raw_answer = rag_chain.invoke(question)
        answer = spacy_polish(raw_answer)
    except Exception as e:
        answer = f"Error while processing question: {e}"
    print("="*30)
    return {"answer": answer}
