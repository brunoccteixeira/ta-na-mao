"""Testes para economia solidaria."""

import pytest
from app.agent.tools.economia_solidaria import (
    buscar_cooperativas,
    buscar_feiras,
    guia_criar_cooperativa,
)


# =============================================================================
# buscar_cooperativas
# =============================================================================

class TestBuscarCooperativas:
    def test_sem_filtro_retorna_todas(self):
        result = buscar_cooperativas()
        assert result["total"] == 4
        assert len(result["cooperativas"]) == 4
        assert "tipos_disponiveis" in result

    def test_filtrar_por_municipio_sp(self):
        result = buscar_cooperativas(municipio_ibge="3550308")
        assert result["total"] >= 1
        for coop in result["cooperativas"]:
            assert coop["municipio_ibge"] == "3550308"

    def test_filtrar_por_uf(self):
        result = buscar_cooperativas(uf="BA")
        assert result["total"] >= 1
        for coop in result["cooperativas"]:
            assert coop["uf"] == "BA"

    def test_filtrar_por_tipo(self):
        result = buscar_cooperativas(tipo="catadores")
        assert result["total"] >= 1
        for coop in result["cooperativas"]:
            assert coop["tipo"] == "catadores"

    def test_sem_resultados(self):
        result = buscar_cooperativas(municipio_ibge="9999999")
        assert result["total"] == 0
        assert "criar" in result["mensagem"].lower() or "nao encontrei" in result["mensagem"].lower()

    def test_moeda_social_sp(self):
        result = buscar_cooperativas(municipio_ibge="3550308")
        assert result["moeda_social"] is not None
        assert result["moeda_social"]["nome"] == "Sampa"

    def test_moeda_social_inexistente(self):
        result = buscar_cooperativas(municipio_ibge="9999999")
        assert result["moeda_social"] is None

    def test_cooperativa_tem_campos(self):
        result = buscar_cooperativas()
        coop = result["cooperativas"][0]
        assert "nome" in coop
        assert "tipo" in coop
        assert "atividade" in coop
        assert "contato" in coop
        assert "como_participar" in coop


# =============================================================================
# buscar_feiras
# =============================================================================

class TestBuscarFeiras:
    def test_sem_filtro(self):
        result = buscar_feiras()
        assert result["total"] == 2
        assert len(result["feiras"]) == 2

    def test_filtrar_por_municipio(self):
        result = buscar_feiras(municipio_ibge="3550308")
        assert result["total"] >= 1
        for feira in result["feiras"]:
            assert feira["municipio_ibge"] == "3550308"

    def test_filtrar_por_dia(self):
        result = buscar_feiras(dia_semana="sabado")
        assert result["total"] >= 1
        for feira in result["feiras"]:
            assert feira["dia_semana"] == "sabado"

    def test_dia_sem_feira(self):
        result = buscar_feiras(dia_semana="segunda")
        assert result["total"] == 0

    def test_feira_tem_campos(self):
        result = buscar_feiras()
        feira = result["feiras"][0]
        assert "nome" in feira
        assert "local" in feira
        assert "horario" in feira
        assert "produtos" in feira
        assert "dia_semana" in feira


# =============================================================================
# guia_criar_cooperativa
# =============================================================================

class TestGuiaCriarCooperativa:
    def test_retorna_passos(self):
        result = guia_criar_cooperativa()
        assert "passos" in result
        assert len(result["passos"]) == 6

    def test_passos_ordenados(self):
        result = guia_criar_cooperativa()
        for i, passo in enumerate(result["passos"]):
            assert passo["passo"] == i + 1

    def test_passo_tem_campos(self):
        result = guia_criar_cooperativa()
        passo = result["passos"][0]
        assert "titulo" in passo
        assert "descricao" in passo
        assert "dica" in passo

    def test_requisitos(self):
        result = guia_criar_cooperativa()
        assert "requisitos" in result
        assert len(result["requisitos"]) >= 3

    def test_onde_pedir_ajuda(self):
        result = guia_criar_cooperativa()
        assert "onde_pedir_ajuda" in result
        ajuda_str = " ".join(result["onde_pedir_ajuda"])
        assert "SEBRAE" in ajuda_str

    def test_programas_fomento(self):
        result = guia_criar_cooperativa()
        assert "programas_fomento" in result
        nomes = [p["nome"] for p in result["programas_fomento"]]
        assert any("PAA" in n for n in nomes)
        assert any("PNAE" in n for n in nomes)
