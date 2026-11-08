from django.utils import timezone

from catalog.models import Topic

from .models import CourseNote


def import_sources(sources):
    """Crée ou met à jour les fiches. Un texte changé repasse en brouillon : l'admin relit
    ce qu'il publie. Renvoie le décompte (créées, mises à jour, repassées en brouillon)."""
    topics = {topic.slug: topic for topic in Topic.objects.all()}
    unknown = sorted({source.topic for source in sources if source.topic and source.topic not in topics})
    if unknown:
        raise ValueError(f"Notions inconnues : {', '.join(unknown)}.")
    created = updated = unpublished = 0
    for source in sources:
        fields = {
            "title": source.title,
            "cycle": source.cycle,
            "programs": source.programs,
            "position": source.position,
            "topic": topics.get(source.topic) if source.topic else None,
            "body": source.body,
            "source_hash": source.digest,
        }
        note = CourseNote.objects.filter(slug=source.slug).first()
        if note is None:
            CourseNote.objects.create(slug=source.slug, **fields)
            created += 1
            continue
        if note.source_hash == source.digest:
            continue
        text_changed = (note.title, note.body) != (source.title, source.body)
        for name, value in fields.items():
            setattr(note, name, value)
        if text_changed and note.published:
            note.published_at = None
            note.published_by = None
            unpublished += 1
        note.save()
        updated += 1
    return created, updated, unpublished


def publish(note, user):
    note.published_at = timezone.now()
    note.published_by = user
    note.save(update_fields=["published_at", "published_by", "updated_at"])


def unpublish(note):
    note.published_at = None
    note.published_by = None
    note.save(update_fields=["published_at", "published_by", "updated_at"])
