from django import forms
from .models import Cliente

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