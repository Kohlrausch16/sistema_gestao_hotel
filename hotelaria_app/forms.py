from django import forms
from datetime import date

from .disponibilidade import quartos_disponiveis
from .models import Cliente, Quarto, Reserva

class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente

        fields = [
            "nome",
            "sobrenome",
            "cpf",
            "data_nascimento",
            "email",
            "telefone",
            "logradouro",
            "numero",
            "bairro",
            "cidade" 
        ]

        labels = {
            "nome": "NOME",
            "sobrenome": "SOBRENOME",
            "cpf": "CPF",
            "data_nascimento": "DATA DE NASCIMENTO",
            "email": "EMAIL",
            "telefone": "TELEFONE",
            "logradouro": "RUA",
            "numero": "NUMERO",
            "bairro": "BAIRRO",
            "cidade": "CIDADE"
        }


        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-nome",
                "placeholder": "João Antônio"
            }),

            "sobrenome": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-sobrenome",
                "placeholder": "Souza Santos"
            }),

            "cpf": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-cpf",
                "placeholder": "000.000.000-00",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "minlength": "11",
                "maxlength": "11"
            }),

            "data_nascimento": forms.DateInput(attrs={
                "type": "date",
                "class": "campo-formulario placeholder-input input-data-nascimento",
                "placeholder": "01/01/1970"
            },
            format = {
                "%Y-%m-%d"
            }),

            "email": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-email",
                "placeholder": "josesantos@gmail.com"
            }),

            "telefone": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-telefone",
                "placeholder": "(51) 99999-9999",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "minlength": "11",
                "maxlength": "11"
            }),

            "logradouro": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-email",
                "placeholder": "Avenida Central"
            }),

            "numero": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-telefone",
                "placeholder": "45",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "minlength": "1",
                "maxlength": "5"
            }),

            "bairro": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-email",
                "placeholder": "Centro"
            }),

            "cidade": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-email",
                "placeholder": "Porto Alegre"
            })
        }

class QuartoForm(forms.ModelForm):
    class Meta:
        model = Quarto

        fields = [
            "numero",
            "tipo",
            "capacidade",
            "preco_diaria"
        ]

        labels = {
            "numero": "NUMERO",
            "tipo": "TIPO",
            "capacidade": "CAPACIDADE",
            "preco_diaria": "PREÇO DIÁRIO"
        }

        widgets = {
            "numero": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-numero",
                "placeholder": "101"
            }),

            "tipo": forms.Select(attrs={
                "class": "campo-formulario placeholder-input input-tipo"
            }),

            "capacidade": forms.NumberInput(attrs={
                "class": "campo-formulario placeholder-input input-capacidade",
                "min": "1",
                "step": "1"
            }),

            "preco_diaria": forms.NumberInput(attrs={
                "class": "campo-formulario placeholder-input input-preco",
                "placeholder": "100.00",
                "min": "0",
                "step": "0.01"
            })
        }

    def clean_capacidade(self):
        capacidade = self.cleaned_data["capacidade"]
        if capacidade < 1:
            raise forms.ValidationError("A capacidade deve ser de pelo menos 1 pessoa.")
        return capacidade


class EditarQuartoForm(QuartoForm):
    class Meta(QuartoForm.Meta):
        fields = [*QuartoForm.Meta.fields, "status"]
        labels = {**QuartoForm.Meta.labels, "status": "STATUS"}
        widgets = {
            **QuartoForm.Meta.widgets,
            "status": forms.Select(attrs={
                "class": "campo-formulario placeholder-input input-status"
            }),
        }

class ReservaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].label_from_instance = (
            lambda cliente: f"{cliente} — CPF: {cliente.cpf}"
        )
        self.fields["quarto"].queryset = Quarto.objects.none()
        self.fields["quarto"].error_messages["invalid_choice"] = (
            "Este quarto não está disponível nas datas escolhidas."
        )

        if self.is_bound:
            try:
                entrada = date.fromisoformat(self.data.get("data_entrada", ""))
                saida = date.fromisoformat(self.data.get("data_saida", ""))
            except (TypeError, ValueError):
                return

            if saida > entrada:
                self.fields["quarto"].queryset = quartos_disponiveis(entrada, saida)

    def clean(self):
        dados = super().clean()
        entrada = dados.get("data_entrada")
        saida = dados.get("data_saida")
        if entrada and saida and saida <= entrada:
            self.add_error("data_saida", "A saída deve ser posterior à entrada.")
        return dados

    class Meta:
        model = Reserva

        fields = [
            "cliente",
            "quarto",
            "data_entrada",
            "data_saida"
        ]

        labels = {
            "cliente": "CLIENTE",
            "quarto": "QUARTO",
            "data_entrada": "DATA DE ENTRADA",
            "data_saida": "DATA DE SAÍDA"
        }

        widgets = {
            "cliente": forms.Select(attrs={
                "class": "campo-formulario placeholder-input input-cliente"
            }),

            "quarto": forms.Select(attrs={
                "class": "campo-formulario placeholder-input input-quarto"
            }),

            "data_entrada": forms.DateInput(attrs={
                "type": "date",
                "class": "campo-formulario placeholder-input input-data-entrada",
                "placeholder": "01/01/2024"
            },
            format = {
                "%Y-%m-%d"
            }),

            "data_saida": forms.DateInput(attrs={
                "type": "date",
                "class": "campo-formulario placeholder-input input-data-saida",
                "placeholder": "05/01/2024"
            },
            format = {
                "%Y-%m-%d"
            }),
        }
