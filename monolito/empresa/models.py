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
