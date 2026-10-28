"""Comptes : vérification de l'adresse, mot de passe oublié, export et suppression (RGPD)."""

import hashlib
import re

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from config.errors import RuleError

from .models import User

EMAIL_TOKEN_SALT = "ximaths.email-verification"
EMAIL_TOKEN_MAX_AGE = 3 * 24 * 3600  # 3 jours


def _email_digest(email):
    # Le lien ne contient qu'une empreinte de l'adresse, pas l'adresse elle-même.
    return hashlib.sha256(email.lower().encode()).hexdigest()[:16]


def email_verification_token(user):
    """Jeton signé, invalidé si l'adresse change entre l'envoi et le clic."""
    return signing.dumps(
        {"uid": user.pk, "email": _email_digest(user.email)}, salt=EMAIL_TOKEN_SALT
    )


def send_verification_email(user):
    link = f"{settings.FRONTEND_URL}/verifier-email?token={email_verification_token(user)}"
    send_mail(
        "Confirme ton adresse email XiMaths",
        f"Bonjour {user.username},\n\n"
        f"Pour confirmer ton adresse et pouvoir contribuer, ouvre ce lien :\n{link}\n\n"
        "Il est valable 3 jours.",
        None,
        [user.email],
    )


def verify_email(token, *, now=None):
    try:
        data = signing.loads(token, salt=EMAIL_TOKEN_SALT, max_age=EMAIL_TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        raise RuleError("Ce lien a expiré : demande un nouvel email de vérification.")
    except signing.BadSignature:
        raise RuleError("Ce lien de vérification n'est pas valide.")
    user = User.objects.filter(pk=data.get("uid")).first()
    if user is None or _email_digest(user.email) != data.get("email"):
        raise RuleError("Ce lien de vérification n'est pas valide.")
    if user.email_verified_at is None:
        user.email_verified_at = now or timezone.now()
        user.save(update_fields=["email_verified_at"])
    return user


# ---------------------------------------------------------------- mot de passe oublié


def send_password_reset(email):
    """Envoie un lien de réinitialisation si un compte actif a cette adresse.
    Ne dit jamais si l'adresse existe : la réponse de l'API est la même."""
    user = User.objects.filter(email__iexact=email.strip(), is_active=True).first()
    if user is None:
        return False
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    link = f"{settings.FRONTEND_URL}/mot-de-passe/nouveau?uid={uid}&token={token}"
    send_mail(
        "Réinitialise ton mot de passe XiMaths",
        f"Bonjour {user.username},\n\n"
        f"Pour choisir un nouveau mot de passe, ouvre ce lien :\n{link}\n\n"
        "Si tu n'as rien demandé, ignore cet email : ton mot de passe ne change pas.",
        None,
        [user.email],
    )
    return True


def reset_password(uid, token, password):
    """Le jeton de Django expire après PASSWORD_RESET_TIMEOUT et ne sert qu'une fois :
    il dépend du mot de passe actuel."""
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)), is_active=True)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None
    if user is None or not default_token_generator.check_token(user, token):
        raise RuleError("Ce lien n'est plus valable : demande un nouvel email.")
    set_password(user, password)
    return user


def set_password(user, password):
    try:
        validate_password(password, user)
    except ValidationError as error:
        raise RuleError(" ".join(error.messages))
    user.set_password(password)
    user.save(update_fields=["password"])


# ---------------------------------------------------------------- RGPD


def export_user_data(user):
    """Toutes les données d'un compte, dans un format lisible et réutilisable."""
    from content.models import Exercise, Review, Solution, Vote
    from gamification.models import Goal, PointTransaction, UserBadge, WeeklyStreak
    from moderation.models import ComprehensionQuestion, Report
    from notifications.models import Notification
    from training.models import TimedSession

    def dates(value):
        return value.isoformat() if value else None

    return {
        "compte": {
            "pseudo": user.username,
            "email": user.email,
            "inscription": dates(user.date_joined),
            "email_verifie": dates(user.email_verified_at),
            "email_academique": (
                {"domaine": user.academic_domain, "verifie": dates(user.academic_verified_at)}
                if user.academic_verified_at
                else None
            ),
            "niveau_declare": user.declared_level.code if user.declared_level else None,
            "niveau_de_confiance": user.get_trust_level_display(),
            "tiers_temps": user.tiers_temps,
            "present_dans_les_classements": user.leaderboard_visible,
            "emails_importants": user.email_notifications,
            "resume_hebdomadaire": user.weekly_digest,
            "notification_defi_du_jour": user.daily_challenge_notifications,
            "objectif_jours_actifs": user.weekly_goal_days,
            "vacances": [dates(user.vacation_from), dates(user.vacation_until)] if user.vacation_from else None,
            "compte_google_lie": bool(user.google_sub),
        },
        "exercices": [
            {"id": e.pk, "titre": e.title, "enonce": e.statement, "statut": e.status, "publie": dates(e.published_at)}
            for e in Exercise.objects.filter(author=user)
        ],
        "solutions": [
            {
                "id": s.pk,
                "exercice": s.exercise_id,
                "texte": s.body,
                "usage_ia": s.ai_usage,
                "statut": s.status,
                "publiee": dates(s.published_at),
            }
            for s in Solution.objects.filter(author=user)
        ],
        "relectures": [
            {"solution": r.solution_id, "verdict": r.verdict, "commentaire": r.feedback, "rendue": dates(r.submitted_at)}
            for r in Review.objects.filter(reviewer=user)
        ],
        "votes": [
            {"exercice": v.exercise_id, "solution": v.solution_id, "date": dates(v.created_at)}
            for v in Vote.objects.filter(voter=user)
        ],
        "points": [
            {"montant": t.amount, "motif": t.reason, "date": dates(t.created_at)}
            for t in PointTransaction.objects.filter(user=user).order_by("created_at")
        ],
        "badges": [{"badge": b.badge, "date": dates(b.awarded_at)} for b in UserBadge.objects.filter(user=user)],
        "signalements": [
            {"exercice": r.exercise_id, "solution": r.solution_id, "motif": r.reason, "precisions": r.details, "statut": r.status}
            for r in Report.objects.filter(reporter=user)
        ],
        "sessions_chronometrees": [
            {
                "exercice": s.exercise_id,
                "duree_s": s.duration_s,
                "temps_s": round(s.elapsed_s),
                "statut": s.status,
                "sorties_onglet": s.focus_losses,
                "collages_externes_caracteres": s.external_paste_chars,
                "debut": dates(s.started_at),
                "defi": s.challenge_id,
                "parametres_tires": s.parameters or None,
            }
            for s in TimedSession.objects.filter(user=user)
        ],
        "semaines": [
            {"semaine": w.week, "objectif": w.goal, "jours_actifs": w.active_days, "statut": w.status}
            for w in WeeklyStreak.objects.filter(user=user)
        ],
        "objectifs": [
            {"intitule": g.title, "cible": g.target, "echeance": dates(g.deadline)}
            for g in Goal.objects.filter(user=user)
        ],
        "questions_de_comprehension": [
            {
                "solution": q.solution_id,
                "question": q.question,
                "reponse": q.answer,
                "statut": q.status,
                "score_integrite": round(q.integrity_score, 2),
            }
            for q in ComprehensionQuestion.objects.filter(user=user)
        ],
        "notifications": [
            {"titre": n.title, "texte": n.body, "date": dates(n.created_at)}
            for n in Notification.objects.filter(user=user)
        ],
    }


@transaction.atomic
def delete_account(user):
    """Efface les données personnelles. Les contributions, sous licence CC BY-SA,
    restent publiées sans pseudo ; le ledger, en ajout seul, reste attaché au
    compte anonymisé pour que les classements passés ne changent pas."""
    from content.models import Exercise, Solution
    from gamification.models import Goal, UserBadge, WeeklyStreak
    from moderation.models import ComprehensionQuestion
    from notifications.models import Notification
    from training.models import TimedSession

    Exercise.objects.filter(author=user).update(author=None)
    Solution.objects.filter(author=user).update(author=None)
    Notification.objects.filter(user=user).delete()
    TimedSession.objects.filter(user=user).delete()
    UserBadge.objects.filter(user=user).delete()
    WeeklyStreak.objects.filter(user=user).delete()
    Goal.objects.filter(user=user).delete()
    ComprehensionQuestion.objects.filter(user=user).delete()
    user.username = f"supprime-{user.pk}"
    user.email = f"supprime-{user.pk}@invalide.ximaths.test"
    user.first_name = user.last_name = ""
    user.set_unusable_password()
    user.is_active = False
    user.email_verified_at = None
    user.academic_verified_at = None
    user.academic_domain = ""
    user.academic_email_digest = None
    user.declared_level = None
    user.google_sub = None
    user.leaderboard_visible = False
    user.tiers_temps = False
    user.email_notifications = False
    user.weekly_digest = False
    user.daily_challenge_notifications = False
    user.vacation_from = user.vacation_until = None
    user.save()
    return user


# ---------------------------------------------------------------- pseudos


def available_username(base):
    """Pseudo libre dérivé d'une adresse ou d'un nom : « marie.curie », « marie.curie2 »…"""
    stem = re.sub(r"[^\w.-]", "", base.split("@")[0])[:26] or "membre"
    if len(stem) < 3:
        stem = f"{stem}-xi"
    candidate, suffix = stem, 1
    while User.objects.filter(username__iexact=candidate).exists():
        suffix += 1
        candidate = f"{stem}{suffix}"
    return candidate
