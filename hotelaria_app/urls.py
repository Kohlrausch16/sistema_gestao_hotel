from django.urls import path
from hotelaria_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cliente/cadastro/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('quarto/cadastro/', views.cadastrar_quarto, name='cadastrar_quarto'),
    path('quartos/', views.listar_quartos, name='listar_quartos'),
    path('quarto/<int:quarto_id>/excluir/', views.excluir_quarto, name='excluir_quarto'),
    path('quarto/<int:quarto_id>/editar/', views.editar_quarto, name='editar_quarto'),
]
