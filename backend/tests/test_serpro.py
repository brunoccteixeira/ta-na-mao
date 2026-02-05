"""
Testes para integracao com SERPRO Consulta CPF.

Testa validacao de CPF, cache de token, e modo mock.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.services.serpro_service import (
    consultar_cpf,
    validar_cpf,
    validar_formato_cpf,
    formatar_cpf,
    is_serpro_configured,
    _limpar_cpf,
    _hash_cpf,
    _mock_consultar_cpf,
    _token_cache,
)


class TestHelpers:
    """Testes para funcoes auxiliares."""

    def test_limpar_cpf_com_formatacao(self):
        """Deve remover pontos e tracos do CPF."""
        assert _limpar_cpf("529.982.247-25") == "52998224725"

    def test_limpar_cpf_sem_formatacao(self):
        """CPF sem formatacao deve permanecer igual."""
        assert _limpar_cpf("52998224725") == "52998224725"

    def test_hash_cpf_comprimento(self):
        """Hash deve ter comprimento fixo."""
        hash_cpf = _hash_cpf("52998224725")
        assert len(hash_cpf) == 12

    def test_hash_cpf_deterministico(self):
        """Hash deve ser deterministico."""
        hash1 = _hash_cpf("52998224725")
        hash2 = _hash_cpf("52998224725")
        assert hash1 == hash2


class TestValidarFormatoCPF:
    """Testes para validacao local de formato CPF."""

    def test_cpf_valido(self):
        """CPF valido deve passar."""
        assert validar_formato_cpf("52998224725") is True

    def test_cpf_valido_formatado(self):
        """CPF formatado valido deve passar."""
        assert validar_formato_cpf("529.982.247-25") is True

    def test_cpf_muito_curto(self):
        """CPF com menos de 11 digitos deve falhar."""
        assert validar_formato_cpf("12345678") is False

    def test_cpf_muito_longo(self):
        """CPF com mais de 11 digitos deve falhar."""
        assert validar_formato_cpf("123456789012") is False

    def test_cpf_todos_iguais(self):
        """CPF com todos digitos iguais deve falhar."""
        assert validar_formato_cpf("11111111111") is False
        assert validar_formato_cpf("00000000000") is False
        assert validar_formato_cpf("99999999999") is False

    def test_cpf_digito_verificador_invalido(self):
        """CPF com digito verificador errado deve falhar."""
        # 52998224725 eh valido, 52998224726 nao eh
        assert validar_formato_cpf("52998224726") is False

    def test_cpf_segundo_digito_invalido(self):
        """CPF com segundo digito verificador errado deve falhar."""
        assert validar_formato_cpf("52998224715") is False


class TestFormatarCPF:
    """Testes para formatacao de CPF."""

    def test_formatar_cpf_limpo(self):
        """CPF limpo deve ser formatado."""
        assert formatar_cpf("52998224725") == "529.982.247-25"

    def test_formatar_cpf_ja_formatado(self):
        """CPF ja formatado deve permanecer."""
        # Vai limpar e reformatar
        assert formatar_cpf("529.982.247-25") == "529.982.247-25"

    def test_formatar_cpf_incompleto(self):
        """CPF incompleto deve retornar como esta."""
        assert formatar_cpf("123") == "123"


class TestMockConsultaCPF:
    """Testes para mock de consulta CPF."""

    def test_cpf_maria_valido(self):
        """CPF de Maria deve ser valido no mock."""
        result = _mock_consultar_cpf("52998224725")
        assert result["valido"] is True
        assert result["nome"] == "MARIA DA SILVA SANTOS"
        assert result["situacao"]["regular"] is True

    def test_cpf_jose_valido(self):
        """CPF de Jose deve ser valido no mock."""
        result = _mock_consultar_cpf("11144477735")
        assert result["valido"] is True
        assert result["nome"] == "JOSE CARLOS OLIVEIRA"

    def test_cpf_zeros_invalido(self):
        """CPF zerado deve ser invalido no mock."""
        result = _mock_consultar_cpf("00000000000")
        assert result["valido"] is False

    def test_cpf_desconhecido_invalido(self):
        """CPF nao mockado deve retornar invalido."""
        result = _mock_consultar_cpf("12345678900")
        assert result["valido"] is False
        assert "erro" in result

    def test_mock_indica_fonte(self):
        """Mock deve indicar que eh mock."""
        result = _mock_consultar_cpf("52998224725")
        assert "Mock" in result["fonte"]


class TestConsultaCPF:
    """Testes para consulta de CPF."""

    @pytest.mark.asyncio
    async def test_consulta_sem_serpro_usa_mock(self):
        """Sem SERPRO configurado deve usar mock."""
        with patch("app.services.serpro_service.is_serpro_configured", return_value=False):
            result = await consultar_cpf("52998224725")
            assert "Mock" in result.get("fonte", "")

    @pytest.mark.asyncio
    async def test_consulta_cpf_formatado(self):
        """Deve aceitar CPF formatado."""
        with patch("app.services.serpro_service.is_serpro_configured", return_value=False):
            result = await consultar_cpf("529.982.247-25")
            assert result["valido"] is True

    @pytest.mark.asyncio
    async def test_consulta_com_token_valido(self):
        """Com token valido deve fazer consulta."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "nome": "TESTE DA SILVA",
            "nascimento": "01/01/1990",
            "situacao": {"codigo": "0", "descricao": "Regular"},
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with patch("app.services.serpro_service.is_serpro_configured", return_value=True):
            with patch("app.services.serpro_service._obter_token", new_callable=AsyncMock, return_value="fake_token"):
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_client_class.return_value.__aenter__.return_value = mock_client
                    result = await consultar_cpf("52998224725")
                    assert result["valido"] is True
                    assert result["nome"] == "TESTE DA SILVA"


class TestValidarCPF:
    """Testes para validacao completa de CPF."""

    @pytest.mark.asyncio
    async def test_validar_cpf_sem_nome(self):
        """Validacao sem nome esperado."""
        with patch("app.services.serpro_service.is_serpro_configured", return_value=False):
            result = await validar_cpf("52998224725")
            assert result["valido"] is True
            assert result["nome_confere"] is None

    @pytest.mark.asyncio
    async def test_validar_cpf_nome_confere(self):
        """Nome informado deve conferir com cadastro."""
        mock_consulta = {
            "valido": True,
            "nome": "MARIA DA SILVA SANTOS",
            "nascimento": "15/03/1985",
            "situacao": {"codigo": "0", "regular": True},
        }
        with patch("app.services.serpro_service.consultar_cpf", return_value=mock_consulta):
            result = await validar_cpf("52998224725", "Maria da Silva")
            assert result["valido"] is True
            assert result["nome_confere"] is True

    @pytest.mark.asyncio
    async def test_validar_cpf_nome_nao_confere(self):
        """Nome diferente deve indicar que nao confere."""
        mock_consulta = {
            "valido": True,
            "nome": "MARIA DA SILVA SANTOS",
            "nascimento": "15/03/1985",
            "situacao": {"codigo": "0", "regular": True},
        }
        with patch("app.services.serpro_service.consultar_cpf", return_value=mock_consulta):
            result = await validar_cpf("52998224725", "Joao Carlos")
            assert result["valido"] is True
            assert result["nome_confere"] is False

    @pytest.mark.asyncio
    async def test_validar_cpf_invalido(self):
        """CPF invalido deve retornar resultado negativo."""
        mock_consulta = {
            "valido": False,
            "erro": "CPF nao encontrado",
        }
        with patch("app.services.serpro_service.consultar_cpf", return_value=mock_consulta):
            result = await validar_cpf("99999999999")
            assert result["valido"] is False


class TestTokenCache:
    """Testes para cache de token."""

    @pytest.mark.asyncio
    async def test_token_usa_cache(self):
        """Token valido em cache deve ser reutilizado."""
        from app.services import serpro_service

        # Simular token em cache
        serpro_service._token_cache = {
            "token": "cached_token",
            "expires_at": datetime.now() + timedelta(hours=1),
        }

        with patch("app.services.serpro_service._get_serpro_config", return_value={
            "consumer_key": "key",
            "consumer_secret": "secret",
            "enabled": True,
        }):
            from app.services.serpro_service import _obter_token

            token = await _obter_token()
            assert token == "cached_token"

        # Limpar cache apos teste
        serpro_service._token_cache = {}

    @pytest.mark.asyncio
    async def test_token_expirado_renova(self):
        """Token expirado deve ser renovado."""
        from app.services import serpro_service

        # Simular token expirado
        serpro_service._token_cache = {
            "token": "expired_token",
            "expires_at": datetime.now() - timedelta(hours=1),
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "expires_in": 3600,
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("app.services.serpro_service._get_serpro_config", return_value={
            "consumer_key": "key",
            "consumer_secret": "secret",
            "enabled": True,
        }):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client_class.return_value.__aenter__.return_value = mock_client
                from app.services.serpro_service import _obter_token

                token = await _obter_token()
                assert token == "new_token"

        # Limpar cache apos teste
        serpro_service._token_cache = {}


class TestIntegracao:
    """Testes de integracao (end-to-end com mocks)."""

    @pytest.mark.asyncio
    async def test_fluxo_completo_cpf_valido(self):
        """Fluxo completo de validacao de CPF valido."""
        with patch("app.services.serpro_service.is_serpro_configured", return_value=False):
            # Consultar CPF
            consulta = await consultar_cpf("52998224725")
            assert consulta["valido"] is True

            # Validar com nome
            validacao = await validar_cpf("52998224725", "Maria")
            assert validacao["valido"] is True

    @pytest.mark.asyncio
    async def test_fluxo_completo_cpf_invalido(self):
        """Fluxo completo para CPF invalido."""
        with patch("app.services.serpro_service.is_serpro_configured", return_value=False):
            # Consultar CPF invalido
            consulta = await consultar_cpf("00000000000")
            assert consulta["valido"] is False

            # Validar CPF invalido
            validacao = await validar_cpf("00000000000")
            assert validacao["valido"] is False
