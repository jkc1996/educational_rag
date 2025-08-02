import logging_setup
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from threading import Lock
from src.pipeline import ingest_pdfs_to_chroma, get_rag_chain
from src.postprocess import spacy_polish
import logging
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import Body
from src.ragas_evaluation import evaluate_ragas, nan_to_none
from src.question_generation import summarize_selected_pdfs, generate_question_paper

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

class IngestRequest(BaseModel):
    subject: str
    filename: str
    use_llamaparse: bool = False  # default to False if not sent

@app.post("/ingest/")
async def ingest_pdf(req: IngestRequest = Body(...)):
    uploads_dir = "./uploads"
    pdf_path = os.path.join(uploads_dir, req.filename)
    if not os.path.exists(pdf_path):
        logging.error({
            "event": "ingest_failed_file_not_found",
            "filename": req.filename,
            "subject": req.subject
        })
        return {"status": "error", "message": "File not found!"}
    try:
        chroma_dir = f"outputs/chroma_{req.subject.replace(' ', '_').lower()}"
        logging.info({
            "event": "ingest_start",
            "filename": req.filename,
            "subject": req.subject,
            "chroma_dir": chroma_dir,
            "use_llamaparse": req.use_llamaparse
        })
        ingest_pdfs_to_chroma(
            [pdf_path],
            chroma_persist_dir=chroma_dir,
            use_llamaparse=req.use_llamaparse  # <--- HERE
        )

        # --- Clear cache for this subject (all LLMs) ---
        with cache_lock:
            keys_to_remove = [key for key in rag_chain_cache if key[0] == chroma_dir]
            for key in keys_to_remove:
                del rag_chain_cache[key]
        logging.info({
            "event": "ingest_done",
            "filename": req.filename,
            "subject": req.subject,
            "chroma_dir": chroma_dir
        })
        return {"status": "success", "message": f"Ingested {req.filename} for {req.subject}!"}
    except Exception as e:
        logging.error({
            "event": "ingest_failed_exception",
            "filename": req.filename,
            "subject": req.subject,
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

@app.post("/evaluate-ragas/")
async def evaluate_ragas_api(
    subject: str = Body(...),
    model_name: str = Body(...),
    eval_json: str = Body("eval_questions.json")
):
    """
    Run RAGAS evaluation for the given subject and model.
    Example POST body:
      {
        "subject": "Machine Learning",
        "model_name": "groq"
      }
    """
    try:
        metrics = evaluate_ragas(subject, model_name, eval_json)
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/generate-question-paper/")
async def generate_question_paper_api(request: Request):
    data = await request.json()
    subject = data.get('subject')
    filenames = data.get('filenames', [])
    llm_choice = data.get('llm_choice', 'groq')
    question_config = data.get('question_config', None)
    extra_context = data.get('extra_context', "").strip()  # <--- NEW LINE

    logging.info({
        "event": "generate_question_paper_called",
        "subject": subject,
        "filenames": filenames,
        "llm_choice": llm_choice,
        "question_config": question_config,
        "extra_context": extra_context
    })

    if not subject or not filenames or not question_config:
        return {"error": "Missing required fields."}

    summary = summarize_selected_pdfs(subject, filenames, llm_choice=llm_choice)
    if not summary or not summary.strip():
        return {
            "summary": summary,
            "questions": "ERROR: No summary was generated from the selected PDFs. Please check your selection and try again."
        }
    questions = generate_question_paper(summary, question_config, llm_choice=llm_choice, extra_context=extra_context)  # <--- pass extra_context

    return {
        "summary": summary,
        "questions": questions
    }

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
