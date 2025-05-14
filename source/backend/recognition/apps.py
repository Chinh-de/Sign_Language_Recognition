from django.apps import AppConfig


class RecognitionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recognition'
    
    def ready(self):
        # Khởi động session manager
        from .tasks import session_manager
        session_manager.start()