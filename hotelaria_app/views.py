from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from hotelaria_app.models import Quarto

from .models import *
from .forms import ClienteForm
from .forms import QuartoForm
from .forms import EditarQuartoForm

def index(request):

    return render(request, "index.html")

def listar_clientes(request):

    clientes = Cliente.objects.all()

    dados = {
        "clientes": clientes
    }

    return render(request, "listagem_clientes.html", dados)


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

            return redirect('listar_quartos')


    return render(request, "cadastrar_quarto.html", {'formulario': form})

def listar_quartos(request):
    pesquisa = request.GET.get("q", "").strip()
    quartos = Quarto.objects.all()
    quartos = quartos.filter(ativo=True)
    if pesquisa:
        quartos = quartos.filter(numero__icontains=pesquisa)

    dados = {
        "quartos": quartos,
        "pesquisa": pesquisa,
    }

    return render(request, "listar_quartos.html", dados)

def editar_quarto(request, quarto_id):
    quarto = Quarto.objects.get(id=quarto_id)
    form = EditarQuartoForm(request.POST or None, instance=quarto)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            mensagem_confirmacao = "Quarto atualizado com sucesso!"
            messages.success(request, mensagem_confirmacao)

            return redirect('listar_quartos')

    return render(request, "editar_quarto.html", {'formulario': form, 'quarto': quarto})

@require_POST
def excluir_quarto(request, quarto_id):
    quarto = Quarto.objects.get(id=quarto_id)
    if quarto.status == 'O':
        mensagem_erro = "Não é possível excluir um quarto ocupado"
        messages.error(request, mensagem_erro)
        return redirect('listar_quartos')
    
    quarto.ativo = False
    quarto.save()

    mensagem_confirmacao = "Quarto excluído com sucesso!"
    messages.success(request, mensagem_confirmacao)

    return redirect('listar_quartos')
