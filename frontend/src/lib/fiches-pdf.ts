import manifest from "./fiches-pdf.json";

/** Fiches de révision en PDF, produites par scripts/fiches-pdf.mjs dans public/fiches-pdf/. */
const PDFS: Record<string, { hash: string; path: string }> = manifest;

/** L'adresse du PDF d'une fiche ou d'une démonstration, ou null s'il n'existe pas. */
export function pdfPath(slug: string) {
  return slug in PDFS ? `/fiches-pdf/${slug}.pdf` : null;
}
