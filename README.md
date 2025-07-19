# Educational RAG: Academic QA System

A modular Retrieval-Augmented Generation (RAG) pipeline for subject-specific academic question answering. Supports PDF upload, semantic chunking, ChromaDB storage, and LLM-based Q&A via a modern React frontend and Python FastAPI backend.

---

## Setup Instructions

### 1. Clone the Repo & Prepare Environment

```
git clone <your-repo-url>
cd educational_rag
```

### 2. Create and Activate Virtual Environment

```
python -m venv venv
# Activate (Windows)
venv\Scripts\activate
# Or on Mac/Linux:
# source venv/bin/activate
```

### 3. Install Requirements

```
pip install -r requirements.txt
```

#### Install spaCy English Model (One-time setup):

```
python -m spacy download en_core_web_sm
```

---

## Backend: FastAPI (Recommended)

This powers the client-server application for the React frontend.

### Start the Backend Server:

```
cd backend
uvicorn app:app --reload
```

- The backend runs at http://localhost:8000 by default.

---

## Frontend: React

### Install Node Modules

```
cd frontend
npm install
```

### Start the React Frontend

```
npm start
```

- The frontend runs at http://localhost:3000 by default.

---

## Legacy Streamlit UI (for quick demos, optional)

You can run the old Streamlit-based QA UI for quick local experimentation:

```
streamlit run streamlit_app.py
```

*(Make sure you are in your backend or root folder where streamlit_app.py is located.)*

---

## Inspecting Your Chroma Vectorstore

You can explore your ChromaDB vectorstore chunks and metadata using the included script:

```
python inspect_chroma_db.py
```

---

## Summary Table

| What           | Command                                                      |
|----------------|-------------------------------------------------------------|
| Backend venv   | `python -m venv venv` + `venv\Scripts\activate`             |
| Install reqs   | `pip install -r requirements.txt`                           |
| Install spaCy  | `python -m spacy download en_core_web_sm`                   |
| Start backend  | `cd backend`<br>`uvicorn app:app --reload`                  |
| Start frontend | `cd frontend`<br>`npm install`<br>`npm start`               |
| Streamlit UI   | `streamlit run streamlit_app.py`                            |
| Inspect Chroma | `python inspect_chroma_db.py`                               |

---

## General Notes

- Make sure to upload and ingest PDFs subject-wise from the React UI before asking questions.
- After ingestion, the backend cache is automatically cleared for the updated subject.
- The pipeline is optimized for subject-level ChromaDB storage and efficient LLM use.
- All model files, logs, and ChromaDB outputs are written to the `outputs/` folder by default.

---
