from django.apps import AppConfig


class RecordingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.recordings"

    def ready(self):
        import apps.recordings.signals
