from django.contrib import admin
from .forms import ReservaForm
from .models import Cliente, Quarto, Reserva, TipoQuarto, Funcionario, Ocorrencia, Relatorio

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","sobrenome", "cpf")

@admin.register(Funcionario)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome","cargo")
@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    list_display = ("numero", "tipo", "capacidade", "status")
@admin.register(TipoQuarto)
class TipoQuartoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "preco_diaria")
@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ("quarto", "descricao", "data_ocorrencia")
@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ("campos",)
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    class FormularioReservaAdmin(ReservaForm):
        class Meta(ReservaForm.Meta):
            fields = [*ReservaForm.Meta.fields, "status", "ativo"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if not self.is_bound and not self.instance.pk:
                self.fields["quarto"].queryset = Quarto.objects.filter(
                    ativo=True
                ).exclude(status__in=("M", "O")).order_by("numero")

    form = FormularioReservaAdmin
    list_display = ("cliente", "quarto", "data_entrada", "data_saida", "preco_total", "status")
