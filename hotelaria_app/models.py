from django.db import models
from .fields import BaseModel

from django.contrib.auth.models import User

class Cliente(BaseModel):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField(max_length=11)
    ativo = models.BooleanField(default=True)
    logradouro = models.CharField(max_length=100, default=True)
    numero = models.CharField(max_length=10, default=True)
    bairro = models.CharField(max_length=100, default=True)
    cidade = models.CharField(max_length=100, default=True) 

    def __str__(self):
        return self.nome + " " + self.sobrenome

class Funcionario(models.Model):

    CARGOS = [

        ('gerente', 'Gerente'),
        ('recepcionista', 'Recepcionista'),
        ('cozinheiro', 'Cozinheiro'),
        ('camareira', 'Camareira')

    ]

    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, choices=CARGOS)
    usuario = models.OneToOneField(User, on_delete = models.CASCADE)

    def __str__(self):
        return self.nome