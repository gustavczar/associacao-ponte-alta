from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Associado, Aviso, Lancamento


class MuralPublicoTest(TestCase):
    def test_morador_ve_so_o_que_foi_publicado_sem_login(self):
        Aviso.objects.create(titulo="Reunião geral", texto="Salão", publicado=True)
        Aviso.objects.create(titulo="Rascunho interno", texto="x", publicado=False)
        Aviso.objects.create(tipo=Aviso.EVENTO, titulo="Festa passada", texto="x",
                             data_evento=timezone.now() - timedelta(days=1))
        Aviso.objects.create(tipo=Aviso.EVENTO, titulo="Mutirão", texto="x",
                             data_evento=timezone.now() + timedelta(days=3))

        r = self.client.get(reverse("inicio"))

        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Reunião geral")
        self.assertContains(r, "Mutirão")
        self.assertNotContains(r, "Rascunho interno")
        self.assertNotContains(r, "Festa passada")


class AcessoRestritoTest(TestCase):
    def test_areas_da_diretoria_exigem_login(self):
        for nome in ["painel", "associados", "financeiro", "avisos", "associado_novo", "lancamento_novo"]:
            r = self.client.get(reverse(nome))
            self.assertRedirects(r, f"{reverse('login')}?next={reverse(nome)}", msg_prefix=nome)


class DiretoriaTest(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user("diretora", password="senha-forte-123"))

    def test_cadastrar_associado(self):
        r = self.client.post(reverse("associado_novo"), {
            "nome": "Maria Aparecida", "telefone": "(16) 99999-0000", "email": "",
            "endereco": "Rua 1, 10", "data_associacao": "2026-09-01", "ativo": "on", "observacoes": "",
        })
        self.assertRedirects(r, reverse("associados"))
        self.assertTrue(Associado.objects.filter(nome="Maria Aparecida", ativo=True).exists())

    def test_busca_de_associado(self):
        Associado.objects.create(nome="João Silva")
        Associado.objects.create(nome="Ana Souza")
        r = self.client.get(reverse("associados"), {"q": "joão"})
        self.assertContains(r, "João Silva")
        self.assertNotContains(r, "Ana Souza")

    def test_saldo_soma_entradas_e_subtrai_saidas(self):
        Lancamento.objects.create(tipo="E", descricao="Mensalidades", valor=Decimal("150.00"))
        Lancamento.objects.create(tipo="E", descricao="Doação", valor=Decimal("50.50"))
        Lancamento.objects.create(tipo="S", descricao="Conta de luz", valor=Decimal("80.25"))

        resumo = Lancamento.resumo(Lancamento.objects.all())

        self.assertEqual(resumo, {"entradas": Decimal("200.50"), "saidas": Decimal("80.25"), "saldo": Decimal("120.25")})
        self.assertContains(self.client.get(reverse("painel")), "R$ 120,25")

    def test_caixa_filtra_pelo_mes_escolhido(self):
        Lancamento.objects.create(tipo="E", descricao="Agosto", valor=10, data=date(2026, 8, 5))
        Lancamento.objects.create(tipo="E", descricao="Setembro", valor=20, data=date(2026, 9, 5))
        r = self.client.get(reverse("financeiro"), {"mes": "2026-08"})
        self.assertContains(r, "Agosto")
        self.assertNotContains(r, "Setembro")
        self.assertEqual(r.context["resumo"]["entradas"], 10)
        self.assertEqual(r.context["saldo_geral"], 30)

    def test_mes_invalido_nao_quebra_a_pagina(self):
        self.assertEqual(self.client.get(reverse("financeiro"), {"mes": "abc"}).status_code, 200)

    def test_lancamento_recusa_valor_zero(self):
        r = self.client.post(reverse("lancamento_novo"), {
            "tipo": "S", "descricao": "Erro", "categoria": "outros", "valor": "0", "data": "2026-09-10",
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Informe um valor maior que zero.")
        self.assertFalse(Lancamento.objects.exists())

    def test_evento_exige_data(self):
        r = self.client.post(reverse("aviso_novo"), {"tipo": "evento", "titulo": "Festa", "texto": "x", "publicado": "on"})
        self.assertContains(r, "Todo evento precisa de data e hora.")
        self.assertFalse(Aviso.objects.exists())

    def test_excluir_so_apos_confirmacao(self):
        a = Associado.objects.create(nome="Pedro")
        self.assertContains(self.client.get(reverse("associado_excluir", args=[a.pk])), "Sim, excluir")
        self.assertTrue(Associado.objects.filter(pk=a.pk).exists())
        self.client.post(reverse("associado_excluir", args=[a.pk]))
        self.assertFalse(Associado.objects.filter(pk=a.pk).exists())

    def test_excluir_associado_preserva_o_historico_do_caixa(self):
        a = Associado.objects.create(nome="Pedro")
        l = Lancamento.objects.create(tipo="E", descricao="Mensalidade", valor=30, associado=a)
        a.delete()
        l.refresh_from_db()
        self.assertIsNone(l.associado)
