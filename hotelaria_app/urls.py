from django.urls import path
from hotelaria_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cliente/cadastro/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('quarto/cadastro/', views.cadastrar_quarto, name='cadastrar_quarto'),
]
