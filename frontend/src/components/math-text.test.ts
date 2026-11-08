import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { MathText } from "./MathText";

const render = (text: string) => renderToStaticMarkup(createElement(MathText, null, text));

describe("MathText", () => {
  it("rend les formules $…$ d'un titre et garde le texte autour", () => {
    const html = render("Reste de $3^{100}$ modulo 7");
    expect(html.startsWith("Reste de <span class=\"math-text\">")).toBe(true);
    expect(html).toContain("katex");
    expect(html.endsWith("</span> modulo 7")).toBe(true);
  });

  it("connaît les macros du site et laisse un titre sans formule intact", () => {
    expect(render("Générateurs du groupe $\\Z/12\\Z$")).toContain("mathbb");
    expect(render("Longueur de l'astroïde")).toBe("Longueur de l&#x27;astroïde");
  });

  it("n'exécute rien : le texte d'une formule est échappé", () => {
    expect(render("$\\text{<script>}$")).not.toContain("<script>");
  });
});
