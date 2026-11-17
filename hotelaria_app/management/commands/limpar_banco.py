"""Remove dados operacionais e usuários comuns, preservando superusuários."""

from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from hotelaria_app.models import (
    Cliente,
    Funcionario,
    Ocorrencia,
    Quarto,
    Relatorio,
    Reserva,
    TarifaSazonal,
    TipoQuarto,
)


class Command(BaseCommand):
    help = (
        "Apaga os dados do hotel e os usuários comuns, preservando superusuários, "
        "estrutura e tabelas internas do Django."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Confirma a exclusão permanente dos dados.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["confirmar"]:
            raise CommandError(
                "Este comando apaga os dados permanentemente. "
                "Execute 'python manage.py limpar_banco --confirmar' para continuar."
            )

        Usuario = get_user_model()
        if not Usuario.objects.filter(is_superuser=True).exists():
            raise CommandError("Nenhum superusuário encontrado; limpeza cancelada.")

        modelos = (
            Reserva,
            Ocorrencia,
            Relatorio,
            Quarto,
            TipoQuarto,
            TarifaSazonal,
            Cliente,
            Funcionario,
        )
        removidos = {}
        for modelo in modelos:
            removidos[modelo._meta.verbose_name_plural] = modelo.objects.count()
            modelo.objects.all().delete()

        LogEntry.objects.all().delete()
        Session.objects.all().delete()
        Group.objects.all().delete()
        usuarios_comuns = Usuario.objects.filter(is_superuser=False)
        quantidade_usuarios = usuarios_comuns.count()
        usuarios_comuns.delete()

        self.stdout.write(self.style.SUCCESS(
            "Banco limpo: "
            + ", ".join(f"{quantidade} {nome}" for nome, quantidade in removidos.items())
            + f" e {quantidade_usuarios} usuários comuns removidos. "
            f"{Usuario.objects.filter(is_superuser=True).count()} superusuário(s) preservado(s)."
        ))
