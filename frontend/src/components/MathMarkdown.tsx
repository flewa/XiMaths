import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";

// Macros fournies aux auteurs, à la place de \def et \newcommand libres.
const MACROS = {
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
      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[[rehypeKatex, katexOptions]]}>
        {normalizeMath(children)}
      </ReactMarkdown>
    </div>
  );
}
