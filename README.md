# Educational RAG

OpenAI-only academic RAG application with a FastAPI backend, ChromaDB vector storage, RAGAS evaluation, cached structured summarization, and a Vite/React frontend.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` from the example file:

```powershell
Copy-Item .env.example .env
```

Then fill in your real OpenAI key:

```env
OPENAI_API_KEY=sk-...
OPENAI_DEFAULT_CHAT_MODEL=gpt-5.4
OPENAI_SUMMARY_MODEL=gpt-5.4-mini
OPENAI_UTILITY_MODEL=gpt-5.4-nano
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

Start the API:

```powershell
cd backend
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`, with docs at `http://localhost:8000/api/docs`.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`. To point it at a different API:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Workflows

- Upload documents, then ingest to chunk, embed, store in Chroma, and cache structured summaries.
- Ask grounded questions with source snippets.
- Generate question papers from cached summaries, not repeated full-document summaries.
- Run RAGAS evaluations across approved OpenAI models.
- Review structured logs and OpenAI usage telemetry.

## Requirements

The backend uses one pinned requirements file:

```powershell
cd backend
pip install -r requirements.txt
```

## Runtime Data

Runtime files are written under `backend/storage/` and ignored by git:

- uploaded files
- Chroma indexes
- cached summaries
- evaluation sets/results
- logs
- feedback
- usage telemetry
