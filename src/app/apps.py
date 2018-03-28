from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'
    def ready(self):
        # registers some single
        import app.signals
