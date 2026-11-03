from django.contrib import admin
from .models import Cliente
from .models import Funcionario

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","sobrenome", "cpf")

@admin.register(Funcionario)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","cargo")