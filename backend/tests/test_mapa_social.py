"""Testes para mapa social."""

import pytest
from app.services.mapa_social import (
    listar_camadas,
    consultar_mapa_social,
    identificar_desertos,
)


# =============================================================================
# listar_camadas
# =============================================================================

class TestListarCamadas:
    def test_retorna_camadas(self):
        result = listar_camadas()
        assert "camadas" in result
        camadas = result["camadas"]
        assert "indicadores" in camadas
        assert "equipamentos" in camadas
        assert "analise" in camadas

    def test_total(self):
        result = listar_camadas()
        assert result["total"] > 0

    def test_indicadores_tem_campos(self):
        result = listar_camadas()
        ind = result["camadas"]["indicadores"][0]
        assert "id" in ind
        assert "nome" in ind
        assert "tipo" in ind


# =============================================================================
# consultar_mapa_social
# =============================================================================

class TestConsultarMapaSocial:
    def test_camada_idh(self):
        result = consultar_mapa_social("idh_m")
        assert result["camada"] == "idh_m"
        assert result["tipo"] == "choropleth"
        assert "dados" in result
        assert result["total"] == 5

    def test_camada_taxa_pobreza(self):
        result = consultar_mapa_social("taxa_pobreza")
        assert result["tipo"] == "choropleth"
        assert result["total"] == 5

    def test_camada_com_filtro_uf(self):
        result = consultar_mapa_social("idh_m", uf="SP")
        assert result["total"] == 1
        assert result["dados"][0]["uf"] == "SP"

    def test_camada_cras(self):
        result = consultar_mapa_social("cras")
        assert result["tipo"] == "pontos"
        assert result["total"] > 0
        assert "pontos" in result

    def test_camada_cras_por_municipio(self):
        result = consultar_mapa_social("cras", municipio_ibge="3550308")
        assert result["total"] > 0
        for p in result["pontos"]:
            assert p["municipio_ibge"] == "3550308"

    def test_camada_deserto_social(self):
        result = consultar_mapa_social("deserto_social")
        assert "desertos" in result
        assert "criticos" in result

    def test_camada_inexistente(self):
        result = consultar_mapa_social("xyz")
        assert "erro" in result

    def test_dado_choropleth_tem_campos(self):
        result = consultar_mapa_social("idh_m")
        dado = result["dados"][0]
        assert "municipio_ibge" in dado
        assert "municipio" in dado
        assert "uf" in dado
        assert "valor" in dado

    def test_ponto_tem_campos(self):
        result = consultar_mapa_social("cras")
        ponto = result["pontos"][0]
        assert "tipo" in ponto
        assert "municipio_ibge" in ponto
        assert "id" in ponto


# =============================================================================
# identificar_desertos
# =============================================================================

class TestIdentificarDesertos:
    def test_todos_municipios(self):
        result = identificar_desertos()
        assert result["total_municipios"] == 5
        assert "desertos" in result
        assert "classificacoes" in result

    def test_filtrar_por_uf(self):
        result = identificar_desertos(uf="SP")
        assert result["total_municipios"] == 1
        assert result["desertos"][0]["uf"] == "SP"

    def test_deserto_tem_campos(self):
        result = identificar_desertos()
        d = result["desertos"][0]
        assert "municipio_ibge" in d
        assert "municipio" in d
        assert "familias_cadunico" in d
        assert "ratio_familias_cras" in d
        assert "classificacao" in d
        assert "cor" in d

    def test_classificacao_valida(self):
        result = identificar_desertos()
        valid = {"ADEQUADO", "INSUFICIENTE", "CRITICO", "SEM_COBERTURA"}
        for d in result["desertos"]:
            assert d["classificacao"] in valid

    def test_ordenacao_por_severidade(self):
        result = identificar_desertos()
        severidade_map = {"SEM_COBERTURA": 4, "CRITICO": 3, "INSUFICIENTE": 2, "ADEQUADO": 1}
        severidades = [severidade_map[d["classificacao"]] for d in result["desertos"]]
        assert severidades == sorted(severidades, reverse=True)

    def test_mensagem_com_criticos(self):
        result = identificar_desertos()
        assert "mensagem" in result

    def test_uf_inexistente(self):
        result = identificar_desertos(uf="XX")
        assert result["total_municipios"] == 0
