from django.contrib import admin

from .models import EmpresaParceira, Motorista, Veiculo


@admin.register(EmpresaParceira)
class EmpresaParceiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'contato', 'email')
    search_fields = ('nome', 'cnpj')


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'celular', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'cpf', 'cnh')


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'modelo', 'capacidade', 'em_manutencao')
    list_filter = ('em_manutencao',)
    search_fields = ('placa', 'modelo')
