from django.db import models
from .fields import BaseModel

tipo_quarto_choices = [
    ('S', 'Simples'),
    ('D', 'Duplo'),
    ('T', 'Triplo'),
]

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

class Quarto(models.Model):
    numero = models.CharField(max_length=10)
    tipo = models.CharField(max_length=1, choices=tipo_quarto_choices)
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.numero + " - " + self.tipo