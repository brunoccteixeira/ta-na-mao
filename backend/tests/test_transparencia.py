"""
Testes para integracao com Portal da Transparencia.

Testa consulta de beneficios (Bolsa Familia, BPC, Auxilio Gas)
usando dados de mock quando API nao esta configurada.
"""

import pytest
from unittest.mock import patch, AsyncMock

from app.services.transparencia_service import (
    consultar_bolsa_familia,
    consultar_bpc,
    consultar_auxilio_gas,
    consultar_seguro_defeso,
    consultar_todos_beneficios,
    consultar_beneficios_ou_mock,
    is_transparencia_configured,
    _limpar_cpf,
    _hash_cpf,
    _mock_consultar_beneficios,
)


class TestHelpers:
    """Testes para funcoes auxiliares."""

    def test_limpar_cpf_com_formatacao(self):
        """Deve remover pontos e tracos do CPF."""
        assert _limpar_cpf("529.982.247-25") == "52998224725"

    def test_limpar_cpf_sem_formatacao(self):
        """CPF sem formatacao deve permanecer igual."""
        assert _limpar_cpf("52998224725") == "52998224725"

    def test_limpar_cpf_com_espacos(self):
        """Deve remover espacos do CPF."""
        assert _limpar_cpf("529 982 247 25") == "52998224725"

    def test_hash_cpf(self):
        """Hash deve ter comprimento fixo e ser deterministico."""
        hash1 = _hash_cpf("52998224725")
        hash2 = _hash_cpf("52998224725")
        assert len(hash1) == 12
        assert hash1 == hash2

    def test_hash_cpf_diferente(self):
        """CPFs diferentes devem gerar hashes diferentes."""
        hash1 = _hash_cpf("52998224725")
        hash2 = _hash_cpf("11144477735")
        assert hash1 != hash2


class TestMockBeneficios:
    """Testes para mock de consulta de beneficios."""

    def test_cpf_maria_tem_bolsa_familia(self):
        """Maria deve ter Bolsa Familia no mock."""
        result = _mock_consultar_beneficios("52998224725")
        assert result["beneficiario_algum_programa"] is True
        assert result["quantidade_beneficios"] == 2

    def test_cpf_maria_tem_auxilio_gas(self):
        """Maria deve ter Auxilio Gas no mock."""
        result = _mock_consultar_beneficios("52998224725")
        programas = [b["programa"] for b in result["beneficios_ativos"]]
        assert "Auxilio Gas" in programas

    def test_cpf_jose_tem_bpc(self):
        """Jose (idoso) deve ter BPC no mock."""
        result = _mock_consultar_beneficios("11144477735")
        assert result["beneficiario_algum_programa"] is True
        programas = [b["programa"] for b in result["beneficios_ativos"]]
        assert "BPC - Beneficio de Prestacao Continuada" in programas

    def test_cpf_jose_valor_bpc(self):
        """BPC do Jose deve ser 1 salario minimo."""
        result = _mock_consultar_beneficios("11144477735")
        assert result["total_mensal_estimado"] == 1412.0

    def test_cpf_desconhecido_nao_eh_beneficiario(self):
        """CPF desconhecido nao deve ter beneficios."""
        result = _mock_consultar_beneficios("99999999999")
        assert result["beneficiario_algum_programa"] is False
        assert result["quantidade_beneficios"] == 0

    def test_mock_indica_fonte(self):
        """Mock deve indicar que eh mock."""
        result = _mock_consultar_beneficios("52998224725")
        assert "Mock" in result["fonte"]


class TestConsultaBeneficios:
    """Testes para consulta de beneficios (usa mock quando API nao configurada)."""

    @pytest.mark.asyncio
    async def test_consultar_beneficios_ou_mock_sem_api(self):
        """Sem API configurada deve usar mock."""
        with patch("app.services.transparencia_service.is_transparencia_configured", return_value=False):
            result = await consultar_beneficios_ou_mock("52998224725")
            assert "Mock" in result["fonte"]
            assert result["beneficiario_algum_programa"] is True

    @pytest.mark.asyncio
    async def test_consultar_beneficios_cpf_formatado(self):
        """Deve aceitar CPF formatado."""
        with patch("app.services.transparencia_service.is_transparencia_configured", return_value=False):
            result = await consultar_beneficios_ou_mock("529.982.247-25")
            assert result["cpf_consultado"] is True


class TestConsultaBolsaFamilia:
    """Testes para consulta especifica de Bolsa Familia."""

    @pytest.mark.asyncio
    async def test_bolsa_familia_sem_api(self):
        """Sem API deve retornar erro amigavel."""
        with patch("app.services.transparencia_service._get_api_key", return_value=""):
            result = await consultar_bolsa_familia("52998224725")
            # Sem API key retorna erro
            assert result["programa"] == "Bolsa Familia / Auxilio Brasil"

    @pytest.mark.asyncio
    async def test_bolsa_familia_com_mock_response(self):
        """Com resposta mockada deve processar parcelas."""
        mock_response = {
            "success": True,
            "data": [
                {
                    "dataReferencia": "2025-01",
                    "valor": 600.0,
                    "municipio": {"nomeIBGE": "SAO PAULO"},
                    "uf": {"sigla": "SP"},
                },
                {
                    "dataReferencia": "2024-12",
                    "valor": 600.0,
                    "municipio": {"nomeIBGE": "SAO PAULO"},
                    "uf": {"sigla": "SP"},
                },
            ],
        }
        with patch("app.services.transparencia_service._fazer_requisicao", return_value=mock_response):
            result = await consultar_bolsa_familia("52998224725")
            assert result["beneficiario"] is True
            assert result["valor_total"] == 1200.0
            assert len(result["parcelas"]) == 2


class TestConsultaBPC:
    """Testes para consulta de BPC."""

    @pytest.mark.asyncio
    async def test_bpc_resposta_vazia(self):
        """Resposta vazia indica nao beneficiario."""
        mock_response = {"success": True, "data": []}
        with patch("app.services.transparencia_service._fazer_requisicao", return_value=mock_response):
            result = await consultar_bpc("99999999999")
            assert result["beneficiario"] is False
            assert "mensagem" in result

    @pytest.mark.asyncio
    async def test_bpc_com_dados(self):
        """BPC com dados deve retornar valor mensal."""
        mock_response = {
            "success": True,
            "data": [
                {
                    "dataReferencia": "2025-01",
                    "valor": 1412.0,
                    "tipoBeneficio": "BPC Idoso",
                    "municipio": {"nomeIBGE": "RECIFE"},
                    "uf": {"sigla": "PE"},
                },
            ],
        }
        with patch("app.services.transparencia_service._fazer_requisicao", return_value=mock_response):
            result = await consultar_bpc("11144477735")
            assert result["beneficiario"] is True
            assert result["tipo"] == "BPC Idoso"
            assert result["valor_mensal"] == 1412.0


class TestConsultaAuxilioGas:
    """Testes para consulta de Auxilio Gas."""

    @pytest.mark.asyncio
    async def test_auxilio_gas_filtra_programa(self):
        """Deve filtrar apenas Auxilio Gas do endpoint de auxilio emergencial."""
        mock_response = {
            "success": True,
            "data": [
                {"programa": "Auxilio Gas", "dataReferencia": "2025-01", "valor": 104.0, "municipio": {}, "uf": {}},
                {"programa": "Outro Auxilio", "dataReferencia": "2025-01", "valor": 300.0, "municipio": {}, "uf": {}},
            ],
        }
        with patch("app.services.transparencia_service._fazer_requisicao", return_value=mock_response):
            result = await consultar_auxilio_gas("52998224725")
            assert result["beneficiario"] is True
            assert result["valor_total"] == 104.0  # Apenas Gas


class TestConsultaTodosBeneficios:
    """Testes para consulta consolidada de todos beneficios."""

    @pytest.mark.asyncio
    async def test_consulta_paralela(self):
        """Todas consultas devem rodar em paralelo."""
        with patch("app.services.transparencia_service._fazer_requisicao", return_value={"success": True, "data": []}):
            result = await consultar_todos_beneficios("52998224725")
            assert "detalhes" in result
            assert "bolsa_familia" in result["detalhes"]
            assert "bpc" in result["detalhes"]
            assert "auxilio_gas" in result["detalhes"]
            assert "seguro_defeso" in result["detalhes"]

    @pytest.mark.asyncio
    async def test_soma_total_mensal(self):
        """Total mensal deve somar todos beneficios."""
        # Mock que retorna Bolsa Familia e BPC
        async def mock_requisicao(endpoint: str, cpf: str, pagina: int = 1):
            if "bolsa-familia" in endpoint:
                return {
                    "success": True,
                    "data": [{"dataReferencia": "2025-01", "valor": 600.0, "municipio": {}, "uf": {}}],
                }
            elif "bpc" in endpoint:
                return {
                    "success": True,
                    "data": [
                        {"dataReferencia": "2025-01", "valor": 1412.0, "tipoBeneficio": "BPC", "municipio": {}, "uf": {}}
                    ],
                }
            return {"success": True, "data": []}

        with patch("app.services.transparencia_service._fazer_requisicao", side_effect=mock_requisicao):
            result = await consultar_todos_beneficios("52998224725")
            # Bolsa Familia (600) + BPC (1412) = 2012
            assert result["total_mensal_estimado"] == 2012.0
            assert result["quantidade_beneficios"] == 2


class TestRateLimiting:
    """Testes para tratamento de rate limit."""

    @pytest.mark.asyncio
    async def test_rate_limit_retorna_erro(self):
        """Rate limit deve retornar erro amigavel."""
        mock_response = {
            "success": False,
            "error": "rate_limit",
            "message": "Limite de requisicoes excedido. Tente novamente em alguns minutos.",
        }
        with patch("app.services.transparencia_service._fazer_requisicao", return_value=mock_response):
            result = await consultar_bolsa_familia("52998224725")
            assert result["beneficiario"] is False
            assert "erro" in result or "Limite" in str(result)
