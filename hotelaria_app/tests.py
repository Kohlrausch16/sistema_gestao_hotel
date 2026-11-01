from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Quarto, Reserva


class DisponibilidadeQuartosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cliente = Cliente.objects.create(
            nome="Ana",
            sobrenome="Silva",
            cpf="12345678901",
            data_nascimento=date(1990, 1, 1),
            email="ana@example.com",
            telefone="11999999999",
        )
        cls.ocupado = Quarto.objects.create(
            numero="101", tipo="S", capacidade=1, preco_diaria="100.00"
        )
        cls.livre = Quarto.objects.create(
            numero="102", tipo="S", capacidade=1, preco_diaria="100.00"
        )
        cls.manutencao = Quarto.objects.create(
            numero="103", tipo="S", capacidade=1, preco_diaria="100.00", status="M"
        )
        Reserva.objects.create(
            cliente=cls.cliente,
            quarto=cls.ocupado,
            data_entrada=date(2026, 11, 10),
            data_saida=date(2026, 11, 12),
        )

    def test_endpoint_exclui_conflitos_e_manutencao(self):
        resposta = self.client.get(reverse("quartos_disponiveis"), {
            "entrada": "2026-11-11", "saida": "2026-11-13"
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            [quarto["id"] for quarto in resposta.json()["quartos"]],
            [self.livre.id],
        )

    def test_saida_e_entrada_no_mesmo_dia_nao_conflitam(self):
        resposta = self.client.get(reverse("quartos_disponiveis"), {
            "entrada": "2026-11-12", "saida": "2026-11-13"
        })

        self.assertEqual(
            [quarto["id"] for quarto in resposta.json()["quartos"]],
            [self.ocupado.id, self.livre.id],
        )

    def test_endpoint_rejeita_periodo_invalido(self):
        resposta = self.client.get(reverse("quartos_disponiveis"), {
            "entrada": "2026-11-12", "saida": "2026-11-12"
        })
        self.assertEqual(resposta.status_code, 400)

    def test_post_rejeita_quarto_ocupado(self):
        resposta = self.client.post(reverse("criar_reserva"), {
            "cliente": self.cliente.id,
            "quarto": self.ocupado.id,
            "data_entrada": "2026-11-11",
            "data_saida": "2026-11-13",
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Este quarto não está disponível")
        self.assertEqual(Reserva.objects.count(), 1)

    def test_post_aceita_quarto_livre(self):
        resposta = self.client.post(reverse("criar_reserva"), {
            "cliente": self.cliente.id,
            "quarto": self.livre.id,
            "data_entrada": "2026-11-11",
            "data_saida": "2026-11-13",
        })

        self.assertRedirects(resposta, reverse("listar_reservas"))
        self.assertEqual(Reserva.objects.count(), 2)
