from .models import Quarto, Reserva


def reservas_ativas_em(dia):
    return Reserva.objects.filter(
        ativo=True,
        status="A",
        data_entrada__lte=dia,
        data_saida__gt=dia,
    )


def quartos_disponiveis(entrada, saida, excluir_reserva_id=None):
    reservas_conflitantes = Reserva.objects.filter(
        ativo=True,
        status="A",
        data_entrada__lt=saida,
        data_saida__gt=entrada,
    ).values("quarto_id")

    if excluir_reserva_id is not None:
        reservas_conflitantes = reservas_conflitantes.exclude(id=excluir_reserva_id)

    return (
        Quarto.objects.filter(ativo=True)
        .exclude(status__in=("M", "O"))
        .exclude(id__in=reservas_conflitantes)
        .order_by("numero")
    )
