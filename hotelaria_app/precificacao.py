from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from .sazonalidade import tarifa_vigente_em


def calcular_preco_total(quarto, entrada, saida):
    """Soma as diárias de [entrada, saida) com os adicionais sazonais vigentes."""
    if saida <= entrada:
        raise ValidationError("A saída deve ser posterior à entrada.")

    tipo = quarto.tipo
    tarifas = [tarifa for tarifa in tipo.TarifaSazonal.all() if tarifa.ativo]
    total = Decimal("0.00")
    dia = entrada
    while dia < saida:
        aplicaveis = [
            tarifa for tarifa in tarifas
            if tarifa_vigente_em(tarifa, dia)
        ]
        total += Decimal(str(tipo.preco_diaria)) + sum(
            (Decimal(str(tarifa.valor)) for tarifa in aplicaveis), Decimal("0.00")
        )
        dia += timedelta(days=1)
    return total
