# Educational RAG Frontend

Vite + React + MUI frontend for the OpenAI-only Educational RAG backend.

The UI is a study workbench with a left rail and five primary areas:

- Ask: grounded QA with markdown/math rendering, retrieved evidence, and feedback.
- Sources: document upload, ingestion, summary cache state, and source registry.
- Assessment: question-paper blueprint controls and generated paper output.
- Evaluate: RAGAS model comparison with metric score bars.
- Monitor: Usage and Logs tabs for OpenAI telemetry and app flow traces.

## Setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The dev server runs at `http://localhost:5173`.

## Environment

The frontend talks to the backend through `VITE_API_BASE_URL`.

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Use `frontend/.env.example` as the template. Keep real local overrides in `frontend/.env`.

## Routes

```text
/             Ask workspace
/sources      Source library
/assessment   Assessment studio
/evaluate     RAGAS evaluation
/monitor      Usage and logs monitor
```

Legacy routes such as `/qa`, `/question-paper`, `/evaluation`, `/usage`, and `/logs` redirect to the new workbench routes.

## Source Layout

```text
src/
  api/client.js              API wrapper for /api/v1
  components/AppShell.jsx    left rail and top context bar
  components/Workspace.jsx   shared panel, KPI, and layout primitives
  components/MarkdownText.jsx markdown, GFM, and KaTeX rendering
  features/documents/        Sources workflow
  features/qa/               Ask workflow
  features/questionPapers/   Assessment workflow
  features/evaluation/       RAGAS workflow
  features/monitor/          combined Usage and Logs screen
  features/usage/            usage table and totals
  features/logs/             structured logs table
```

## Scripts

```powershell
npm run dev
npm run build
npm run preview
npm run test
```

- `npm run dev` starts Vite for local development.
- `npm run build` creates a production build in `dist/`.
- `npm run preview` serves the production build locally.
- `npm run test` runs Vitest.

## Notes

- Backend must be running at the configured `VITE_API_BASE_URL`.
- The app expects backend-driven subjects, models, documents, logs, usage, and evaluation sets.
- Answers use `react-markdown`, `remark-gfm`, `remark-math`, and `rehype-katex` for readable markdown and formulas.
- Question paper PDF download is handled client-side with `jspdf`.
- Large Vite chunk warnings can appear because of PDF and math-rendering dependencies; they do not mean the build failed.
