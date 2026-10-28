from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    """Compte XiMaths. `username` sert de pseudo public."""

    class TrustLevel(models.IntegerChoices):
        NEW = 0, "Nouveau"
        MEMBER = 1, "Membre"
        REVIEWER = 2, "Relecteur"
        EXPERT = 3, "Expert"
        MODERATOR = 4, "Modérateur"

    class Status(models.TextChoices):
        ACTIVE = "active", "Actif"
        RESTRICTED = "restricted", "Restreint"
        SUSPENDED = "suspended", "Suspendu"
        BANNED = "banned", "Banni"

    email = models.EmailField("adresse email", unique=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    academic_verified_at = models.DateTimeField(null=True, blank=True)
    verified_teacher = models.BooleanField(default=False)
    declared_level = models.ForeignKey(
        "catalog.Level",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    trust_level = models.PositiveSmallIntegerField(
        choices=TrustLevel.choices, default=TrustLevel.NEW
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    leaderboard_visible = models.BooleanField(default=True)
    tiers_temps = models.BooleanField(default=False)
    google_sub = models.CharField(
        max_length=64, null=True, blank=True, unique=True, help_text="Identifiant du compte Google lié."
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Emails pour ce qui te concerne directement : retrait, sanction, question d'intégrité.",
    )
    weekly_digest = models.BooleanField(default=False, help_text="Résumé hebdomadaire par email, sur opt-in.")
    daily_challenge_notifications = models.BooleanField(
        default=False, help_text="Notification à l'ouverture du défi du jour, sur opt-in."
    )
    # Série hebdomadaire : objectif de 2 à 7 jours actifs, et mode examens ou vacances.
    weekly_goal_days = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(2), MaxValueValidator(7)]
    )
    vacation_from = models.DateField(null=True, blank=True)
    vacation_until = models.DateField(null=True, blank=True)


class AccountLink(models.Model):
    """Deux comptes probablement tenus par la même personne, ou qui s'entraident.

    Ce n'est pas une sanction : leurs votes mutuels ne comptent plus, ils ne se
    relisent pas, et leurs solutions ne font pas monter les exercices de l'autre.
    `user_a` a toujours l'identifiant le plus petit.
    """

    class LinkType(models.TextChoices):
        VOTE_RECIPROCITY = "votes", "Réciprocité de votes"
        REVIEW_COLLUSION = "relectures", "Collusion de relecture"
        SAME_DEVICE = "appareil", "Même appareil"
        SAME_NETWORK = "reseau", "Même réseau"

    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    link_type = models.CharField(max_length=16, choices=LinkType.choices)
    strength = models.FloatField(help_text="De 0 à 1.")
    confirmed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Modérateur qui a confirmé ou créé le lien ; vide s'il est automatique.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "comptes liés"
        verbose_name_plural = "comptes liés"
        constraints = [
            models.UniqueConstraint(
                fields=["user_a", "user_b", "link_type"], name="account_link_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(user_a__lt=models.F("user_b")), name="account_link_ordered"
            ),
        ]

    def __str__(self):
        return f"{self.user_a} ↔ {self.user_b} ({self.get_link_type_display()})"

    def save(self, *args, **kwargs):
        if self.user_a_id > self.user_b_id:
            self.user_a_id, self.user_b_id = self.user_b_id, self.user_a_id
        super().save(*args, **kwargs)
