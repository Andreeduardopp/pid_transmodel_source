from django.apps import AppConfig


class EmpresaConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'empresa'
    verbose_name: str = 'Gestão Empresarial'
