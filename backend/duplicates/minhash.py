"""Signatures MinHash des énoncés normalisés, et clés LSH pour trouver les candidats."""

import random
from hashlib import blake2b

NUM_PERMUTATIONS = 128
SHINGLE_SIZE = 5
# 16 bandes de 8 lignes : deux énoncés à J = 0,85 partagent une bande avec une
# probabilité de 99 %, à J = 0,5 avec une probabilité de 6 %.
LSH_BANDS = 16
LSH_ROWS = NUM_PERMUTATIONS // LSH_BANDS
_PRIME = (1 << 61) - 1
# Graine fixe : les signatures stockées doivent rester comparables d'une version à l'autre.
_rng = random.Random(1729)
_PERMUTATIONS = [(_rng.randrange(1, _PRIME), _rng.randrange(_PRIME)) for _ in range(NUM_PERMUTATIONS)]


def _hash(text):
    return int.from_bytes(blake2b(text.encode(), digest_size=8).digest(), "big")


def shingles(tokens, size=SHINGLE_SIZE):
    if len(tokens) <= size:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + size]) for i in range(len(tokens) - size + 1)}


def signature(tokens):
    """128 minima de hachages ; liste vide pour un énoncé sans jeton."""
    hashes = [_hash(shingle) for shingle in shingles(tokens)]
    if not hashes:
        return []
    return [min((a * h + b) % _PRIME for h in hashes) for a, b in _PERMUTATIONS]


def similarity(first, second):
    """Estimation de l'indice de Jaccard entre les deux ensembles de shingles."""
    if not first or not second:
        return 0.0
    return sum(x == y for x, y in zip(first, second)) / NUM_PERMUTATIONS


def lsh_keys(sig):
    """Une clé par bande : deux signatures qui partagent une clé sont candidates."""
    if not sig:
        return []
    return [
        int.from_bytes(
            blake2b(f"{band}:{sig[band * LSH_ROWS : (band + 1) * LSH_ROWS]}".encode(), digest_size=8).digest(),
            "big",
            signed=True,
        )
        for band in range(LSH_BANDS)
    ]
