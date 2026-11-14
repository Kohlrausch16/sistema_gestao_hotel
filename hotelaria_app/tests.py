from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Quarto, Reserva, TipoQuarto, TarifaSazonal
from .precificacao import calcular_preco_total


class DisponibilidadeQuartosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tipo_simples = TipoQuarto.objects.create(tipo="Simples", preco_diaria="100.00")
        cls.cliente = Cliente.objects.create(
            nome="Ana",
            sobrenome="Silva",
            cpf="12345678901",
            data_nascimento=date(1990, 1, 1),
            email="ana@example.com",
            telefone="11999999999",
        )
        cls.ocupado = Quarto.objects.create(
            numero="101", tipo=cls.tipo_simples, capacidade=1, preco_diaria="100.00"
        )
        cls.livre = Quarto.objects.create(
            numero="102", tipo=cls.tipo_simples, capacidade=1, preco_diaria="100.00"
        )
        cls.manutencao = Quarto.objects.create(
            numero="103", tipo=cls.tipo_simples, capacidade=1, preco_diaria="100.00", status="M"
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
        self.assertEqual(resposta.json()["quartos"][0]["tipo"], "Simples")

    def test_listagem_e_cadastro_exibem_tipo_relacionado(self):
        listagem = self.client.get(reverse("listar_quartos"))
        cadastro = self.client.get(reverse("cadastrar_quarto"))

        self.assertContains(listagem, "Simples")
        self.assertContains(cadastro, "Simples")

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
        self.assertEqual(Reserva.objects.get(quarto=self.livre).preco_total, Decimal("200.00"))

    def test_adicionais_sazonais_somam_somente_nas_noites_aplicaveis(self):
        alta = TarifaSazonal.objects.create(
            descricao="Alta temporada", valor="30.00",
            data_inicio=date(2026, 11, 11), data_fim=date(2026, 11, 12),
        )
        feriado = TarifaSazonal.objects.create(
            descricao="Feriado", valor="10.00",
            data_inicio=date(2026, 11, 12), data_fim=date(2026, 11, 13),
        )
        self.tipo_simples.TarifaSazonal.add(alta, feriado)

        total = calcular_preco_total(
            self.livre, date(2026, 11, 10), date(2026, 11, 13)
        )
        self.assertEqual(total, Decimal("370.00"))

        consulta = self.client.get(reverse("quartos_disponiveis"), {
            "entrada": "2026-11-10", "saida": "2026-11-13"
        })
        preco_livre = next(
            item["preco_total"] for item in consulta.json()["quartos"]
            if item["id"] == self.livre.id
        )
        self.assertEqual(preco_livre, "370.00")

        resposta = self.client.post(reverse("criar_reserva"), {
            "cliente": self.cliente.id,
            "quarto": self.livre.id,
            "data_entrada": "2026-11-10",
            "data_saida": "2026-11-13",
        })
        self.assertRedirects(resposta, reverse("listar_reservas"))
        reserva = Reserva.objects.get(quarto=self.livre)
        self.assertEqual(reserva.preco_total, Decimal("370.00"))

        alta.valor = Decimal("50.00")
        alta.save(update_fields=["valor"])
        reserva.refresh_from_db()
        self.assertEqual(reserva.preco_total, Decimal("370.00"))
        self.assertContains(self.client.get(reverse("listar_reservas")), "370,00")

    def test_edicao_recalcula_total_para_novas_datas(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        reserva.preco_total = Decimal("200.00")
        reserva.save(update_fields=["preco_total"])
        tarifa = TarifaSazonal.objects.create(
            descricao="Feriado", valor="25.00",
            data_inicio=date(2026, 11, 12), data_fim=date(2026, 11, 12),
        )
        self.tipo_simples.TarifaSazonal.add(tarifa)

        with patch("hotelaria_app.views.timezone.localdate", return_value=date(2026, 11, 9)):
            resposta = self.client.post(reverse("editar_reserva", args=[reserva.id]), {
                "cliente": self.cliente.id,
                "quarto": self.ocupado.id,
                "data_entrada": "2026-11-10",
                "data_saida": "2026-11-13",
            })

        self.assertRedirects(resposta, reverse("listar_reservas"))
        reserva.refresh_from_db()
        self.assertEqual(reserva.preco_total, Decimal("325.00"))

    def test_tarifa_na_data_de_saida_nao_entra_no_total(self):
        tarifa = TarifaSazonal.objects.create(
            descricao="Próximo período", valor="50.00",
            data_inicio=date(2026, 11, 13), data_fim=date(2026, 11, 13),
        )
        self.tipo_simples.TarifaSazonal.add(tarifa)

        self.assertEqual(
            calcular_preco_total(self.livre, date(2026, 11, 11), date(2026, 11, 13)),
            Decimal("200.00"),
        )

    def test_cancelamento_libera_quarto_e_mantem_historico(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        with patch("hotelaria_app.views.timezone.localdate", return_value=date(2026, 11, 9)):
            resposta = self.client.post(reverse("cancelar_reserva", args=[reserva.id]))

        self.assertRedirects(resposta, reverse("listar_reservas"))
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "C")
        self.assertTrue(reserva.ativo)

        disponibilidade = self.client.get(reverse("quartos_disponiveis"), {
            "entrada": "2026-11-11", "saida": "2026-11-13"
        })
        self.assertIn(
            self.ocupado.id,
            [quarto["id"] for quarto in disponibilidade.json()["quartos"]],
        )

        listagem = self.client.get(reverse("listar_reservas"))
        self.assertContains(listagem, "Cancelada")
        self.assertContains(listagem, self.ocupado.numero)

    def test_cancelamento_exige_post(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        resposta = self.client.get(reverse("cancelar_reserva", args=[reserva.id]))

        self.assertEqual(resposta.status_code, 405)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "A")

    def test_cancelamento_na_data_do_checkin_e_recusado(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        url = reverse("cancelar_reserva", args=[reserva.id])

        with patch("hotelaria_app.views.timezone.localdate", return_value=date(2026, 11, 10)):
            listagem = self.client.get(reverse("listar_reservas"))
            resposta = self.client.post(url, follow=True)

        self.assertNotContains(listagem, url)
        self.assertContains(resposta, "A reserva só pode ser cancelada antes do check-in.")
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "A")

    def test_cancelamento_apos_checkin_e_recusado(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)

        with patch("hotelaria_app.views.timezone.localdate", return_value=date(2026, 11, 11)):
            resposta = self.client.post(reverse("cancelar_reserva", args=[reserva.id]))

        self.assertRedirects(resposta, reverse("listar_reservas"))
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "A")

    def test_edicao_antes_do_checkin_aceita_propria_reserva(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        url = reverse("editar_reserva", args=[reserva.id])

        with patch("hotelaria_app.views.timezone.localdate", return_value=date(2026, 11, 9)):
            pagina = self.client.get(url)
            resposta = self.client.post(url, {
                "cliente": self.cliente.id,
                "quarto": self.ocupado.id,
                "data_entrada": "2026-11-10",
                "data_saida": "2026-11-13",
            })

        self.assertContains(pagina, 'value="2026-11-10"')
        self.assertContains(pagina, f'value="{self.ocupado.id}" selected')
        self.assertRedirects(resposta, reverse("listar_reservas"))
        reserva.refresh_from_db()
        self.assertEqual(reserva.data_saida, date(2026, 11, 13))

    def test_consulta_da_edicao_inclui_o_quarto_da_propria_reserva(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        resposta = self.client.get(reverse("quartos_disponiveis"), {
            "entrada": "2026-11-10",
            "saida": "2026-11-12",
            "reserva_id": reserva.id,
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            self.ocupado.id,
            [quarto["id"] for quarto in resposta.json()["quartos"]],
        )

    def test_edicao_no_checkin_e_recusada(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        url = reverse("editar_reserva", args=[reserva.id])

        with patch("hotelaria_app.views.timezone.localdate", return_value=date(2026, 11, 10)):
            listagem = self.client.get(reverse("listar_reservas"))
            pagina = self.client.get(url)
            resposta = self.client.post(url, {
                "cliente": self.cliente.id,
                "quarto": self.livre.id,
                "data_entrada": "2026-11-11",
                "data_saida": "2026-11-13",
            })

        self.assertNotContains(listagem, url)
        self.assertRedirects(pagina, reverse("listar_reservas"))
        self.assertRedirects(resposta, reverse("listar_reservas"))
        reserva.refresh_from_db()
        self.assertEqual(reserva.quarto_id, self.ocupado.id)

    def test_edicao_nao_aceita_nova_entrada_no_passado(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        url = reverse("editar_reserva", args=[reserva.id])

        with patch("hotelaria_app.views.timezone.localdate", return_value=date(2026, 11, 9)):
            resposta = self.client.post(url, {
                "cliente": self.cliente.id,
                "quarto": self.ocupado.id,
                "data_entrada": "2026-11-09",
                "data_saida": "2026-11-12",
            })

        self.assertContains(resposta, "A entrada deve ser uma data futura.")
        reserva.refresh_from_db()
        self.assertEqual(reserva.data_entrada, date(2026, 11, 10))

    def test_edicao_recusa_quarto_de_outra_reserva(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        Reserva.objects.create(
            cliente=self.cliente,
            quarto=self.livre,
            data_entrada=date(2026, 11, 11),
            data_saida=date(2026, 11, 14),
        )

        with patch("hotelaria_app.views.timezone.localdate", return_value=date(2026, 11, 9)):
            resposta = self.client.post(reverse("editar_reserva", args=[reserva.id]), {
                "cliente": self.cliente.id,
                "quarto": self.livre.id,
                "data_entrada": "2026-11-10",
                "data_saida": "2026-11-13",
            })

        self.assertContains(resposta, "Este quarto não está disponível")
        reserva.refresh_from_db()
        self.assertEqual(reserva.quarto_id, self.ocupado.id)

    def test_reserva_finalizada_nao_bloqueia_quarto(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        reserva.status = "F"
        reserva.save(update_fields=["status"])

        resposta = self.client.get(reverse("quartos_disponiveis"), {
            "entrada": "2026-11-11", "saida": "2026-11-13"
        })
        self.assertIn(
            self.ocupado.id,
            [quarto["id"] for quarto in resposta.json()["quartos"]],
        )

    def test_reserva_excluida_logicamente_nao_aparece_na_listagem(self):
        reserva = Reserva.objects.get(quarto=self.ocupado)
        reserva.ativo = False
        reserva.save(update_fields=["ativo"])

        resposta = self.client.get(reverse("listar_reservas"))
        self.assertNotContains(resposta, self.ocupado.numero)


class IntegracaoClientesTests(TestCase):
    def test_menu_e_paginas_de_clientes(self):
        resposta = self.client.get(reverse("listagem_clientes"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, reverse("cadastrar_cliente"))
        self.assertContains(resposta, reverse("listar_reservas"))

        cadastro = self.client.get(reverse("cadastrar_cliente"))
        self.assertEqual(cadastro.status_code, 200)

    def test_cadastro_invalido_nao_salva_cliente(self):
        resposta = self.client.post(reverse("cadastrar_cliente"), {})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Cliente.objects.count(), 0)


class TarifasSazonaisTests(TestCase):
    def test_cadastro_rejeita_periodo_invertido_e_adicional_negativo(self):
        resposta = self.client.post(reverse("criar_tarifa_sazonal"), {
            "descricao": "Período inválido",
            "valor": "-10.00",
            "data_inicio": "2026-12-10",
            "data_fim": "2026-12-09",
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(TarifaSazonal.objects.count(), 0)
        self.assertContains(resposta, "O adicional sazonal não pode ser negativo.")
        self.assertContains(resposta, "O fim deve ser igual ou posterior ao início.")

    def test_tipo_de_quarto_usa_tarifa_sazonal_sem_tarifa_adicional(self):
        tarifa = TarifaSazonal.objects.create(
            descricao="Alta temporada",
            valor="180.00",
            data_inicio=date(2026, 12, 1),
            data_fim=date(2027, 1, 31),
        )

        cadastro = self.client.get(reverse("criar_tipo_quarto"))
        self.assertContains(cadastro, 'type="checkbox"')
        self.assertContains(cadastro, "Alta temporada")

        resposta = self.client.post(reverse("criar_tipo_quarto"), {
            "tipo": "Duplo especial",
            "preco_diaria": "150.00",
            "TarifaSazonal": [tarifa.id],
        })

        self.assertRedirects(resposta, reverse("listar_tipos_quarto"))
        tipo = TipoQuarto.objects.get(tipo="Duplo especial")
        self.assertEqual(list(tipo.TarifaSazonal.all()), [tarifa])
        listagem = self.client.get(reverse("listar_tipos_quarto"))
        self.assertContains(listagem, "Alta temporada")
        self.assertNotContains(listagem, "Tarifa adicional")
