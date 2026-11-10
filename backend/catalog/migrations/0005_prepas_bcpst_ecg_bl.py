"""Prépas BCPST, ECG et B/L (deux années chacune) et MPI. Les prépas ECG et B/L forment une
filière à part dans les menus : leurs programmes de maths n'ont pas grand-chose de commun avec
ceux des prépas scientifiques. Avec elles vient une notion que le catalogue n'avait pas :
les variables à densité et l'estimation."""

from django.db import migrations, models

NEW = [
    ("MPI", "Prépa MPI", "prepa", 2),
    ("BCPST1", "Prépa BCPST 1re année", "prepa", 1),
    ("BCPST2", "Prépa BCPST 2e année", "prepa", 2),
    ("ECG1", "Prépa ECG 1re année", "prepa_eco", 1),
    ("ECG2", "Prépa ECG 2e année", "prepa_eco", 2),
    ("BL1", "Prépa B/L 1re année", "prepa_eco", 1),
    ("BL2", "Prépa B/L 2e année", "prepa_eco", 2),
]
ORDER = [
    "L1", "L2", "L3", "M1", "M2",
    "MPSI", "MP2I", "PCSI", "PTSI", "BCPST1",
    "MP", "MPI", "PC", "PSI", "PT", "BCPST2",
    "ECG1", "ECG2", "BL1", "BL2",
]  # fmt: skip
NOTION = ("variables-a-densite", "Variables à densité et estimation", "probabilites")
FORMER_ORDER = ["L1", "L2", "L3", "M1", "M2", "MPSI", "MP2I", "PCSI", "PTSI", "MP", "PC", "PSI", "PT"]


def add_levels(apps, schema_editor):
    Level = apps.get_model("catalog", "Level")
    for code, name, track, year in NEW:
        Level.objects.update_or_create(code=code, defaults={"name": name, "track": track, "year": year})
    for position, code in enumerate(ORDER):
        Level.objects.filter(code=code).update(display_order=position)
    Topic = apps.get_model("catalog", "Topic")
    slug, name, chapter = NOTION
    Topic.objects.update_or_create(slug=slug, defaults={"name": name, "parent": Topic.objects.get(slug=chapter)})


def remove_levels(apps, schema_editor):
    Level = apps.get_model("catalog", "Level")
    Level.objects.filter(code__in=[code for code, *_ in NEW]).delete()
    for position, code in enumerate(FORMER_ORDER):
        Level.objects.filter(code=code).update(display_order=position)
    apps.get_model("catalog", "Topic").objects.filter(slug=NOTION[0]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_notions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="level",
            name="track",
            field=models.CharField(
                choices=[
                    ("universite", "Université"),
                    ("prepa", "Classe préparatoire scientifique"),
                    ("prepa_eco", "Classe préparatoire ECG ou B/L"),
                ],
                max_length=16,
            ),
        ),
        migrations.RunPython(add_levels, remove_levels),
    ]
