import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import App from "./App.jsx";

vi.mock("./hooks/useBootstrap.js", () => ({
  useBootstrap: () => ({
    models: [{ id: "gpt-5.4", label: "gpt-5.4", role: "qa-default", default: true }],
    embeddingModel: "text-embedding-3-large",
    subjects: [],
    documents: [],
    loading: false,
    error: "",
    refresh: vi.fn(),
  }),
}));

describe("App", () => {
  it("renders the ask workspace first", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole("heading", { name: "Ask" })).toBeInTheDocument();
    expect(screen.getByText("Question Setup")).toBeInTheDocument();
  });
});
