from django.urls import path
from hotelaria_app import views

urlpatterns = [
    path('', views.index, name='index'),

    path('cliente/cadastro/', views.cadastrar_cliente, name='cadastrar_cliente'),

    path('funcionario/cadastro/', views.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('funcionario/lista/', views.listar_funcionarios, name='listar_funcionarios'),
    path('funcionario/editar/<int:id>/', views.editar_funcionario, name='editar_funcionario'),
    path('funcionario/desativar/<int:id>/', views.desativar_funcionario, name='desativar_funcionario'),
    path('funcionario/ativar/<int:id>/', views.ativar_funcionario, name='ativar_funcionario'),
    path('funcionario/funcionarios_inativos/', views.funcionarios_inativos, name='funcionarios_inativos'),

    path('quarto/cadastro/', views.cadastrar_quarto, name='cadastrar_quarto'),
    path('quartos/', views.listar_quartos, name='listar_quartos'),
    path('quarto/<int:quarto_id>/excluir/', views.excluir_quarto, name='excluir_quarto'),
    path('quarto/<int:quarto_id>/editar/', views.editar_quarto, name='editar_quarto'),
    path('quartos/disponiveis/', views.quartos_disponiveis, name='quartos_disponiveis'),

    path('reserva/criar/', views.criar_reserva, name='criar_reserva'),
    path('reserva/<int:reserva_id>/editar/', views.editar_reserva, name='editar_reserva'),
    path('reserva/<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas/', views.listar_reservas, name='listar_reservas'),

    path('clientes/', views.listar_clientes, name='listagem_clientes'),
    path('clientes/cadastro/', views.cadastrar_cliente, name='cadastrar_cliente'),

    path('ocorrencias/registrar_ocorrencia', views.registrar_ocorrencia, name='registrar_ocorrencia'),
    path('ocorrencias/', views.listar_ocorrencia, name='listar_ocorrencia'),
    path('ocorrencias/<int:ocorrencia_id>/concluir/', views.concluir_ocorrencia, name='concluir_ocorrencia'),
    path('ocorrencias/concluidas/', views.ocorrencias_concluidas, name='ocorrencias_concluidas'),
    path('ocorrencias/<int:ocorrencia_id>/reabrir/', views.reabrir_ocorrencia, name='reabrir_ocorrencia'),
    path('ocorrencias/<int:ocorrencia_id>/', views.visualizar_ocorrencia, name='visualizar_ocorrencia'),

    path('tarifa_sazonal/criar/', views.criar_tarifa_sazonal, name='criar_tarifa_sazonal'),
    path('tarifa_sazonal/listar/', views.listar_tarifas_sazonais, name='listar_tarifas_sazonais'),
    path('tarifa_sazonal/<int:tarifa_id>/editar/', views.editar_tarifa_sazonal, name='editar_tarifa_sazonal'),
    path('tarifa_sazonal/<int:tarifa_id>/excluir/', views.excluir_tarifa_sazonal, name='excluir_tarifa_sazonal'),

    path('tipo_quarto/criar/', views.criar_tipo_quarto, name='criar_tipo_quarto'),
    path('tipo_quarto/listar/', views.listar_tipos_quarto, name='listar_tipos_quarto'),
    path('tipo_quarto/<int:tipo_id>/editar/', views.editar_tipo_quarto, name='editar_tipo_quarto'),
    path('tipo_quarto/<int:tipo_id>/excluir/', views.excluir_tipo_quarto, name='excluir_tipo_quarto'),
]
