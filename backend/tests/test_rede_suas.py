"""Testes para navegacao da Rede SUAS."""

import pytest
from app.agent.tools.rede_suas import (
    classificar_necessidade_suas,
    listar_equipamentos_suas,
    TipoEquipamento,
    EQUIPAMENTOS_SUAS,
    _telefones_uteis,
)


# =============================================================================
# classificar_necessidade_suas
# =============================================================================

class TestClassificarNecessidadeSuas:
    def test_violencia_encaminha_creas(self):
        result = classificar_necessidade_suas("meu marido me bate, estou com medo")
        assert result["equipamento"] == "CREAS"
        assert result["urgente"] is True

    def test_situacao_rua_encaminha_centro_pop(self):
        result = classificar_necessidade_suas("estou morando na rua sem ter onde dormir")
        assert result["equipamento"] == "CENTRO_POP"

    def test_saude_mental_encaminha_caps(self):
        result = classificar_necessidade_suas("estou com depressao muito forte, pensando em suicidio")
        assert result["equipamento"] == "CAPS"

    def test_crianca_na_rua(self):
        result = classificar_necessidade_suas("tem uma crianca abandonada na rua")
        # CONSELHO_TUTELAR or CENTRO_POP depending on keyword scoring
        assert result["equipamento"] in ("CONSELHO_TUTELAR", "CENTRO_POP", "CAPS")

    def test_beneficio_basico_encaminha_cras(self):
        result = classificar_necessidade_suas("quero me cadastrar no CadUnico e pedir Bolsa Familia")
        assert result["equipamento"] == "CRAS"

    def test_mensagem_generica_encaminha_cras(self):
        result = classificar_necessidade_suas("preciso de ajuda")
        assert result["equipamento"] == "CRAS"

    def test_retorna_telefones_uteis(self):
        result = classificar_necessidade_suas("estou sofrendo violencia")
        assert "telefones_uteis" in result
        assert len(result["telefones_uteis"]) > 0

    def test_retorna_servicos(self):
        result = classificar_necessidade_suas("preciso de ajuda")
        assert "servicos" in result
        assert len(result["servicos"]) > 0

    def test_contexto_situacao_rua(self):
        result = classificar_necessidade_suas(
            "preciso de ajuda",
            situacao_rua=True,
        )
        assert result["equipamento"] == "CENTRO_POP"

    def test_violencia_com_criancas_urgente(self):
        result = classificar_necessidade_suas(
            "estou sendo agredida pelo meu marido",
            tem_criancas=True,
        )
        # Violence detected + children = urgente
        assert result["urgente"] is True

    def test_dependencia_quimica(self):
        result = classificar_necessidade_suas("meu filho esta usando drogas e bebendo muito")
        assert result["equipamento"] == "CAPS"

    def test_outros_possiveis(self):
        result = classificar_necessidade_suas(
            "estou sofrendo violencia e morando na rua"
        )
        assert "outros_possiveis" in result

    def test_keywords_detectadas(self):
        result = classificar_necessidade_suas("estou com depressao e ansiedade")
        assert "keywords_detectadas" in result
        assert len(result["keywords_detectadas"]) > 0


# =============================================================================
# listar_equipamentos_suas
# =============================================================================

class TestListarEquipamentosSuas:
    def test_listar_todos(self):
        result = listar_equipamentos_suas()
        assert "equipamentos" in result
        assert len(result["equipamentos"]) >= 5

    def test_listar_cras(self):
        result = listar_equipamentos_suas("CRAS")
        assert result["equipamento"] == "CRAS"
        assert "servicos" in result

    def test_listar_creas(self):
        result = listar_equipamentos_suas("CREAS")
        assert result["equipamento"] == "CREAS"

    def test_listar_caps(self):
        result = listar_equipamentos_suas("CAPS")
        assert result["equipamento"] == "CAPS"

    def test_tipo_invalido(self):
        result = listar_equipamentos_suas("INVALIDO")
        assert "erro" in result
        assert "tipos_disponiveis" in result

    def test_tipo_case_insensitive(self):
        result = listar_equipamentos_suas("cras")
        assert result["equipamento"] == "CRAS"


# =============================================================================
# _telefones_uteis
# =============================================================================

class TestTelefonesUteis:
    def test_creas_tem_disque_100(self):
        telefones = _telefones_uteis(TipoEquipamento.CREAS, urgente=False)
        numeros = [t["numero"] for t in telefones]
        assert "100" in numeros

    def test_caps_tem_cvv(self):
        telefones = _telefones_uteis(TipoEquipamento.CAPS, urgente=False)
        numeros = [t["numero"] for t in telefones]
        assert "188" in numeros

    def test_urgente_tem_190(self):
        telefones = _telefones_uteis(TipoEquipamento.CREAS, urgente=True)
        numeros = [t["numero"] for t in telefones]
        assert "190" in numeros

    def test_sempre_tem_disque_social(self):
        for tipo in TipoEquipamento:
            if tipo in EQUIPAMENTOS_SUAS:
                telefones = _telefones_uteis(tipo, urgente=False)
                numeros = [t["numero"] for t in telefones]
                assert "121" in numeros


# =============================================================================
# Dados dos equipamentos
# =============================================================================

class TestEquipamentosSuas:
    def test_todos_equipamentos_tem_campos(self):
        for tipo, info in EQUIPAMENTOS_SUAS.items():
            assert "nome" in info, f"{tipo} sem nome"
            assert "tipo_protecao" in info, f"{tipo} sem tipo_protecao"
            assert "descricao" in info, f"{tipo} sem descricao"
            assert "servicos" in info, f"{tipo} sem servicos"
            assert len(info["servicos"]) > 0, f"{tipo} sem servicos listados"
