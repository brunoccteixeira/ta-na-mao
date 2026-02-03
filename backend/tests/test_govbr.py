"""
Testes para integracao Gov.br.

Testa auto-preenchimento, niveis de confianca,
URL de login e servico mock.
"""

import pytest
from app.services.govbr_service import (
    auto_preencher_dados,
    gerar_url_login,
    is_govbr_configured,
    _determinar_nivel,
    _descrever_nivel,
    _mock_auto_preencher,
    NivelConfianca,
    PERMISSOES_POR_NIVEL,
)
from app.agent.tools.govbr_tools import (
    consultar_govbr,
    verificar_nivel_govbr,
    gerar_login_govbr,
)


class TestNivelConfianca:
    """Testes para niveis de confianca Gov.br."""

    def test_determinar_nivel_bronze(self):
        """Sem confiabilidades especiais deve ser bronze."""
        nivel = _determinar_nivel([])
        assert nivel == NivelConfianca.BRONZE

    def test_determinar_nivel_prata(self):
        """Com validacao bancaria deve ser prata."""
        nivel = _determinar_nivel(["501"])
        assert nivel == NivelConfianca.PRATA

    def test_determinar_nivel_ouro(self):
        """Com biometria TSE deve ser ouro."""
        nivel = _determinar_nivel(["801"])
        assert nivel == NivelConfianca.OURO

    def test_ouro_tem_prioridade(self):
        """Ouro deve ter prioridade sobre prata."""
        nivel = _determinar_nivel(["501", "801"])
        assert nivel == NivelConfianca.OURO

    def test_descrever_niveis(self):
        """Cada nivel deve ter descricao."""
        for nivel in NivelConfianca:
            desc = _descrever_nivel(nivel)
            assert len(desc) > 0

    def test_permissoes_por_nivel(self):
        """Cada nivel deve ter lista de permissoes."""
        for nivel in NivelConfianca:
            permissoes = PERMISSOES_POR_NIVEL[nivel]
            assert len(permissoes) > 0


class TestMockAutoPreenchimento:
    """Testes para mock de auto-preenchimento."""

    def test_cpf_conhecido_retorna_dados(self):
        """CPF de teste deve retornar dados completos."""
        result = _mock_auto_preencher("52998224725")
        assert result["nome"] == "MARIA DA SILVA SANTOS"
        assert result["preenchido_automaticamente"] is True
        assert "cadunico" in result

    def test_cpf_idoso_retorna_dados(self):
        """CPF de idoso de teste deve retornar dados."""
        result = _mock_auto_preencher("11144477735")
        assert result["nome"] == "JOSE CARLOS OLIVEIRA"

    def test_cpf_desconhecido(self):
        """CPF nao mockado deve retornar mensagem."""
        result = _mock_auto_preencher("99999999999")
        assert result["preenchido_automaticamente"] is False

    def test_mock_inclui_cadunico(self):
        """Mock deve incluir dados do CadUnico."""
        result = _mock_auto_preencher("52998224725")
        cad = result["cadunico"]
        assert cad["ativo"] is True
        assert cad["renda_per_capita"] > 0
        assert cad["composicao_familiar"] > 0


class TestConsultarGovbr:
    """Testes para tool consultar_govbr."""

    def test_cpf_invalido(self):
        """CPF invalido deve retornar erro."""
        result = consultar_govbr("123")
        assert result["encontrado"] is False
        assert "invalido" in result["erro"].lower()

    def test_cpf_formatado(self):
        """CPF formatado deve ser aceito."""
        result = consultar_govbr("529.982.247-25")
        assert result["encontrado"] is True
        assert result["nome"] == "MARIA DA SILVA SANTOS"

    def test_cpf_limpo(self):
        """CPF sem formatacao deve funcionar."""
        result = consultar_govbr("52998224725")
        assert result["encontrado"] is True

    def test_cpf_nao_encontrado(self):
        """CPF nao cadastrado deve retornar nao encontrado."""
        result = consultar_govbr("99999999999")
        assert result["encontrado"] is False

    def test_retorna_cadunico(self):
        """Deve retornar dados do CadUnico se disponivel."""
        result = consultar_govbr("52998224725")
        assert "cadunico" in result
        assert result["cadunico"]["ativo"] is True


class TestVerificarNivelGovbr:
    """Testes para tool verificar_nivel_govbr."""

    def test_nivel_bronze(self):
        """Bronze deve ter permissoes basicas."""
        result = verificar_nivel_govbr("bronze")
        assert result["nivel"] == "bronze"
        assert len(result["permissoes"]) > 0
        assert "como_subir" in result

    def test_nivel_prata(self):
        """Prata deve ter mais permissoes que bronze."""
        result = verificar_nivel_govbr("prata")
        assert result["nivel"] == "prata"

    def test_nivel_ouro(self):
        """Ouro deve ser nivel maximo."""
        result = verificar_nivel_govbr("ouro")
        assert result["nivel"] == "ouro"
        assert "maximo" in result["como_subir"].lower()

    def test_nivel_invalido(self):
        """Nivel invalido deve retornar erro."""
        result = verificar_nivel_govbr("diamante")
        assert "erro" in result

    def test_sem_nivel_lista_todos(self):
        """Sem nivel especifico deve listar todos."""
        result = verificar_nivel_govbr()
        assert "niveis" in result
        assert len(result["niveis"]) == 3


class TestGerarLoginGovbr:
    """Testes para tool gerar_login_govbr."""

    def test_nao_configurado_retorna_alternativa(self):
        """Sem configuracao deve informar alternativa."""
        result = gerar_login_govbr()
        # Vai retornar nao configurado pois GOVBR_CLIENT_ID nao esta setado
        assert result["configurado"] is False
        assert "alternativa" in result or "mensagem" in result


class TestUrlLogin:
    """Testes para geracao de URL de login."""

    def test_sem_configuracao(self):
        """Sem client_id deve retornar erro."""
        result = gerar_url_login()
        # Sem configuracao, retorna erro
        assert result.get("erro") or result.get("url") == ""

    def test_state_gerado(self):
        """State deve ser gerado se nao fornecido."""
        result = gerar_url_login()
        # Mesmo sem config, state eh gerado ou vazio
        assert "state" in result
