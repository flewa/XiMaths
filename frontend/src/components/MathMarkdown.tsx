import type { Element, ElementContent, Root, RootContent } from "hast";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";

// Macros fournies aux auteurs, à la place de \def et \newcommand libres.
export const MACROS = {
  "\\R": "\\mathbb{R}",
  "\\N": "\\mathbb{N}",
  "\\Z": "\\mathbb{Z}",
  "\\Q": "\\mathbb{Q}",
  "\\C": "\\mathbb{C}",
  "\\K": "\\mathbb{K}",
};

/**
 * Ramène les écritures LaTeX usuelles à celles de remark-math, qui ne lit un bloc
 * que si les `$$` sont seuls sur leur ligne : `$$…$$` sur une ligne et `\[…\]`
 * deviennent des blocs, `\(…\)` des formules en ligne.
 */
export function normalizeMath(source: string) {
  return source
    .replace(/\\\[([\s\S]+?)\\\]/g, (_, body: string) => `\n$$\n${body.trim()}\n$$\n`)
    .replace(/^[ \t]*\$\$(.+?)\$\$[ \t]*$/gm, (_, body: string) => `$$\n${body.trim()}\n$$`)
    .replace(/\\\((.+?)\\\)/g, (_, body: string) => `$${body}$`);
}

// Ponctuation haute précédée d'une espace insécable (typographie française).
const GLUED_PUNCTUATION = /^\u00a0[:;!?]/;

function isFormula(node: RootContent | ElementContent | undefined): node is Element {
  const className = node?.type === "element" ? node.properties?.className : undefined;
  return Array.isArray(className) && className.includes("katex");
}

/** Garde « formule + espace insécable + ponctuation » sur une même ligne : le navigateur
 * couperait sinon entre la formule et l'espace, et la ligne suivante commencerait par « : ». */
export function keepPunctuationWithMath() {
  function glue(node: Root | Element) {
    const children: (RootContent | ElementContent)[] = node.children;
    for (let index = 0; index < children.length; index++) {
      const child = children[index];
      if (child.type === "element") glue(child);
      const next = children[index + 1];
      if (isFormula(child) && next?.type === "text" && GLUED_PUNCTUATION.test(next.value)) {
        const wrapper: Element = {
          type: "element",
          tagName: "span",
          properties: { className: ["math-glue"] },
          children: [child, { type: "text", value: next.value.slice(0, 2) }],
        };
        const rest = next.value.slice(2);
        children.splice(index, 2, wrapper, ...(rest ? [{ type: "text" as const, value: rest }] : []));
      }
    }
  }
  return (tree: Root) => glue(tree);
}

/** Markdown + LaTeX rendu côté serveur. Le HTML brut est ignoré par react-markdown. */
export function MathMarkdown({ children }: { children: string }) {
  const katexOptions = {
    trust: false,
    strict: "ignore" as const,
    throwOnError: false,
    maxExpand: 1000,
    maxSize: 20,
    // Copie fraîche : une macro définie dans un texte ne fuit pas dans le suivant.
    macros: { ...MACROS },
  };
  return (
    <div className="math-markdown">
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[[rehypeKatex, katexOptions], keepPunctuationWithMath]}
      >
        {normalizeMath(children)}
      </ReactMarkdown>
    </div>
  );
}
