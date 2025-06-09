from django.apps import AppConfig


class AuthentificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentifications"

    def ready(self):
        import authentifications.signals  # Connecte les signaux au démarrage
