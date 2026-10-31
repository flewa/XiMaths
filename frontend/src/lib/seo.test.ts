import { describe, expect, it } from "vitest";

import { excerpt, latexToText } from "./seo";

describe("excerpt", () => {
  it("drops Markdown markup and math delimiters", () => {
    const markdown = "## Énoncé\n\nÉtudier la **convergence** de $\\sum 1/n^2$, voir [le cours](https://example.com).";
    expect(excerpt(markdown)).toBe("Énoncé Étudier la convergence de ∑ 1/n², voir le cours.");
  });

  it("keeps short texts whole", () => {
    expect(excerpt("Montrer que $\\sqrt 2$ est irrationnel.")).toBe("Montrer que √2 est irrationnel.");
  });

  it("cuts long texts on a word, with an ellipsis", () => {
    const text = excerpt("mot ".repeat(100), 30);
    expect(text.length).toBeLessThanOrEqual(30);
    expect(text).toMatch(/^(mot )*mot…$/);
  });
});

describe("latexToText", () => {
  it("turns formulas into readable text", () => {
    expect(latexToText("\\displaystyle\\sum_{n \\geq 1} \\frac{1}{n^2}")).toBe("∑ (n ≥ 1) 1/n²");
    expect(latexToText("A \\in \\mathcal{M}_n(\\R)")).toBe("A ∈ Mₙ(ℝ)");
    expect(latexToText("\\frac{1}{n(n-1)} \\le \\sqrt{2}")).toBe("1/(n(n-1)) ≤ √2");
    expect(latexToText("\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1")).toBe("lim (x → 0) (sin x)/x = 1");
  });

  it("feeds the description of an exercise", () => {
    expect(excerpt("Montrer que la série $\\displaystyle\\sum_{n \\geq 1} \\frac{1}{n^2}$ converge.")).toBe(
      "Montrer que la série ∑ (n ≥ 1) 1/n² converge.",
    );
  });
});
