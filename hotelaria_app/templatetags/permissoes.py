from django import template
from hotelaria_app.pode_acessar import pode_acessar as usuario_pode_acessar

register = template.Library()

@register.simple_tag(takes_context=True)
def pode_acessar(context, nome_view):
    return usuario_pode_acessar(context["request"].user, nome_view)


ROTAS_MENU = {
    "listagem_clientes": {"listagem_clientes", "cadastrar_cliente", "editar_cliente"},
    "listar_quartos": {"listar_quartos", "cadastrar_quarto", "editar_quarto"},
    "listar_tipos_quarto": {"listar_tipos_quarto", "criar_tipo_quarto", "editar_tipo_quarto"},
    "listar_tarifas_sazonais": {
        "listar_tarifas_sazonais", "criar_tarifa_sazonal", "editar_tarifa_sazonal",
    },
    "listar_reservas": {
        "listar_reservas", "criar_reserva", "editar_reserva", "checkin_page", "checkin",
    },
    "listar_funcionarios": {
        "listar_funcionarios", "cadastrar_funcionario", "editar_funcionario",
        "funcionarios_inativos",
    },
    "listar_ocorrencia": {
        "listar_ocorrencia", "registrar_ocorrencia", "visualizar_ocorrencia",
        "ocorrencias_concluidas",
    },
    "gerar_relatorio": {"gerar_relatorio"},
}


@register.simple_tag(takes_context=True)
def menu_ativo(context, nome_menu):
    rota = getattr(context["request"], "resolver_match", None)
    return rota is not None and rota.url_name in ROTAS_MENU.get(nome_menu, set())


