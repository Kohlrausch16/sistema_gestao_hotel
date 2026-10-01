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

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "campo-formulario",
                "placeholder": "Informe o nome"
            }),
        }