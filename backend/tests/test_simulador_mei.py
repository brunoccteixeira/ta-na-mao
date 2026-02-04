"""Testes para simulador MEI."""

import pytest
from app.agent.tools.simulador_mei import (
    simular_impacto_mei,
    guia_formalizacao_mei,
    _analisar_bolsa_familia,
    _analisar_bpc,
    _analisar_tsee,
    _listar_obrigacoes,
    _SALARIO_MINIMO,
    _DAS_MENSAL,
    _BOLSA_FAMILIA_POBREZA,
    _BOLSA_FAMILIA_PROTECAO,
    _BPC_LIMITE,
)


# =============================================================================
# simular_impacto_mei
# =============================================================================

class TestSimularImpactoMei:
    def test_simulacao_basica(self):
        result = simular_impacto_mei(faturamento_estimado=2000)
        assert "impactos" in result
        assert "comparativo" in result
        assert "beneficios_mei" in result
        assert "veredicto" in result
        assert "obrigacoes_mei" in result

    def test_mei_recomendado_sem_perda(self):
        result = simular_impacto_mei(
            faturamento_estimado=2000,
            despesas_estimadas=500,
            membros_familia=4,
            renda_familiar_atual=400,
        )
        # Renda baixa + ganho liquido -> pode ser recomendado
        assert result["vale_a_pena"] is True
        assert result["comparativo"]["ganho_liquido_mensal"] > 0

    def test_mei_nao_recomendado_custo_alto(self):
        result = simular_impacto_mei(
            faturamento_estimado=50,
            despesas_estimadas=40,
        )
        # Lucro 10 - DAS ~75 = negativo
        assert result["vale_a_pena"] is False
        assert result["veredicto"] == "NAO_RECOMENDADO"

    def test_comparativo_financeiro(self):
        result = simular_impacto_mei(
            faturamento_estimado=3000,
            despesas_estimadas=1000,
            membros_familia=3,
            renda_familiar_atual=1000,
        )
        comp = result["comparativo"]
        assert comp["lucro_estimado_mensal"] == 2000.0
        assert comp["custo_mei_mensal"] == _DAS_MENSAL
        assert comp["renda_com_mei"] == 3000.0  # 1000 + 2000

    def test_impacto_com_beneficios(self):
        result = simular_impacto_mei(
            faturamento_estimado=2000,
            membros_familia=4,
            renda_familiar_atual=500,
            beneficios_atuais=["BOLSA_FAMILIA", "TSEE"],
        )
        # Deve analisar impacto nos beneficios listados
        beneficios_analisados = [i["beneficio"] for i in result["impactos"]]
        assert "Bolsa Familia" in beneficios_analisados
        assert "Tarifa Social de Energia" in beneficios_analisados

    def test_beneficios_mei_listados(self):
        result = simular_impacto_mei(faturamento_estimado=2000)
        assert len(result["beneficios_mei"]) >= 5
        assert any("CNPJ" in b for b in result["beneficios_mei"])
        assert any("Aposentadoria" in b for b in result["beneficios_mei"])


# =============================================================================
# _analisar_bolsa_familia
# =============================================================================

class TestAnalisarBolsaFamilia:
    def test_mantem_renda_baixa(self):
        result = _analisar_bolsa_familia(100, 150, 500)
        assert result["status"] == "MANTEM"

    def test_protegido_renda_media(self):
        # Renda per capita entre pobreza e protecao
        renda_pc = (_BOLSA_FAMILIA_POBREZA + _BOLSA_FAMILIA_PROTECAO) / 2
        result = _analisar_bolsa_familia(100, renda_pc, 1000)
        assert result["status"] == "PROTEGIDO"

    def test_pode_perder_renda_alta(self):
        result = _analisar_bolsa_familia(100, 1000, 3000)
        assert result["status"] == "PODE_PERDER"


class TestAnalisarBpc:
    def test_mantem_renda_baixa(self):
        result = _analisar_bpc(100)
        assert result["status"] == "MANTEM"

    def test_pode_perder_renda_alta(self):
        result = _analisar_bpc(1000)
        assert result["status"] == "PODE_PERDER"

    def test_limite_bpc(self):
        # Exatamente no limite
        result = _analisar_bpc(_BPC_LIMITE)
        assert result["status"] == "MANTEM"


class TestAnalisarTsee:
    def test_mantem_renda_baixa(self):
        result = _analisar_tsee(200)
        assert result["status"] == "MANTEM"

    def test_pode_perder_renda_alta(self):
        result = _analisar_tsee(2000)
        assert result["status"] == "PODE_PERDER"


# =============================================================================
# guia_formalizacao_mei
# =============================================================================

class TestGuiaFormalizacaoMei:
    def test_guia_completo(self):
        result = guia_formalizacao_mei()
        assert "titulo" in result
        assert "requisitos" in result
        assert "passos" in result
        assert len(result["passos"]) == 5

    def test_passos_ordenados(self):
        result = guia_formalizacao_mei()
        for i, passo in enumerate(result["passos"], 1):
            assert passo["numero"] == i

    def test_tem_custos(self):
        result = guia_formalizacao_mei()
        assert "custo_total" in result
        assert str(_DAS_MENSAL) in result["custo_total"]

    def test_onde_pedir_ajuda(self):
        result = guia_formalizacao_mei()
        assert "onde_pedir_ajuda" in result
        assert len(result["onde_pedir_ajuda"]) >= 2


class TestObrigacoes:
    def test_obrigacoes_listadas(self):
        obrigacoes = _listar_obrigacoes()
        assert len(obrigacoes) >= 4
        nomes = [o["nome"] for o in obrigacoes]
        assert "DAS mensal" in nomes
        assert "DASN-SIMEI anual" in nomes
