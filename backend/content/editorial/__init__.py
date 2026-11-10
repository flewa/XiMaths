"""Exercices de la rédaction, publiés par le compte « XiMaths ».

Énoncés originaux sur des résultats classiques, un fichier par lot. Chaque réponse finale
est lisible par SymPy (training.answers) et a été vérifiée par un calcul indépendant ; un
gabarit de défi donne sa réponse en fonction des paramètres tirés. `manage.py
import_exercises` les publie, en passant par la même validation et la même détection de
doublons qu'un exercice proposé sur le site.
"""

from .lot1 import EXERCISES as LOT1
from .lot2 import EXERCISES as LOT2
from .lot3 import EXERCISES as LOT3

EXERCISES = LOT1 + LOT2 + LOT3
