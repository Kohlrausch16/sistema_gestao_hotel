from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError


def calcular_preco_total(quarto, entrada, saida):
    """Soma as diárias de [entrada, saida) com os adicionais sazonais vigentes."""
    if saida <= entrada:
        raise ValidationError("A saída deve ser posterior à entrada.")

    tipo = quarto.tipo
    tarifas = [
        tarifa for tarifa in tipo.TarifaSazonal.all()
        if tarifa.ativo and tarifa.data_inicio < saida and tarifa.data_fim >= entrada
    ]
    total = Decimal("0.00")
    dia = entrada
    while dia < saida:
        aplicaveis = [
            tarifa for tarifa in tarifas
            if tarifa.data_inicio <= dia <= tarifa.data_fim
        ]
        total += Decimal(str(tipo.preco_diaria)) + sum(
            (Decimal(str(tarifa.valor)) for tarifa in aplicaveis), Decimal("0.00")
        )
        dia += timedelta(days=1)
    return total
