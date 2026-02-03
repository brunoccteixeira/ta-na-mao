"""
Testes para monitoramento de legislacao.

Testa deteccao de keywords, classificacao de tipo,
analise de impacto e consulta de mudancas.
"""

import pytest
from app.services.monitor_legislacao import (
    monitorar_dou,
    monitorar_projetos_lei,
    analisar_impacto,
    consultar_mudancas_legislativas,
    _estimar_severidade,
    _classificar_tipo,
    _gerar_resumo_simples,
    _determinar_publico,
    _recomendar_acao,
    _scrape_dou_html,
    _processar_publicacoes,
    _fallback_resultado,
    Severidade,
    TipoPublicacao,
    KEYWORDS_MONITORADAS,
    BENEFICIOS_POR_KEYWORD,
)
from app.agent.tools.monitor_legislacao_tools import (
    consultar_mudancas_legislativas as tool_consultar_mudancas,
)


class TestKeywords:
    """Testes para keywords monitoradas."""

    def test_keywords_nao_vazia(self):
        """Deve ter keywords monitoradas."""
        assert len(KEYWORDS_MONITORADAS) > 20

    def test_keywords_inclui_programas_principais(self):
        """Deve monitorar programas principais."""
        keywords_lower = [k.lower() for k in KEYWORDS_MONITORADAS]
        assert any("bolsa" in k for k in keywords_lower)
        assert any("bpc" in k for k in keywords_lower)
        assert any("cadunico" in k or "cadúnico" in k for k in keywords_lower)

    def test_beneficios_por_keyword(self):
        """Cada keyword relevante deve mapear para beneficios."""
        assert "BOLSA_FAMILIA" in BENEFICIOS_POR_KEYWORD.get("bolsa familia", [])
        assert "BPC" in BENEFICIOS_POR_KEYWORD.get("bpc", [])
        assert "FARMACIA_POPULAR" in BENEFICIOS_POR_KEYWORD.get("farmacia popular", [])


class TestSeveridade:
    """Testes para estimativa de severidade."""

    def test_decreto_eh_alta(self):
        """Decreto deve ser severidade alta."""
        sev = _estimar_severidade(["bolsa familia"], "decreto altera regras")
        assert sev == Severidade.ALTA

    def test_medida_provisoria_eh_alta(self):
        """Medida provisoria deve ser alta."""
        sev = _estimar_severidade([], "medida provisoria sobre renda")
        assert sev == Severidade.ALTA

    def test_keyword_critica_eh_alta(self):
        """Keywords criticas (bolsa familia, bpc) devem ser alta."""
        sev = _estimar_severidade(["bolsa familia"], "informacao geral")
        assert sev == Severidade.ALTA

    def test_portaria_eh_media(self):
        """Portaria deve ser severidade media."""
        sev = _estimar_severidade(["tarifa social"], "portaria 123")
        assert sev == Severidade.MEDIA

    def test_sem_indicadores_eh_baixa(self):
        """Sem indicadores especiais deve ser baixa."""
        sev = _estimar_severidade(["dignidade menstrual"], "informacao geral")
        assert sev == Severidade.BAIXA


class TestClassificarTipo:
    """Testes para classificacao de tipo de publicacao."""

    def test_medida_provisoria(self):
        """Deve classificar medida provisoria."""
        tipo = _classificar_tipo("Medida Provisoria No 1234")
        assert tipo == TipoPublicacao.MEDIDA_PROVISORIA

    def test_decreto(self):
        """Deve classificar decreto."""
        tipo = _classificar_tipo("Decreto No 12345")
        assert tipo == TipoPublicacao.DECRETO

    def test_lei(self):
        """Deve classificar lei."""
        tipo = _classificar_tipo("Lei No 14.601")
        assert tipo == TipoPublicacao.LEI

    def test_portaria(self):
        """Deve classificar portaria."""
        tipo = _classificar_tipo("Portaria MDS No 789")
        assert tipo == TipoPublicacao.PORTARIA

    def test_tipo_desconhecido(self):
        """Texto sem tipo reconhecido deve ser OUTRO."""
        tipo = _classificar_tipo("Comunicado interno")
        assert tipo == TipoPublicacao.OUTRO


class TestResumoSimples:
    """Testes para geracao de resumo em linguagem simples."""

    def test_resumo_com_beneficio(self):
        """Resumo deve mencionar beneficio."""
        resumo = _gerar_resumo_simples(
            "Decreto altera Bolsa Familia",
            "Altera regras do programa",
            ["BOLSA_FAMILIA"],
        )
        assert "bolsa" in resumo.lower() or "familia" in resumo.lower()

    def test_resumo_sem_beneficio(self):
        """Resumo generico quando sem beneficio especifico."""
        resumo = _gerar_resumo_simples(
            "Titulo generico",
            "Ementa generica",
            [],
        )
        assert len(resumo) > 10


class TestDeterminarPublico:
    """Testes para determinacao de publico afetado."""

    def test_bolsa_familia_publico(self):
        """Bolsa Familia afeta familias de baixa renda."""
        publico = _determinar_publico(["BOLSA_FAMILIA"])
        assert "baixa renda" in publico

    def test_bpc_publico(self):
        """BPC afeta idosos e pessoas com deficiencia."""
        publico = _determinar_publico(["BPC"])
        assert "idoso" in publico or "deficiencia" in publico

    def test_sem_beneficio_publico_geral(self):
        """Sem beneficio especifico, publico eh geral."""
        publico = _determinar_publico([])
        assert "geral" in publico


class TestRecomendarAcao:
    """Testes para recomendacao de acao."""

    def test_alta_severidade_recomenda_cras(self):
        """Severidade alta deve recomendar procurar CRAS."""
        acao = _recomendar_acao(Severidade.ALTA, ["BOLSA_FAMILIA"])
        assert "cras" in acao.lower() or "atento" in acao.lower()

    def test_baixa_severidade_tranquiliza(self):
        """Severidade baixa deve tranquilizar."""
        acao = _recomendar_acao(Severidade.BAIXA, [])
        assert "nao precisa" in acao.lower() or "acompanhando" in acao.lower()


class TestAnalisarImpacto:
    """Testes para analise de impacto."""

    def test_analise_completa(self):
        """Analise deve retornar todos os campos."""
        pub = {
            "titulo": "Decreto altera Bolsa Familia",
            "ementa": "Altera valor do beneficio",
            "tipo": "decreto",
            "keywords_detectadas": ["bolsa familia"],
            "beneficios_afetados": ["BOLSA_FAMILIA"],
        }
        resultado = analisar_impacto(pub)
        assert "severidade" in resultado
        assert "resumo_simples" in resultado
        assert "publico_afetado" in resultado
        assert "acao_recomendada" in resultado

    def test_analise_severidade_alta(self):
        """Decreto sobre bolsa familia deve ser alta severidade."""
        pub = {
            "titulo": "Decreto altera regras do Bolsa Familia",
            "ementa": "Novos criterios",
            "tipo": "decreto",
            "keywords_detectadas": ["bolsa familia"],
            "beneficios_afetados": ["BOLSA_FAMILIA"],
        }
        resultado = analisar_impacto(pub)
        assert resultado["severidade"] == "alta"


class TestScrapeHtml:
    """Testes para scraping do HTML do DOU."""

    def test_encontra_keywords_no_html(self):
        """Deve encontrar keywords no HTML."""
        html = "<html><body>Alteracao no bolsa familia e bpc</body></html>"
        resultado = _scrape_dou_html(html, "2025-01-01")
        assert len(resultado["keywords_encontradas"]) >= 1

    def test_html_sem_keywords(self):
        """HTML sem keywords relevantes nao deve ter resultados."""
        html = "<html><body>Nada relevante aqui</body></html>"
        resultado = _scrape_dou_html(html, "2025-01-01")
        assert len(resultado["keywords_encontradas"]) == 0


class TestFallback:
    """Testes para fallback quando API indisponivel."""

    def test_fallback_retorna_estrutura(self):
        """Fallback deve retornar estrutura valida."""
        resultado = _fallback_resultado("2025-01-01", "timeout")
        assert resultado["data"] == "2025-01-01"
        assert resultado["erro"] == "timeout"
        assert resultado["publicacoes_relevantes"] == []


class TestProcessarPublicacoes:
    """Testes para processamento de publicacoes."""

    def test_filtra_relevantes(self):
        """Deve filtrar publicacoes com keywords."""
        publicacoes = [
            {"title": "Decreto sobre Bolsa Familia", "abstract": "Altera regras"},
            {"title": "Comunicado interno", "abstract": "Nada relevante"},
        ]
        resultado = _processar_publicacoes(publicacoes, "2025-01-01")
        assert resultado["total_relevantes"] >= 1

    def test_publicacoes_vazias(self):
        """Lista vazia deve retornar resultado vazio."""
        resultado = _processar_publicacoes([], "2025-01-01")
        assert resultado["total_relevantes"] == 0


class TestToolConsultarMudancas:
    """Testes para a tool do agente."""

    def test_retorna_estrutura(self):
        """Tool deve retornar estrutura padrao."""
        resultado = tool_consultar_mudancas()
        assert "total_mudancas" in resultado
        assert "mudancas" in resultado
        assert "fontes_consultadas" in resultado
        assert "mensagem" in resultado
