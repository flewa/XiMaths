from django.apps import AppConfig


class ModerationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "moderation"
    verbose_name = "Modération"

    def ready(self):
        from duplicates.signals import pair_decided

        from .services import settle_duplicate_reports

        pair_decided.connect(settle_duplicate_reports, dispatch_uid="moderation.settle_duplicate_reports")
