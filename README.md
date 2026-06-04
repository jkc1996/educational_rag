# Educational RAG

Educational RAG is an OpenAI-only study workbench for academic documents. It uses a FastAPI backend, LangChain, ChromaDB, cached structured summarization, RAGAS evaluation, and a Vite + React + MUI frontend.

The current app is organized around five workflows:

- Ask: grounded QA with retrieved sources and feedback.
- Sources: upload documents, ingest chunks, create embeddings, and cache summaries.
- Assessment: generate question papers from cached structured summaries.
- Evaluate: run RAGAS metrics against approved OpenAI models.
- Monitor: inspect OpenAI token usage, pricing snapshots, request IDs, and app logs.

## Project Layout

```text
backend/
  app/
    api/              FastAPI routes under /api/v1
    core/             settings, dependency wiring, logging setup
    infrastructure/   OpenAI, Chroma, repositories, pricing, usage logging
    prompts/          prompt registry
    schemas/          Pydantic request/response and structured output models
    services/         document, ingestion, RAG, summarization, eval services
  storage/            runtime files ignored by git
  tests/              backend tests
  requirements.txt    pinned Python dependencies

frontend/
  src/
    components/       shell, shared controls, markdown renderer, workspace UI
    features/         sources, ask, assessment, evaluate, monitor pages
    api/              frontend API client
  package.json
```

## Backend Setup

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set your real OpenAI key:

```env
OPENAI_API_KEY=sk-...
OPENAI_ALLOWED_CHAT_MODELS=gpt-5.5,gpt-5.4,gpt-5.4-mini,gpt-5.4-nano
OPENAI_DEFAULT_CHAT_MODEL=gpt-5.4
OPENAI_SUMMARY_MODEL=gpt-5.4-mini
OPENAI_UTILITY_MODEL=gpt-5.4-nano
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

- Swagger docs: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- API prefix: `http://localhost:8000/api/v1`

## Frontend Setup

In a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173`.

The default API URL is:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Runtime Configuration

Important backend settings are defined in `backend/.env.example`:

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
CHUNK_SIZE=1800
CHUNK_OVERLAP=180
RETRIEVAL_TOP_K=5
MAX_SUMMARY_CHUNKS_PER_DOCUMENT=18
MAX_QUESTIONS_PER_PAPER=50
MAX_RAGAS_QUESTIONS=25
DAILY_SOFT_BUDGET_USD=5.0
```

The default cost policy is:

- QA and final question-paper synthesis use `OPENAI_DEFAULT_CHAT_MODEL`.
- Chunk/document summaries and blueprints use `OPENAI_SUMMARY_MODEL`.
- Utility work uses `OPENAI_UTILITY_MODEL`.
- Embeddings use `OPENAI_EMBEDDING_MODEL`.

## Runtime Storage

Runtime files are created under `backend/storage/` and are ignored by git:

```text
backend/storage/uploads/       uploaded source files
backend/storage/chroma/        ChromaDB vector store
backend/storage/summaries/     cached structured summaries
backend/storage/eval_sets/     RAGAS evaluation sets
backend/storage/eval_results/  evaluation outputs
backend/storage/logs/app.jsonl structured app logs
backend/storage/documents.json document registry
backend/storage/feedback.jsonl QA feedback
backend/storage/usage.jsonl    token and pricing telemetry
```

Summary cache entries are keyed from document hash, prompt/model configuration, and chunking settings. Re-ingestion can reuse cached summaries unless you enable summary regeneration.

## Public API

All routes are under `/api/v1`:

```text
GET  /models
GET  /subjects
GET  /documents
POST /documents/upload
POST /documents/ingest
GET  /documents/{document_id}/summary
POST /rag/ask
POST /question-papers
GET  /evaluations/eval-sets
POST /evaluations/ragas
POST /feedback
GET  /logs
GET  /usage
```

## Usage And Cost Notes

The backend records token usage and OpenAI response IDs from OpenAI/LangChain response metadata when available. Cost is calculated locally from the pricing snapshot in the backend pricing catalog and written with each usage record.

For 30-35 page PDFs, the intended flow is:

1. Upload the PDF in Sources.
2. Ingest once to chunk, embed, and cache compact structured summaries.
3. Ask questions against Chroma retrieval.
4. Generate question papers from cached summaries instead of repeatedly summarizing the full PDF.
5. Review usage and logs in Monitor.

## Verification

Backend tests:

```powershell
cd backend
pytest
```

Frontend checks:

```powershell
cd frontend
npm run build
npm run test
```

The Vite production build may warn about large chunks because of PDF and math-rendering dependencies. That warning is not a build failure.
