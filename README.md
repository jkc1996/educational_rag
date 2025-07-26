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
| Backend venv   | `python -m venv myenv` + `myenv\Scripts\activate`             |
| Install reqs   | `pip install -r requirements.txt`                           |
| Install spaCy  | `python -m spacy download en_core_web_sm`                   |
| Start backend  | `cd backend`<br>`uvicorn app:app --reload`                  |
| Start frontend | `cd frontend`<br>`npm install`<br>`npm start`               |
| Streamlit UI   | `streamlit run streamlit_app.py`                            |
| Inspect Chroma | `python inspect_chroma_db.py`                               |

---

## Using Ollama (Local LLM) for RAG QA

Ollama allows you to run open-source LLMs fully **locally**—no API keys or cloud required!  
With this setup, you can use models like Llama3, Mistral, and your own custom models for fast, private question-answering.

### 1. Download and Install Ollama

- Go to [https://ollama.com/download](https://ollama.com/download) and download the latest release for your operating system.
- Install and follow any prompts.  
  After install, open a terminal and check version:
  ```
  ollama --version
  ```

### 2. Start (or Verify) Ollama Server

Ollama runs as a background service.  
**You usually don't need to start it manually.**  
To check if it’s running:
```
ollama list
```
If you see your models, it’s running!  
If not, you can (rarely needed) run:
```
ollama serve
```
> If you get a "bind" error, it's already running—just move on!

### 3. Create or Pull a Model

**A. To pull a ready-made model:**
```
ollama pull llama3
```

**B. To create your own model (example):**

1. Create a file called `Modelfile` in your project directory:
    ```
    FROM llama3
    PARAMETER temperature 0.2
    SYSTEM "You are EDUsage, a helpful and knowledgeable assistant for educational Q&A."
    ```

2. Build your custom model:
    ```
    ollama create edusage -f Modelfile
    ```

You should now see `edusage` in the output of `ollama list`.

### 4. Configure Your Project for Ollama

- In your backend `.env` file, add:
    ```
    OLLAMA_BASE_URL=http://localhost:11434
    ```
- Make sure `langchain_ollama` is installed:
    ```
    pip install langchain_ollama
    ```

- In your `src/config.py`, make sure you load `OLLAMA_BASE_URL`.

### 5. Using Ollama in the Application

- When you use the QA page, select **"Ollama (Local)"** in the LLM dropdown.
- Ask questions—your backend will route them to the local Ollama model (`edusage` or whatever you built).
- Check backend logs for confirmation that the Ollama LLM is being loaded.

### 6. Example Commands

| Command                                 | Purpose                                  |
|------------------------------------------|------------------------------------------|
| `ollama list`                            | See which models are available           |
| `ollama pull llama3`                     | Download the Llama3 model                |
| `ollama create edusage -f Modelfile`     | Create a new custom model                |
| `ollama serve`                           | Start the Ollama server (usually auto)   |
| `curl http://localhost:11434/api/tags`   | Check server is running                  |

### 7. Troubleshooting

- If `ollama serve` says the port is in use, it's already running—no problem!
- If the QA page fails with LLM errors, make sure:
    - Ollama is running
    - The model name matches what you created (`edusage` by default)
    - `langchain_ollama` is installed
    - Your `.env` and `config.py` are set up as above

---

### Advanced PDF Parsing (LlamaParse)

To enable advanced, structure-aware parsing for academic PDFs:

Check the box Advanced PDF Parsing (LlamaParse) on the Upload page before clicking Process/Ingest.

When enabled, the backend uses LlamaParse for smarter chunking (recommended for textbooks, papers, or PDFs with tables/equations).

Make sure your .env has your LlamaParse API key:
LLAMA_PARSE_API_KEY=llx-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

---
## General Notes

- Make sure to upload and ingest PDFs subject-wise from the React UI before asking questions.
- After ingestion, the backend cache is automatically cleared for the updated subject.
- The pipeline is optimized for subject-level ChromaDB storage and efficient LLM use.
- All model files, logs, and ChromaDB outputs are written to the `outputs/` folder by default.

---
