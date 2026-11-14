import type { CourseNoteSummary, ProofStatus } from "./api";

export const CYCLES = [
  { cycle: "sup", label: "Première année (sup)", short: "Sup" },
  { cycle: "spe", label: "Deuxième année (spé)", short: "Spé" },
] as const;

export function cycleOf(note: Pick<CourseNoteSummary, "cycle">) {
  return CYCLES.find((item) => item.cycle === note.cycle) ?? CYCLES[0];
}

export function courseNotePath(slug: string) {
  return `/rappels/${slug}`;
}

export function demonstrationPath(slug: string) {
  return `/demonstrations/${slug}`;
}

/** L'adresse d'un texte de cours selon sa nature : fiche de rappels ou démonstration. */
export function notePath(note: Pick<CourseNoteSummary, "slug" | "kind">) {
  return note.kind === "demonstration" ? demonstrationPath(note.slug) : courseNotePath(note.slug);
}

/** Place d'une démonstration par rapport au programme de prépa (MPSI, MP), telle qu'on
 * l'affiche. */
export const PROOF_STATUS: Record<Exclude<ProofStatus, "">, { label: string; short: string }> = {
  "au-programme": { label: "Au programme de prépa", short: "Au programme" },
  "preuve-hors-programme": {
    label: "Énoncé au programme, démonstration hors programme",
    short: "Preuve hors programme",
  },
  "hors-programme": { label: "Hors programme de prépa", short: "Hors programme" },
};

/** Les démonstrations en deux parties : celles des théorèmes du cours, puis les autres. */
export function proofSections(proofs: CourseNoteSummary[]) {
  return [
    {
      id: "cours",
      title: "Théorèmes du cours",
      proofs: proofs.filter((proof) => proof.status !== "hors-programme"),
    },
    {
      id: "hors-programme",
      title: "En dehors du cours",
      proofs: proofs.filter((proof) => proof.status === "hors-programme"),
    },
  ].filter((section) => section.proofs.length > 0);
}

/** Fiches voisines dans le sommaire de son cycle, pour lire à la suite. */
export function neighbours(notes: CourseNoteSummary[], slug: string) {
  const current = notes.find((note) => note.slug === slug);
  if (!current) return { previous: null, next: null };
  const sameCycle = notes.filter((note) => note.cycle === current.cycle);
  const index = sameCycle.indexOf(current);
  return { previous: sameCycle[index - 1] ?? null, next: sameCycle[index + 1] ?? null };
}

// Une formule en bloc ou en ligne, à laisser telle quelle ; sinon une espace devant « : ; ! ? ».
const MATH_OR_PUNCTUATION = /(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)| ([:;!?])/g;

/** Typographie française : espace insécable devant « : ; ! ? », hors des formules, pour que
 * la ponctuation ne passe jamais seule en début de ligne. */
export function frenchSpacing(markdown: string) {
  return markdown.replace(MATH_OR_PUNCTUATION, (match, math: string | undefined, mark: string | undefined) =>
    math ? match : `\u00a0${mark}`,
  );
}

/** Conventions communes à toutes les fiches, rappelées en tête du sommaire. */
export const CONVENTIONS = String.raw`- $\N$ désigne l'ensemble des entiers naturels ; il contient $0$. On note $\N^* = \N \setminus \{0\}$.
- $\K$ désigne $\R$ ou $\C$.
- Pour deux entiers $p \leq q$, $[\![p, q]\!]$ désigne l'ensemble des entiers $k$ tels que $p \leq k \leq q$.
- Sauf mention contraire, un intervalle est une partie de $\R$ convexe, non vide et non réduite à un point.
- Chaque énoncé donne ses hypothèses en entier : une hypothèse qui n'y figure pas n'est pas nécessaire, une hypothèse qui y figure ne peut pas être omise.`;
