# Educational RAG Frontend

Vite + React + MUI frontend for the OpenAI-only Educational RAG backend.

## Setup

```powershell
npm install
npm run dev
```

The app defaults to `http://localhost:8000/api/v1`.

Create `.env` from the example when you need to override the backend URL:

```powershell
Copy-Item .env.example .env
```

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Scripts

- `npm run dev` starts the local Vite dev server.
- `npm run build` creates a production build in `dist/`.
- `npm run preview` serves the production build locally.
- `npm run test` runs Vitest.
