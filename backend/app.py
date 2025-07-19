import logging_setup
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
from threading import Lock
from src.pipeline import ingest_pdfs_to_chroma, get_rag_chain
from src.postprocess import spacy_polish
import logging
import json
from fastapi.responses import JSONResponse

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
    logging.info({
        "event": "pdf_uploaded",
        "filename": file.filename,
        "subject": subject,
        "description": description,
        "file_location": file_location
    })

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
        logging.error({
            "event": "ingest_failed_file_not_found",
            "filename": filename,
            "subject": subject
        })
        return {"status": "error", "message": "File not found!"}
    try:
        chroma_dir = f"outputs/chroma_{subject.replace(' ', '_').lower()}"
        logging.info({
            "event": "ingest_start",
            "filename": filename,
            "subject": subject,
            "chroma_dir": chroma_dir
        })
        ingest_pdfs_to_chroma([pdf_path], chroma_persist_dir=chroma_dir)

        # --- Clear cache for this subject (all LLMs) ---
        with cache_lock:
            keys_to_remove = [key for key in rag_chain_cache if key[0] == chroma_dir]
            for key in keys_to_remove:
                del rag_chain_cache[key]
        logging.info({
            "event": "ingest_done",
            "filename": filename,
            "subject": subject,
            "chroma_dir": chroma_dir
        })
        return {"status": "success", "message": f"Ingested {filename} for {subject}!"}
    except Exception as e:
        logging.error({
            "event": "ingest_failed_exception",
            "filename": filename,
            "subject": subject,
            "error": str(e)
        })
        return {"status": "error", "message": f"Failed to ingest: {e}"}

@app.post("/ask-question/")
async def ask_question(
    subject: str = Form(...),
    question: str = Form(...),
    llm_choice: str = Form(...)
):
    chroma_dir = f"outputs/chroma_{subject.replace(' ', '_').lower()}"
    cache_key = (chroma_dir, llm_choice)

    logging.info({
        "event": "question_asked",
        "subject": subject,
        "question": question,
        "llm_choice": llm_choice
    })

    try:
        with cache_lock:
            if cache_key in rag_chain_cache:
                logging.info({
                    "event": "rag_cache_hit",
                    "cache_key": str(cache_key)
                })
                rag_chain = rag_chain_cache[cache_key]
            else:
                logging.info({
                    "event": "rag_cache_miss",
                    "cache_key": str(cache_key)
                })
                rag_chain = get_rag_chain(chroma_dir, llm_backend=llm_choice)
                rag_chain_cache[cache_key] = rag_chain

        raw_answer = rag_chain.invoke(question)
        answer = spacy_polish(raw_answer)

        logging.info({
            "event": "answer_generated",
            "subject": subject,
            "question": question,
            "llm_choice": llm_choice,
            "answer_length": len(answer)
        })
    except Exception as e:
        logging.error({
            "event": "answer_failed",
            "subject": subject,
            "question": question,
            "llm_choice": llm_choice,
            "error": str(e)
        })
        answer = f"Error while processing question: {e}"
    return {"answer": answer}

@app.get("/logs")
def get_logs(limit: int = 500):
    try:
        with open("app.log", "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        logs = []
        for line in lines:
            try:
                logs.append(json.loads(line))
            except Exception:
                continue
        # Return newest first
        return JSONResponse(content=logs[::-1])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
