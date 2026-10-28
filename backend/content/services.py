"""Règles métier des contenus : publication, relecture par les pairs, votes.

Chaque fonction applique une règle du document de conception et crédite les
points correspondants dans le ledger.
"""

import math
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from accounts.links import are_linked, check_vote_reciprocity, linked_ids
from config.errors import RuleError
from gamification.badges import check_badges
from gamification.models import PointTransaction
from gamification.scoring import PER_TARGET_CAPS, POINTS, validated_solution_points
from gamification.services import award, points_from

from .models import Exercise, Review, Solution, Vote

User = get_user_model()
Reason = PointTransaction.Reason

REVIEWERS_PER_SOLUTION = 3
# Validée si Σ poids « correcte » ≥ 2 et Σ poids « incorrecte » < 1.
VALIDATION_THRESHOLD = Decimal(2)
DISSENT_THRESHOLD = Decimal(1)
# Les votes d'un compte de moins de 7 jours ne rapportent rien.
NEW_ACCOUNT_DAYS = 7
VOTE_WINDOW_DAYS = 30
# Poids d'un vote selon le nombre de votes déjà donnés au même auteur sur 30 jours.
REPEATED_VOTE_WEIGHTS = [Decimal(1), Decimal("0.5"), Decimal("0.25")]
# Au-delà, un votant n'est plus tiré au sort pour relire cet auteur.
MAX_VOTES_FOR_AUTHOR_AS_REVIEWER = 3


def reviewer_weight(user, *, assigned=True):
    """Poids d'une relecture : 1 au niveau 2, 1,5 au niveau 3, 2 pour un enseignant
    vérifié ; moitié pour une relecture spontanée."""
    if user.verified_teacher:
        base = Decimal(2)
    elif user.trust_level >= User.TrustLevel.EXPERT:
        base = Decimal("1.5")
    elif user.trust_level >= User.TrustLevel.REVIEWER:
        base = Decimal(1)
    else:
        return Decimal(0)
    return base if assigned else base / 2


@transaction.atomic
def publish_exercise(exercise, *, now=None):
    if exercise.status != Exercise.Status.DRAFT:
        raise RuleError("Seul un brouillon peut être publié.")
    now = now or timezone.now()
    exercise.status = Exercise.Status.PUBLISHED
    exercise.published_at = now
    exercise.save(update_fields=["status", "published_at", "updated_at"])
    if exercise.author:
        award(
            exercise.author,
            Reason.EXERCISE_PUBLISHED,
            exercise,
            level=exercise.primary_level,
            now=now,
        )
    return exercise


@transaction.atomic
def publish_solution(solution, *, rng=None, now=None):
    """Publie une tentative : +2 pour l'effort, puis tirage au sort des relecteurs."""
    if solution.status != Solution.Status.DRAFT:
        raise RuleError("Seul un brouillon peut être publié.")
    if solution.exercise.status != Exercise.Status.PUBLISHED:
        raise RuleError("L'exercice n'est pas publié.")
    now = now or timezone.now()
    solution.status = Solution.Status.UNDER_REVIEW
    solution.published_at = now
    solution.save(update_fields=["status", "published_at", "updated_at"])
    if solution.author:
        award(
            solution.author,
            Reason.SOLUTION_ATTEMPT,
            solution,
            level=solution.exercise.primary_level,
            now=now,
        )
        check_badges(solution.author, now=now)
    assign_reviewers(solution, rng=rng, now=now)
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
        [Review(solution=solution, reviewer_id=pk, assigned=True) for pk in chosen]
    )
    return chosen


@transaction.atomic
def submit_review(review, verdict, *, feedback="", now=None):
    """Enregistre un verdict, rendu à l'aveugle, puis réévalue la solution."""
    if review.submitted_at is not None:
        raise RuleError("Cette relecture est déjà rendue.")
    if review.reviewer_id == review.solution.author_id:
        raise PermissionDenied("On ne relit pas sa propre solution.")
    weight = reviewer_weight(review.reviewer, assigned=review.assigned)
    if weight == 0:
        raise PermissionDenied("Niveau de confiance insuffisant pour relire.")
    review.verdict = verdict
    review.feedback = feedback
    review.weight = weight
    review.submitted_at = now or timezone.now()
    review.save()
    return evaluate_solution(review.solution, now=now)


def tally(solution):
    """Sommes des poids rendus : (vers « correcte », vers « incorrecte »).
    « Correcte avec lacunes » compte pour moitié vers « correcte »."""
    correct = incorrect = Decimal(0)
    for review in solution.reviews.exclude(submitted_at=None):
        if review.verdict == Review.Verdict.CORRECT:
            correct += review.weight
        elif review.verdict == Review.Verdict.GAPS:
            correct += review.weight / 2
        else:
            incorrect += review.weight
    return correct, incorrect


def evaluate_solution(solution, *, now=None):
    """Applique la règle de quorum ; renvoie le statut de la solution."""
    if solution.status != Solution.Status.UNDER_REVIEW:
        return solution.status
    correct, incorrect = tally(solution)
    assigned = solution.reviews.filter(assigned=True)
    if correct >= VALIDATION_THRESHOLD and incorrect < DISSENT_THRESHOLD:
        _validate(solution, now=now)
    elif correct >= DISSENT_THRESHOLD and incorrect >= DISSENT_THRESHOLD:
        # Désaccord : un expert ou un modérateur tranche (resolve_contested).
        solution.status = Solution.Status.CONTESTED
        solution.save(update_fields=["status", "updated_at"])
    elif incorrect >= VALIDATION_THRESHOLD and correct < DISSENT_THRESHOLD:
        _close_as_needs_work(solution, now=now)
    elif assigned.exists() and not assigned.filter(submitted_at=None).exists():
        # Toutes les relectures tirées au sort sont rendues, sans majorité nette.
        _close_as_needs_work(solution, now=now)
    return solution.status


@transaction.atomic
def resolve_contested(solution, moderator, *, validate, now=None):
    if moderator.trust_level < User.TrustLevel.EXPERT:
        raise PermissionDenied("Seuls les experts et les modérateurs tranchent.")
    if solution.status != Solution.Status.CONTESTED:
        raise RuleError("La solution n'est pas contestée.")
    if validate:
        _validate(solution, now=now)
    else:
        _close_as_needs_work(solution, now=now)
    return solution.status


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

    if solution.author and not generated:
        award(
            solution.author,
            Reason.SOLUTION_VALIDATED,
            solution,
            amount=validated_solution_points(exercise.difficulty, solution.ai_usage),
            level=level,
            now=now,
        )
        if not earlier.exists():
            award(solution.author, Reason.FIRST_VALIDATED, solution, level=level, now=now)

    # L'auteur de l'exercice gagne +3 par auteur de solution distinct, 30 au plus.
    exercise_author = exercise.author
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

    _settle_reviews(solution, agreeing={Review.Verdict.CORRECT, Review.Verdict.GAPS}, now=now)
    check_badges(solution.author, now=now)
    if exercise_author and exercise_author.pk != solution.author_id:
        check_badges(exercise_author, now=now)


def _close_as_needs_work(solution, *, now=None):
    solution.status = Solution.Status.NEEDS_WORK
    solution.save(update_fields=["status", "updated_at"])
    _settle_reviews(
        solution, agreeing={Review.Verdict.INCORRECT, Review.Verdict.GAPS}, now=now
    )


def _settle_reviews(solution, *, agreeing, now=None):
    """Marque la concordance de chaque relecture et rémunère les relecteurs concordants."""
    level = solution.exercise.primary_level
    for review in solution.reviews.exclude(submitted_at=None).select_related("reviewer"):
        review.agrees_with_consensus = review.verdict in agreeing
        review.save(update_fields=["agrees_with_consensus"])
        if review.agrees_with_consensus:
            award(review.reviewer, Reason.REVIEW_AGREED, review, level=level, now=now)
        check_badges(review.reviewer, now=now)


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
def cast_vote(voter, *, exercise=None, solution=None, now=None):
    """Vote « utile ». Le poids baisse quand on vote souvent pour le même auteur."""
    if (exercise is None) == (solution is None):
        raise ValueError("Un vote porte sur un exercice ou sur une solution.")
    target = exercise or solution
    author = target.author
    if author is not None and author.pk == voter.pk:
        raise PermissionDenied("On ne vote pas pour soi-même.")
    now = now or timezone.now()
    weight = vote_weight(voter, author, now=now) if author else Decimal(0)
    vote = Vote.objects.create(
        voter=voter, exercise=exercise, solution=solution, weight=weight
    )
    if weight > 0:
        reason = Reason.EXERCISE_UPVOTED if exercise else Reason.SOLUTION_UPVOTED
        already = points_from(author, reason, target.votes.exclude(pk=vote.pk))
        amount = min(
            math.floor(POINTS[reason] * weight + Decimal("0.5")),
            PER_TARGET_CAPS[reason] - already,
        )
        if amount > 0:
            level = (exercise or solution.exercise).primary_level
            award(author, reason, vote, amount=amount, level=level, now=now)
        if solution is not None:
            check_badges(author, now=now)
    # Après le vote : s'il crée le lien, link_accounts neutralise aussi celui-ci.
    check_vote_reciprocity(voter, author)
    return vote
