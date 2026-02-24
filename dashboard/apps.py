from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    verbose_name = 'AI Usage Dashboard'
    
    def ready(self):
        """Import signals when Django starts."""
        import dashboard.signals
