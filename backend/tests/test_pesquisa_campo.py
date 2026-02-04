"""Testes para pesquisa de campo."""

import pytest
from app.services.pesquisa_campo import (
    listar_questionarios,
    obter_questionario,
    registrar_resposta,
    gerar_relatorio_pesquisa,
    _respostas_coletadas,
)


@pytest.fixture(autouse=True)
def limpar_respostas():
    """Limpa respostas entre testes."""
    _respostas_coletadas.clear()
    yield
    _respostas_coletadas.clear()


# =============================================================================
# listar_questionarios
# =============================================================================

class TestListarQuestionarios:
    def test_lista_todos(self):
        result = listar_questionarios()
        assert result["total"] == 3
        assert len(result["questionarios"]) == 3

    def test_questionario_tem_campos(self):
        result = listar_questionarios()
        q = result["questionarios"][0]
        assert "id" in q
        assert "titulo" in q
        assert "descricao" in q
        assert "total_perguntas" in q


# =============================================================================
# obter_questionario
# =============================================================================

class TestObterQuestionario:
    def test_satisfacao(self):
        result = obter_questionario("satisfacao")
        assert result["id"] == "satisfacao_v1"
        assert "perguntas" in result
        assert len(result["perguntas"]) == 4

    def test_necessidades(self):
        result = obter_questionario("necessidades")
        assert result["id"] == "necessidades_v1"

    def test_atendimento_cras(self):
        result = obter_questionario("atendimento_cras")
        assert result["id"] == "atendimento_cras_v1"

    def test_inexistente(self):
        result = obter_questionario("xyz")
        assert "erro" in result
        assert "disponiveis" in result

    def test_pergunta_tem_campos(self):
        result = obter_questionario("satisfacao")
        p = result["perguntas"][0]
        assert "id" in p
        assert "texto" in p
        assert "tipo" in p


# =============================================================================
# registrar_resposta
# =============================================================================

class TestRegistrarResposta:
    def test_registro_basico(self):
        result = registrar_resposta(
            "satisfacao",
            {"q1": "Sim, tudo certo", "q2": "Facil"},
        )
        assert result["sucesso"] is True
        assert result["anonimo"] is True

    def test_com_canal_e_municipio(self):
        result = registrar_resposta(
            "satisfacao",
            {"q1": "Sim, tudo certo"},
            canal="whatsapp",
            municipio_ibge="3550308",
        )
        assert result["sucesso"] is True

    def test_questionario_inexistente(self):
        result = registrar_resposta("xyz", {})
        assert "erro" in result

    def test_respostas_armazenadas(self):
        registrar_resposta("satisfacao", {"q1": "Sim, tudo certo"})
        registrar_resposta("satisfacao", {"q1": "Mais ou menos"})
        assert len(_respostas_coletadas) == 2


# =============================================================================
# gerar_relatorio_pesquisa
# =============================================================================

class TestGerarRelatorioPesquisa:
    def test_menos_de_10_respostas(self):
        for i in range(5):
            registrar_resposta("satisfacao", {"q1": "Sim, tudo certo"})
        result = gerar_relatorio_pesquisa("satisfacao")
        assert result["relatorio_disponivel"] is False
        assert result["total_respostas"] == 5

    def test_com_10_respostas(self):
        for i in range(10):
            registrar_resposta("satisfacao", {
                "q1": "Sim, tudo certo",
                "q2": "Facil",
                "q3": "Com certeza sim",
            })
        result = gerar_relatorio_pesquisa("satisfacao")
        assert result["relatorio_disponivel"] is True
        assert result["total_respostas"] == 10
        assert "resultados" in result

    def test_distribuicao_respostas(self):
        for i in range(6):
            registrar_resposta("satisfacao", {"q1": "Sim, tudo certo", "q3": "Com certeza sim"})
        for i in range(4):
            registrar_resposta("satisfacao", {"q1": "Nao consegui", "q3": "Talvez"})
        result = gerar_relatorio_pesquisa("satisfacao")
        assert result["relatorio_disponivel"] is True
        q1 = result["resultados"]["q1"]
        assert q1["distribuicao"]["Sim, tudo certo"] == 6
        assert q1["distribuicao"]["Nao consegui"] == 4

    def test_nps_calculado(self):
        for i in range(10):
            registrar_resposta("satisfacao", {"q3": "Com certeza sim"})
        result = gerar_relatorio_pesquisa("satisfacao")
        assert result["nps"] is not None
        assert "score" in result["nps"]
        assert "classificacao" in result["nps"]

    def test_nps_promotores(self):
        # "Com certeza sim" maps to 10 -> promoter
        for i in range(10):
            registrar_resposta("satisfacao", {"q3": "Com certeza sim"})
        result = gerar_relatorio_pesquisa("satisfacao")
        assert result["nps"]["promotores_pct"] == 100.0

    def test_nps_detratores(self):
        # "Com certeza nao" maps to 0 -> detractor
        for i in range(10):
            registrar_resposta("satisfacao", {"q3": "Com certeza nao"})
        result = gerar_relatorio_pesquisa("satisfacao")
        assert result["nps"]["detratores_pct"] == 100.0

    def test_canais_contados(self):
        for i in range(5):
            registrar_resposta("satisfacao", {"q1": "Sim, tudo certo"}, canal="app")
        for i in range(5):
            registrar_resposta("satisfacao", {"q1": "Sim, tudo certo"}, canal="whatsapp")
        result = gerar_relatorio_pesquisa("satisfacao")
        assert result["canais"]["app"] == 5
        assert result["canais"]["whatsapp"] == 5

    def test_texto_livre(self):
        for i in range(10):
            registrar_resposta("satisfacao", {"q4": f"Comentario {i}"})
        result = gerar_relatorio_pesquisa("satisfacao")
        q4 = result["resultados"]["q4"]
        assert q4["tipo"] == "texto_livre"
        assert len(q4["amostra"]) <= 5

    def test_questionario_necessidades(self):
        for i in range(10):
            registrar_resposta("necessidades", {"q1": "Nao sei quais tenho direito"})
        result = gerar_relatorio_pesquisa("necessidades")
        assert result["relatorio_disponivel"] is True
        # NPS only for satisfacao
        assert result["nps"] is None
