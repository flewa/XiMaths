from django.dispatch import Signal

# Envoyé quand un modérateur tranche une paire (arguments : pair, moderator).
# Les signalements de doublon rattachés à la paire s'y résolvent.
pair_decided = Signal()
