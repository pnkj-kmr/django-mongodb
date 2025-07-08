from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = "MongoDB Blog Application"

    def ready(self):
        # Import any startup code or signals here
        print("📚 Blog app loaded successfully!")
