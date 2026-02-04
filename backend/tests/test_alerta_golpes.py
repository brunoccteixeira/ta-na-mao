"""Testes para educacao financeira e alerta de golpes."""

import pytest
from app.agent.tools.alerta_golpes import (
    verificar_golpe,
    simular_orcamento,
    consultar_educacao_financeira,
    GOLPES_COMUNS,
    MICROLECOES,
    OPCOES_MICROCREDITO,
)


# =============================================================================
# verificar_golpe
# =============================================================================

class TestVerificarGolpe:
    def test_detecta_golpe_pix(self):
        result = verificar_golpe("recebi um comprovante de PIX e pediram pra devolver troco")
        assert result["alerta"] is True
        assert "golpe_principal" in result

    def test_detecta_golpe_emprestimo(self):
        result = verificar_golpe("ligaram oferecendo emprestimo consignado com taxa baixa sem consulta")
        assert result["alerta"] is True

    def test_detecta_golpe_cadastro_falso(self):
        result = verificar_golpe("mandaram link para atualizar cadastro do CadUnico rapido online")
        assert result["alerta"] is True

    def test_mensagem_segura(self):
        result = verificar_golpe("quero saber como pedir Bolsa Familia")
        assert result["alerta"] is False

    def test_golpe_piramide(self):
        result = verificar_golpe("me convidaram pra investimento com lucro garantido, preciso convidar amigos")
        assert result["alerta"] is True

    def test_retorna_como_evitar(self):
        result = verificar_golpe("recebi comprovante de PIX mas o dinheiro nao caiu na conta")
        assert result["alerta"] is True
        assert "como_evitar" in result

    def test_golpe_falso_beneficio(self):
        result = verificar_golpe("recebi mensagem dizendo que tenho beneficio aprovado e preciso pagar taxa para receber")
        assert result["alerta"] is True

    def test_golpes_comuns_nao_vazio(self):
        assert len(GOLPES_COMUNS) >= 3


# =============================================================================
# simular_orcamento
# =============================================================================

class TestSimularOrcamento:
    def test_orcamento_basico(self):
        result = simular_orcamento(
            renda_total=1500,
            aluguel=500,
            alimentacao=400,
            transporte=100,
            luz_agua_gas=150,
        )
        assert "total_gastos" in result
        assert "sobra" in result
        assert result["renda_total"] == 1500

    def test_orcamento_deficit(self):
        result = simular_orcamento(
            renda_total=1000,
            aluguel=600,
            alimentacao=500,
            transporte=200,
        )
        assert result["sobra"] < 0
        assert result["situacao"] == "no_vermelho"

    def test_orcamento_positivo(self):
        result = simular_orcamento(
            renda_total=3000,
            aluguel=500,
            alimentacao=400,
        )
        assert result["sobra"] > 0
        assert result["situacao"] == "ok"

    def test_orcamento_sem_gastos(self):
        result = simular_orcamento(renda_total=1500)
        assert result["renda_total"] == 1500
        assert result["total_gastos"] == 0
        assert result["sobra"] == 1500

    def test_orcamento_com_orientacoes(self):
        result = simular_orcamento(
            renda_total=1500,
            aluguel=800,
        )
        assert "orientacoes" in result
        assert len(result["orientacoes"]) > 0

    def test_alerta_aluguel_alto(self):
        result = simular_orcamento(
            renda_total=1500,
            aluguel=800,
        )
        # Aluguel > 30% da renda deve gerar alerta
        assert len(result["alertas"]) > 0
        alerta_moradia = any("moradia" in a.lower() or "aluguel" in a.lower() for a in result["alertas"])
        assert alerta_moradia

    def test_beneficios_sugeridos(self):
        result = simular_orcamento(
            renda_total=200,
            luz_agua_gas=50,
            saude=30,
        )
        assert "beneficios_sugeridos" in result
        assert len(result["beneficios_sugeridos"]) > 0

    def test_categorias_detalhadas(self):
        result = simular_orcamento(
            renda_total=2000,
            aluguel=500,
            alimentacao=400,
        )
        assert "categorias" in result
        nomes = [c["nome"] for c in result["categorias"]]
        assert "Moradia" in nomes
        assert "Alimentacao" in nomes


# =============================================================================
# consultar_educacao_financeira
# =============================================================================

class TestConsultarEducacaoFinanceira:
    def test_tema_golpes(self):
        result = consultar_educacao_financeira("golpes")
        assert result["tema"] == "golpes"
        assert "golpes" in result

    def test_tema_microcredito(self):
        result = consultar_educacao_financeira("microcredito")
        assert "opcoes" in result

    def test_tema_poupanca(self):
        result = consultar_educacao_financeira("reserva")
        assert "licao" in result

    def test_sem_tema(self):
        result = consultar_educacao_financeira()
        assert "temas_disponiveis" in result

    def test_microlecoes_nao_vazio(self):
        assert len(MICROLECOES) >= 3

    def test_opcoes_microcredito_nao_vazio(self):
        assert len(OPCOES_MICROCREDITO) >= 2
        for opcao in OPCOES_MICROCREDITO:
            assert "nome" in opcao
