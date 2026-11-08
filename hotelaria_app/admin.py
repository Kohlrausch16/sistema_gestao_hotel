from django.contrib import admin
from .models import Cliente, Quarto, Funcionario, Ocorrencia

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","sobrenome", "cpf")

@admin.register(Funcionario)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","cargo")
@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    list_display = ("numero", "tipo", "preco_diaria")
@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ("reserva", "descricao", "data_ocorrencia")