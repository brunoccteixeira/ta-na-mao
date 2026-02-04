"""Testes para auditoria de legibilidade textual."""

import pytest
from app.services.legibilidade import (
    calcular_legibilidade,
    detectar_jargoes,
    auditar_texto,
    _contar_silabas,
    JARGOES_GOVERNAMENTAIS,
)


# =============================================================================
# _contar_silabas
# =============================================================================

class TestContarSilabas:
    def test_palavra_simples(self):
        assert _contar_silabas("casa") == 2

    def test_palavra_monossilaba(self):
        assert _contar_silabas("sol") == 1
        assert _contar_silabas("paz") == 1

    def test_palavra_longa(self):
        assert _contar_silabas("beneficiario") >= 5

    def test_palavra_com_acento(self):
        assert _contar_silabas("família") >= 3

    def test_palavra_vazia(self):
        assert _contar_silabas("") == 0

    def test_minimo_uma_silaba(self):
        assert _contar_silabas("x") >= 1


# =============================================================================
# calcular_legibilidade
# =============================================================================

class TestCalcularLegibilidade:
    def test_texto_facil(self):
        texto = "O sol brilha. O dia esta bom. Eu vou sair."
        result = calcular_legibilidade(texto)
        assert result["score"] >= 50
        assert result["nivel"] in ("Muito facil", "Facil", "Adequado")

    def test_texto_dificil(self):
        texto = (
            "A implementacao de politicas intersetoriais de protecao "
            "socioassistencial demanda articulacao institucional entre os "
            "equipamentos publicos da rede de atendimento, considerando "
            "as condicionalidades estabelecidas pela legislacao vigente."
        )
        result = calcular_legibilidade(texto)
        assert result["score"] < 60
        assert result["aprovado"] is False

    def test_texto_vazio(self):
        result = calcular_legibilidade("")
        assert result["score"] == 0
        assert result["aprovado"] is False

    def test_texto_none(self):
        result = calcular_legibilidade("   ")
        assert result["aprovado"] is False

    def test_estatisticas_presentes(self):
        texto = "Voce tem direito ao beneficio. Va ao CRAS com seus documentos."
        result = calcular_legibilidade(texto)
        assert "estatisticas" in result
        stats = result["estatisticas"]
        assert "palavras" in stats
        assert "sentencas" in stats
        assert "silabas" in stats
        assert stats["palavras"] > 0
        assert stats["sentencas"] > 0

    def test_score_entre_0_e_100(self):
        texto = "Texto simples para teste."
        result = calcular_legibilidade(texto)
        assert 0 <= result["score"] <= 100

    def test_sugestoes_texto_dificil(self):
        texto = (
            "A intersetorialidade das politicas socioassistenciais "
            "requer articulacao permanente entre equipamentos publicos "
            "para garantir a protecao social integral dos beneficiarios."
        )
        result = calcular_legibilidade(texto)
        assert "sugestoes" in result
        assert len(result["sugestoes"]) > 0

    def test_sugestoes_texto_bom(self):
        texto = "O sol brilha. O dia esta bom."
        result = calcular_legibilidade(texto)
        assert "sugestoes" in result

    def test_meta_descrita(self):
        result = calcular_legibilidade("Texto para teste.")
        assert "meta" in result


# =============================================================================
# detectar_jargoes
# =============================================================================

class TestDetectarJargoes:
    def test_detecta_jargao_beneficiario(self):
        result = detectar_jargoes("O beneficiario deve comparecer ao equipamento publico.")
        assert result["total_jargoes"] >= 2
        assert result["aprovado"] is False

    def test_texto_sem_jargoes(self):
        result = detectar_jargoes("Va ao posto de atendimento com seus documentos.")
        assert result["aprovado"] is True
        assert result["total_jargoes"] == 0

    def test_alternativa_sugerida(self):
        result = detectar_jargoes("O pedido foi deferido.")
        assert result["total_jargoes"] >= 1
        jargao = result["jargoes"][0]
        assert "alternativa" in jargao
        assert "aprovado" in jargao["alternativa"].lower() or len(jargao["alternativa"]) > 0

    def test_contexto_mostrado(self):
        result = detectar_jargoes("O beneficiario precisa atualizar o cadastro.")
        if result["jargoes"]:
            assert "contexto" in result["jargoes"][0]

    def test_jargoes_governamentais_nao_vazio(self):
        assert len(JARGOES_GOVERNAMENTAIS) >= 15

    def test_detecta_per_capita(self):
        result = detectar_jargoes("A renda per capita da familia eh de R$ 200.")
        jargoes_encontrados = [j["jargao"] for j in result["jargoes"]]
        assert "per capita" in jargoes_encontrados

    def test_detecta_condicionalidades(self):
        result = detectar_jargoes("As condicionalidades do programa devem ser cumpridas.")
        assert result["total_jargoes"] >= 1


# =============================================================================
# auditar_texto (completo)
# =============================================================================

class TestAuditarTexto:
    def test_texto_acessivel(self):
        texto = "Va ao CRAS perto de voce. Leve seus documentos. O atendimento eh de graca."
        result = auditar_texto(texto)
        assert "legibilidade" in result
        assert "jargoes" in result
        assert "resumo" in result

    def test_texto_inacessivel(self):
        texto = (
            "O beneficiario elegivel deve protocolar seu requerimento na "
            "unidade de atendimento, observando as condicionalidades do programa."
        )
        result = auditar_texto(texto)
        assert result["aprovado"] is False
        assert result["jargoes"]["total_jargoes"] >= 3

    def test_aprovado_geral(self):
        texto = "O sol brilha. O dia esta bom."
        result = auditar_texto(texto)
        # Sem jargoes + boa legibilidade = aprovado
        assert result["jargoes"]["aprovado"] is True
