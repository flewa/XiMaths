from datetime import datetime

from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import django_auth

from . import services
from .models import CourseNote

router = Router(tags=["Rappels de cours"])


class CourseNoteSummaryOut(Schema):
    slug: str
    title: str
    kind: str
    status: str
    cycle: str
    programs: str
    position: int
    topic: str | None
    topic_name: str | None
    published: bool
    updated_at: datetime

    @staticmethod
    def resolve_topic(note):
        return note.topic.slug if note.topic else None

    @staticmethod
    def resolve_topic_name(note):
        return note.topic.name if note.topic else None


class CourseNoteOut(CourseNoteSummaryOut):
    body: str
    published_at: datetime | None


def visible_notes(user):
    """Toutes les fiches pour l'équipe (accès à l'admin) ; les publiées pour les autres."""
    # La sup, puis la spé, chacune dans l'ordre de son sommaire.
    first_year = Case(When(cycle=CourseNote.Cycle.SUP, then=Value(0)), default=Value(1), output_field=IntegerField())
    notes = CourseNote.objects.select_related("topic").order_by(first_year, "position", "title")
    if user.is_authenticated and user.is_staff:
        return notes
    return notes.filter(published_at__isnull=False)


def staff_note(request, slug):
    if not request.user.is_staff:
        raise HttpError(403, "Seule l'équipe du site publie les rappels de cours.")
    return get_object_or_404(CourseNote.objects.select_related("topic"), slug=slug)


@router.get("/course-notes", response=list[CourseNoteSummaryOut])
def list_course_notes(request, topic: str | None = None, kind: str = CourseNote.Kind.FICHE):
    """Les fiches de rappels, ou avec `kind=demonstration` les démonstrations."""
    if kind not in CourseNote.Kind.values:
        raise HttpError(400, "Nature de texte inconnue.")
    notes = visible_notes(request.user).filter(kind=kind)
    if topic:
        notes = notes.filter(topic__slug=topic)
    return list(notes)


@router.get("/course-notes/{slug}", response=CourseNoteOut)
def course_note(request, slug: str):
    return get_object_or_404(visible_notes(request.user), slug=slug)


@router.post("/course-notes/{slug}/publish", response=CourseNoteOut, auth=django_auth)
def publish_course_note(request, slug: str):
    note = staff_note(request, slug)
    services.publish(note, request.user)
    return note


@router.post("/course-notes/{slug}/unpublish", response=CourseNoteOut, auth=django_auth)
def unpublish_course_note(request, slug: str):
    note = staff_note(request, slug)
    services.unpublish(note)
    return note
