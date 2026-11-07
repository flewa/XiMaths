"""Notions : les sous-chapitres que les étudiants cherchent (« séries entières »,
« réduction des endomorphismes »…), rangés sous leur chapitre. Chacune a sa page
d'entrée, /chapitres/<slug>."""

from django.db import migrations

# (slug, nom, chapitre parent)
NOTIONS = [
    ("nombres-reels", "Nombres réels", "analyse"),
    ("fonctions-usuelles", "Fonctions usuelles", "analyse"),
    ("limites-continuite", "Limites et continuité", "analyse"),
    ("derivation", "Dérivation", "analyse"),
    ("developpements-limites", "Développements limités et équivalents", "analyse"),
    ("suites-numeriques", "Suites numériques", "analyse"),
    ("calcul-integral", "Calcul intégral", "analyse"),
    ("integrales-generalisees", "Intégrales généralisées", "analyse"),
    ("integrales-a-parametre", "Intégrales à paramètre", "analyse"),
    ("equations-differentielles", "Équations différentielles", "analyse"),
    ("series-numeriques", "Séries numériques", "analyse"),
    ("series-entieres", "Séries entières", "analyse"),
    ("suites-series-fonctions", "Suites et séries de fonctions", "analyse"),
    ("series-de-fourier", "Séries de Fourier", "analyse"),
    ("fonctions-plusieurs-variables", "Fonctions de plusieurs variables", "analyse"),
    ("integration-lebesgue", "Intégration de Lebesgue", "analyse"),
    ("analyse-fonctionnelle", "Analyse fonctionnelle", "analyse"),
    ("nombres-complexes", "Nombres complexes", "algebre"),
    ("sommes-recurrence", "Sommes et récurrence", "algebre"),
    ("denombrement", "Dénombrement", "algebre"),
    ("ensembles-applications", "Ensembles et applications", "algebre"),
    ("polynomes", "Polynômes", "algebre"),
    ("groupes-anneaux", "Groupes et anneaux", "algebre"),
    ("divisibilite-pgcd", "Divisibilité, PGCD et Bézout", "arithmetique"),
    ("congruences", "Congruences", "arithmetique"),
    ("calcul-matriciel", "Calcul matriciel", "algebre-lineaire"),
    ("applications-lineaires", "Applications linéaires et rang", "algebre-lineaire"),
    ("determinants", "Déterminants", "algebre-lineaire"),
    ("reduction", "Réduction des endomorphismes", "algebre-lineaire"),
    ("espaces-euclidiens", "Espaces euclidiens", "algebre-lineaire"),
    ("espaces-vectoriels-normes", "Espaces vectoriels normés", "topologie"),
    ("espaces-metriques", "Espaces métriques et compacité", "topologie"),
    ("probabilites-conditionnelles", "Probabilités conditionnelles", "probabilites"),
    ("variables-aleatoires-discretes", "Variables aléatoires discrètes", "probabilites"),
    ("theoremes-limites", "Inégalités et théorèmes limites", "probabilites"),
    ("marches-aleatoires", "Marches aléatoires et processus", "probabilites"),
    ("geometrie-plan-espace", "Géométrie du plan et de l'espace", "geometrie"),
    ("courbes-coniques", "Courbes paramétrées et coniques", "geometrie"),
]


def add_notions(apps, schema_editor):
    Topic = apps.get_model("catalog", "Topic")
    chapters = {topic.slug: topic for topic in Topic.objects.filter(parent=None)}
    for slug, name, parent in NOTIONS:
        Topic.objects.update_or_create(slug=slug, defaults={"name": name, "parent": chapters[parent]})


def remove_notions(apps, schema_editor):
    apps.get_model("catalog", "Topic").objects.filter(slug__in=[slug for slug, _, _ in NOTIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_prepa_first_year"),
    ]

    operations = [
        migrations.RunPython(add_notions, remove_notions),
    ]
