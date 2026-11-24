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

/** Identifiant d'ancre d'un titre : minuscules, sans accents ni formules. */
export function anchorOf(title: string) {
  return (
    title
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/\\[a-zA-Z]+/g, " ")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "partie"
  );
}

/** Les parties d'un texte (ses titres « ## »), dans l'ordre, avec une ancre unique chacune :
 * de quoi faire un sommaire. Les blocs de code et de formules sont ignorés. */
export function outline(markdown: string) {
  const items: { id: string; title: string }[] = [];
  const used = new Map<string, number>();
  let inCode = false;
  let inMath = false;
  for (const line of markdown.split("\n")) {
    const trimmed = line.trim();
    if (trimmed.startsWith("```")) inCode = !inCode;
    if (inCode) continue;
    if ((trimmed.match(/\$\$/g) ?? []).length % 2 === 1) {
      inMath = !inMath;
      continue;
    }
    if (inMath || !line.startsWith("## ")) continue;
    const title = line.slice(3).trim();
    const base = anchorOf(title);
    const seen = used.get(base) ?? 0;
    used.set(base, seen + 1);
    items.push({ id: seen === 0 ? base : `${base}-${seen + 1}`, title });
  }
  return items;
}

/** Les filières d'un texte (« MPSI, MP2I, PCSI ») sous forme de liste. */
export function programList(note: Pick<CourseNoteSummary, "programs">) {
  return note.programs
    .split(",")
    .map((code) => code.trim())
    .filter(Boolean);
}

/** Les textes dont le programme couvre ce niveau (MPSI, L2…). */
export function forLevel<T extends Pick<CourseNoteSummary, "programs">>(notes: T[], code: string) {
  return notes.filter((note) => programList(note).includes(code));
}

/** Les textes rattachés à l'un de ces chapitres ou notions, dans l'ordre de la liste. */
export function aboutTopics<T extends Pick<CourseNoteSummary, "topic">>(notes: T[], slugs: string[]) {
  return slugs.flatMap((slug) => notes.filter((note) => note.topic === slug));
}

/** Données schema.org d'une fiche ou d'une démonstration : ce qu'elle enseigne, à quel niveau. */
export function noteData(
  note: Pick<CourseNoteSummary, "title" | "kind" | "programs" | "topic" | "topic_name" | "updated_at"> & {
    published_at?: string | null;
  },
  { url, description, siteUrl, topicUrl }: { url: string; description: string; siteUrl: string; topicUrl: string | null },
) {
  return {
    "@context": "https://schema.org",
    "@type": "LearningResource",
    name: note.title,
    description,
    url: `${siteUrl}${url}`,
    inLanguage: "fr",
    learningResourceType: note.kind === "demonstration" ? "Démonstration" : "Résumé de cours",
    educationalLevel: programList(note),
    ...(note.topic_name ? { about: { "@type": "Thing", name: note.topic_name, ...(topicUrl ? { url: topicUrl } : {}) } } : {}),
    isAccessibleForFree: true,
    ...(note.published_at ? { datePublished: note.published_at } : {}),
    dateModified: note.updated_at,
    publisher: { "@type": "Organization", name: "XiMaths", url: siteUrl },
  };
}

// Les formulaires, par leur nom de fichier : « Fonctions usuelles » est une fiche de cours,
// « Dérivées et primitives usuelles » un formulaire. Un nouveau formulaire : « formulaire-… ».
const FORMULA_SHEETS = new Set([
  "derivees-primitives-usuelles",
  "sommes-usuelles",
  "limites-equivalents-usuels",
  "inegalites-classiques",
]);

/** Un formulaire plutôt qu'un résumé de cours : il se titre et se range à part. */
export function isFormulaSheet(note: Pick<CourseNoteSummary, "slug">) {
  return note.slug.startsWith("formulaire-") || FORMULA_SHEETS.has(note.slug);
}
