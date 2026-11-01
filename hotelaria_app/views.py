from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect

from hotelaria_app.models import Quarto

from .forms import ClienteForm
from .forms import QuartoForm

def index(request):

    return render(request, "index.html")

def cadastrar_cliente(request):

    form = ClienteForm()

    dados = {
        'formulario': form
    }

    if(request.method == "POST"):

        form = ClienteForm(request.POST)

        if(form.is_valid):
            form.save()

            mensagem_confirmacao = "Cliente cadastrado com sucesso!"
            messages.success(request, mensagem_confirmacao)

            # TODO - Alterar o redirecionamento para a página de listagem de clientes
            return redirect('index')


    return render(request, "cadastrar_cliente.html", dados)

def cadastrar_quarto(request):
    form = QuartoForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            mensagem_confirmacao = "Quarto cadastrado com sucesso!"
            messages.success(request, mensagem_confirmacao)

            return redirect('index')


    return render(request, "cadastrar_quarto.html", {'formulario': form})

def listar_quartos(request):
    quartos = Quarto.objects.all()
    
    dados = {
        'quartos': quartos
    }

    return render(request, "listar_quartos.html", dados)