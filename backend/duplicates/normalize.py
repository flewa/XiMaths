"""Normalisation déterministe des énoncés, première étape de la détection de doublons.

Un même énoncé donne trois sorties :
- canonical : texte où les synonymes de notation sont unifiés (\\R, ℝ et \\mathbb{R} ;
  \\le, \\leqslant et ≤…), entrée de l'embedding E1 ;
- alpha : jetons où les variables sont renommées dans leur ordre d'apparition
  (f, g → F1, F2 ; n, x → V1, V2), entrée de la signature F ;
- abstract : la version alpha où les constantes numériques deviennent NUM,
  entrée de la signature F′, qui repère les variantes paramétriques.
"""

import re
import unicodedata
from dataclasses import dataclass

# Segments mathématiques, du délimiteur le plus long au plus court.
MATH_RE = re.compile(
    r"\$\$(?P<a>.+?)\$\$"
    r"|\\\[(?P<b>.+?)\\\]"
    r"|\\begin\{(?P<env>equation|align|gather|multline)\*?\}(?P<c>.+?)\\end\{(?P=env)\*?\}"
    r"|\\\((?P<d>.+?)\\\)"
    r"|\$(?P<e>.+?)\$",
    re.S,
)
MATH_TOKEN_RE = re.compile(r"\\[A-Za-z]+|\\.|[A-Za-z]|\d+(?:[.,]\d+)?|\S")
TEXT_TOKEN_RE = re.compile(r"[A-Za-z]+|\d+(?:[.,]\d+)?|[^\sA-Za-z0-9.,;:!?'’\"()\[\]«»*#>`_\-]")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")

DOUBLE_STRUCK = {"N": "ℕ", "Z": "ℤ", "Q": "ℚ", "R": "ℝ", "C": "ℂ", "K": "𝕂"}
# \mathbb{R}, \mathbb R, et les macros \R, \N… de XiMaths.
BLACKBOARD_RE = re.compile(r"\\mathbb\s*\{?\s*([A-Z])\s*\}?|\\([NZQRCK])(?![A-Za-z])")
# \operatorname{rg}, \mathrm{d} : un seul jeton, pour ne pas prendre r et g pour des variables.
NAMED_RE = re.compile(r"\\(?:operatorname\*?|mathrm|textrm|mathsf|mathit)\s*\{([^{}]*)\}")
TEXT_IN_MATH_RE = re.compile(r"\\(?:text|textup|textnormal|mbox)\s*\{([^{}]*)\}")
# \frac12 vaut \frac{1}{2}, et non \frac{12}.
FRAC_DIGITS_RE = re.compile(r"\\[dtc]?frac\s*(\d)\s*(\d)")

SYNONYMS = {
    "\\le": "≤", "\\leq": "≤", "\\leqslant": "≤", "⩽": "≤",
    "\\ge": "≥", "\\geq": "≥", "\\geqslant": "≥", "⩾": "≥",
    "\\ne": "≠", "\\neq": "≠",
    "\\dfrac": "\\frac", "\\tfrac": "\\frac", "\\cfrac": "\\frac",
    "\\to": "→", "\\rightarrow": "→", "\\longrightarrow": "→",
    "\\mapsto": "↦", "\\longmapsto": "↦",
    "\\Rightarrow": "⇒", "\\implies": "⇒", "\\Longrightarrow": "⇒",
    "\\Leftrightarrow": "⇔", "\\iff": "⇔", "\\Longleftrightarrow": "⇔",
    "\\infty": "∞", "\\in": "∈", "\\notin": "∉",
    "\\subset": "⊂", "\\subseteq": "⊂", "⊆": "⊂",
    "\\forall": "∀", "\\exists": "∃", "\\emptyset": "∅", "\\varnothing": "∅",
    "\\cap": "∩", "\\cup": "∪", "\\circ": "∘", "\\partial": "∂", "\\nabla": "∇",
    "\\sqrt": "√", "\\sum": "∑", "Σ": "∑", "\\prod": "∏", "\\int": "∫",
    "\\ldots": "…", "\\dots": "…", "\\cdots": "…",
    "\\vert": "|", "\\lvert": "|", "\\rvert": "|", "\\mid": "|",
    "\\Vert": "‖", "\\lVert": "‖", "\\rVert": "‖", "\\|": "‖",
    "\\cdot": "·", "\\times": "×", "\\pm": "±",
    "\\approx": "≈", "\\sim": "∼", "\\equiv": "≡",
    "\\langle": "⟨", "\\rangle": "⟩",
    "\\varepsilon": "\\epsilon", "\\varphi": "\\phi", "\\vartheta": "\\theta", "\\varrho": "\\rho",
    "−": "-",
    # Lettres grecques tapées en Unicode.
    "α": "\\alpha", "β": "\\beta", "γ": "\\gamma", "δ": "\\delta", "ε": "\\epsilon",
    "θ": "\\theta", "λ": "\\lambda", "μ": "\\mu", "π": "\\pi", "ρ": "\\rho",
    "σ": "\\sigma", "φ": "\\phi", "ω": "\\omega",
}
SUPERSCRIPTS = {"²": ("^", "2"), "³": ("^", "3")}
DROPPED = {
    "{", "}", "~", "&", "\\\\", "\\,", "\\;", "\\:", "\\!", "\\ ", "\\quad", "\\qquad",
    "\\left", "\\right", "\\bigl", "\\bigr", "\\Bigl", "\\Bigr", "\\big", "\\Big",
    "\\bigg", "\\Bigg", "\\displaystyle", "\\textstyle", "\\limits", "\\nolimits",
}
# Lettres grecques traitées comme des variables (π est une constante).
GREEK_VARIABLES = {
    f"\\{name}"
    for name in (
        "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi rho "
        "sigma tau phi chi psi omega Gamma Delta Theta Lambda Xi Phi Psi Omega"
    ).split()
}
# Formules d'amorce équivalentes : « démontrer que », « prouver que »… → « montrer que ».
STARTERS = {"demontrer": "montrer", "prouver": "montrer", "etablir": "montrer"}


@dataclass(frozen=True)
class Normalized:
    canonical: str
    alpha: tuple[str, ...]
    abstract: tuple[str, ...]


def _strip_accents(text):
    """é → e. Seules les lettres latines sont touchées : ≠ se décompose aussi en
    = suivi d'une marque combinante, et doit rester ≠."""
    stripped = []
    for char in text:
        base = unicodedata.normalize("NFD", char)[0]
        stripped.append(base if base.isascii() and base.isalpha() else char)
    return "".join(stripped)


def _segments(statement):
    """(est_mathématique, contenu), dans l'ordre de l'énoncé."""
    position = 0
    for match in MATH_RE.finditer(statement):
        if match.start() > position:
            yield False, statement[position : match.start()]
        yield True, next(match[group] for group in "abcde" if match[group] is not None)
        position = match.end()
    if position < len(statement):
        yield False, statement[position:]


def _canonical_symbols(tokens):
    for token in tokens:
        token = SYNONYMS.get(token, token)
        if token in SUPERSCRIPTS:
            yield from SUPERSCRIPTS[token]
        elif token not in DROPPED:
            yield token


def _blackboard(match):
    letter = match[1] or match[2]
    return " " + DOUBLE_STRUCK.get(letter, "\\bb" + letter) + " "


def _math_tokens(source):
    source = FRAC_DIGITS_RE.sub(r"\\frac{\1}{\2}", source)
    source = BLACKBOARD_RE.sub(_blackboard, source)
    source = NAMED_RE.sub(lambda m: " \\op" + re.sub(r"[^A-Za-z]", "", m[1]) + " ", source)
    source = TEXT_IN_MATH_RE.sub(
        lambda m: " " + " ".join(f"\\w{word}" for word in re.findall(r"[a-z]+", m[1].lower())) + " ",
        source,
    )
    tokens = list(_canonical_symbols(MATH_TOKEN_RE.findall(source)))
    # Ponctuation de la phrase placée dans la formule : « $$\sum u_n.$$ ».
    while tokens and tokens[-1] in {".", ",", ";"}:
        tokens.pop()
    return tokens


def _text_tokens(source):
    tokens = []
    for token in _canonical_symbols(TEXT_TOKEN_RE.findall(source)):
        if token.isascii() and token.isalpha():
            token = token.lower()
            token = STARTERS.get(token, token)
        tokens.append(token)
    return tokens


def _is_variable(token):
    return (len(token) == 1 and token.isascii() and token.isalpha()) or token in GREEK_VARIABLES


def _alpha(sequence):
    """Renomme les variables mathématiques dans leur ordre d'apparition. Une lettre
    suivie d'une parenthèse au moins une fois est une fonction (F1, F2…), les autres
    sont des variables (V1, V2…)."""
    functions = {
        token
        for (is_math, token), (_, following) in zip(sequence, sequence[1:])
        if is_math and _is_variable(token) and following == "("
    }
    names = {}
    counts = {"F": 0, "V": 0}
    renamed = []
    for is_math, token in sequence:
        if is_math and _is_variable(token):
            if token not in names:
                kind = "F" if token in functions else "V"
                counts[kind] += 1
                names[token] = f"{kind}{counts[kind]}"
            token = names[token]
        renamed.append(token)
    return tuple(renamed)


def normalize(statement):
    sequence = []
    parts = []
    for is_math, source in _segments(_strip_accents(statement)):
        tokens = _math_tokens(source) if is_math else _text_tokens(source)
        if not tokens:
            continue
        sequence.extend((is_math, token) for token in tokens)
        parts.append(f"$ {' '.join(tokens)} $" if is_math else " ".join(tokens))
    alpha = _alpha(sequence)
    abstract = tuple("NUM" if NUMBER_RE.fullmatch(token) else token for token in alpha)
    return Normalized(canonical=" ".join(parts), alpha=alpha, abstract=abstract)
