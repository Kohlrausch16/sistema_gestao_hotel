from datetime import date

from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from hotelaria_app.models import Quarto, Reserva

from .disponibilidade import quartos_disponiveis as buscar_quartos_disponiveis
from .forms import ClienteForm, ReservaForm
from .forms import QuartoForm
from .forms import EditarQuartoForm

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

    quartos = buscar_quartos_disponiveis(entrada, saida, excluir_reserva_id=reserva_id)
    return JsonResponse({
        "quartos": [
            {"id": quarto.id, "numero": quarto.numero, "tipo": quarto.get_tipo_display()}
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
