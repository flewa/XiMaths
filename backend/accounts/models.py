from django.contrib.auth.models import AbstractUser
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
