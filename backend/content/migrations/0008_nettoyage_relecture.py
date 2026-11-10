# Les statuts « en vérification » et « contestée » disparaissent.

from django.db import migrations, models


def back_to_review(apps, schema_editor):
    """Une copie restée en vérification (détection de plagiat par texte, retirée) ou
    contestée (ancienne règle d'arbitrage) repart en relecture normale : la tâche horaire
    lui tire ses relecteurs, et l'équipe peut la corriger."""
    Solution = apps.get_model("content", "Solution")
    Solution.objects.filter(status__in=["held", "contested"]).update(status="under_review")


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0007_solution_photos"),
    ]

    operations = [
        migrations.RunPython(back_to_review, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="solution",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Brouillon"),
                    ("under_review", "En relecture"),
                    ("validated", "Validée"),
                    ("needs_work", "À compléter"),
                    ("hidden", "Masquée"),
                ],
                default="draft",
                max_length=16,
            ),
        ),
    ]
