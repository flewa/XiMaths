// Référencement : descriptions courtes, tirées du Markdown + LaTeX des énoncés.

export const DESCRIPTION_LENGTH = 160;

/** Texte brut d'un énoncé, pour une balise description : sans balisage Markdown ni
 * délimiteurs `$`, sur une ligne, coupé à un mot près avec « … ». */
export function excerpt(markdown: string, max = DESCRIPTION_LENGTH) {
  const text = markdown
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "") // images
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1") // liens : on garde le texte
    .replace(/\$\$?/g, "")
    .replace(/^\s{0,3}(#{1,6}|>|[-*+]|\d+\.)\s+/gm, "")
    .replace(/[*_`~]+/g, "")
    .replace(/\s+/g, " ")
    .trim();
  if (text.length <= max) return text;
  const cut = text.slice(0, max - 1);
  const space = cut.lastIndexOf(" ");
  return `${(space > max / 2 ? cut.slice(0, space) : cut).replace(/[\s,;:.]+$/, "")}…`;
}
