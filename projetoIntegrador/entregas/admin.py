# Register your models here.
from django.contrib import admin
from .models import Motorista, Veiculo, Cliente, Rota, Entrega



@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
        list_display = ('cpf', 'nome_motorista', 'telefone', 'cnh', 'status_motorista')
        search_fields = ('cpf', 'nome_motorista')
        list_filter = ('status_motorista', 'cnh')


@admin.register(Veiculo) 
class VeiculoAdmin(admin.ModelAdmin): 
    list_display = ('placa', 'modelo', 'tipo', 'status_veiculo', 'km_atual') 
    list_filter = ('tipo', 'status_veiculo') 
    search_fields = ('placa', 'modelo') 


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin): 
    list_display = ('cpf_cliente', 'nome_cliente', 'cidade', 'estado') 
    search_fields = ('cpf_cliente', 'nome_cliente') 


@admin.register(Rota) 
class RotaAdmin(admin.ModelAdmin): 
    list_display = ('nome_rota', 'motorista', 'veiculo', 'data_rota', 'status_rota') 
    list_filter = ('status_rota',) 
    search_fields = ('nome_rota',) 


@admin.register(Entrega) 
class EntregaAdmin(admin.ModelAdmin): 
    list_display = ('codigo_rastreio', 'cliente', 'rota', 'status', 'data_entrega_prevista') 
    list_filter = ('status',) 
    search_fields = ('codigo_rastreio',)