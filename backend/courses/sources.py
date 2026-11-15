"""Textes de la rédaction : un fichier Markdown + LaTeX par texte. Les fiches de rappels sont
dans notes/sup/ et notes/spe/ (le dossier donne le cycle), les démonstrations dans
notes/demonstrations/ (niveau deuxième année). Le nom du fichier donne l'adresse
(/rappels/<nom> ou /demonstrations/<nom>). Chaque fichier commence par un en-tête :

    ---
    titre: Séries entières
    programmes: MP, PSI
    ordre: 3
    notion: series-entieres
    ---

`notion` (facultatif) est le chapitre ou la notion du site où le texte publié est proposé.
Une démonstration ajoute `statut` : au-programme, preuve-hors-programme ou hors-programme,
sa place par rapport au programme de prépa (MPSI, MP).
"""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

NOTES_DIR = Path(__file__).resolve().parent / "notes"
CYCLES = ("sup", "spe")
# Dossier, nature des textes qu'il contient, cycle.
FOLDERS = (("sup", "fiche", "sup"), ("spe", "fiche", "spe"), ("demonstrations", "demonstration", "spe"))
STATUSES = ("au-programme", "preuve-hors-programme", "hors-programme")
REQUIRED = {"titre", "programmes", "ordre"}
KNOWN = REQUIRED | {"notion", "statut"}
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
    kind: str = "fiche"
    status: str = ""

    @property
    def digest(self):
        fields = (self.cycle, self.title, self.programs, str(self.position), self.topic or "", self.body)
        if self.kind != "fiche":
            fields += (self.kind, self.status)
        return hashlib.sha256("\x1f".join(fields).encode()).hexdigest()


def parse(text, *, slug, cycle, kind="fiche"):
    """Un texte lu depuis son fichier ; ValueError si l'en-tête est incomplet ou inconnu."""
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
    status = fields.get("statut", "")
    if kind == "demonstration" and status not in STATUSES:
        raise ValueError(f"{slug} : « statut » doit valoir {', '.join(STATUSES)}.")
    if kind == "fiche" and status:
        raise ValueError(f"{slug} : « statut » est réservé aux démonstrations.")
    return Source(
        slug=slug,
        cycle=cycle,
        title=fields["titre"],
        programs=fields["programmes"],
        position=int(fields["ordre"]),
        topic=fields.get("notion") or None,
        body=body.strip() + "\n",
        kind=kind,
        status=status,
    )


def load_sources(directory=NOTES_DIR):
    """Tous les textes : fiches de sup, fiches de spé, puis démonstrations, chacun dans l'ordre
    de son sommaire."""
    sources = []
    for folder, kind, cycle in FOLDERS:
        for path in sorted((directory / folder).glob("*.md")):
            sources.append(parse(path.read_text(encoding="utf-8"), slug=path.stem, cycle=cycle, kind=kind))
    slugs = [source.slug for source in sources]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise ValueError(f"Fiches en double : {', '.join(duplicates)}.")
    order = [(kind, cycle) for _, kind, cycle in FOLDERS]
    return sorted(sources, key=lambda source: (order.index((source.kind, source.cycle)), source.position, source.title))
