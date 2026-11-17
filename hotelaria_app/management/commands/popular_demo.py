"""Popula dados fictícios de apresentação sem alterar funcionários."""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from hotelaria_app.models import Cliente, Funcionario, Ocorrencia, Quarto, Reserva, TarifaSazonal, TipoQuarto
from hotelaria_app.precificacao import calcular_preco_total


TIPOS = (
    ("Standard", "249.00", 2),
    ("Duplo Comfort", "329.00", 2),
    ("Família", "469.00", 4),
    ("Suíte Premium", "649.00", 2),
)

SENHA_FUNCIONARIOS = "Senha99@"
FUNCIONARIOS = (
    ("gregory", "Gregory", "gerente", False),
    ("KeenanYuri", "Keenan yuri", "recepcionista", False),
    ("Cozinheiro", "Cozinheiro", "cozinheiro", True),
    ("Recepcionista", "Recepcionista", "recepcionista", True),
    ("Gerente", "Gerente", "gerente", True),
    ("Camareira", "Camareira", "camareira", True),
)

# Nome, sobrenome e cidade fictícios. CPFs e e-mails são gerados apenas para demonstração.
HOSPEDES = (
    ("Mariana", "Almeida", "São Paulo"),
    ("Rafael", "Costa", "Curitiba"),
    ("Camila", "Ferreira", "Belo Horizonte"),
    ("Lucas", "Mendes", "Porto Alegre"),
    ("Beatriz", "Oliveira", "Rio de Janeiro"),
    ("Gabriel", "Santos", "Florianópolis"),
    ("Isabela", "Rocha", "Campinas"),
    ("Pedro", "Martins", "Brasília"),
    ("Larissa", "Ribeiro", "Salvador"),
    ("Daniel", "Carvalho", "Recife"),
    ("Juliana", "Lima", "Goiânia"),
    ("Felipe", "Barbosa", "Niterói"),
    ("Renata", "Pereira", "Santos"),
    ("André", "Gomes", "Joinville"),
    ("Patrícia", "Nogueira", "Vitória"),
    ("Thiago", "Araújo", "Londrina"),
    ("Aline", "Moreira", "São José dos Campos"),
    ("Bruno", "Cardoso", "Ribeirão Preto"),
    ("Fernanda", "Teixeira", "Maringá"),
    ("Eduardo", "Vieira", "Sorocaba"),
    ("Priscila", "Dias", "Fortaleza"),
    ("Rodrigo", "Monteiro", "Natal"),
    ("Vanessa", "Castro", "Maceió"),
    ("Marcelo", "Freitas", "João Pessoa"),
    ("Carolina", "Campos", "Aracaju"),
    ("Gustavo", "Moraes", "Belém"),
    ("Natália", "Pinto", "Manaus"),
    ("Henrique", "Machado", "Cuiabá"),
    ("Bianca", "Duarte", "Campo Grande"),
    ("Leonardo", "Batista", "Uberlândia"),
    ("Sofia", "Correia", "Blumenau"),
    ("Diego", "Azevedo", "Petrópolis"),
)

DDDS = (
    11, 41, 31, 51, 21, 48, 19, 61,
    71, 81, 62, 21, 13, 47, 27, 43,
    12, 16, 44, 15, 85, 84, 82, 83,
    79, 91, 92, 65, 67, 34, 47, 24,
)

LOGRADOUROS = (
    "Rua das Palmeiras", "Avenida Brasil", "Rua das Acácias",
    "Rua São José", "Avenida Central", "Rua do Comércio",
    "Alameda dos Ipês", "Rua das Flores",
)

BAIRROS = ("Centro", "Boa Vista", "Vila Nova", "Santa Cruz", "São Pedro", "Bela Vista")

# Número, índice do hóspede, entrada relativa a hoje, noites e status.
RESERVAS = (
    ("201", 0, 0, 3, "A"),
    ("202", 1, 0, 2, "A"),
    ("301", 2, 0, 4, "A"),
    ("302", 3, 0, 2, "A"),
    ("203", 4, -3, 3, "E"),
    ("204", 5, -2, 2, "E"),
    ("303", 6, -2, 5, "E"),
    ("304", 7, -1, 4, "E"),
    ("401", 8, -1, 3, "E"),
    ("402", 9, -2, 5, "E"),
    ("205", 10, 2, 3, "A"),
    ("206", 11, 3, 2, "A"),
    ("305", 12, 1, 4, "A"),
    ("306", 13, 5, 3, "A"),
    ("403", 14, 4, 2, "A"),
    ("404", 15, 6, 3, "A"),
    ("405", 16, 2, 2, "A"),
    ("406", 17, 7, 4, "A"),
    ("407", 18, 8, 3, "A"),
    ("408", 19, 1, 5, "A"),
    ("201", 20, -12, 3, "F"),
    ("202", 21, -9, 2, "F"),
    ("301", 22, -16, 4, "F"),
    ("302", 23, -8, 3, "F"),
    ("203", 24, -14, 2, "F"),
    ("204", 25, -11, 3, "F"),
    ("305", 26, -7, 2, "F"),
    ("306", 27, -13, 4, "F"),
    ("401", 28, -10, 2, "F"),
    ("402", 29, -15, 5, "F"),
    ("206", 30, 12, 3, "C"),
    ("307", 31, 3, 2, "C"),
    ("308", 20, 5, 2, "C"),
)

OCORRENCIAS = (
    ("207", "Ar-condicionado sem refrigeração; manutenção solicitada.", False, -1),
    ("208", "Vazamento no banheiro; quarto interditado para reparo.", False, 0),
    ("205", "Controle remoto da televisão não funciona.", False, 0),
    ("306", "Lâmpada da luminária de leitura queimada.", False, -1),
    ("202", "Troca de fechadura eletrônica concluída.", True, -5),
    ("302", "Limpeza extra solicitada e concluída.", True, -3),
    ("404", "Ajuste do ar-condicionado concluído.", True, -2),
)


def cpf_ficticio(indice):
    """Gera CPF com dígitos verificadores válidos para dados fictícios."""
    base = [int(digito) for digito in f"970000{indice:03d}"]
    for peso_inicial in (10, 11):
        soma = sum(digito * peso for digito, peso in zip(base, range(peso_inicial, 1, -1)))
        resto = (soma * 10) % 11
        base.append(0 if resto == 10 else resto)
    return "".join(map(str, base))


class Command(BaseCommand):
    help = "Cria dados de apresentação e prepara os funcionários para a demonstração."

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-base",
            type=date.fromisoformat,
            default=None,
            help="Data de referência no formato AAAA-MM-DD; padrão: data local atual.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        hoje = options["data_base"] or timezone.localdate()
        Usuario = get_user_model()
        for login, nome, cargo, ativo in FUNCIONARIOS:
            usuario, _ = Usuario.objects.get_or_create(username=login)
            if usuario.is_superuser:
                raise CommandError(f"O usuário {login} é administrador e não pode ser usado como funcionário de demonstração.")
            campos_alterados = []
            if not usuario.check_password(SENHA_FUNCIONARIOS):
                usuario.set_password(SENHA_FUNCIONARIOS)
                campos_alterados.append("password")
            if usuario.is_active != ativo:
                usuario.is_active = ativo
                campos_alterados.append("is_active")
            if campos_alterados:
                usuario.save(update_fields=campos_alterados)
            Funcionario.objects.update_or_create(
                usuario=usuario,
                defaults={"nome": nome, "cargo": cargo},
            )

        tipos = {}
        for nome, preco, capacidade in TIPOS:
            tipo, _ = TipoQuarto.objects.update_or_create(
                tipo=nome,
                defaults={
                    "preco_diaria": Decimal(preco),
                    "capacidade": capacidade,
                    "ativo": True,
                },
            )
            tipos[nome] = tipo

        proxima_sexta = hoje + timedelta(days=(4 - hoje.weekday()) % 7)
        tarifas = {}
        ano_verao = hoje.year - 1 if hoje.month == 1 and hoje.day <= 15 else hoje.year
        for nome, valor, inicio, fim, anual in (
            ("Fim de semana especial", "45.00", proxima_sexta, proxima_sexta + timedelta(days=2), False),
            ("Feriado prolongado", "90.00", hoje + timedelta(days=10), hoje + timedelta(days=13), False),
            ("Alta temporada de verão", "120.00", date(ano_verao, 12, 15), date(ano_verao + 1, 1, 15), True),
        ):
            tarifa, _ = TarifaSazonal.objects.update_or_create(
                descricao=nome,
                defaults={
                    "valor": Decimal(valor),
                    "data_inicio": inicio,
                    "data_fim": fim,
                    "repetir_anualmente": anual,
                    "ativo": True,
                },
            )
            tarifas[nome] = tarifa

        tipos["Standard"].TarifaSazonal.set((tarifas["Fim de semana especial"],))
        tipos["Duplo Comfort"].TarifaSazonal.set((
            tarifas["Fim de semana especial"], tarifas["Feriado prolongado"],
        ))
        tipos["Família"].TarifaSazonal.set((
            tarifas["Feriado prolongado"], tarifas["Alta temporada de verão"],
        ))
        tipos["Suíte Premium"].TarifaSazonal.set(tarifas.values())

        quartos = {}
        distribuicao = {
            "Standard": ("201", "202", "203", "204", "205", "206", "207", "208"),
            "Duplo Comfort": ("301", "302", "303", "304", "305", "306", "307", "308"),
            "Família": ("401", "402", "403", "404"),
            "Suíte Premium": ("405", "406", "407", "408"),
        }
        for nome, numeros in distribuicao.items():
            for numero in numeros:
                existente = Quarto.objects.filter(numero=numero).first()
                if existente and existente.tipo_id != tipos[nome].id:
                    raise CommandError(f"Quarto {numero} já existe com outro tipo.")
                quarto, _ = Quarto.objects.update_or_create(
                    numero=numero,
                    defaults={
                        "tipo": tipos[nome],
                        "status": "M" if numero in ("207", "208") else "D",
                        "ativo": True,
                    },
                )
                quartos[numero] = quarto

        clientes = []
        for indice, (nome, sobrenome, cidade) in enumerate(HOSPEDES, start=1):
            cpf = cpf_ficticio(indice)
            email = f"hospede{indice:02d}@example.com"
            existente = Cliente.objects.filter(cpf=cpf).first()
            if existente and existente.email != email:
                raise CommandError(f"CPF fictício {cpf} já pertence a outro cliente.")
            cliente, _ = Cliente.objects.update_or_create(
                cpf=cpf,
                defaults={
                    "nome": nome,
                    "sobrenome": sobrenome,
                    "data_nascimento": date(1979 + indice % 22, (indice % 12) + 1, (indice % 27) + 1),
                    "email": email,
                    "telefone": f"{DDDS[indice - 1]}98{indice:07d}",
                    "logradouro": LOGRADOUROS[(indice - 1) % len(LOGRADOUROS)],
                    "numero": str(100 + indice),
                    "bairro": BAIRROS[(indice - 1) % len(BAIRROS)],
                    "cidade": cidade,
                    "ativo": True,
                },
            )
            clientes.append(cliente)

        for numero, indice, deslocamento, noites, status in RESERVAS:
            entrada = hoje + timedelta(days=deslocamento)
            saida = entrada + timedelta(days=noites)
            quarto = quartos[numero]
            Reserva.objects.update_or_create(
                quarto=quarto,
                cliente=clientes[indice],
                defaults={
                    "data_entrada": entrada,
                    "data_saida": saida,
                    "status": status,
                    "preco_total": calcular_preco_total(quarto, entrada, saida),
                    "ativo": True,
                },
            )

        agora = timezone.now()
        for numero, descricao, concluida, dias_antes in OCORRENCIAS:
            ocorrencia, _ = Ocorrencia.objects.update_or_create(
                quarto=quartos[numero],
                descricao=descricao,
                defaults={"concluida": concluida, "campos": []},
            )
            Ocorrencia.objects.filter(pk=ocorrencia.pk).update(
                data_ocorrencia=agora + timedelta(days=dias_antes)
            )

        self.stdout.write(self.style.SUCCESS(
            f"Dados de apresentação prontos para {hoje:%d/%m/%Y}: "
            f"{len(tipos)} tipos, {len(tarifas)} tarifas, {len(quartos)} quartos, "
            f"{len(clientes)} clientes, {len(RESERVAS)} reservas, "
            f"{len(OCORRENCIAS)} ocorrências e {len(FUNCIONARIOS)} funcionários "
            f"com senha de demonstração."
        ))
