from django import template
from hotelaria_app.pode_acessar import pode_acessar as usuario_pode_acessar

register = template.Library()

@register.simple_tag(takes_context=True)
def pode_acessar(context, nome_view):
    return usuario_pode_acessar(context["request"].user, nome_view)


