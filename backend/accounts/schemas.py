"""Un membre vu en petit (pseudo, avatar, vitrine) : schémas partagés par les listes
d'exercices, les classements et le profil."""

from ninja import Schema

from gamification.badges import BADGES_BY_SLUG

from .profile import avatar_of


class AvatarOut(Schema):
    # Nom de couleur (voir accounts/profile.py) et symbole : choisi, ou l'initiale du pseudo.
    color: str
    symbol: str
    custom_symbol: bool


class BadgeRefOut(Schema):
    slug: str
    name: str


def featured_refs(user):
    """Vitrine d'un membre. Elle ne contient que des badges obtenus (vérifié à
    l'enregistrement, et un badge obtenu reste acquis)."""
    return [{"slug": slug, "name": BADGES_BY_SLUG[slug].name} for slug in user.featured_badges if slug in BADGES_BY_SLUG]


class MemberRefOut(Schema):
    username: str
    avatar: AvatarOut
    featured_badges: list[BadgeRefOut]

    @staticmethod
    def resolve_avatar(obj):
        return avatar_of(obj)

    @staticmethod
    def resolve_featured_badges(obj):
        return featured_refs(obj)
