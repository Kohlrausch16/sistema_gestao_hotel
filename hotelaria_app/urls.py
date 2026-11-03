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
]
