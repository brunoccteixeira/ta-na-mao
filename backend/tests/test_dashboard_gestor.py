"""Testes para dashboard do gestor (painel-gestor)."""

import pytest
from app.services.dashboard_gestor import (
    visao_geral,
    analise_lacunas,
    benchmark,
    consultar_dashboard_gestor,
)


# =============================================================================
# visao_geral
# =============================================================================

class TestVisaoGeral:
    def test_sao_paulo(self):
        result = visao_geral("3550308")
        assert result["municipio"] == "Sao Paulo"
        assert result["uf"] == "SP"
        assert "kpis" in result
        assert "equipamentos_suas" in result
        assert "alertas" in result

    def test_kpis(self):
        result = visao_geral("3550308")
        kpis = result["kpis"]
        assert kpis["populacao"] == 12396372
        assert kpis["familias_cadunico"] == 1200000
        assert kpis["idhm"] == 0.805

    def test_equipamentos_suas_recomendados(self):
        result = visao_geral("3550308")
        eq = result["equipamentos_suas"]
        assert eq["cras_recomendados"] > 0
        assert eq["creas_recomendados"] > 0

    def test_municipio_inexistente(self):
        result = visao_geral("0000000")
        assert "erro" in result

    def test_alertas_cobertura_baixa(self):
        # Brasilia tem cobertura BF 60% < 70%
        result = visao_geral("5300108")
        alertas_tipos = [a["tipo"] for a in result["alertas"]]
        assert "cobertura_baixa" in alertas_tipos

    def test_alertas_pobreza_alta(self):
        # Manaus tem taxa_pobreza 28.7% > 25%
        result = visao_geral("1302603")
        alertas_tipos = [a["tipo"] for a in result["alertas"]]
        assert "pobreza_alta" in alertas_tipos

    def test_alertas_saneamento(self):
        # Manaus tem saneamento 48% < 60%
        result = visao_geral("1302603")
        alertas_tipos = [a["tipo"] for a in result["alertas"]]
        assert "saneamento_critico" in alertas_tipos


# =============================================================================
# analise_lacunas
# =============================================================================

class TestAnaliseLacunas:
    def test_brasilia_lacuna_bf(self):
        # Brasilia BF coverage 60% < 80%
        result = analise_lacunas("5300108")
        assert result["total_lacunas"] >= 1
        programas = [l["programa"] for l in result["lacunas"]]
        assert "Bolsa Familia" in programas

    def test_resumo_familias(self):
        result = analise_lacunas("3550308")
        resumo = result["resumo"]
        assert resumo["familias_cadunico"] == 1200000
        assert resumo["familias_com_bf"] > 0
        assert resumo["valor_nao_acessado_mensal"] >= 0

    def test_municipio_inexistente(self):
        result = analise_lacunas("0000000")
        assert "erro" in result

    def test_manaus_multiplas_lacunas(self):
        # Manaus: saneamento 48% < 80, analfabetismo 5.3% (media 5.6 - not above)
        result = analise_lacunas("1302603")
        programas = [l["programa"] for l in result["lacunas"]]
        assert "Saneamento Basico" in programas


# =============================================================================
# benchmark
# =============================================================================

class TestBenchmark:
    def test_sao_paulo(self):
        result = benchmark("3550308")
        assert result["municipio"] == "Sao Paulo"
        assert "ranking_idhm" in result
        assert "vs_media_nacional" in result

    def test_ranking_posicao(self):
        result = benchmark("3550308")
        ranking = result["ranking_idhm"]
        assert ranking["posicao"] >= 1
        assert ranking["total_comparados"] == 5

    def test_vs_media_nacional(self):
        result = benchmark("3550308")
        vs = result["vs_media_nacional"]
        assert vs["idhm"]["status"] == "acima"
        assert vs["taxa_pobreza"]["status"] == "melhor"

    def test_municipio_inexistente(self):
        result = benchmark("0000000")
        assert "erro" in result


# =============================================================================
# consultar_dashboard_gestor (tool wrapper)
# =============================================================================

class TestConsultarDashboardGestor:
    def test_default_visao_geral(self):
        result = consultar_dashboard_gestor("3550308")
        assert "kpis" in result

    def test_modulo_lacunas(self):
        result = consultar_dashboard_gestor("3550308", modulo="lacunas")
        assert "lacunas" in result

    def test_modulo_benchmark(self):
        result = consultar_dashboard_gestor("3550308", modulo="benchmark")
        assert "ranking_idhm" in result
