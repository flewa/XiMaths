"""Profil public d'un membre : avatar (couleur et symbole), présentation, vitrine de
badges et chapitres favoris. Rien de tout cela n'est obligatoire."""

import hashlib
import re

# Couleurs proposées (noms, traduits en teintes par le site) : lisibles en sombre et en clair.
AVATAR_COLORS = ["corail", "ambre", "jade", "ciel", "lavande", "rose", "menthe", "sable"]
# Symboles proposés pour l'avatar ; sans symbole, l'initiale du pseudo.
AVATAR_SYMBOLS = ["∑", "∫", "∂", "∇", "∞", "π", "φ", "λ", "ξ", "ζ", "Ω", "ℵ", "∀", "∃", "√", "ε"]
BIO_MAX_LENGTH = 200
FEATURED_MAX = 3
FAVORITE_TOPICS_MAX = 3
# Une présentation n'est pas un endroit pour de la publicité.
LINK = re.compile(r"https?://|www\.|\b[\w-]+\.(?:com|fr|net|org|io|gg|ly|me)\b", re.IGNORECASE)


def default_color(username):
    """Couleur stable tirée du pseudo, tant que le membre n'en a pas choisi."""
    digest = hashlib.sha256(username.lower().encode()).digest()
    return AVATAR_COLORS[digest[0] % len(AVATAR_COLORS)]


def avatar_of(user):
    return {
        "color": user.avatar_color or default_color(user.username),
        "symbol": user.avatar_symbol or user.username[:1].upper(),
        "custom_symbol": bool(user.avatar_symbol),
    }


def profile_problems(*, bio, avatar_color, avatar_symbol, featured_badges, owned_badges, favorite_topics, known_topics):
    """Erreurs d'un profil soumis, dans l'ordre des champs du formulaire."""
    problems = []
    if avatar_color and avatar_color not in AVATAR_COLORS:
        problems.append("Couleur d'avatar inconnue.")
    if avatar_symbol and avatar_symbol not in AVATAR_SYMBOLS:
        problems.append("Symbole d'avatar inconnu.")
    if len(bio) > BIO_MAX_LENGTH:
        problems.append(f"Ta présentation fait {BIO_MAX_LENGTH} caractères au plus.")
    if LINK.search(bio):
        problems.append("Pas de lien dans ta présentation.")
    if len(featured_badges) > FEATURED_MAX:
        problems.append(f"{FEATURED_MAX} badges au plus dans ta vitrine.")
    if set(featured_badges) - set(owned_badges):
        problems.append("Ta vitrine ne peut montrer que des badges que tu as obtenus.")
    if len(favorite_topics) > FAVORITE_TOPICS_MAX:
        problems.append(f"{FAVORITE_TOPICS_MAX} chapitres favoris au plus.")
    if set(favorite_topics) - set(known_topics):
        problems.append("Chapitre inconnu.")
    return problems
