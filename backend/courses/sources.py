"""Fiches de la rédaction : un fichier Markdown + LaTeX par fiche, dans notes/sup/ et
notes/spe/. Le nom du fichier donne l'adresse de la fiche (/rappels/<nom>), son dossier le
cycle. Chaque fichier commence par un en-tête :

    ---
    titre: Séries entières
    programmes: MP, PSI
    ordre: 3
    notion: series-entieres
    ---

`notion` (facultatif) est le chapitre ou la notion du site où la fiche publiée est proposée.
"""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

NOTES_DIR = Path(__file__).resolve().parent / "notes"
CYCLES = ("sup", "spe")
REQUIRED = {"titre", "programmes", "ordre"}
KNOWN = REQUIRED | {"notion"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Source:
    slug: str
    cycle: str
    title: str
    programs: str
    position: int
    topic: str | None
    body: str

    @property
    def digest(self):
        fields = (self.cycle, self.title, self.programs, str(self.position), self.topic or "", self.body)
        return hashlib.sha256("\x1f".join(fields).encode()).hexdigest()


def parse(text, *, slug, cycle):
    """Une fiche lue depuis son texte ; ValueError si l'en-tête est incomplet ou inconnu."""
    if not SLUG.match(slug):
        raise ValueError(f"{slug} : nom de fichier invalide (minuscules, chiffres et tirets).")
    if not text.startswith("---\n"):
        raise ValueError(f"{slug} : l'en-tête (entre deux lignes ---) manque.")
    header, separator, body = text[4:].partition("\n---\n")
    if not separator:
        raise ValueError(f"{slug} : l'en-tête n'est pas fermé par une ligne ---.")
    fields = {}
    for line in header.splitlines():
        key, colon, value = line.partition(":")
        if not colon or key.strip() not in KNOWN:
            raise ValueError(f"{slug} : ligne d'en-tête inconnue « {line} ».")
        fields[key.strip()] = value.strip()
    missing = REQUIRED - fields.keys()
    if missing:
        raise ValueError(f"{slug} : il manque {', '.join(sorted(missing))} dans l'en-tête.")
    if not fields["ordre"].isdigit():
        raise ValueError(f"{slug} : « ordre » doit être un entier.")
    if not body.strip():
        raise ValueError(f"{slug} : la fiche est vide.")
    return Source(
        slug=slug,
        cycle=cycle,
        title=fields["titre"],
        programs=fields["programmes"],
        position=int(fields["ordre"]),
        topic=fields.get("notion") or None,
        body=body.strip() + "\n",
    )


def load_sources(directory=NOTES_DIR):
    """Toutes les fiches, sup puis spé, dans l'ordre de leurs sommaires."""
    sources = []
    for cycle in CYCLES:
        for path in sorted((directory / cycle).glob("*.md")):
            sources.append(parse(path.read_text(encoding="utf-8"), slug=path.stem, cycle=cycle))
    slugs = [source.slug for source in sources]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise ValueError(f"Fiches en double : {', '.join(duplicates)}.")
    return sorted(sources, key=lambda source: (CYCLES.index(source.cycle), source.position, source.title))
