from django.contrib import admin
from .models import Cliente, Quarto, Funcionario

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","sobrenome", "cpf")

@admin.register(Funcionario)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","cargo")
@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    list_display = ("numero", "tipo", "preco_diaria")
