from django.db import models
from .fields import BaseModel

TIPO_QUARTO_CHOICES = [
    ('S', 'Simples'),
    ('D', 'Duplo'),
    ('S', 'Suíte'),
]

STATUS_QUARTO_CHOICES = [
    ('D', 'Disponível'),
    ('O', 'Ocupado'),
    ('M', 'Manutenção'),
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
    tipo = models.CharField(max_length=1, choices=TIPO_QUARTO_CHOICES)
    capacidade = models.IntegerField(default=1)
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=1, default='D', choices=STATUS_QUARTO_CHOICES)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.numero + " - " + self.tipo