from django.db import models
from .fields import BaseModel

from django.contrib.auth.models import User


STATUS_QUARTO_CHOICES = [
    ('D', 'Disponível'),
    ('O', 'Ocupado'),
    ('M', 'Manutenção'),
]

STATUS_RESERVA_CHOICES = [
    ('A', 'Ativa'),
    ('C', 'Cancelada'),
    ('F', 'Finalizada'),
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

class TipoQuarto(models.Model):
    tipo = models.CharField(max_length=20)
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    TarifaSazonal = models.ManyToManyField('TarifaSazonal', blank=True)

    def __str__(self):
        return self.tipo

class TarifaSazonal(models.Model):
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    def __str__(self):
        return self.descricao

class Quarto(models.Model):
    numero = models.CharField(max_length=10)
    tipo = models.ForeignKey(TipoQuarto, on_delete=models.PROTECT)
    capacidade = models.IntegerField(default=1)
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=1, default='D', choices=STATUS_QUARTO_CHOICES)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.numero} - {self.tipo}"

class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    quarto = models.ForeignKey(Quarto, on_delete=models.CASCADE)
    data_entrada = models.DateField()
    data_saida = models.DateField()
    ativo = models.BooleanField(default=True)
    status = models.CharField(max_length=1, default='A', choices=STATUS_RESERVA_CHOICES)

    def __str__(self):
        return f"Reserva de {self.cliente} no quarto {self.quarto} de {self.data_entrada} a {self.data_saida}"
    
class Ocorrencia(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    descricao = models.TextField()
    data_ocorrencia = models.DateTimeField(auto_now_add=True)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return f"Ocorrência para a reserva {self.reserva.id} em {self.data_ocorrencia}"
