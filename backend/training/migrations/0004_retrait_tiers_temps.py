# Retrait du tiers-temps.

from django.db import migrations, models

OPEN = ("en_cours", "en_pause")


def keep_open_sessions_whole(apps, schema_editor):
    """Une session encore ouverte au moment du déploiement garde le temps qu'on lui a
    promis : son tiers-temps passe dans sa durée. Les sessions rendues ont déjà leur bonus
    calculé ; le facteur disparaît simplement avec la colonne."""
    TimedSession = apps.get_model("training", "TimedSession")
    for session in TimedSession.objects.filter(status__in=OPEN).exclude(extra_time_factor=1.0):
        session.duration_s = round(session.duration_s * session.extra_time_factor)
        session.save(update_fields=["duration_s"])


class Migration(migrations.Migration):

    dependencies = [
        ("training", "0003_session_photo_upload"),
    ]

    operations = [
        migrations.RunPython(keep_open_sessions_whole, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="timedsession",
            name="extra_time_factor",
        ),
        migrations.AlterField(
            model_name="timedsession",
            name="duration_s",
            field=models.PositiveIntegerField(help_text="Durée choisie."),
        ),
    ]
