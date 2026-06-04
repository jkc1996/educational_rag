const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      message = payload.detail || payload.message || message;
    } catch {
      // keep HTTP message
    }
    throw new Error(message);
  }
  return response.json();
}

export const api = {
  baseUrl: API_BASE_URL,

  models: () => request("/models"),
  subjects: () => request("/subjects"),
  documents: (subject) => request(`/documents${subject ? `?subject=${encodeURIComponent(subject)}` : ""}`),
  documentSummary: (documentId) => request(`/documents/${documentId}/summary`),

  uploadDocument: ({ subject, description, file }) => {
    const data = new FormData();
    data.append("subject", subject);
    data.append("description", description || "");
    data.append("file", file);
    return request("/documents/upload", { method: "POST", body: data });
  },

  ingestDocument: ({ documentId, modelId, forceSummaryRefresh = false }) =>
    request("/documents/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        document_id: documentId,
        model_id: modelId || null,
        force_summary_refresh: forceSummaryRefresh,
      }),
    }),

  ask: (payload) =>
    request("/rag/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  feedback: (payload) =>
    request("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  questionPaper: (payload) =>
    request("/question-papers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  evaluateRagas: (payload) =>
    request("/evaluations/ragas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  evaluationSets: () => request("/evaluations/eval-sets"),

  logs: ({ limit = 500, query = "", level = "", category = "" } = {}) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (query) params.set("q", query);
    if (level) params.set("level", level);
    if (category) params.set("category", category);
    return request(`/logs?${params.toString()}`);
  },
  usage: (limit = 500) => request(`/usage?limit=${limit}`),
};
