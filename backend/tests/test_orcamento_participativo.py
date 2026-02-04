"""Testes para orcamento participativo."""

import pytest
from app.agent.tools.orcamento_participativo import (
    buscar_consultas_abertas,
    explicar_proposta,
)


# =============================================================================
# buscar_consultas_abertas
# =============================================================================

class TestBuscarConsultasAbertas:
    def test_sem_filtro_retorna_abertas(self):
        result = buscar_consultas_abertas()
        assert result["total"] > 0
        assert "consultas" in result
        assert "guia_votacao" in result

    def test_filtrar_por_municipio_sp(self):
        result = buscar_consultas_abertas(municipio_ibge="3550308")
        assert result["total"] >= 1
        # Federal + SP municipal
        for c in result["consultas"]:
            assert c["esfera"] in ("federal", "municipal")

    def test_filtrar_por_uf(self):
        result = buscar_consultas_abertas(uf="RJ")
        assert result["total"] >= 1
        for c in result["consultas"]:
            assert c["esfera"] == "federal" or "Rio" in c["titulo"]

    def test_municipio_sem_consulta(self):
        result = buscar_consultas_abertas(municipio_ibge="9999999")
        # Deve retornar apenas federais
        for c in result["consultas"]:
            assert c["esfera"] == "federal"

    def test_consulta_tem_campos(self):
        result = buscar_consultas_abertas()
        consulta = result["consultas"][0]
        assert "titulo" in consulta
        assert "descricao" in consulta
        assert "url" in consulta
        assert "canais" in consulta
        assert "propostas_destaque" in consulta

    def test_guia_votacao_web(self):
        result = buscar_consultas_abertas()
        guia = result["guia_votacao"]
        assert "web" in guia
        assert "passos" in guia["web"]
        assert len(guia["web"]["passos"]) > 0

    def test_guia_votacao_presencial(self):
        result = buscar_consultas_abertas()
        guia = result["guia_votacao"]
        assert "presencial" in guia
        assert "requisitos" in guia["presencial"]

    def test_mensagem_presente(self):
        result = buscar_consultas_abertas()
        assert "mensagem" in result


# =============================================================================
# explicar_proposta
# =============================================================================

class TestExplicarProposta:
    def test_com_valor(self):
        result = explicar_proposta("Mais creches", valor=50000000)
        assert result["proposta"] == "Mais creches"
        assert "50.000.000" in result["valor"]
        assert "explicacao" in result
        assert "dica" in result

    def test_sem_valor(self):
        result = explicar_proposta("Saneamento basico")
        assert "nao informado" in result["valor"]

    def test_valor_zero(self):
        result = explicar_proposta("Iluminacao publica", valor=0)
        assert "nao informado" in result["valor"]

    def test_explicacao_tem_titulo(self):
        result = explicar_proposta("Reforma de UBS", valor=1000000)
        assert "Reforma de UBS" in result["explicacao"]

    def test_dica_incentiva_participacao(self):
        result = explicar_proposta("Parques", valor=5000000)
        assert "direito" in result["dica"].lower() or "participar" in result["dica"].lower()
