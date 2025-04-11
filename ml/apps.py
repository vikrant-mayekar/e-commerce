from django.apps import AppConfig
import os

class MlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml'
    verbose_name = 'Machine Learning'

    def ready(self):
        # Only run initialization when not in manage.py check or migrate
        if os.environ.get('RUN_MAIN') or os.environ.get('DJANGO_SETTINGS_MODULE'):
            # Initialize the ML app when Django starts
            from .app import init_db
            init_db() 