import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { pdfPath } from "./fiches-pdf";
import manifest from "./fiches-pdf.json";

const NOTES = join(__dirname, "../../../backend/courses/notes");
const PUBLIC = join(__dirname, "../../public");

function notes() {
  return ["sup", "spe", "demonstrations"].flatMap((folder) =>
    readdirSync(join(NOTES, folder))
      .filter((name) => name.endsWith(".md"))
      .map((name) => ({ slug: name.replace(/\.md$/, ""), text: readFileSync(join(NOTES, folder, name), "utf8") })),
  );
}

describe("fiches PDF", () => {
  const entries: Record<string, { hash: string; engine?: string; pages?: number }> = manifest;

  it.each(notes())("$slug : le PDF suit la dernière version de la fiche", ({ slug, text }) => {
    const hash = createHash("sha256").update(text).digest("hex");
    // Fiche modifiée : relancer « npm run fiches-pdf » avec le site lancé en local.
    expect(entries[slug]?.hash, `PDF à refaire : npm run fiches-pdf (${slug})`).toBe(hash);
    expect(existsSync(join(PUBLIC, "fiches-pdf", `${slug}.pdf`))).toBe(true);
    // Composée en LaTeX, et une fiche de révision : deux pages au plus.
    expect(entries[slug].engine).toBe("latex");
    expect(entries[slug].pages).toBeLessThanOrEqual(2);
  });

  it("donne l'adresse d'un PDF connu, et rien pour une fiche inconnue", () => {
    expect(pdfPath("formulaire-trigonometrie")).toBe("/fiches-pdf/formulaire-trigonometrie.pdf");
    expect(pdfPath("fiche-inconnue")).toBeNull();
  });
});
