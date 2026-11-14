from django import forms
from django.core.exceptions import ValidationError
from datetime import date

from .disponibilidade import quartos_disponiveis
from .precificacao import calcular_preco_total
from .models import Cliente, Quarto, Reserva, Funcionario, Ocorrencia, TarifaSazonal, TipoQuarto

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

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nome', 'cargo']
        
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
        elif self.instance.pk:
            entrada = self.instance.data_entrada
            saida = self.instance.data_saida
        else:
            return

        if saida > entrada:
            self.fields["quarto"].queryset = quartos_disponiveis(
                entrada, saida, excluir_reserva_id=self.instance.pk
            )

    def clean(self):
        dados = super().clean()
        entrada = dados.get("data_entrada")
        saida = dados.get("data_saida")
        if entrada and saida and saida <= entrada:
            self.add_error("data_saida", "A saída deve ser posterior à entrada.")
        quarto = dados.get("quarto")
        if quarto and entrada and saida and saida > entrada:
            try:
                self.preco_total_calculado = calcular_preco_total(quarto, entrada, saida)
            except ValidationError as erro:
                self.add_error(None, erro)
        return dados

    def save(self, commit=True):
        reserva = super().save(commit=False)
        reserva.preco_total = self.preco_total_calculado
        if commit:
            reserva.save()
            self.save_m2m()
        return reserva

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
            format="%Y-%m-%d"),

            "data_saida": forms.DateInput(attrs={
                "type": "date",
                "class": "campo-formulario placeholder-input input-data-saida",
                "placeholder": "05/01/2024"
            },
            format="%Y-%m-%d"),
        }

class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['reserva', 'descricao']
        labels = {
            'reserva': 'RESERVA',
            'descricao': 'DESCRIÇÃO'
        }
        widgets = {
            'reserva': forms.Select(attrs={
                "class": "campo-formulario placeholder-input input-reserva"
            }),
            'descricao': forms.Textarea(attrs={
                "class": "campo-formulario placeholder-input input-descricao",
                "placeholder": "Descreva a ocorrência aqui..."
            }),
        }

class TipoQuartoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['TarifaSazonal'].label_from_instance = (
            lambda tarifa: (
                f"{tarifa.descricao} · "
                f"{tarifa.data_inicio:%d/%m/%Y} a {tarifa.data_fim:%d/%m/%Y} · "
                f"R$ {tarifa.valor:.2f}"
            )
        )

    def clean_preco_diaria(self):
        preco = self.cleaned_data['preco_diaria']
        if preco < 0:
            raise forms.ValidationError("O preço diário não pode ser negativo.")
        return preco

    class Meta:
        model = TipoQuarto
        fields = ['tipo', 'preco_diaria', 'TarifaSazonal']
        labels = {
            'tipo': 'TIPO',
            'preco_diaria': 'PREÇO DIÁRIO',
            'TarifaSazonal': 'TARIFAS SAZONAIS'
        }
        widgets = {
            'tipo': forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-tipo",
                "placeholder": "Tipo do quarto"
            }),
            'preco_diaria': forms.NumberInput(attrs={
                "class": "campo-formulario placeholder-input input-preco-diaria",
                "placeholder": "100.00",
                "min": "0",
                "step": "0.01"
            }),
            'TarifaSazonal': forms.CheckboxSelectMultiple(),
        }

class TarifaSazonalForm(forms.ModelForm):
    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor < 0:
            raise forms.ValidationError("O adicional sazonal não pode ser negativo.")
        return valor

    def clean(self):
        dados = super().clean()
        inicio = dados.get('data_inicio')
        fim = dados.get('data_fim')
        if inicio and fim and fim < inicio:
            self.add_error('data_fim', "O fim deve ser igual ou posterior ao início.")
        return dados

    class Meta:
        model = TarifaSazonal
        fields = ['descricao', 'valor', 'data_inicio', 'data_fim']
        labels = {
            'descricao': 'DESCRIÇÃO',
            'valor': 'ADICIONAL POR DIÁRIA',
            'data_inicio': 'DATA DE INÍCIO',
            'data_fim': 'DATA DE FIM'
        }
        widgets = {
            'descricao': forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input input-descricao",
                "placeholder": "Descrição da tarifa sazonal"
            }),
            'valor': forms.NumberInput(attrs={
                "class": "campo-formulario placeholder-input input-valor",
                "placeholder": "100.00",
                "min": "0",
                "step": "0.01"
            }),
            'data_inicio': forms.DateInput(attrs={
                "type": "date",
                "class": "campo-formulario placeholder-input input-data-inicio",
                "placeholder": "01/01/2024"
            },
            format="%Y-%m-%d"),
            'data_fim': forms.DateInput(attrs={
                "type": "date",
                "class": "campo-formulario placeholder-input input-data-fim",
                "placeholder": "05/01/2024"
            },
            format="%Y-%m-%d"),
        }
