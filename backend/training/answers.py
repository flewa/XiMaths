"""Vérification d'une réponse finale par SymPy : « 2 », « sqrt(2)/2 », « π/4 », « 1,5 ».

Les réponses viennent des utilisateurs : seule une petite grammaire passe (chiffres,
opérateurs, parenthèses, une lettre par variable et quelques fonctions connues)
avant toute analyse par SymPy, qui évalue du Python.
"""

import re

from sympy import (
    E,
    Add,
    Float,
    I,
    Integer,
    Mul,
    Pow,
    Rational,
    Symbol,
    cos,
    exp,
    log,
    oo,
    pi,
    simplify,
    sin,
    sqrt,
    tan,
)
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

MAX_LENGTH = 100
# Garde contre les calculs interminables : 9^9^9 bloquerait le serveur.
MAX_EXPONENT = 100
ALLOWED_RE = re.compile(r"^[0-9A-Za-z+\-*/^()., ]*$")
NAMES = {
    "sqrt": sqrt,
    "exp": exp,
    "ln": log,
    "log": log,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "pi": pi,
    "e": E,
    "i": I,
    "oo": oo,
    "inf": oo,
    "infty": oo,
}
TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application, convert_xor)
# Tout ce que l'expression analysée peut appeler : ni builtins, ni module.
GLOBALS = {
    "__builtins__": {},
    "Integer": Integer,
    "Float": Float,
    "Rational": Rational,
    "Symbol": Symbol,
    # Écrits explicitement par parse_expr quand l'évaluation est désactivée.
    "Add": Add,
    "Mul": Mul,
    "Pow": Pow,
}


def _parse(text):
    """Expression SymPy, ou None si le texte sort de la grammaire autorisée."""
    # √2 → sqrt(2) ; √(…) → sqrt(…).
    text = re.sub(r"√\s*(\d+|[A-Za-z])", r"sqrt(\1)", text.strip()).replace("√", "sqrt")
    text = text.replace("π", "pi").replace("∞", "oo").replace("−", "-")
    # « R = 2 » : on garde le membre de droite.
    text = text.rsplit("=", 1)[-1].strip()
    # Virgule décimale française, seulement entre deux chiffres.
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)
    if not text or len(text) > MAX_LENGTH or not ALLOWED_RE.match(text):
        return None
    # Un point n'est permis qu'entre deux chiffres : pas d'accès aux attributs.
    if re.search(r"\.(?!\d)|(?<!\d)\.", text) or "," in text:
        return None
    for word in re.findall(r"[A-Za-z]+", text):
        if word not in NAMES and len(word) > 1:
            return None
    local = dict(NAMES)
    for letter in set(re.findall(r"\b[A-Za-z]\b", text)) - NAMES.keys():
        local[letter] = Symbol(letter)
    try:
        expression = parse_expr(
            text,
            local_dict=local,
            global_dict=dict(GLOBALS),
            transformations=TRANSFORMATIONS,
            evaluate=False,
        )
    except Exception:
        return None
    return expression if _small_powers(expression) else None


def _small_powers(expression):
    """Pas de tour de puissances, et des exposants numériques modestes."""
    for power in expression.atoms(Pow):
        exponent = power.exp
        if exponent.atoms(Pow):
            return False
        if exponent.is_number and abs(exponent.evalf(5)) > MAX_EXPONENT:
            return False
    return True


def check_answer(given, expected):
    """True ou False si les deux réponses se comparent ; None sinon (pas de réponse
    attendue, ou une réponse qui ne se lit pas)."""
    if not expected.strip():
        return None
    target = _parse(expected)
    answer = _parse(given)
    if target is None or answer is None:
        return None
    try:
        if answer == target:  # couvre aussi les infinis, dont la différence n'est pas définie
            return True
        return bool(simplify(answer - target) == 0)
    except Exception:
        return None
