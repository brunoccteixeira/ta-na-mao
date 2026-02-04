"""Testes para seguranca cidada (LGPD)."""

import pytest
import app.services.seguranca_cidada as seguranca_mod
from app.services.seguranca_cidada import (
    hash_cpf,
    hash_ip,
    registrar_consentimento,
    verificar_consentimento,
    revogar_consentimento,
    exportar_dados,
    excluir_dados,
    consultar_politica_privacidade,
    registrar_acesso,
    FINALIDADES,
    CLASSIFICACAO_DADOS,
)


@pytest.fixture(autouse=True)
def limpar_dados():
    """Limpa dados entre testes."""
    seguranca_mod._consentimentos = []
    seguranca_mod._log_auditoria = []
    yield
    seguranca_mod._consentimentos = []
    seguranca_mod._log_auditoria = []


# =============================================================================
# hash_cpf / hash_ip
# =============================================================================

class TestHash:
    def test_hash_cpf_deterministic(self):
        h1 = hash_cpf("529.982.247-25")
        h2 = hash_cpf("52998224725")
        assert h1 == h2

    def test_hash_cpf_different_cpfs(self):
        h1 = hash_cpf("52998224725")
        h2 = hash_cpf("12345678901")
        assert h1 != h2

    def test_hash_cpf_is_sha256(self):
        h = hash_cpf("52998224725")
        assert len(h) == 64  # SHA-256 hex digest

    def test_hash_ip(self):
        h = hash_ip("192.168.1.1")
        assert len(h) == 16  # Truncated

    def test_hash_ip_deterministic(self):
        h1 = hash_ip("10.0.0.1")
        h2 = hash_ip("10.0.0.1")
        assert h1 == h2


# =============================================================================
# registrar_consentimento
# =============================================================================

class TestRegistrarConsentimento:
    def test_consentimento_valido(self):
        result = registrar_consentimento("52998224725", "consulta_beneficio")
        assert result["consentimento_registrado"] is True
        assert result["finalidade"] == "consulta_beneficio"
        assert "mensagem_cidadao" in result

    def test_consentimento_farmacia(self):
        result = registrar_consentimento("52998224725", "farmacia")
        assert result["consentimento_registrado"] is True
        assert "receita" in result["mensagem_cidadao"].lower() or "remedio" in result["mensagem_cidadao"].lower()

    def test_consentimento_armazenado(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        assert len(seguranca_mod._consentimentos) == 1
        assert seguranca_mod._consentimentos[0]["finalidade"] == "consulta_beneficio"
        assert seguranca_mod._consentimentos[0]["revogado"] is False

    def test_finalidade_invalida(self):
        result = registrar_consentimento("52998224725", "xyz")
        assert "erro" in result
        assert "finalidades_disponiveis" in result

    def test_retencao_informada(self):
        result = registrar_consentimento("52998224725", "consulta_beneficio")
        assert result["retencao"] == "durante_sessao"

    def test_canal_informado(self):
        registrar_consentimento("52998224725", "consulta_beneficio", canal="whatsapp")
        assert seguranca_mod._consentimentos[0]["canal"] == "whatsapp"

    def test_cpf_hasheado(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        assert seguranca_mod._consentimentos[0]["cpf_hash"] == hash_cpf("52998224725")
        # CPF em texto nao esta no registro
        for key, val in seguranca_mod._consentimentos[0].items():
            if isinstance(val, str) and key != "cpf_hash":
                assert "52998224725" not in val


# =============================================================================
# verificar_consentimento
# =============================================================================

class TestVerificarConsentimento:
    def test_consentimento_existe(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        assert verificar_consentimento("52998224725", "consulta_beneficio") is True

    def test_consentimento_nao_existe(self):
        assert verificar_consentimento("52998224725", "consulta_beneficio") is False

    def test_consentimento_revogado(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        revogar_consentimento("52998224725", "consulta_beneficio")
        assert verificar_consentimento("52998224725", "consulta_beneficio") is False

    def test_outra_finalidade(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        assert verificar_consentimento("52998224725", "farmacia") is False


# =============================================================================
# revogar_consentimento
# =============================================================================

class TestRevogarConsentimento:
    def test_revogar_especifico(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        registrar_consentimento("52998224725", "farmacia")
        result = revogar_consentimento("52998224725", "consulta_beneficio")
        assert result["revogados"] == 1
        assert verificar_consentimento("52998224725", "farmacia") is True

    def test_revogar_todos(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        registrar_consentimento("52998224725", "farmacia")
        result = revogar_consentimento("52998224725")
        assert result["revogados"] == 2

    def test_nada_para_revogar(self):
        result = revogar_consentimento("52998224725")
        assert result["revogados"] == 0
        assert "nenhum" in result["mensagem"].lower()


# =============================================================================
# exportar_dados
# =============================================================================

class TestExportarDados:
    def test_sem_dados(self):
        result = exportar_dados("52998224725")
        assert result["titular"]["cpf_parcial"] is not None
        assert result["consentimentos"] == []
        assert result["acessos_registrados"] == 0

    def test_com_consentimentos(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        registrar_consentimento("52998224725", "farmacia")
        result = exportar_dados("52998224725")
        assert len(result["consentimentos"]) == 2

    def test_formatos_disponiveis(self):
        result = exportar_dados("52998224725")
        assert "json" in result["formatos_disponiveis"]

    def test_cpf_parcial(self):
        result = exportar_dados("52998224725")
        # CPF parcial should not contain full CPF
        assert "52998224725" not in result["titular"]["cpf_parcial"]


# =============================================================================
# excluir_dados
# =============================================================================

class TestExcluirDados:
    def test_sem_confirmacao(self):
        result = excluir_dados("52998224725")
        assert "aviso" in result
        assert "confirmar" in result

    def test_com_confirmacao(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        registrar_consentimento("52998224725", "farmacia")
        result = excluir_dados("52998224725", confirmar=True)
        assert result["sucesso"] is True
        assert result["registros_removidos"] == 2
        # After deletion, consent should not be found
        assert verificar_consentimento("52998224725", "consulta_beneficio") is False
        assert verificar_consentimento("52998224725", "farmacia") is False

    def test_nao_afeta_outros_cpfs(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        registrar_consentimento("12345678901", "consulta_beneficio")
        excluir_dados("52998224725", confirmar=True)
        assert verificar_consentimento("12345678901", "consulta_beneficio") is True
        assert verificar_consentimento("52998224725", "consulta_beneficio") is False

    def test_registra_exclusao_na_auditoria(self):
        registrar_consentimento("52998224725", "consulta_beneficio")
        excluir_dados("52998224725", confirmar=True)
        assert any(a["tipo"] == "exclusao_dados" for a in seguranca_mod._log_auditoria)

    def test_mensagem_tranquiliza(self):
        result = excluir_dados("52998224725", confirmar=True)
        assert "NAO afeta" in result["mensagem"] or "beneficios" in result["mensagem"].lower()


# =============================================================================
# consultar_politica_privacidade
# =============================================================================

class TestConsultarPoliticaPrivacidade:
    def test_retorna_politica(self):
        result = consultar_politica_privacidade()
        assert "titulo" in result
        assert "o_que_fazemos" in result
        assert "seus_direitos" in result
        assert "como_exercer" in result
        assert "base_legal" in result

    def test_lgpd_mencionada(self):
        result = consultar_politica_privacidade()
        assert "LGPD" in result["base_legal"]

    def test_contato_dpo(self):
        result = consultar_politica_privacidade()
        assert "contato_dpo" in result


# =============================================================================
# registrar_acesso
# =============================================================================

class TestRegistrarAcesso:
    def test_registra_acesso(self):
        registrar_acesso("/api/beneficios", "GET", ip="192.168.1.1")
        assert len(seguranca_mod._log_auditoria) == 1
        assert seguranca_mod._log_auditoria[0]["tipo"] == "acesso"
        assert seguranca_mod._log_auditoria[0]["endpoint"] == "/api/beneficios"

    def test_ip_hasheado(self):
        registrar_acesso("/api/beneficios", "GET", ip="192.168.1.1")
        assert seguranca_mod._log_auditoria[0]["ip_hash"] is not None
        assert "192.168.1.1" not in str(seguranca_mod._log_auditoria[0])

    def test_sem_ip(self):
        registrar_acesso("/api/beneficios", "GET")
        assert seguranca_mod._log_auditoria[0]["ip_hash"] is None

    def test_status_code(self):
        registrar_acesso("/api/beneficios", "GET", status_code=404)
        assert seguranca_mod._log_auditoria[0]["status_code"] == 404


# =============================================================================
# CLASSIFICACAO_DADOS / FINALIDADES
# =============================================================================

class TestConstantes:
    def test_classificacao_dados_pessoais(self):
        assert "DADOS_PESSOAIS" in CLASSIFICACAO_DADOS
        assert "cpf" in CLASSIFICACAO_DADOS["DADOS_PESSOAIS"]["campos"]

    def test_classificacao_dados_sensiveis(self):
        assert "DADOS_SENSIVEIS" in CLASSIFICACAO_DADOS
        assert "saude" in CLASSIFICACAO_DADOS["DADOS_SENSIVEIS"]["campos"]

    def test_finalidades_completas(self):
        assert len(FINALIDADES) == 5
        for f in FINALIDADES.values():
            assert "descricao" in f
            assert "base_legal" in f
            assert "retencao" in f
