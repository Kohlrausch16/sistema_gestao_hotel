from django.db import models
from .fields import BaseModel

class Endereco(BaseModel):
    logradouro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)        

    def __str__(self):
        return self.logradouro


class Cliente(BaseModel):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField(max_length=11)
    ativo = models.BooleanField(default=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.nome + " " + self.sobrenome