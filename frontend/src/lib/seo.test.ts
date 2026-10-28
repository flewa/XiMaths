import { describe, expect, it } from "vitest";

import { excerpt } from "./seo";

describe("excerpt", () => {
  it("drops Markdown markup and math delimiters", () => {
    const markdown = "## Énoncé\n\nÉtudier la **convergence** de $\\sum 1/n^2$, voir [le cours](https://example.com).";
    expect(excerpt(markdown)).toBe("Énoncé Étudier la convergence de \\sum 1/n^2, voir le cours.");
  });

  it("keeps short texts whole", () => {
    expect(excerpt("Montrer que $\\sqrt 2$ est irrationnel.")).toBe("Montrer que \\sqrt 2 est irrationnel.");
  });

  it("cuts long texts on a word, with an ellipsis", () => {
    const text = excerpt("mot ".repeat(100), 30);
    expect(text.length).toBeLessThanOrEqual(30);
    expect(text).toMatch(/^(mot )*mot…$/);
  });
});
