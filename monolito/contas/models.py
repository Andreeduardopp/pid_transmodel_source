from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado com suporte a múltiplos tipos.
    Estende AbstractUser para manter compatibilidade com o sistema
    de autenticação do Django.
    """

    class TipoUsuario(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CLIENTE = 'cliente', 'Cliente'
        MEMBRO_EQUIPE = 'membro_equipe', 'Membro da Equipe'

    tipo_usuario: str = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.MEMBRO_EQUIPE,
        verbose_name="Tipo de Usuário",
    )
    celular: str | None = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Celular",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_tipo_usuario_display()})"

    @property
    def is_admin(self) -> bool:
        return self.tipo_usuario == self.TipoUsuario.ADMIN

    @property
    def is_cliente(self) -> bool:
        return self.tipo_usuario == self.TipoUsuario.CLIENTE

    @property
    def is_membro_equipe(self) -> bool:
        return self.tipo_usuario == self.TipoUsuario.MEMBRO_EQUIPE

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
