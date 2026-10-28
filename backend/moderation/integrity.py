"""Anti-plagiat interne : chaque solution est comparée aux solutions antérieures des
autres auteurs, sur l'exercice et les doublons fusionnés avec lui.

Au-delà d'un Jaccard de 0,7 (0,85 sous 400 caractères : les preuves classiques
courtes se ressemblent légitimement), la solution est mise en vérification et
l'auteur reçoit une question neutre. Un modérateur tranche ; rien n'est automatique.
"""

from content.models import Exercise, Solution
from duplicates.minhash import signature, similarity
from duplicates.normalize import normalize

from .models import IntegritySignal, SolutionPrint

PLAGIARISM_JACCARD = 0.7
SHORT_PROOF_LENGTH = 400
SHORT_PROOF_JACCARD = 0.85
NEUTRAL_QUESTION = (
    "Ta solution ressemble beaucoup à une autre solution déjà proposée pour cet exercice. "
    "Cela arrive avec les preuves classiques. As-tu travaillé à partir d'un livre, d'un cours "
    "ou d'un autre document ? Tu peux le préciser : un modérateur regardera, sans a priori."
)


def fingerprint(solution):
    print_, _ = SolutionPrint.objects.update_or_create(
        solution=solution,
        defaults={"signature": signature(normalize(solution.body).alpha), "length": len(solution.body)},
    )
    return print_


def _cluster(exercise):
    """L'exercice, ceux fusionnés avec lui, et son canonique s'il a été fusionné."""
    ids = {exercise.pk}
    ids |= set(Exercise.objects.filter(merged_into=exercise).values_list("pk", flat=True))
    if exercise.merged_into_id:
        ids.add(exercise.merged_into_id)
    return ids


def closest_prior(solution, print_):
    """(solution antérieure la plus proche d'un autre auteur, Jaccard), ou (None, 0)."""
    candidates = (
        SolutionPrint.objects.filter(solution__exercise_id__in=_cluster(solution.exercise), solution__pk__lt=solution.pk)
        .exclude(solution__status__in=[Solution.Status.DRAFT, Solution.Status.HIDDEN])
        .exclude(solution__author_id=solution.author_id)
        .select_related("solution")
    )
    best, best_score = None, 0.0
    for candidate in candidates:
        score = similarity(print_.signature, candidate.signature)
        if score > best_score:
            best, best_score = candidate.solution, score
    return best, best_score


def check_solution(solution):
    """Empreinte la solution ; renvoie un signal ouvert si elle est trop proche d'une autre."""
    print_ = fingerprint(solution)
    match, score = closest_prior(solution, print_)
    threshold = SHORT_PROOF_JACCARD if print_.length < SHORT_PROOF_LENGTH else PLAGIARISM_JACCARD
    if match is None or score < threshold:
        return None
    return IntegritySignal.objects.create(
        user=solution.author,
        solution=solution,
        kind=IntegritySignal.Kind.PLAGIARISM,
        value=score,
        matched_solution=match,
    )
