"""Vérification d'une adresse email académique, qui donne le badge « Étudiant vérifié ».

On ne garde pas l'adresse académique : seulement son domaine, affiché dans les réglages,
et une empreinte (HMAC) qui empêche qu'une même adresse vérifie plusieurs comptes.

Est académique une adresse d'un établissement du supérieur français reconnu à son
domaine (ACADEMIC_PATTERNS et ACADEMIC_DOMAINS), ou d'un domaine ajouté par la variable
d'environnement ACADEMIC_EXTRA_DOMAINS. Un modérateur peut aussi marquer un compte dans
l'admin.
"""

import re

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac

from config.errors import RuleError

from .models import User

TOKEN_SALT = "ximaths.academic-email"
TOKEN_MAX_AGE = 3 * 24 * 3600  # 3 jours

# Familles de domaines, puis domaines isolés. Un sous-domaine compte aussi
# (etu.univ-lyon1.fr, etu.unistra.fr).
ACADEMIC_PATTERNS = [
    re.compile(pattern)
    for pattern in (
        r"univ-[a-z0-9-]+\.fr",  # univ-lyon1.fr, univ-grenoble-alpes.fr
        r"universite-[a-z0-9-]+\.fr",  # universite-paris-saclay.fr
        r"u-[a-z0-9-]+\.fr",  # u-paris.fr, u-bordeaux.fr
        r"sorbonne-[a-z0-9-]+\.fr",  # sorbonne-universite.fr, sorbonne-nouvelle.fr
        r"ens(-[a-z0-9-]+)?\.fr",  # ens.fr, ens-lyon.fr, ens-paris-saclay.fr
        r"insa-[a-z0-9-]+\.fr",
        r"ec-[a-z]+\.fr",  # écoles centrales
        # Académies : les lycées à classes préparatoires.
        r"ac-[a-z-]+\.fr",
    )
]
ACADEMIC_DOMAINS = frozenset(
    {
        "unistra.fr",
        "unicaen.fr",
        "unilim.fr",
        "unimes.fr",
        "umontpellier.fr",
        "uca.fr",
        "uvsq.fr",
        "uha.fr",
        "parisnanterre.fr",
        "utc.fr",
        "utt.fr",
        "cnam.fr",
        "psl.eu",
        "polytechnique.edu",
        "polytechnique.fr",
        "centralesupelec.fr",
        "enpc.fr",
        "ensae.fr",
        "ensta-paris.fr",
        "telecom-paris.fr",
        "imt-atlantique.fr",
    }
)


def _domain(email):
    return email.rsplit("@", 1)[1]


def is_academic(email):
    labels = _domain(email).split(".")
    # Le domaine entier, puis ses parents : « etu.univ-lyon1.fr », puis « univ-lyon1.fr ».
    candidates = [".".join(labels[start:]) for start in range(len(labels) - 1)]
    domains = ACADEMIC_DOMAINS | set(settings.ACADEMIC_EXTRA_DOMAINS)
    return any(
        candidate in domains or any(pattern.fullmatch(candidate) for pattern in ACADEMIC_PATTERNS)
        for candidate in candidates
    )


def digest(email):
    """Empreinte de l'adresse : elle reconnaît une adresse déjà utilisée sans la conserver."""
    return salted_hmac(TOKEN_SALT, email.lower(), algorithm="sha256").hexdigest()


def _clean(email):
    email = email.strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        raise RuleError("Cette adresse email n'est pas valide.")
    return email


def _taken(user, email_digest):
    return User.objects.filter(academic_email_digest=email_digest).exclude(pk=user.pk).exists()


def send_academic_link(user, email):
    """Envoie un lien signé à l'adresse académique. Le lien porte le domaine et
    l'empreinte de l'adresse, jamais l'adresse elle-même."""
    email = _clean(email)
    if not is_academic(email):
        raise RuleError(
            "Ce domaine n'est pas reconnu comme celui d'un établissement du supérieur. "
            "Si c'est une erreur, écris à la modération."
        )
    email_digest = digest(email)
    if _taken(user, email_digest):
        raise RuleError("Cette adresse académique a déjà servi à vérifier un autre compte.")
    token = signing.dumps(
        {"uid": user.pk, "digest": email_digest, "domain": _domain(email)}, salt=TOKEN_SALT
    )
    link = f"{settings.FRONTEND_URL}/verifier-email?academique={token}"
    send_mail(
        "Confirme ton adresse académique XiMaths",
        f"Bonjour {user.username},\n\n"
        f"Pour confirmer cette adresse académique et recevoir le badge « Étudiant vérifié », "
        f"ouvre ce lien :\n{link}\n\n"
        "Il est valable 3 jours. XiMaths ne garde pas cette adresse : seulement son domaine.",
        None,
        [email],
    )


def verify_academic(token, *, now=None):
    from gamification.badges import check_badges

    try:
        data = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        raise RuleError("Ce lien a expiré : demande un nouveau lien depuis tes réglages.")
    except signing.BadSignature:
        raise RuleError("Ce lien de vérification n'est pas valide.")
    user = User.objects.filter(pk=data.get("uid"), is_active=True).first()
    if user is None:
        raise RuleError("Ce lien de vérification n'est pas valide.")
    if user.academic_email_digest != data["digest"]:
        if _taken(user, data["digest"]):
            raise RuleError("Cette adresse académique a déjà servi à vérifier un autre compte.")
        user.academic_email_digest = data["digest"]
        user.academic_domain = data["domain"]
        user.academic_verified_at = now or timezone.now()
        try:
            with transaction.atomic():
                user.save(update_fields=["academic_email_digest", "academic_domain", "academic_verified_at"])
        except IntegrityError:
            raise RuleError("Cette adresse académique a déjà servi à vérifier un autre compte.")
    check_badges(user, now=now)
    return user
