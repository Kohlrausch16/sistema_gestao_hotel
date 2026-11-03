from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from .forms import ClienteForm

from django.contrib.auth.forms import UserCreationForm
from .models import Funcionario
from django.db.models.functions import Lower
from .forms import FuncionarioForm


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

def cadastrar_funcionario(request):

    if request.method == 'POST':
        formulario_de_funcionario = UserCreationForm(request.POST)

        if formulario_de_funcionario.is_valid():

            usuario = formulario_de_funcionario.save()
            usuario.is_active = True
            usuario.save()

            nome = request.POST.get('nome')
            cargo = request.POST.get('cargo')

            Funcionario.objects.create(
                nome=nome,
                cargo=cargo,
                usuario=usuario
            )

            messages.success(
                request,
                f'Funcionário {nome} cadastrado com sucesso!'
            )

            return redirect('cadastrar_funcionario')

    else:
        formulario_de_funcionario = UserCreationForm()

    dados = {
        'formulario': formulario_de_funcionario,
        'cargos': Funcionario.CARGOS
    }

    return render(request, 'cadastrar_funcionario.html', dados)


def listar_funcionarios(request):
    
    ordem = request.GET.get('ordem')
    nome_da_pesquisa = request.GET.get('nome_da_pesquisa', '')
    
    
    funcionarios = Funcionario.objects.filter(
        nome__icontains=nome_da_pesquisa,
        usuario__is_active=True
    ).order_by(Lower('nome'))

    if ordem=='decrescente':
        funcionarios = Funcionario.objects.filter(
            nome__icontains=nome_da_pesquisa,
            usuario__is_active=True
        ).order_by(Lower('nome').desc())
   
    dados = {
        'funcionarios': funcionarios,
        'nome_da_pesquisa': nome_da_pesquisa,
    }

    return render(request, 'listar_funcionarios.html', dados)

def editar_funcionario(request, id):

    funcionario = Funcionario.objects.get(id=id)

    form = FuncionarioForm(instance=funcionario)

    if request.method == 'POST':

        form = FuncionarioForm(request.POST, instance=funcionario)
        
        if form.is_valid():
            form.save()
            nome = form.cleaned_data['nome']

            mensagem_confirmacao = f'Funcionário {nome} alterado com sucesso!'
            messages.success(request, mensagem_confirmacao)
                
            return redirect('listar_funcionarios')

    dados = {
        'formulario': form
    }

    return render(request, 'editar_funcionario.html', dados)


def desativar_funcionario(request, id):

    funcionario = Funcionario.objects.get(id=id)

    nome = funcionario.nome

    funcionario.usuario.is_active = False
    funcionario.usuario.save(update_fields=['is_active'])

    mensagem = f'Funcionário {nome} Desativado com sucesso'
    messages.success(request, mensagem)

    return redirect('listar_funcionarios') 

def funcionarios_inativos(request):

    funcionarios = Funcionario.objects.filter(
        usuario__is_active=False
    )

    dados = {
        'funcionarios' : funcionarios
    }

    return render(request, 'funcionarios_inativos.html', dados)

def ativar_funcionario(request, id):

    funcionario = Funcionario.objects.get(id=id)

    nome = funcionario.nome
    funcionario.usuario.is_active = True
    funcionario.usuario.save(update_fields=['is_active'])

    mensagem = f'Funcionário {nome} ativado com sucesso'
    messages.success(request, mensagem)

    return redirect('listar_funcionarios')