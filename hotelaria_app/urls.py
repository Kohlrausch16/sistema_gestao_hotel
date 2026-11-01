from django.urls import path
from hotelaria_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('clientes/', views.listar_clientes, name='listagem_clientes'),
    path('clientes/cadastro/', views.cadastrar_cliente, name='cadastrar_cliente'),
]