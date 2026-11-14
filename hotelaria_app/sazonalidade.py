from calendar import monthrange
from datetime import date


def _mover_ano(dia, ano):
    """Mantém mês/dia; 29 de fevereiro passa a 28 em anos não bissextos."""
    return date(ano, dia.month, min(dia.day, monthrange(ano, dia.month)[1]))


def periodo_no_ano(tarifa, ano_inicio):
    deslocamento = ano_inicio - tarifa.data_inicio.year
    return (
        _mover_ano(tarifa.data_inicio, ano_inicio),
        _mover_ano(tarifa.data_fim, tarifa.data_fim.year + deslocamento),
    )


def tarifa_vigente_em(tarifa, dia):
    if not tarifa.repetir_anualmente:
        return tarifa.data_inicio <= dia <= tarifa.data_fim

    # O início pode estar no ano anterior quando o período cruza dezembro/janeiro.
    for ano_inicio in (dia.year - 1, dia.year):
        if ano_inicio < tarifa.data_inicio.year:
            continue
        inicio, fim = periodo_no_ano(tarifa, ano_inicio)
        if inicio <= dia <= fim:
            return True
    return False


def proximidade_tarifa(tarifa, hoje):
    """Ordena períodos vigentes, próximos e encerrados nessa ordem."""
    if tarifa.data_inicio > hoje:
        return (1, (tarifa.data_inicio - hoje).days,
                tarifa.descricao.casefold(), tarifa.pk)

    if tarifa.repetir_anualmente:
        periodos = [
            periodo_no_ano(tarifa, ano)
            for ano in (hoje.year - 1, hoje.year, hoje.year + 1)
            if ano >= tarifa.data_inicio.year
        ]
    else:
        periodos = [(tarifa.data_inicio, tarifa.data_fim)]

    if any(inicio <= hoje <= fim for inicio, fim in periodos):
        return (0, 0, tarifa.descricao.casefold(), tarifa.pk)

    futuros = [inicio for inicio, _ in periodos if inicio > hoje]
    if futuros:
        return (1, (min(futuros) - hoje).days, tarifa.descricao.casefold(), tarifa.pk)

    return (2, (hoje - max(fim for _, fim in periodos)).days,
            tarifa.descricao.casefold(), tarifa.pk)


def periodo_para_exibir(tarifa, hoje):
    """Mostra a ocorrência atual ou a próxima nas tarifas anuais."""
    if not tarifa.repetir_anualmente or tarifa.data_inicio > hoje:
        return tarifa.data_inicio, tarifa.data_fim

    periodos = [
        periodo_no_ano(tarifa, ano)
        for ano in (hoje.year - 1, hoje.year, hoje.year + 1)
        if ano >= tarifa.data_inicio.year
    ]
    vigentes = [periodo for periodo in periodos if periodo[0] <= hoje <= periodo[1]]
    if vigentes:
        return vigentes[0]
    return min((periodo for periodo in periodos if periodo[0] > hoje),
               key=lambda periodo: periodo[0])
