from django.apps import AppConfig


class ContasConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'contas'
    verbose_name: str = 'Contas e Usuários'
