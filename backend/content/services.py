"""Règles métier des contenus : publication, relecture par les pairs, votes.

Chaque fonction applique une règle du document de conception et crédite les
points correspondants dans le ledger.
"""

import difflib
import math
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, F, Q
from django.utils import timezone

from accounts.links import are_linked, check_vote_reciprocity, linked_ids
from accounts.permissions import is_moderator
from config.errors import RuleError
from gamification.badges import check_badges
from gamification.models import PointTransaction
from gamification.scoring import PER_TARGET_CAPS, POINTS, validated_solution_points
from gamification.services import award, points_from
from gamification.trust import promote
from moderation.comprehension import EXTRA_REVIEW, assess, points_on_hold
from notifications.models import Notification
from notifications.services import notify

from . import photos
from .models import Exercise, ModelCopyView, Review, Solution, Vote

Kind = Notification.Kind

User = get_user_model()
Reason = PointTransaction.Reason

REVIEWERS_PER_SOLUTION = 3
# Verdicts qui jugent la copie juste : une copie n'est validée (et ne rapporte de points)
# que si tous ses relecteurs, trois au moins, la jugent ainsi.
SOUND_VERDICTS = {Review.Verdict.CORRECT, Review.Verdict.GAPS}
# Les votes d'un compte de moins de 7 jours ne rapportent rien.
NEW_ACCOUNT_DAYS = 7
VOTE_WINDOW_DAYS = 30
# Poids d'un vote selon le nombre de votes déjà donnés au même auteur sur 30 jours.
REPEATED_VOTE_WEIGHTS = [Decimal(1), Decimal("0.5"), Decimal("0.25")]
# Au-delà, un votant n'est plus tiré au sort pour relire cet auteur.
MAX_VOTES_FOR_AUTHOR_AS_REVIEWER = 3


def can_review(user):
    """Peut relire : un relecteur (niveau de confiance 2 ou plus), un enseignant vérifié,
    ou l'équipe du site."""
    return user.verified_teacher or user.trust_level >= User.TrustLevel.REVIEWER or is_moderator(user)


@transaction.atomic
def publish_exercise(exercise, *, now=None):
    if exercise.status != Exercise.Status.DRAFT:
        raise RuleError("Seul un brouillon peut être publié.")
    now = now or timezone.now()
    exercise.status = Exercise.Status.PUBLISHED
    exercise.published_at = now
    exercise.save(update_fields=["status", "published_at", "updated_at"])
    # Pas de points à la publication : un exercice bâclé n'en rapporterait pas moins. Les +5
    # viennent à sa première copie validée d'un autre membre (_validate).
    return exercise


def saw_model_copy(solution):
    """Vrai si l'auteur a déjà ouvert la copie modèle de l'exercice."""
    return ModelCopyView.objects.filter(exercise_id=solution.exercise_id, user_id=solution.author_id).exists()


def model_copy(exercise):
    """La copie modèle de l'exercice, ou None : choisie par l'équipe, toujours validée,
    et dont l'auteur maintient son accord."""
    return (
        Solution.objects.filter(
            exercise=exercise, model_at__isnull=False, model_consent=True, status=Solution.Status.VALIDATED
        )
        .order_by("-model_at")
        .first()
    )


def model_candidates(exercise):
    """Copies que l'équipe peut choisir : validées, avec l'accord de leur auteur, pas générées."""
    return (
        Solution.objects.filter(exercise=exercise, status=Solution.Status.VALIDATED, model_consent=True)
        .exclude(ai_usage=Solution.AiUsage.GENERATED)
        .order_by("-model_at", "-validated_at")
    )


@transaction.atomic
def choose_model_copy(solution, chosen, *, now=None):
    """L'équipe choisit (ou retire) la copie modèle d'un exercice : une seule à la fois."""
    if not chosen:
        solution.model_at = None
        solution.save(update_fields=["model_at", "updated_at"])
        return solution
    if not model_candidates(solution.exercise).filter(pk=solution.pk).exists():
        raise RuleError("Cette copie ne peut pas servir de modèle : il faut qu'elle soit validée et que son auteur soit d'accord.")
    Solution.objects.filter(exercise=solution.exercise, model_at__isnull=False).exclude(pk=solution.pk).update(model_at=None)
    already = solution.model_at is not None
    solution.model_at = now or timezone.now()
    solution.save(update_fields=["model_at", "updated_at"])
    if not already:
        notify(
            solution.author,
            Kind.SOLUTION_RECOMMENDED,
            "Ta copie a été choisie comme copie modèle",
            f"Elle est montrée, sans ton pseudo, aux membres qui ont envoyé leur copie sur « {solution.exercise.title} ». "
            "Tu peux retirer ton accord à tout moment, depuis la page de l'exercice.",
            f"/exercices/{solution.exercise_id}",
            now=now,
        )
    return solution


def set_model_consent(solution, consent):
    """L'auteur donne ou retire son accord. Retiré, la copie cesse aussitôt d'être le modèle."""
    solution.model_consent = consent
    if not consent:
        solution.model_at = None
    solution.save(update_fields=["model_consent", "model_at", "updated_at"])
    return solution


def can_open_model_copy(user, exercise):
    """La copie modèle se débloque une fois sa propre copie envoyée ; l'auteur de l'exercice
    et l'équipe la voient aussi."""
    if not user.is_authenticated:
        return False
    if exercise.author_id == user.pk or is_moderator(user):
        return True
    return Solution.objects.filter(exercise=exercise, author=user).exclude(status=Solution.Status.DRAFT).exists()


@transaction.atomic
def publish_solution(solution, *, rng=None, now=None):
    """Publie une tentative, puis tire au sort ses relecteurs. Elle ne rapporte rien en
    soi : les points viennent du consensus des relecteurs (evaluate_solution)."""
    if solution.status != Solution.Status.DRAFT:
        raise RuleError("Seul un brouillon peut être publié.")
    if solution.exercise.status != Exercise.Status.PUBLISHED:
        raise RuleError("L'exercice n'est pas publié.")
    now = now or timezone.now()
    solution.status = Solution.Status.UNDER_REVIEW
    solution.published_at = now
    solution.after_model = saw_model_copy(solution)
    solution.save(update_fields=["status", "published_at", "after_model", "updated_at"])
    if solution.author:
        # « Premier pas » : la première copie envoyée, sans point.
        check_badges(solution.author, now=now)
    drawn = assign_reviewers(solution, rng=rng, now=now)
    # Solution classée ou à fort enjeu : score d'intégrité, puis une relecture de plus
    # ou une question de compréhension au-delà des seuils.
    if assess(solution, now=now) == EXTRA_REVIEW:
        assign_reviewers(solution, k=1, rng=rng, now=now)
    # Pas assez de relecteurs pour cette copie : l'équipe est prévenue tout de suite, sans
    # attendre trois jours (au lancement, les relecteurs sont rares).
    if len(drawn) < REVIEWERS_PER_SOLUTION:
        alert_team(now=now)
    return solution


def eligible_reviewers(solution, *, now=None):
    """Relecteurs possibles : niveau de confiance 2 ou plus et niveau déclaré au moins
    égal à celui de l'exercice (ou enseignant vérifié), hors auteur, comptes liés à
    l'auteur et votants trop fréquents pour lui."""
    now = now or timezone.now()
    author_id = solution.author_id
    year = solution.exercise.primary_level.year
    frequent_voters = [
        row["voter"]
        for row in Vote.objects.filter(
            created_at__gte=now - timedelta(days=VOTE_WINDOW_DAYS)
        )
        .filter(Q(exercise__author_id=author_id) | Q(solution__author_id=author_id))
        .values("voter")
        .annotate(n=Count("pk"))
        .filter(n__gt=MAX_VOTES_FOR_AUTHOR_AS_REVIEWER)
    ]
    return (
        User.objects.filter(is_active=True, status=User.Status.ACTIVE)
        .filter(
            Q(verified_teacher=True)
            | Q(
                trust_level__gte=User.TrustLevel.REVIEWER,
                declared_level__year__gte=year,
            )
        )
        .exclude(pk=author_id)
        .exclude(pk__in=linked_ids(author_id))
        .exclude(pk__in=frequent_voters)
        .exclude(reviews__solution=solution)
    )


def assign_reviewers(solution, *, k=REVIEWERS_PER_SOLUTION, rng=None, now=None):
    """Tire au sort k relecteurs : l'auteur ne choisit pas qui le relit."""
    candidates = sorted(eligible_reviewers(solution, now=now).values_list("pk", flat=True))
    rng = rng or random.SystemRandom()
    chosen = rng.sample(candidates, min(k, len(candidates)))
    Review.objects.bulk_create(
        [Review(solution=solution, reviewer_id=pk, assigned=True, round=solution.review_round) for pk in chosen]
    )
    for reviewer in User.objects.filter(pk__in=chosen):
        notify(
            reviewer,
            Kind.REVIEW_ASSIGNED,
            "Une solution t'attend en relecture",
            f"Exercice « {solution.exercise.title} ». Relecture anonyme, à rendre sous 72 heures.",
            "/relectures",
            now=now,
        )
    return chosen


@transaction.atomic
def submit_review(review, verdict, *, feedback="", now=None):
    """Enregistre un verdict, rendu à l'aveugle, puis réévalue la solution. L'auteur est
    prévenu à chaque relecture : il en lit aussitôt le verdict et le commentaire."""
    if review.submitted_at is not None:
        raise RuleError("Cette relecture est déjà rendue.")
    if review.expired_at is not None or review.round != review.solution.review_round:
        raise RuleError("Cette relecture a été confiée à quelqu'un d'autre.")
    if review.solution.status != Solution.Status.UNDER_REVIEW:
        # Décidée entre-temps (par les autres relecteurs, ou par l'équipe).
        raise RuleError("Cette copie n'est plus en relecture.")
    if review.reviewer_id == review.solution.author_id:
        raise PermissionDenied("On ne relit pas sa propre solution.")
    if not can_review(review.reviewer):
        raise PermissionDenied("Niveau de confiance insuffisant pour relire.")
    review.verdict = verdict
    review.feedback = feedback
    review.submitted_at = now or timezone.now()
    review.save()
    solution = review.solution
    status = evaluate_solution(solution, now=now)
    # La dernière relecture conclut : la notification de validation ou de reprise suffit.
    if status == Solution.Status.UNDER_REVIEW:
        done, expected = review_progress(solution)
        notify(
            solution.author,
            Kind.SOLUTION_REVIEWED,
            "Ta copie a été relue",
            f"Un relecteur a corrigé ta copie de « {solution.exercise.title} » "
            f"({done} relecture{'s' if done > 1 else ''} sur {expected}). Son commentaire t'attend.",
            f"/exercices/{solution.exercise_id}",
            now=now,
        )
    return status


def review_progress(solution):
    """(relectures rendues, relectures attendues) pour le tour en cours ; au moins trois
    sont attendues, même si le tirage n'a pas encore trouvé assez de relecteurs."""
    reviews = current_reviews(solution)
    assigned = reviews.filter(assigned=True, expired_at=None)
    done = reviews.exclude(submitted_at=None).count()
    expected = max(assigned.count() + reviews.filter(assigned=False).count(), REVIEWERS_PER_SOLUTION)
    return done, expected


def current_reviews(solution):
    """Relectures du tour en cours : une révision importante en ouvre un nouveau."""
    return solution.reviews.filter(round=solution.review_round)


def team_verdicts(solution):
    """Verdicts rendus par l'équipe du site sur le tour en cours."""
    submitted = current_reviews(solution).exclude(submitted_at=None).select_related("reviewer")
    return [review.verdict for review in submitted if is_moderator(review.reviewer)]


def evaluate_solution(solution, *, now=None):
    """Règle du consensus : une fois rendues toutes les relectures tirées au sort (trois au
    moins), la copie est validée si tous les relecteurs la jugent juste (« correcte » ou
    « correcte avec lacunes »), et rapporte alors ses points ; sinon elle est à reprendre.

    Le filet : une relecture de l'équipe du site vaut décision, sans attendre les autres.
    Tant que les relecteurs manquent, aucune copie ne reste ainsi sans réponse.
    Renvoie le statut de la solution."""
    if solution.status != Solution.Status.UNDER_REVIEW:
        return solution.status
    team = team_verdicts(solution)
    if team:
        if all(verdict in SOUND_VERDICTS for verdict in team):
            _validate(solution, now=now)
        else:
            _close_as_needs_work(solution, agreeing={Review.Verdict.INCORRECT}, now=now)
        return solution.status
    reviews = current_reviews(solution)
    assigned = reviews.filter(assigned=True, expired_at=None)
    if assigned.filter(submitted_at=None).exists() or assigned.count() < REVIEWERS_PER_SOLUTION:
        return solution.status
    verdicts = list(reviews.exclude(submitted_at=None).values_list("verdict", flat=True))
    sound = sum(verdict in SOUND_VERDICTS for verdict in verdicts)
    if sound == len(verdicts):
        _validate(solution, now=now)
    else:
        # Sans consensus, les relecteurs qui rejoignent la majorité sont dans le vrai.
        unsound = len(verdicts) - sound
        if unsound > sound:
            agreeing = {Review.Verdict.INCORRECT}
        elif sound > unsound:
            agreeing = SOUND_VERDICTS
        else:
            agreeing = set()
        _close_as_needs_work(solution, agreeing=agreeing, now=now)
    return solution.status


def award_author_points(solution, *, now=None):
    """Points de l'auteur d'une solution validée : le barème libre, ou les 40 % restants
    d'un défi. Idempotent ; appelé aussi quand une question de compréhension est réussie."""
    if solution.author is None:
        return
    # Envoyée après avoir vu la copie modèle : elle peut être validée, pas rapporter de points.
    if solution.after_model:
        return
    exercise = solution.exercise
    level = exercise.primary_level
    session = getattr(solution, "timed_session", None)
    if session is not None and session.challenge_id:
        award(
            solution.author,
            Reason.CHALLENGE_JUSTIFIED,
            session,
            amount=session.justification_points,
            level=level,
            now=now,
        )
        return
    if solution.ai_usage == Solution.AiUsage.GENERATED:
        return
    award(
        solution.author,
        Reason.SOLUTION_VALIDATED,
        solution,
        amount=validated_solution_points(exercise.difficulty, solution.ai_usage),
        level=level,
        now=now,
    )
    earlier = Solution.objects.filter(
        exercise=exercise, status=Solution.Status.VALIDATED, validated_at__lt=solution.validated_at
    ).exclude(pk=solution.pk)
    if not earlier.exists():
        award(solution.author, Reason.FIRST_VALIDATED, solution, level=level, now=now)


def _validate(solution, *, now=None):
    now = now or timezone.now()
    solution.status = Solution.Status.VALIDATED
    solution.validated_at = now
    solution.save(update_fields=["status", "validated_at", "updated_at"])

    exercise = solution.exercise
    level = exercise.primary_level
    generated = solution.ai_usage == Solution.AiUsage.GENERATED
    earlier = Solution.objects.filter(
        exercise=exercise, status=Solution.Status.VALIDATED
    ).exclude(pk=solution.pk)

    # Une question de compréhension en cours retient les points de l'auteur.
    if not points_on_hold(solution):
        award_author_points(solution, now=now)

    # La première copie validée d'un autre membre montre que l'exercice tient : son auteur
    # reçoit alors les points de publication, une seule fois.
    exercise_author = exercise.author
    if (
        exercise_author
        and exercise_author.pk != solution.author_id
        and not generated
        and not PointTransaction.objects.filter(
            user=exercise_author, reason=Reason.EXERCISE_PUBLISHED, source_type="content.exercise", source_id=exercise.pk
        ).exists()
    ):
        award(exercise_author, Reason.EXERCISE_PUBLISHED, exercise, level=level, now=now)

    # L'auteur de l'exercice gagne +3 par auteur de solution distinct, 30 au plus.
    if (
        exercise_author
        and exercise_author.pk != solution.author_id
        and not generated
        and not earlier.filter(author_id=solution.author_id).exists()
    ):
        already = points_from(exercise_author, Reason.EXERCISE_SOLVED, exercise.solutions.all())
        amount = min(
            POINTS[Reason.EXERCISE_SOLVED],
            PER_TARGET_CAPS[Reason.EXERCISE_SOLVED] - already,
        )
        if amount > 0:
            award(
                exercise_author,
                Reason.EXERCISE_SOLVED,
                solution,
                amount=amount,
                level=level,
                now=now,
            )

    _settle_reviews(solution, agreeing=SOUND_VERDICTS, now=now)
    check_badges(solution.author, now=now)
    promote(solution.author, now=now)
    url = f"/exercices/{exercise.pk}"
    notify(
        solution.author,
        Kind.SOLUTION_VALIDATED,
        "Ta copie est validée",
        f"Ta copie de « {exercise.title} » a été jugée juste : tes points sont crédités.",
        url,
        now=now,
    )
    if exercise_author and exercise_author.pk != solution.author_id:
        check_badges(exercise_author, now=now)
        if not generated:
            notify(
                exercise_author,
                Kind.EXERCISE_SOLVED,
                "Ton exercice a une nouvelle solution validée",
                f"« {exercise.title} » vient d'être résolu par un membre.",
                url,
                now=now,
            )


def _close_as_needs_work(solution, *, agreeing, now=None):
    solution.status = Solution.Status.NEEDS_WORK
    solution.save(update_fields=["status", "updated_at"])
    _settle_reviews(solution, agreeing=agreeing, now=now)
    notify(
        solution.author,
        Kind.SOLUTION_NEEDS_WORK,
        "Ta copie est à reprendre",
        f"Ta copie de « {solution.exercise.title} » n'a pas été jugée juste. "
        "Lis les commentaires de relecture, puis renvoie-la : les points viennent avec la validation.",
        f"/exercices/{solution.exercise_id}",
        now=now,
    )


def _settle_reviews(solution, *, agreeing, now=None):
    """Marque la concordance de chaque relecture et rémunère les relecteurs concordants."""
    level = solution.exercise.primary_level
    for review in current_reviews(solution).exclude(submitted_at=None).select_related("reviewer"):
        review.agrees_with_consensus = review.verdict in agreeing
        review.save(update_fields=["agrees_with_consensus"])
        if review.agrees_with_consensus:
            award(review.reviewer, Reason.REVIEW_AGREED, review, level=level, now=now)
        check_badges(review.reviewer, now=now)
        promote(review.reviewer, now=now)


def vote_weight(voter, author, *, now=None):
    now = now or timezone.now()
    if voter.date_joined > now - timedelta(days=NEW_ACCOUNT_DAYS) or are_linked(voter, author):
        return Decimal(0)
    previous = (
        Vote.objects.filter(
            voter=voter, created_at__gte=now - timedelta(days=VOTE_WINDOW_DAYS)
        )
        .filter(Q(exercise__author=author) | Q(solution__author=author))
        .count()
    )
    if previous < len(REPEATED_VOTE_WEIGHTS):
        return REPEATED_VOTE_WEIGHTS[previous]
    return Decimal(0)


@transaction.atomic
def cast_vote(voter, *, exercise, now=None):
    """Vote « utile » pour un exercice (les copies sont privées : on ne vote pas pour elles).
    Le poids baisse quand on vote souvent pour le même auteur."""
    author = exercise.author
    if author is not None and author.pk == voter.pk:
        raise PermissionDenied("On ne vote pas pour soi-même.")
    now = now or timezone.now()
    weight = vote_weight(voter, author, now=now) if author else Decimal(0)
    vote = Vote.objects.create(voter=voter, exercise=exercise, weight=weight)
    if weight > 0:
        reason = Reason.EXERCISE_UPVOTED
        already = points_from(author, reason, exercise.votes.exclude(pk=vote.pk))
        amount = min(
            math.floor(POINTS[reason] * weight + Decimal("0.5")),
            PER_TARGET_CAPS[reason] - already,
        )
        if amount > 0:
            award(author, reason, vote, amount=amount, level=exercise.primary_level, now=now)
    # Après le vote : s'il crée le lien, link_accounts neutralise aussi celui-ci.
    check_vote_reciprocity(voter, author)
    return vote


# ---------------------------------------------------------------- délais, volontaires, révisions

REMINDER_AFTER = timedelta(hours=48)
REASSIGN_AFTER = timedelta(hours=72)
# Une révision qui change plus de 20 % du texte repasse en relecture.
REVISION_THRESHOLD = 0.8


def review_deadlines(*, now=None):
    """Relance à 48 h, puis réattribution à 72 h des relectures tirées au sort non
    rendues. Renvoie (relances, réattributions)."""
    now = now or timezone.now()
    late = Review.objects.filter(
        assigned=True,
        submitted_at=None,
        expired_at=None,
        solution__status=Solution.Status.UNDER_REVIEW,
    ).select_related("solution__exercise", "reviewer")
    reminded = reassigned = 0
    for review in late:
        if review.round != review.solution.review_round:
            continue
        age = now - review.assigned_at
        if age >= REASSIGN_AFTER:
            review.expired_at = now
            review.save(update_fields=["expired_at"])
            assign_reviewers(review.solution, k=1, now=now)
            reassigned += 1
        elif age >= REMINDER_AFTER and review.reminded_at is None:
            review.reminded_at = now
            review.save(update_fields=["reminded_at"])
            notify(
                review.reviewer,
                Kind.REVIEW_REMINDER,
                "Une relecture t'attend encore",
                f"Exercice « {review.solution.exercise.title} ». Sans réponse sous 24 heures, "
                "elle sera confiée à quelqu'un d'autre, sans pénalité.",
                "/relectures",
                now=now,
            )
            reminded += 1
    # Tirage incomplet (pas assez de relecteurs possibles à l'envoi) : on complète dès
    # que de nouveaux relecteurs le permettent, sans quoi le consensus n'arriverait jamais.
    for solution in Solution.objects.filter(status=Solution.Status.UNDER_REVIEW):
        active = current_reviews(solution).filter(assigned=True, expired_at=None).count()
        if active < REVIEWERS_PER_SOLUTION:
            assign_reviewers(solution, k=REVIEWERS_PER_SOLUTION - active, now=now)
    return reminded, reassigned


# Une copie sans décision après ce délai : l'équipe est prévenue, une fois par jour.
TEAM_ALERT_AFTER = timedelta(hours=72)
TEAM_ALERT_EVERY = timedelta(hours=20)


def with_active_reviews(queryset):
    """Annote chaque copie du nombre de relectures en cours ou rendues pour son tour
    (`active_reviews`), réattribuées exclues."""
    return queryset.annotate(
        active_reviews=Count("reviews", filter=Q(reviews__round=F("review_round"), reviews__expired_at=None))
    )


def waiting_solutions(*, now=None):
    """Copies qui attendent l'équipe : en relecture depuis plus de 72 heures (depuis l'envoi,
    ou la dernière révision), ou sans assez de relecteurs pour atteindre le consensus."""
    now = now or timezone.now()
    return with_active_reviews(Solution.objects.filter(status=Solution.Status.UNDER_REVIEW)).filter(
        Q(updated_at__lte=now - TEAM_ALERT_AFTER) | Q(active_reviews__lt=REVIEWERS_PER_SOLUTION)
    )


def alert_team(*, now=None):
    """Prévient l'équipe du site, au plus une fois par jour, des copies qui attendent
    depuis plus de 72 heures : elle peut les corriger elle-même, sa relecture vaut décision.
    Renvoie le nombre de personnes prévenues."""
    now = now or timezone.now()
    waiting = waiting_solutions(now=now).count()
    if waiting == 0:
        return 0
    team = User.objects.filter(is_active=True, status=User.Status.ACTIVE).filter(
        Q(is_staff=True) | Q(trust_level__gte=User.TrustLevel.MODERATOR)
    )
    alerted = 0
    for member in team:
        recent = Notification.objects.filter(
            user=member, kind=Kind.TEAM_ALERT, created_at__gte=now - TEAM_ALERT_EVERY
        ).exists()
        if recent:
            continue
        notify(
            member,
            Kind.TEAM_ALERT,
            "Une copie attend l'équipe" if waiting == 1 else f"{waiting} copies attendent l'équipe",
            "Relecteurs trop peu nombreux, ou plus de 3 jours d'attente. Tu peux la corriger toi-même "
            "depuis la page Relectures : une relecture de l'équipe vaut décision.",
            "/relectures",
            email=True,
            now=now,
        )
        alerted += 1
    return alerted


@transaction.atomic
def volunteer_review(solution, user):
    """Relecture choisie, sans tirage au sort : celle d'un relecteur s'ajoute aux relectures
    tirées au sort ; celle de l'équipe du site vaut décision (evaluate_solution)."""
    if solution.status != Solution.Status.UNDER_REVIEW:
        raise RuleError("Cette solution n'est pas en relecture.")
    if solution.author_id == user.pk or are_linked(user, solution.author):
        raise PermissionDenied("On ne relit pas sa propre solution, ni celle d'un compte lié.")
    if not can_review(user):
        raise PermissionDenied("Les relectures sont ouvertes à partir du niveau Relecteur.")
    review, created = Review.objects.get_or_create(
        solution=solution,
        reviewer=user,
        defaults={"assigned": False, "round": solution.review_round},
    )
    if not created:
        raise RuleError("Tu relis déjà cette solution.")
    return review


@transaction.atomic
def revise_solution(solution, body, *, upload=None, rng=None, now=None):
    """Révision par l'auteur. Une solution à compléter repart en relecture ; une
    solution validée aussi, si plus de 20 % du texte change ou si de nouvelles photos
    de la copie (`upload`) remplacent les précédentes."""
    if solution.status not in (Solution.Status.NEEDS_WORK, Solution.Status.VALIDATED):
        raise RuleError("Seule une solution à compléter ou validée se révise.")
    body = body.strip()
    ratio = difflib.SequenceMatcher(None, solution.body, body).ratio()
    solution.body = body
    if upload is not None:
        photos.attach(upload, solution)
        ratio = 0.0
    if solution.status == Solution.Status.VALIDATED and ratio >= REVISION_THRESHOLD:
        solution.save(update_fields=["body", "updated_at"])
        return solution, False
    solution.status = Solution.Status.UNDER_REVIEW
    solution.validated_at = None
    solution.review_round += 1
    # Une copie révisée n'est plus celle que l'équipe avait choisie comme modèle.
    solution.model_at = None
    solution.after_model = solution.after_model or saw_model_copy(solution)
    solution.save(
        update_fields=["body", "status", "validated_at", "review_round", "model_at", "after_model", "updated_at"]
    )
    assign_reviewers(solution, rng=rng, now=now)
    return solution, True
