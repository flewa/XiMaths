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
