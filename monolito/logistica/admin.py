from django.contrib import admin
from .models import EmpresaParceira, Motorista, Veiculo, RotaFixa, RotaExtra, Parada

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

@admin.register(RotaFixa)
class RotaFixaAdmin(admin.ModelAdmin):
    list_display = ('origem_nome', 'destino_nome', 'horario_partida', 'dias_da_semana', 'empresa', 'motorista', 'veiculo')
    list_filter = ('dias_da_semana', 'empresa')
    search_fields = ('origem_nome', 'destino_nome')

class ParadaInline(admin.TabularInline):
    model = Parada
    extra = 1
    classes = ['collapse']

@admin.register(RotaExtra)
class RotaExtraAdmin(admin.ModelAdmin):
    list_display = ('origem_nome', 'destino_nome', 'data_hora_execucao', 'status', 'empresa', 'origem_whatsapp')
    list_filter = ('status', 'data_hora_execucao', 'origem_whatsapp', 'empresa')
    search_fields = ('origem_nome', 'destino_nome')
    inlines = [ParadaInline]
    date_hierarchy = 'data_hora_execucao'
