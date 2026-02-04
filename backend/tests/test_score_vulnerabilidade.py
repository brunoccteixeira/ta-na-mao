"""Testes para score de vulnerabilidade preditiva."""

import pytest
from app.services.score_vulnerabilidade import (
    analisar_vulnerabilidade,
    calcular_score,
    gerar_recomendacoes,
    PerfilFamiliar,
    FaixaRisco,
)


# =============================================================================
# PerfilFamiliar e calcular_score
# =============================================================================

class TestCalcularScore:
    def test_familia_alta_vulnerabilidade(self):
        perfil = PerfilFamiliar(
            renda_per_capita=80,
            membros_familia=6,
            criancas_0_6=2,
            idosos_60_mais=1,
            pessoas_com_deficiencia=1,
            gestantes=1,
            tipo_moradia="ocupacao",
            trabalho_formal=False,
            desempregados=2,
            cadunico_atualizado=False,
        )
        resultado = calcular_score(perfil)
        assert resultado["score"] >= 70
        assert resultado["faixa"] in ("ALTO", "CRITICO")

    def test_familia_baixa_vulnerabilidade(self):
        perfil = PerfilFamiliar(
            renda_per_capita=2000,
            membros_familia=3,
            tipo_moradia="propria",
            trabalho_formal=True,
            cadunico_atualizado=True,
            beneficios_ativos=["BOLSA_FAMILIA", "TSEE"],
        )
        resultado = calcular_score(perfil)
        assert resultado["score"] <= 40
        assert resultado["faixa"] in ("BAIXO", "MODERADO")

    def test_score_entre_0_e_100(self):
        perfil = PerfilFamiliar(renda_per_capita=500, membros_familia=4)
        resultado = calcular_score(perfil)
        assert 0 <= resultado["score"] <= 100

    def test_fatores_presentes(self):
        perfil = PerfilFamiliar(
            renda_per_capita=100,
            membros_familia=5,
            criancas_0_6=2,
        )
        resultado = calcular_score(perfil)
        assert "fatores_principais" in resultado
        assert len(resultado["fatores_principais"]) > 0

    def test_faixa_critico(self):
        perfil = PerfilFamiliar(
            renda_per_capita=0,
            membros_familia=8,
            criancas_0_6=3,
            idosos_60_mais=1,
            pessoas_com_deficiencia=1,
            gestantes=1,
            tipo_moradia="rua",
            trabalho_formal=False,
            desempregados=3,
            cadunico_atualizado=False,
        )
        resultado = calcular_score(perfil)
        assert resultado["faixa"] == "CRITICO"

    def test_faixa_baixo(self):
        perfil = PerfilFamiliar(
            renda_per_capita=3000,
            membros_familia=2,
            tipo_moradia="propria",
            trabalho_formal=True,
            cadunico_atualizado=True,
            beneficios_ativos=["BOLSA_FAMILIA", "TSEE"],
        )
        resultado = calcular_score(perfil)
        assert resultado["faixa"] == "BAIXO"

    def test_dimensoes_presentes(self):
        perfil = PerfilFamiliar(renda_per_capita=500, membros_familia=3)
        resultado = calcular_score(perfil)
        assert "dimensoes" in resultado
        assert "renda" in resultado["dimensoes"]
        assert "composicao" in resultado["dimensoes"]
        assert "moradia" in resultado["dimensoes"]
        assert "trabalho" in resultado["dimensoes"]


# =============================================================================
# gerar_recomendacoes
# =============================================================================

class TestGerarRecomendacoes:
    def test_recomendacoes_renda_baixa_sem_cadunico(self):
        perfil = PerfilFamiliar(
            renda_per_capita=100,
            membros_familia=4,
            cadunico_atualizado=False,
        )
        score_result = calcular_score(perfil)
        recomendacoes = gerar_recomendacoes(perfil, score_result["score"])
        assert len(recomendacoes) > 0
        # Deve recomendar Bolsa Familia e alertar sobre CadUnico
        tipos = [r.get("beneficio", r.get("tipo", "")) for r in recomendacoes]
        textos = " ".join(str(r) for r in recomendacoes).lower()
        assert "bolsa_familia" in str(tipos).lower() or "cadunico" in textos

    def test_recomendacoes_idoso(self):
        perfil = PerfilFamiliar(
            renda_per_capita=200,
            membros_familia=2,
            idosos_60_mais=1,
            pessoas_com_deficiencia=0,
        )
        score_result = calcular_score(perfil)
        recomendacoes = gerar_recomendacoes(perfil, score_result["score"])
        textos = " ".join(str(r) for r in recomendacoes).lower()
        assert "bpc" in textos

    def test_recomendacoes_pcd(self):
        perfil = PerfilFamiliar(
            renda_per_capita=200,
            membros_familia=3,
            pessoas_com_deficiencia=1,
        )
        score_result = calcular_score(perfil)
        recomendacoes = gerar_recomendacoes(perfil, score_result["score"])
        textos = " ".join(str(r) for r in recomendacoes).lower()
        assert "bpc" in textos

    def test_recomendacoes_familia_ok(self):
        perfil = PerfilFamiliar(
            renda_per_capita=3000,
            membros_familia=2,
            tipo_moradia="propria",
            trabalho_formal=True,
            cadunico_atualizado=True,
            beneficios_ativos=["BOLSA_FAMILIA", "TSEE", "FARMACIA_POPULAR", "BPC"],
        )
        score_result = calcular_score(perfil)
        recomendacoes = gerar_recomendacoes(perfil, score_result["score"])
        # Pode ter poucas recomendacoes (familia ja acessa beneficios e tem renda boa)
        assert isinstance(recomendacoes, list)

    def test_recomendacoes_ordenadas_por_prioridade(self):
        perfil = PerfilFamiliar(
            renda_per_capita=100,
            membros_familia=4,
            idosos_60_mais=1,
            cadunico_atualizado=False,
        )
        score_result = calcular_score(perfil)
        recomendacoes = gerar_recomendacoes(perfil, score_result["score"])
        if len(recomendacoes) >= 2:
            # Alta prioridade deve vir primeiro
            prioridades = [r["prioridade"] for r in recomendacoes]
            ordem = {"alta": 0, "media": 1, "baixa": 2}
            numeros = [ordem.get(p, 3) for p in prioridades]
            assert numeros == sorted(numeros)


# =============================================================================
# analisar_vulnerabilidade (tool wrapper)
# =============================================================================

class TestAnalisarVulnerabilidade:
    def test_analise_completa(self):
        result = analisar_vulnerabilidade(
            renda_per_capita=200,
            membros_familia=5,
            criancas_0_6=2,
            tipo_moradia="alugada",
            trabalho_formal=False,
        )
        assert "score" in result
        assert "faixa" in result
        assert "recomendacoes" in result

    def test_analise_minima(self):
        result = analisar_vulnerabilidade(
            renda_per_capita=500,
            membros_familia=3,
        )
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_analise_situacao_rua(self):
        result = analisar_vulnerabilidade(
            renda_per_capita=0,
            membros_familia=1,
            tipo_moradia="rua",
            trabalho_formal=False,
            desempregados=1,
        )
        assert result["score"] >= 50
        assert result["faixa"] in ("ALTO", "CRITICO")

    def test_analise_retorna_recomendacoes(self):
        result = analisar_vulnerabilidade(
            renda_per_capita=100,
            membros_familia=4,
            cadunico_atualizado=False,
        )
        assert "recomendacoes" in result
        assert "total_recomendacoes" in result
        assert result["total_recomendacoes"] > 0
