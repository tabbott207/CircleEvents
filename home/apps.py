from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'home'

class HomeConfig(AppConfig):  # Replace `HomeConfig` with your app’s config class
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        import home.signals  # Import the signals module