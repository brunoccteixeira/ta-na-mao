"""Testes para comandos de voz (voz-acessivel)."""

import pytest
from app.agent.tools.comandos_voz import (
    mapear_comando_voz,
    listar_comandos_voz,
    configurar_voz,
)


# =============================================================================
# mapear_comando_voz
# =============================================================================

class TestMapearComandoVoz:
    def test_farmacia_popular_remedio(self):
        result = mapear_comando_voz("quero pegar remedio de graca")
        assert result["reconhecido"] is True
        assert result["intencao"] == "FARMACIA_POPULAR"
        assert result["tool_recomendada"] == "buscar_farmacia"

    def test_farmacia_popular_farmacia(self):
        result = mapear_comando_voz("farmacia popular")
        assert result["reconhecido"] is True
        assert result["intencao"] == "FARMACIA_POPULAR"

    def test_bolsa_familia(self):
        result = mapear_comando_voz("quero o bolsa familia")
        assert result["reconhecido"] is True
        assert result["intencao"] == "BOLSA_FAMILIA"
        assert result["tool_recomendada"] == "gerar_checklist"

    def test_bpc(self):
        result = mapear_comando_voz("beneficio para idoso")
        assert result["reconhecido"] is True
        assert result["intencao"] == "BPC"

    def test_consultar_beneficios(self):
        result = mapear_comando_voz("meus beneficios")
        assert result["reconhecido"] is True
        assert result["intencao"] == "CONSULTAR_BENEFICIOS"
        assert result["tool_recomendada"] == "consultar_beneficio"

    def test_buscar_cras(self):
        result = mapear_comando_voz("onde fica o cras")
        assert result["reconhecido"] is True
        assert result["intencao"] == "BUSCAR_CRAS"
        assert result["tool_recomendada"] == "buscar_cras"

    def test_dinheiro_esquecido(self):
        result = mapear_comando_voz("dinheiro esquecido")
        assert result["reconhecido"] is True
        assert result["intencao"] == "DINHEIRO_ESQUECIDO"
        assert result["tool_recomendada"] == "consultar_dinheiro_esquecido"

    def test_pis_pasep(self):
        result = mapear_comando_voz("pis pasep")
        assert result["reconhecido"] is True
        assert result["intencao"] == "DINHEIRO_ESQUECIDO"

    def test_fgts(self):
        result = mapear_comando_voz("fgts")
        assert result["reconhecido"] is True
        assert result["intencao"] == "DINHEIRO_ESQUECIDO"

    def test_ajuda(self):
        result = mapear_comando_voz("ajuda")
        assert result["reconhecido"] is True
        assert result["intencao"] == "AJUDA"
        assert result["tool_recomendada"] is None

    def test_nao_reconhecido(self):
        result = mapear_comando_voz("alskdjfalskdjf")
        assert result["reconhecido"] is False
        assert result["intencao"] == "GERAL"
        assert result["tool_recomendada"] is None

    def test_case_insensitive(self):
        result = mapear_comando_voz("BOLSA FAMILIA")
        assert result["reconhecido"] is True
        assert result["intencao"] == "BOLSA_FAMILIA"

    def test_transcricao_original_preservada(self):
        result = mapear_comando_voz("Quero pedir remedio")
        assert result["transcricao_original"] == "Quero pedir remedio"


# =============================================================================
# listar_comandos_voz
# =============================================================================

class TestListarComandosVoz:
    def test_retorna_comandos(self):
        result = listar_comandos_voz()
        assert "comandos" in result
        assert result["total"] == 7
        assert len(result["comandos"]) == 7

    def test_comando_tem_campos(self):
        result = listar_comandos_voz()
        cmd = result["comandos"][0]
        assert "intencao" in cmd
        assert "exemplos" in cmd
        assert "resposta" in cmd

    def test_tem_dica(self):
        result = listar_comandos_voz()
        assert "dica" in result


# =============================================================================
# configurar_voz
# =============================================================================

class TestConfigurarVoz:
    def test_speech_to_text_config(self):
        result = configurar_voz()
        stt = result["speech_to_text"]
        assert stt["lang"] == "pt-BR"
        assert stt["continuous"] is False
        assert stt["interimResults"] is True

    def test_text_to_speech_config(self):
        result = configurar_voz()
        tts = result["text_to_speech"]
        assert tts["lang"] == "pt-BR"
        assert tts["rate"] == 0.85

    def test_dicas_acessibilidade(self):
        result = configurar_voz()
        assert "dicas_acessibilidade" in result
        assert len(result["dicas_acessibilidade"]) > 0
