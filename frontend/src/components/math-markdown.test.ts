import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { MathMarkdown } from "./MathMarkdown";

function render(markdown: string) {
  return renderToStaticMarkup(createElement(MathMarkdown, null, markdown));
}

describe("MathMarkdown", () => {
  it("colle à la formule la ponctuation précédée d'une espace insécable", () => {
    const html = render("Soit $x \\in \\R$\u00a0: alors $y$\u00a0; fin.");
    expect(html.match(/class="math-glue"/g)).toHaveLength(2);
    expect(html).toContain("\u00a0:</span> alors");
    expect(html).toContain("\u00a0;</span> fin.");
  });

  it("ne touche ni au texte ordinaire ni à une ponctuation sans espace insécable", () => {
    const html = render("Soit $x$ : alors $y$.");
    expect(html).not.toContain("math-glue");
    expect(html).toContain("katex");
  });
});
