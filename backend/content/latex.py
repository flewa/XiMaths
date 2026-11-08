"""Contrôle des commandes LaTeX : pas de macros libres ni de commandes qui sortent du texte."""

import re

FORBIDDEN_COMMANDS = (
    # Définitions de macros : on fournit \R, \N, \Z, \Q, \C, \K à la place.
    "def",
    "gdef",
    "edef",
    "xdef",
    "let",
    "newcommand",
    "renewcommand",
    "providecommand",
    "DeclareMathOperator",
    # Liens, fichiers et HTML : passer par le Markdown ou l'envoi d'images.
    "href",
    "url",
    "includegraphics",
    "input",
    "include",
    "htmlClass",
    "htmlId",
    "htmlStyle",
    "htmlData",
)

_PATTERN = re.compile(r"\\(" + "|".join(FORBIDDEN_COMMANDS) + r")(?![A-Za-z])")


def forbidden_commands(text):
    """Commandes interdites présentes dans `text`, triées et sans doublon (ex. ['\\def'])."""
    return sorted({f"\\{name}" for name in _PATTERN.findall(text)})


# ---------------------------------------------------------------- formules des titres en texte

# Ce que l'Unicode sait écrire en exposant et en indice.
_SUPERSCRIPTS = dict(zip("0123456789+−=()nikx", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱᵏˣ"))
_SUBSCRIPTS = dict(zip("0123456789+−=()aeoxnk", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓₙₖ"))
_SYMBOLS = {
    "R": "ℝ", "Z": "ℤ", "Q": "ℚ", "N": "ℕ", "C": "ℂ", "K": "𝕂",
    "infty": "∞", "times": "×", "circ": "∘", "cdot": "·", "in": "∈", "notin": "∉",
    "dots": "…", "ldots": "…", "cdots": "⋯", "ell": "ℓ", "to": "→", "mapsto": "↦",
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "neq": "≠", "ne": "≠", "sim": "∼",
    "lfloor": "⌊", "rfloor": "⌋", "sum": "∑", "prod": "∏", "int": "∫", "partial": "∂",
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "varepsilon": "ε", "epsilon": "ε",
    "theta": "θ", "lambda": "λ", "mu": "μ", "pi": "π", "sigma": "σ", "varphi": "φ", "phi": "φ",
    "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Omega": "Ω",
    ",": " ", ";": " ", "!": "", " ": " ", "{": "{", "}": "}",
}
_FRAKTUR = {"S": "𝔖", "A": "𝔄"}
_TITLE_MATH = re.compile(r"\$([^$]+)\$")


def _group(source, start):
    """L'argument qui commence en `start` : un groupe {…} (accolades imbriquées), une
    commande, ou un caractère. Renvoie (argument, position suivante)."""
    while start < len(source) and source[start] == " ":
        start += 1
    if start >= len(source):
        return "", start
    if source[start] == "{":
        depth = 0
        for index in range(start, len(source)):
            depth += {"{": 1, "}": -1}.get(source[index], 0)
            if depth == 0:
                return source[start + 1 : index], index + 1
        return source[start + 1 :], len(source)
    if source[start] == "\\":
        match = re.match(r"\\([A-Za-z]+|.)", source[start:])
        return match.group(0), start + match.end()
    return source[start], start + 1


def _scripted(text, table, mark):
    if text and all(char in table for char in text):
        return "".join(table[char] for char in text)
    return f"{mark}{text}" if len(text) == 1 else f"{mark}({text})"


def _wrapped(text):
    return text if len(text) == 1 or text.isalnum() else f"({text})"


def _formula(source):
    """Une formule LaTeX en texte : exposants et indices Unicode, symboles, racines."""
    out = []
    index = 0
    while index < len(source):
        char = source[index]
        if char == "\\":
            match = re.match(r"\\([A-Za-z]+|.)", source[index:])
            name = match.group(1)
            index += match.end()
            if name == "sqrt":
                argument, index = _group(source, index)
                out.append("√" + _wrapped(_formula(argument)))
            elif name == "frac":
                top, index = _group(source, index)
                bottom, index = _group(source, index)
                out.append(f"{_wrapped(_formula(top))}/{_wrapped(_formula(bottom))}")
            elif name == "binom":
                top, index = _group(source, index)
                bottom, index = _group(source, index)
                out.append(f"({_formula(bottom)} parmi {_formula(top)})")
            elif name == "mathfrak":
                argument, index = _group(source, index)
                out.append(_FRAKTUR.get(argument, argument))
            elif name in ("operatorname", "mathrm", "text", "mathbf", "mathcal"):
                argument, index = _group(source, index)
                out.append(_formula(argument))
            elif name in ("left", "right", "big", "Big"):
                continue
            else:
                out.append(_SYMBOLS.get(name, name))
        elif char in "^_":
            argument, index = _group(source, index + 1)
            table = _SUPERSCRIPTS if char == "^" else _SUBSCRIPTS
            out.append(_scripted(_formula(argument), table, char))
        elif char == "-":
            out.append("−")
            index += 1
        elif char in "{}":
            index += 1
        else:
            out.append(char)
            index += 1
    return "".join(out)


def plain_math(text):
    """Le texte d'un titre (ou d'une notification) avec ses formules $…$ écrites en clair :
    « Reste de $3^{100}$ modulo 7 » devient « Reste de 3¹⁰⁰ modulo 7 ». Pour l'onglet du
    navigateur, les moteurs de recherche, les notifications et les emails."""
    converted = _TITLE_MATH.sub(lambda match: _formula(match.group(1)), text)
    converted = re.sub(r"⌊\s+", "⌊", re.sub(r"\s+⌋", "⌋", converted))
    return re.sub(r"[ \t]+", " ", converted).strip()


def title_problems(title):
    """Erreurs d'un titre : formules non fermées, commandes interdites."""
    problems = []
    if title.count("$") % 2:
        problems.append("Une formule du titre n'est pas fermée : écris-la entre deux $.")
    forbidden = forbidden_commands(title)
    if forbidden:
        problems.append(f"Commandes LaTeX non autorisées dans le titre : {', '.join(forbidden)}.")
    return problems
