# greentrace/apps.py

from django.apps import AppConfig


class GreentraceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name               = "greentrace"
    verbose_name       = "GreenTrace — Environmental Monitoring"

    def ready(self):
        # Load signals so they are registered when Django starts
        import greentrace.api.signals  # noqa: F401
