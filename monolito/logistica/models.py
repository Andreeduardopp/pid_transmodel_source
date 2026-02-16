from django.db import models
from django.core.exceptions import ValidationError

class EmpresaParceira(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    contato = models.CharField(max_length=100, verbose_name="Nome do Contato")
    email = models.EmailField(verbose_name="E-mail")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Empresa Parceira"
        verbose_name_plural = "Empresas Parceiras"


class Motorista(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    cnh = models.CharField(max_length=20, unique=True, verbose_name="CNH")
    celular = models.CharField(max_length=20, verbose_name="Celular")
    ativo = models.BooleanField(default=True, verbose_name="Ativo?")

    def __str__(self):
        return f"{self.nome} ({self.cnh})"

    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"


class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True, verbose_name="Placa")
    modelo = models.CharField(max_length=100, verbose_name="Modelo")
    capacidade = models.PositiveIntegerField(verbose_name="Capacidade de Passageiros")
    em_manutencao = models.BooleanField(default=False, verbose_name="Em Manutenção?")

    def __str__(self):
        return f"{self.modelo} - {self.placa}"

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"


class RotaBase(models.Model):
    """
    Classe abstrata para rotas, contendo campos comuns.
    """
    origem_nome = models.CharField(max_length=255, verbose_name="Nome da Origem")
    destino_nome = models.CharField(max_length=255, verbose_name="Nome do Destino")
    empresa = models.ForeignKey(EmpresaParceira, on_delete=models.CASCADE, verbose_name="Empresa Responsável")
    veiculo = models.ForeignKey(Veiculo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Veículo")
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Motorista")

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
    dias_da_semana = models.CharField(max_length=20, choices=DIAS_DA_SEMANA_CHOICES, verbose_name="Dias da Semana")

    def __str__(self):
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
    quantidade_passageiros = models.PositiveIntegerField(verbose_name="Qtd. Passageiros")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    origem_whatsapp = models.BooleanField(default=False, verbose_name="Origem WhatsApp?")

    def __str__(self):
        return f"Extra: {self.origem_nome} -> {self.destino_nome} em {self.data_hora_execucao.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Rota Extra"
        verbose_name_plural = "Rotas Extras"


class Parada(models.Model):
    rota = models.ForeignKey(RotaExtra, on_delete=models.CASCADE, related_name='paradas', verbose_name="Rota Extra")
    endereco = models.CharField(max_length=255, verbose_name="Endereço")
    ordem = models.PositiveIntegerField(verbose_name="Ordem da Parada")
    referencia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ponto de Referência")

    def __str__(self):
        return f"{self.ordem}ª Parada: {self.endereco}"

    class Meta:
        verbose_name = "Parada"
        verbose_name_plural = "Paradas"
        ordering = ['ordem']
