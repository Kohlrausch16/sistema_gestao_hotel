from datetime import date

from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from .models import Cliente, Quarto, Reserva, TarifaSazonal, TipoQuarto
from .disponibilidade import quartos_disponiveis as buscar_quartos_disponiveis
from .precificacao import calcular_preco_total
from .forms import ClienteForm, ReservaForm, TarifaSazonalForm, TipoQuartoForm
from .forms import QuartoForm
from .forms import EditarQuartoForm
from django.contrib.auth.forms import UserCreationForm
from .models import Funcionario
from django.db.models.functions import Lower
from .forms import FuncionarioForm
from .models import Ocorrencia


def index(request):

    return render(request, "index.html")

def listar_clientes(request):

    clientes = Cliente.objects.all()

    dados = {
        "clientes": clientes
    }

    return render(request, "listagem_clientes.html", dados)


def cadastrar_cliente(request):
    form = ClienteForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            mensagem_confirmacao = "Cliente cadastrado com sucesso!"
            messages.success(request, mensagem_confirmacao)

            return redirect('listagem_clientes')

    return render(request, "cadastrar_cliente.html", {'formulario': form})

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
    quartos = Quarto.objects.select_related('tipo')
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

def criar_reserva(request):
    form = ReservaForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Reserva criada com sucesso!")
            return redirect('listar_reservas')

    dados = {
        "formulario": form,
    }
    return render(request, "criar_reserva.html", dados)


@require_GET
def quartos_disponiveis(request):
    try:
        entrada = date.fromisoformat(request.GET["entrada"])
        saida = date.fromisoformat(request.GET["saida"])
    except (KeyError, ValueError):
        return JsonResponse({"erro": "Informe datas válidas."}, status=400)

    if saida <= entrada:
        return JsonResponse(
            {"erro": "A saída deve ser posterior à entrada."}, status=400
        )

    reserva_id = request.GET.get("reserva_id")
    if reserva_id:
        try:
            reserva_id = int(reserva_id)
        except ValueError:
            return JsonResponse({"erro": "Reserva inválida."}, status=400)

    quartos = buscar_quartos_disponiveis(
        entrada, saida, excluir_reserva_id=reserva_id
    ).select_related('tipo').prefetch_related('tipo__TarifaSazonal')
    return JsonResponse({
        "quartos": [
            {
                "id": quarto.id,
                "numero": quarto.numero,
                "tipo": str(quarto.tipo),
                "preco_total": str(calcular_preco_total(quarto, entrada, saida)),
            }
            for quarto in quartos
        ]
    })

def listar_reservas(request):
    reservas = Reserva.objects.all()
    reservas = reservas.filter(ativo=True)

    dados = {
        "reservas": reservas,
        "hoje": timezone.localdate(),
    }

    return render(request, "listar_reservas.html", dados)

def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, ativo=True)
    if reserva.status != 'A' or reserva.data_entrada <= timezone.localdate():
        messages.error(request, "A reserva só pode ser editada antes do check-in enquanto estiver ativa.")
        return redirect('listar_reservas')

    form = ReservaForm(request.POST or None, instance=reserva)

    if request.method == "POST":
        if form.is_valid():
            if form.cleaned_data["data_entrada"] <= timezone.localdate():
                form.add_error("data_entrada", "A entrada deve ser uma data futura.")
            else:
                form.save()
                messages.success(request, "Reserva atualizada com sucesso!")
                return redirect('listar_reservas')

    dados = {
        "formulario": form,
        "reserva": reserva,
    }
    return render(request, "editar_reserva.html", dados)

@require_POST
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, ativo=True)
    if reserva.status != 'A':
        messages.error(request, "Apenas reservas ativas podem ser canceladas.")
        return redirect('listar_reservas')

    if reserva.data_entrada <= timezone.localdate():
        messages.error(request, "A reserva só pode ser cancelada antes do check-in.")
        return redirect('listar_reservas')

    reserva.status = 'C'
    reserva.save(update_fields=['status'])
    messages.success(request, "Reserva cancelada com sucesso!")
    return redirect('listar_reservas')

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

            return redirect('listar_funcionarios')
        else:
            messages.error(
                request,
                'Erro ao cadastrar funcionário. Verifique os dados e tente novamente.'
            )
            
            dados = {
                'formulario': formulario_de_funcionario,
                'cargos': Funcionario.CARGOS
            }
            return render(request, 'cadastrar_funcionario.html', dados)

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

def registrar_ocorrencia(request):
    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        descricao = request.POST.get('descricao')

        reserva = get_object_or_404(Reserva, id=reserva_id)

        if reserva.status != 'A':
            messages.error(request, "Não é possível registrar ocorrências para reservas que não estão ativas.")
            return redirect('listar_ocorrencia')

        Ocorrencia.objects.create(
            reserva=reserva,
            descricao=descricao
        )

        messages.success(request, "Ocorrência registrada com sucesso!")
        return redirect('listar_ocorrencia')

    reservas_ativas = Reserva.objects.filter(status='A')
    dados = {
        'reservas': reservas_ativas
    }
    return render(request, 'registrar_ocorrencia.html', dados)

def listar_ocorrencia(request):
    ordem = request.GET.get('ordem')
    pesquisar_quarto = request.GET.get('pesquisar_quarto', '')

    ocorrencias = Ocorrencia.objects.filter(
        concluida=False,
        reserva__quarto__numero__icontains=pesquisar_quarto
    ).order_by('data_ocorrencia')

    if ordem == 'decrescente':
        ocorrencias = Ocorrencia.objects.filter(
            concluida=False,
            reserva__quarto__numero__icontains=pesquisar_quarto
        ).order_by('-data_ocorrencia')

    dados = {
        'ocorrencias': ocorrencias,
        'pesquisar_quarto': pesquisar_quarto,
    }
    return render(request, 'listar_ocorrencia.html', dados)

@require_POST
def concluir_ocorrencia(request, ocorrencia_id):
    ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id)
    ocorrencia.concluida = True
    ocorrencia.save(update_fields=['concluida'])
    messages.success(request, "Ocorrência marcada como concluída.")
    return redirect('listar_ocorrencia')

def ocorrencias_concluidas(request):
    ordem = request.GET.get('ordem')
    pesquisar_quarto = request.GET.get('pesquisar_quarto', '')

    ocorrencias_concluidas = Ocorrencia.objects.filter(
        concluida=True,
        reserva__quarto__numero__icontains=pesquisar_quarto,
    ).order_by('data_ocorrencia')

    if ordem == 'decrescente':
        ocorrencias_concluidas = Ocorrencia.objects.filter(
            concluida=True,
            reserva__quarto__numero__icontains=pesquisar_quarto,
        ).order_by('-data_ocorrencia')

    dados = {
        'ocorrencias_concluidas': ocorrencias_concluidas,
        'pesquisar_quarto': pesquisar_quarto,
    }
    return render(request, 'ocorrencias_concluidas.html', dados)

def reabrir_ocorrencia(request, ocorrencia_id):
    ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id)
    ocorrencia.concluida = False
    ocorrencia.save(update_fields=['concluida'])
    messages.success(request, "Ocorrência reaberta com sucesso.")
    return redirect('listar_ocorrencia')

def visualizar_ocorrencia(request, ocorrencia_id):
    ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id)
    if request.method == 'POST':
            descricao = request.POST.get('descricao', '').strip()
            if not descricao:
                messages.error(request, "A descrição da ocorrência não pode ficar vazia.")
            else:
                ocorrencia.descricao = descricao
                ocorrencia.save(update_fields=['descricao'])
                messages.success(request, "Ocorrência atualizada com sucesso.")
                if ocorrencia.concluida:
                    return redirect('ocorrencias_concluidas')
                return redirect('listar_ocorrencia')
    
    dados = {
            'ocorrencia': ocorrencia
    }
    return render(request, 'visualizar_ocorrencia.html', dados)

def criar_tipo_quarto(request):
    formulario = TipoQuartoForm(request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        messages.success(request, "Tipo de quarto criado com sucesso!")
        return redirect('listar_tipos_quarto')

    return render(request, 'criar_tipo_quarto.html', {'formulario': formulario})

def listar_tipos_quarto(request):
    tipos_quarto = TipoQuarto.objects.prefetch_related('TarifaSazonal').order_by('tipo')
    dados = {
        'tipos_quarto': tipos_quarto
    }
    return render(request, 'listar_tipos_quarto.html', dados)

def editar_tipo_quarto(request, tipo_id):
    tipo_quarto = get_object_or_404(TipoQuarto, id=tipo_id)
    formulario = TipoQuartoForm(request.POST or None, instance=tipo_quarto)

    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        messages.success(request, "Tipo de quarto atualizado com sucesso!")
        return redirect('listar_tipos_quarto')

    dados = {
        'tipo_quarto': tipo_quarto,
        'formulario': formulario
    }
    return render(request, 'editar_tipo_quarto.html', dados)

def criar_tarifa_sazonal(request):
    formulario = TarifaSazonalForm(request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        messages.success(request, "Tarifa sazonal criada com sucesso!")
        return redirect('listar_tarifas_sazonais')

    return render(request, 'criar_tarifa_sazonal.html', {'formulario': formulario})

def listar_tarifas_sazonais(request):
    tarifas_sazonais = TarifaSazonal.objects.all().order_by('data_inicio', 'descricao')
    return render(request, 'listar_tarifas_sazonais.html', {
        'tarifas_sazonais': tarifas_sazonais,
    })

def editar_tarifa_sazonal(request, tarifa_id):
    tarifa_sazonal = get_object_or_404(TarifaSazonal, id=tarifa_id)
    formulario = TarifaSazonalForm(request.POST or None, instance=tarifa_sazonal)
    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        messages.success(request, "Tarifa sazonal atualizada com sucesso!")
        return redirect('listar_tarifas_sazonais')

    return render(request, 'editar_tarifa_sazonal.html', {
        'tarifa_sazonal': tarifa_sazonal,
        'formulario': formulario,
    })
