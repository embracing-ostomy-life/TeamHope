from django.apps import AppConfig


class TeamHopeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "team_hope"
    verbose_name = "User and Profiles"

    def ready(self):
        import team_hope.signals  # Import the signals module
