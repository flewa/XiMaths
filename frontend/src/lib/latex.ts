// Barre de symboles de l'éditeur : chaque bouton insère du LaTeX autour de la sélection.

export type Snippet = {
  /** Texte du bouton, court. */
  label: string;
  /** Nom lu par les lecteurs d'écran et affiché au survol. */
  title: string;
  before: string;
  after?: string;
};

export const SNIPPETS: Snippet[] = [
  { label: "$x$", title: "Formule dans le texte", before: "$", after: "$" },
  { label: "$$", title: "Formule en bloc", before: "$$\n", after: "\n$$" },
  { label: "a/b", title: "Fraction", before: "\\frac{", after: "}{}" },
  { label: "√", title: "Racine carrée", before: "\\sqrt{", after: "}" },
  { label: "xⁿ", title: "Exposant", before: "^{", after: "}" },
  { label: "xₙ", title: "Indice", before: "_{", after: "}" },
  { label: "∑", title: "Somme", before: "\\sum_{", after: "}^{}" },
  { label: "∫", title: "Intégrale", before: "\\int_{", after: "}^{}" },
  { label: "lim", title: "Limite", before: "\\lim_{", after: "}" },
  { label: "∞", title: "Infini", before: "\\infty" },
  { label: "→", title: "Tend vers", before: "\\to " },
  { label: "≤", title: "Inférieur ou égal", before: "\\leq " },
  { label: "≥", title: "Supérieur ou égal", before: "\\geq " },
  { label: "≠", title: "Différent", before: "\\neq " },
  { label: "∈", title: "Appartient à", before: "\\in " },
  { label: "⊂", title: "Inclus dans", before: "\\subset " },
  { label: "∀", title: "Pour tout", before: "\\forall " },
  { label: "∃", title: "Il existe", before: "\\exists " },
  { label: "⇒", title: "Implique", before: "\\Rightarrow " },
  { label: "⇔", title: "Équivaut à", before: "\\Leftrightarrow " },
  { label: "ℝ", title: "Ensemble des réels", before: "\\R" },
  { label: "ℕ", title: "Ensemble des entiers naturels", before: "\\N" },
  { label: "ε", title: "Epsilon", before: "\\varepsilon" },
];

export type Edit = {
  from: number;
  to: number;
  insert: string;
  /** Sélection après l'insertion : la sélection d'origine, ou le curseur entre les deux parties. */
  anchor: number;
  head: number;
};

/** Insère `snippet` autour de `text.slice(from, to)`, qui reste sélectionné ; une
 * sélection vide place le curseur entre les deux parties. Un symbole seul remplace
 * la sélection, et le curseur va après lui. */
export function applySnippet(text: string, from: number, to: number, snippet: Snippet): Edit {
  const start = from + snippet.before.length;
  if (snippet.after === undefined) {
    return { from, to, insert: snippet.before, anchor: start, head: start };
  }
  const selected = text.slice(from, to);
  return {
    from,
    to,
    insert: `${snippet.before}${selected}${snippet.after}`,
    anchor: start,
    head: start + selected.length,
  };
}
