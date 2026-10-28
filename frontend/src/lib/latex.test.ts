import { describe, expect, it } from "vitest";

import { SNIPPETS, applySnippet, type Snippet } from "./latex";

const fraction: Snippet = { label: "a/b", title: "Fraction", before: "\\frac{", after: "}{}" };
const infinity: Snippet = { label: "∞", title: "Infini", before: "\\infty" };

describe("applySnippet", () => {
  it("places the cursor inside an empty pair", () => {
    const edit = applySnippet("x = ", 4, 4, fraction);
    expect(edit).toEqual({ from: 4, to: 4, insert: "\\frac{}{}", anchor: 10, head: 10 });
  });

  it("wraps the selection and keeps it selected", () => {
    const edit = applySnippet("x = 1", 4, 5, fraction);
    expect(edit.insert).toBe("\\frac{1}{}");
    expect([edit.anchor, edit.head]).toEqual([10, 11]);
  });

  it("replaces the selection with a lone symbol", () => {
    const edit = applySnippet("n → oo", 4, 6, infinity);
    expect(edit).toEqual({ from: 4, to: 6, insert: "\\infty", anchor: 10, head: 10 });
  });

  it("offers snippets with distinct names", () => {
    const titles = SNIPPETS.map((snippet) => snippet.title);
    expect(new Set(titles).size).toBe(titles.length);
  });
});
