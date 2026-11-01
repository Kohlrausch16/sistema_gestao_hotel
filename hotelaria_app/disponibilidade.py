from .models import Quarto, Reserva


def quartos_disponiveis(entrada, saida):
    reservas_conflitantes = Reserva.objects.filter(
        ativo=True,
        data_entrada__lt=saida,
        data_saida__gt=entrada,
    ).values("quarto_id")

    return (
        Quarto.objects.filter(ativo=True)
        .exclude(status="M")
        .exclude(id__in=reservas_conflitantes)
        .order_by("numero")
    )
