import katex from "katex";
import { Fragment } from "react";

import { MACROS } from "@/lib/katex-macros";

// Une formule en ligne : $…$, sans $ à l'intérieur.
const FORMULA = /\$([^$]+)\$/g;

const OPTIONS = { throwOnError: false, strict: "ignore" as const, trust: false, maxExpand: 1000, maxSize: 10 };

/** Une ligne de texte (un titre d'exercice) dont les formules $…$ sont rendues par KaTeX.
 * Le reste est du texte ordinaire ; une formule invalide s'affiche en rouge, sans casser
 * la page. */
export function MathText({ children }: { children: string }) {
  const parts: React.ReactNode[] = [];
  let last = 0;
  for (const match of children.matchAll(FORMULA)) {
    if (match.index > last) parts.push(<Fragment key={`t${last}`}>{children.slice(last, match.index)}</Fragment>);
    const html = katex.renderToString(match[1], { ...OPTIONS, macros: { ...MACROS } });
    // KaTeX échappe le texte et n'accepte aucune commande d'inclusion (trust: false).
    parts.push(<span key={`m${match.index}`} className="math-text" dangerouslySetInnerHTML={{ __html: html }} />);
    last = match.index + match[0].length;
  }
  if (last < children.length) parts.push(<Fragment key={`t${last}`}>{children.slice(last)}</Fragment>);
  return <>{parts}</>;
}
