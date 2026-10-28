"""Premières années de prépa (MPSI, MP2I, PCSI, PTSI), rangées avant les deuxièmes années."""

from django.db import migrations

FIRST_YEAR = [
    ("MPSI", "Prépa MPSI"),
    ("MP2I", "Prépa MP2I"),
    ("PCSI", "Prépa PCSI"),
    ("PTSI", "Prépa PTSI"),
]
ORDER = ["L1", "L2", "L3", "M1", "M2", "MPSI", "MP2I", "PCSI", "PTSI", "MP", "PC", "PSI", "PT"]


def add_first_year(apps, schema_editor):
    Level = apps.get_model("catalog", "Level")
    for code, name in FIRST_YEAR:
        Level.objects.update_or_create(
            code=code, defaults={"name": name, "track": "prepa", "year": 1}
        )
    for position, code in enumerate(ORDER):
        Level.objects.filter(code=code).update(display_order=position)


def remove_first_year(apps, schema_editor):
    apps.get_model("catalog", "Level").objects.filter(code__in=[c for c, _ in FIRST_YEAR]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_seed_levels_topics"),
    ]

    operations = [
        migrations.RunPython(add_first_year, remove_first_year),
    ]
