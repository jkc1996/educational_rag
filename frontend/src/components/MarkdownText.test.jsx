import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MarkdownText } from "./MarkdownText.jsx";

describe("MarkdownText", () => {
  it("renders common answer markdown as formatted elements", () => {
    const { container } = render(
      <MarkdownText>
        {"**SVM** stands for **Support Vector Machine**.\n\n### Key idea\n- Finds a boundary\n- Maximizes the **margin**"}
      </MarkdownText>,
    );

    expect(screen.getByText("Key idea")).toBeInTheDocument();
    expect(screen.getByText("Finds a boundary")).toBeInTheDocument();
    expect(container.querySelectorAll("strong")).toHaveLength(3);
    expect(container.textContent).not.toContain("###");
    expect(container.textContent).not.toContain("**");
  });

  it("renders legacy slash-delimited math with KaTeX", () => {
    const { container } = render(
      <MarkdownText>
        {"This is the mapping \\(\\phi(x)\\).\n\n\\[ K(x,z)=\\phi(x)\\cdot\\phi(z) \\]\n\n- Gaussian: \\(K(x,z)=\\exp(-||x-z||^2/(2\\sigma^2))\\)"}
      </MarkdownText>,
    );

    expect(container.querySelector(".katex")).toBeInTheDocument();
    expect(container.querySelector(".katex-display")).toBeInTheDocument();
    expect(container.textContent).not.toContain("\\(");
    expect(container.textContent).not.toContain("\\[");
  });

  it("renders standard dollar-delimited math with KaTeX", () => {
    const { container } = render(
      <MarkdownText>
        {"Inline $K(x,z)=x\\cdot z$ and block:\n\n$$\nK(x,z)=\\exp(-||x-z||^2/(2\\sigma^2))\n$$"}
      </MarkdownText>,
    );

    expect(container.querySelectorAll(".katex").length).toBeGreaterThan(1);
    expect(container.querySelector(".katex-display")).toBeInTheDocument();
  });
});
