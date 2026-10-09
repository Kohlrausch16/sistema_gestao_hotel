from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect

from .models import *
from .forms import ClienteForm

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