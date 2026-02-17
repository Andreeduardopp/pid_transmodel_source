from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models


class EmpresaParceira(models.Model):
    nome: str = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    cnpj: str = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    contato: str = models.CharField(max_length=100, verbose_name="Nome do Contato")
    email: str = models.EmailField(verbose_name="E-mail")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self) -> str:
        return self.nome

    class Meta:
        verbose_name = "Empresa Parceira"
        verbose_name_plural = "Empresas Parceiras"


class Motorista(models.Model):
    nome: str = models.CharField(max_length=255, verbose_name="Nome Completo")
    cpf: str = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    cnh: str = models.CharField(max_length=20, unique=True, verbose_name="CNH")
    celular: str = models.CharField(max_length=20, verbose_name="Celular")
    ativo: bool = models.BooleanField(default=True, verbose_name="Ativo?")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self) -> str:
        return f"{self.nome} ({self.cnh})"

    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"


class Veiculo(models.Model):
    placa: str = models.CharField(max_length=10, unique=True, verbose_name="Placa")
    modelo: str = models.CharField(max_length=100, verbose_name="Modelo")
    capacidade: int = models.PositiveIntegerField(verbose_name="Capacidade de Passageiros")
    em_manutencao: bool = models.BooleanField(default=False, verbose_name="Em Manutenção?")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self) -> str:
        return f"{self.modelo} - {self.placa}"

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"


class RotaBase(models.Model):
    """
    Classe abstrata para rotas, contendo campos comuns.
    """
    origem_nome: str = models.CharField(max_length=255, verbose_name="Nome da Origem")
    destino_nome: str = models.CharField(max_length=255, verbose_name="Nome do Destino")
    origem_localizacao = gis_models.PointField(
        srid=4326,
        geography=True,
        null=True,
        blank=True,
        verbose_name="Localização da Origem",
    )
    destino_localizacao = gis_models.PointField(
        srid=4326,
        geography=True,
        null=True,
        blank=True,
        verbose_name="Localização do Destino",
    )
    empresa = models.ForeignKey(
        "EmpresaParceira",
        on_delete=models.CASCADE,
        verbose_name="Empresa Responsável",
    )
    veiculo = models.ForeignKey(
        "Veiculo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Veículo",
    )
    motorista = models.ForeignKey(
        "Motorista",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Motorista",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True


class RotaFixa(RotaBase):
    """
    Rotas recorrentes, ex: transporte diário de funcionários.
    """
    DIAS_DA_SEMANA_CHOICES = [
        ('SEG_SEX', 'Segunda a Sexta'),
        ('SEG_SAB', 'Segunda a Sábado'),
        ('TODO_DIA', 'Todos os dias'),
        ('FIM_SEMANA', 'Fim de Semana'),
    ]

    horario_partida = models.TimeField(verbose_name="Horário de Partida")
    dias_da_semana: str = models.CharField(
        max_length=20,
        choices=DIAS_DA_SEMANA_CHOICES,
        verbose_name="Dias da Semana",
    )

    def __str__(self) -> str:
        return f"Fixa: {self.origem_nome} -> {self.destino_nome} ({self.get_dias_da_semana_display()})"

    class Meta:
        verbose_name = "Rota Fixa"
        verbose_name_plural = "Rotas Fixas"


class RotaExtra(RotaBase):
    """
    Rotas eventuais ou charters, criadas sob demanda (inclusive via WhatsApp).
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('em_curso', 'Em Curso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    data_hora_execucao = models.DateTimeField(verbose_name="Data e Hora de Execução")
    quantidade_passageiros: int = models.PositiveIntegerField(verbose_name="Qtd. Passageiros")
    status: str = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name="Status",
    )
    origem_whatsapp: bool = models.BooleanField(default=False, verbose_name="Origem WhatsApp?")

    def __str__(self) -> str:
        return f"Extra: {self.origem_nome} -> {self.destino_nome} em {self.data_hora_execucao.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Rota Extra"
        verbose_name_plural = "Rotas Extras"


class Parada(models.Model):
    """
    Ponto de parada independente, com localização geográfica.
    Vinculada a rotas através da tabela intermediária RotaParada.
    """
    endereco: str = models.CharField(max_length=255, verbose_name="Endereço")
    referencia: str | None = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Ponto de Referência",
    )
    localizacao = gis_models.PointField(
        srid=4326,
        geography=True,
        null=True,
        blank=True,
        verbose_name="Localização",
        help_text="Coordenadas geográficas da parada (GeoJSON Point).",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self) -> str:
        return f"Parada: {self.endereco}"

    class Meta:
        verbose_name = "Parada"
        verbose_name_plural = "Paradas"


class RotaParada(models.Model):
    """
    Tabela intermediária que conecta Paradas a Rotas (Fixa ou Extra).
    Permite versionamento das paradas de uma mesma rota.
    """
    parada = models.ForeignKey(
        Parada,
        on_delete=models.CASCADE,
        related_name="rota_paradas",
        verbose_name="Parada",
    )
    rota_fixa = models.ForeignKey(
        RotaFixa,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rota_paradas",
        verbose_name="Rota Fixa",
    )
    rota_extra = models.ForeignKey(
        RotaExtra,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rota_paradas",
        verbose_name="Rota Extra",
    )
    ordem: int = models.PositiveIntegerField(verbose_name="Ordem da Parada")
    versao: int = models.PositiveIntegerField(default=1, verbose_name="Versão")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def clean(self) -> None:
        """Garante que exatamente uma rota (fixa OU extra) esteja vinculada."""
        super().clean()
        tem_fixa = self.rota_fixa_id is not None
        tem_extra = self.rota_extra_id is not None

        if tem_fixa == tem_extra:
            raise ValidationError(
                "É necessário vincular exatamente uma rota: "
                "preencha 'Rota Fixa' ou 'Rota Extra', nunca ambos ou nenhum."
            )

    def __str__(self) -> str:
        rota = self.rota_fixa or self.rota_extra
        return f"{self.ordem}ª Parada (v{self.versao}): {self.parada} — {rota}"

    class Meta:
        verbose_name = "Rota-Parada"
        verbose_name_plural = "Rota-Paradas"
        ordering = ["ordem"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(rota_fixa__isnull=False, rota_extra__isnull=True)
                    | models.Q(rota_fixa__isnull=True, rota_extra__isnull=False)
                ),
                name="rotaparada_exatamente_uma_rota",
            ),
            models.UniqueConstraint(
                fields=["rota_fixa", "parada", "versao"],
                name="unique_parada_rota_fixa_versao",
            ),
            models.UniqueConstraint(
                fields=["rota_extra", "parada", "versao"],
                name="unique_parada_rota_extra_versao",
            ),
        ]
