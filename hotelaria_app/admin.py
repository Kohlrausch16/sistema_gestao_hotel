from django.contrib import admin
from .models import Cliente, Endereco

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","sobrenome", "cpf")

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ("logradouro","numero", "cidade")