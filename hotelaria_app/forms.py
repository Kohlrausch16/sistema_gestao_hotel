from django import forms
from .models import Cliente, Endereco

class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente

        fields = [
            "nome",
            "sobrenome",
            "cpf",
            "data_nascimento",
            "email",
            "telefone"
        ]

        labels = {
            "nome": "NOME",
            "sobrenome": "SOBRENOME",
            "cpf": "CPF",
            "data_nascimento": "DATA DE NASCIMENTO",
            "email": "EMAIL",
            "telefone": "TELEFONE"
        }

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input",
                "placeholder": "João Antônio"
            }),

            "sobrenome": forms.TextInput(attrs={
                "class": "campo-formulario placeholder-input",
                "placeholder": "Souza Santos"
            }),

            "cpf": forms.NumberInput(attrs={
                "class": "campo-formulario placeholder-input",
                "placeholder": "000.000.000-00",
                "min": "11",
                "max": "11"
            }),

            "data_nascimento": forms.DateInput(attrs={
                "type": "date",
                "class": "campo-formulario placeholder-input",
                "placeholder": "01/01/1970"
            },
            format = {
                "%Y-%m-%d"
            }),

            "email": forms.TextInput(attrs={
                            "class": "campo-formulario placeholder-input",
                            "placeholder": "josesantos@gmail.com"
                        }),

            "telefone": forms.NumberInput(attrs={
                "class": "campo-formulario placeholder-input",
                "placeholder": "(51) 99999-9999",
                "min": "11",
                "max": "11"
            })
        }