# Retrait de la détection de plagiat par comparaison de textes.

from django.db import migrations
from django.utils import timezone


def close_open_signals(apps, schema_editor):
    """Un signal encore ouvert ne sera plus tranché : il est levé, sa copie est déjà
    repartie en relecture (content 0008). Les signaux tranchés restent, pour l'historique."""
    IntegritySignal = apps.get_model("moderation", "IntegritySignal")
    IntegritySignal.objects.filter(status="ouvert").update(
        status="leve",
        decided_at=timezone.now(),
        decision_note="Détection automatique retirée : la copie est repartie en relecture.",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("moderation", "0004_comprehension_question"),
        ("content", "0008_nettoyage_relecture"),
    ]

    operations = [
        migrations.RunPython(close_open_signals, migrations.RunPython.noop),
        migrations.DeleteModel(
            name="SolutionPrint",
        ),
    ]
