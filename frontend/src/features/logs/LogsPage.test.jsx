import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { api } from "../../api/client.js";
import { LogsPage } from "./LogsPage.jsx";

vi.mock("../../api/client.js", () => ({
  api: {
    logs: vi.fn(),
  },
}));

describe("LogsPage", () => {
  it("renders normalized log summary and rows", async () => {
    api.logs.mockResolvedValue({
      summary: { total: 1, errors: 0, warnings: 0, qa_events: 0, llm_events: 1, openai_events: 1, ingestion_events: 0, noisy_events: 0 },
      levels: ["INFO"],
      categories: ["llm"],
      items: [
        {
          timestamp: "2026-06-04 13:42:25",
          level: "INFO",
          category: "llm",
          flow: "qa",
          flow_id: "qa_123456789",
          step: "rag_answer",
          event: "openai_chat_model_create",
          message: "OpenAI model prepared for rag_answer: gpt-5.4",
          details_preview: "feature: rag_answer · model_id: gpt-5.4",
          details: { feature: "rag_answer", model_id: "gpt-5.4" },
          fingerprint: "openai_chat_model_create",
          is_noise: false,
        },
      ],
    });

    render(<LogsPage />);

    expect(await screen.findByText("OpenAI model prepared for rag_answer: gpt-5.4")).toBeInTheDocument();
    expect(screen.getByText("LLM Events")).toBeInTheDocument();
    await waitFor(() => expect(api.logs).toHaveBeenCalledWith({ limit: 500, query: "", level: "", category: "" }));
  });
});
