"""Testes para indicadores sociais."""

import pytest
from app.services.indicadores_sociais import (
    consultar_indicadores,
    comparar_municipios,
)


# =============================================================================
# consultar_indicadores
# =============================================================================

class TestConsultarIndicadores:
    def test_sem_municipio_lista_disponiveis(self):
        result = consultar_indicadores()
        assert "indicadores_disponiveis" in result
        assert "ibge" in result["indicadores_disponiveis"]
        assert "ipea" in result["indicadores_disponiveis"]

    def test_sao_paulo_painel_completo(self):
        result = consultar_indicadores(municipio_ibge="3550308")
        assert result["municipio"] == "Sao Paulo"
        assert result["uf"] == "SP"
        assert "indicadores" in result
        assert "protecao_social" in result
        assert "interpretacoes" in result
        assert "comparacao_nacional" in result

    def test_indicadores_presentes(self):
        result = consultar_indicadores(municipio_ibge="3550308")
        ind = result["indicadores"]
        assert ind["populacao"] == 12396372
        assert ind["idhm"] == 0.805
        assert ind["gini"] == 0.6153
        assert ind["taxa_pobreza"] == 8.4

    def test_protecao_social(self):
        result = consultar_indicadores(municipio_ibge="3550308")
        ps = result["protecao_social"]
        assert ps["cadunico_familias"] == 1200000
        assert ps["bolsa_familia_cobertura_pct"] == 72.0

    def test_interpretacao_idh_alto(self):
        result = consultar_indicadores(municipio_ibge="3550308")
        assert "muito alto" in result["interpretacoes"]["idhm"].lower()

    def test_indicador_especifico_idhm(self):
        result = consultar_indicadores(municipio_ibge="3550308", indicador="idhm")
        assert result["indicador"] == "idhm"
        assert result["valor"] == 0.805
        assert "media_nacional" in result

    def test_indicador_especifico_pobreza(self):
        result = consultar_indicadores(municipio_ibge="3550308", indicador="pobreza")
        assert result["valor"] == 8.4

    def test_municipio_inexistente(self):
        result = consultar_indicadores(municipio_ibge="0000000")
        assert "erro" in result

    def test_indicador_inexistente(self):
        result = consultar_indicadores(municipio_ibge="3550308", indicador="xyz")
        assert "erro" in result

    def test_manaus_pobreza_alta(self):
        result = consultar_indicadores(municipio_ibge="1302603")
        assert result["indicadores"]["taxa_pobreza"] == 28.7
        assert "alta" in result["interpretacoes"]["taxa_pobreza"].lower()

    def test_brasilia_idhm_muito_alto(self):
        result = consultar_indicadores(municipio_ibge="5300108")
        assert result["indicadores"]["idhm"] == 0.824

    def test_comparacao_nacional_renda(self):
        result = consultar_indicadores(municipio_ibge="3550308")
        assert result["comparacao_nacional"]["renda_vs_media"] == "acima"

    def test_comparacao_nacional_pobreza(self):
        result = consultar_indicadores(municipio_ibge="3550308")
        assert result["comparacao_nacional"]["pobreza_vs_media"] == "abaixo"


# =============================================================================
# comparar_municipios
# =============================================================================

class TestCompararMunicipios:
    def test_comparar_dois(self):
        result = comparar_municipios(["3550308", "3304557"])
        assert result["total"] == 2
        assert len(result["comparativo"]) == 2

    def test_comparar_tem_media_nacional(self):
        result = comparar_municipios(["3550308", "3304557"])
        assert "media_nacional" in result
        assert "idhm" in result["media_nacional"]

    def test_comparativo_tem_campos(self):
        result = comparar_municipios(["3550308", "3304557"])
        mun = result["comparativo"][0]
        assert "municipio" in mun
        assert "idhm" in mun
        assert "gini" in mun
        assert "taxa_pobreza" in mun

    def test_menos_de_dois_retorna_erro(self):
        result = comparar_municipios(["3550308"])
        assert "erro" in result

    def test_maximo_cinco(self):
        result = comparar_municipios(["3550308", "3304557", "2927408", "5300108", "1302603", "9999999"])
        # Limita a 5, e 9999999 nao existe
        assert result["total"] == 5

    def test_municipio_inexistente_ignorado(self):
        result = comparar_municipios(["3550308", "0000000"])
        assert result["total"] == 1
