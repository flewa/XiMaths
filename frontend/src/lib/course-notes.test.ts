import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

import katex from "katex";
import remarkMath from "remark-math";
import remarkParse from "remark-parse";
import { unified } from "unified";
import { visit } from "unist-util-visit";
import { describe, expect, it } from "vitest";

import { normalizeMath } from "@/components/MathMarkdown";
import { MACROS } from "@/lib/katex-macros";

import type { CourseNoteSummary } from "./api";
import { CONVENTIONS, frenchSpacing, neighbours, notePath, proofSections } from "./course-notes";

// Les fiches et les démonstrations de la rédaction, écrites côté serveur (backend/courses/notes/).
const NOTES = join(__dirname, "../../../backend/courses/notes");

function notes() {
  return ["sup", "spe", "demonstrations"].flatMap((cycle) =>
    readdirSync(join(NOTES, cycle))
      .filter((name) => name.endsWith(".md"))
      .map((name) => ({ name: `${cycle}/${name}`, text: readFileSync(join(NOTES, cycle, name), "utf8") })),
  );
}

/** Formules d'un texte telles que le site les lit, et texte resté hors formule. */
function parse(markdown: string) {
  const tree = unified().use(remarkParse).use(remarkMath).parse(normalizeMath(markdown));
  const formulas: string[] = [];
  const text: string[] = [];
  visit(tree, (node) => {
    if (node.type === "math" || node.type === "inlineMath") formulas.push((node as { value: string }).value);
    else if (node.type === "text") text.push((node as { value: string }).value);
  });
  return { formulas, text };
}

function render(formula: string) {
  katex.renderToString(formula, { throwOnError: true, strict: "error", macros: { ...MACROS } });
}

describe("fiches de rappels de cours", () => {
  const all = notes();

  it("existent", () => {
    expect(all.length).toBeGreaterThan(0);
  });

  it.each(all)("$name : chaque formule passe dans KaTeX, et aucun $ ne reste hors formule", ({ text }) => {
    const body = text.slice(text.indexOf("\n---\n") + 5);
    // Le texte tel que la page le rend, espaces insécables comprises.
    const parsed = parse(frenchSpacing(body));
    expect(parsed.formulas.length).toBeGreaterThan(0);
    for (const formula of parsed.formulas) expect(() => render(formula), formula).not.toThrow();
    expect(parsed.text.filter((value) => value.includes("$"))).toEqual([]);
  });

  it("les conventions du sommaire passent aussi dans KaTeX", () => {
    for (const formula of parse(CONVENTIONS).formulas) expect(() => render(formula), formula).not.toThrow();
  });
});

describe("frenchSpacing", () => {
  it("met une espace insécable devant la ponctuation haute, jamais dans une formule", () => {
    expect(frenchSpacing("Soit $x \\in \\{ y : y > 0 \\}$ : alors ; vrai ? oui !")).toBe(
      "Soit $x \\in \\{ y : y > 0 \\}$\u00a0: alors\u00a0; vrai\u00a0? oui\u00a0!",
    );
    expect(frenchSpacing("> $$\n> a : b\n> $$\nFin :")).toBe("> $$\n> a : b\n> $$\nFin\u00a0:");
  });
});

describe("démonstrations", () => {
  const proof = (slug: string, status: CourseNoteSummary["status"]) =>
    ({ slug, kind: "demonstration", status }) as CourseNoteSummary;

  it("ont leur propre adresse", () => {
    expect(notePath(proof("lemme-des-noyaux", "au-programme"))).toBe("/demonstrations/lemme-des-noyaux");
    expect(notePath({ slug: "polynomes", kind: "fiche" })).toBe("/rappels/polynomes");
  });

  it("se rangent en théorèmes du cours, puis hors programme", () => {
    const list = [proof("a", "au-programme"), proof("b", "hors-programme"), proof("c", "preuve-hors-programme")];
    expect(proofSections(list).map((section) => [section.id, section.proofs.map((item) => item.slug)])).toEqual([
      ["cours", ["a", "c"]],
      ["hors-programme", ["b"]],
    ]);
    expect(proofSections([proof("b", "hors-programme")]).map((section) => section.id)).toEqual(["hors-programme"]);
  });
});

describe("neighbours", () => {
  const note = (slug: string, cycle: "sup" | "spe") => ({ slug, cycle }) as CourseNoteSummary;
  const list = [note("a", "sup"), note("b", "sup"), note("c", "spe"), note("d", "spe")];

  it("reste dans le cycle de la fiche", () => {
    expect(neighbours(list, "b")).toEqual({ previous: list[0], next: null });
    expect(neighbours(list, "c")).toEqual({ previous: null, next: list[3] });
    expect(neighbours(list, "z")).toEqual({ previous: null, next: null });
  });
});
