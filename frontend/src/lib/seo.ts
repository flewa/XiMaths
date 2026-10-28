// Référencement : descriptions courtes, tirées du Markdown + LaTeX des énoncés.

export const DESCRIPTION_LENGTH = 160;

// Commandes LaTeX rendues par un symbole Unicode.
const SYMBOLS: Record<string, string> = {
  sum: "∑", prod: "∏", int: "∫", oint: "∮", infty: "∞", partial: "∂", nabla: "∇",
  le: "≤", leq: "≤", leqslant: "≤", ge: "≥", geq: "≥", geqslant: "≥", neq: "≠", ne: "≠",
  approx: "≈", sim: "∼", equiv: "≡", in: "∈", notin: "∉", subset: "⊂", subseteq: "⊆",
  cup: "∪", cap: "∩", emptyset: "∅", varnothing: "∅", forall: "∀", exists: "∃",
  to: "→", rightarrow: "→", longrightarrow: "⟶", mapsto: "↦", Rightarrow: "⇒", implies: "⇒",
  Leftrightarrow: "⇔", iff: "⇔", times: "×", cdot: "·", pm: "±", circ: "∘", dots: "…",
  ldots: "…", cdots: "⋯", R: "ℝ", N: "ℕ", Z: "ℤ", Q: "ℚ", C: "ℂ", K: "𝕂",
  alpha: "α", beta: "β", gamma: "γ", delta: "δ", epsilon: "ε", varepsilon: "ε", zeta: "ζ",
  eta: "η", theta: "θ", lambda: "λ", mu: "μ", nu: "ν", xi: "ξ", pi: "π", rho: "ρ",
  sigma: "σ", tau: "τ", varphi: "φ", phi: "φ", chi: "χ", psi: "ψ", omega: "ω",
  Gamma: "Γ", Delta: "Δ", Theta: "Θ", Lambda: "Λ", Pi: "Π", Sigma: "Σ", Phi: "Φ", Omega: "Ω",
};
// Commandes de mise en forme : on garde leur contenu, pas leur nom.
const FORMATTING = new Set([
  "displaystyle", "textstyle", "left", "right", "big", "Big", "bigg", "Bigg", "quad", "qquad",
  "mathbb", "mathcal", "mathrm", "mathbf", "mathit", "mathscr", "mathfrak", "text", "textbf",
  "textit", "operatorname", "boldsymbol", "limits", "nolimits",
]);
const SUPERSCRIPTS: Record<string, string> = {
  "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
};

const SUBSCRIPTS: Record<string, string> = {
  "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
  a: "ₐ", e: "ₑ", h: "ₕ", i: "ᵢ", j: "ⱼ", k: "ₖ", l: "ₗ", m: "ₘ", n: "ₙ", o: "ₒ", p: "ₚ",
  r: "ᵣ", s: "ₛ", t: "ₜ", u: "ᵤ", v: "ᵥ", x: "ₓ",
};

/** Formules LaTeX en texte lisible, pour une description : ∑ (n ≥ 1) 1/n² plutôt que
 * \sum_{n \geq 1} \frac{1}{n^2}. Une approximation, qui n'a pas à être réversible. */
export function latexToText(latex: string) {
  let text = latex
    .replace(/\\\\/g, " ")
    .replace(/\\[,;:! ]/g, " ")
    // Exposants d'un chiffre d'abord : n^2 devient n² avant d'entrer dans une fraction.
    .replace(/\^(?:\{(\d)\}|(\d)(?!\d))/g, (_, braced?: string, bare?: string) => SUPERSCRIPTS[braced ?? bare ?? ""]);
  // Fractions et racines, des plus profondes aux plus extérieures.
  for (let previous = ""; previous !== text; ) {
    previous = text;
    text = text
      .replace(/\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}/g, (_, a: string, b: string) => `${wrap(a)}/${wrap(b)}`)
      .replace(/\\sqrt\{([^{}]*)\}/g, (_, a: string) => `√${wrap(a)}`);
  }
  text = text
    .replace(/\\sqrt\s*(\w)/g, "√$1")
    .replace(/\\([A-Za-z]+)/g, (_, name: string) => SYMBOLS[name] ?? (FORMATTING.has(name) ? "" : name))
    .replace(/_(?:\{(\w)\}|(\w)(?![\w{]))/g, (_, braced?: string, bare?: string) => {
      const char = braced ?? bare ?? "";
      return SUBSCRIPTS[char] ?? `_${char}`;
    })
    // Indice ou exposant composé : entre parenthèses (le « _ » du Markdown serait retiré).
    .replace(/_\{([^{}]*)\}/g, (_, inner: string) => ` (${inner.trim()})`)
    .replace(/\^\{([^{}]*)\}/g, (_, inner: string) => `^(${inner.trim()})`)
    .replace(/[{}]/g, "");
  return text.replace(/\s+/g, " ").trim();
}

function wrap(term: string) {
  const trimmed = term.trim();
  return /^[\p{L}\p{N}.]+$/u.test(trimmed) ? trimmed : `(${trimmed})`;
}

/** Texte brut d'un énoncé, pour une balise description : sans balisage Markdown, les
 * formules en texte lisible, sur une ligne, coupé à un mot près avec « … ». */
export function excerpt(markdown: string, max = DESCRIPTION_LENGTH) {
  const text = markdown
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "") // images
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1") // liens : on garde le texte
    .replace(/\$\$?([^$]+)\$\$?/g, (_, formula: string) => latexToText(formula))
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
