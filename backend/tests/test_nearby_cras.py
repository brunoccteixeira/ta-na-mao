"""Tests for CRAS search functions.

Tests the CRAS (Centro de Referencia de Assistencia Social) search functions,
which support both coordinate-based (GPS) and CEP-based searches.

These tests use direct module imports to avoid triggering heavy agent initialization.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import importlib.util
import os
import sys

# =============================================================================
# Direct Module Import
# =============================================================================
# Import buscar_cras.py directly without going through app.agent.tools.__init__.py
# which imports many heavy modules that can cause timeouts or missing dependencies.

_MODULE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "app", "agent", "tools", "buscar_cras.py"
)

spec = importlib.util.spec_from_file_location("buscar_cras_direct", _MODULE_PATH)
buscar_cras_module = importlib.util.module_from_spec(spec)
sys.modules["buscar_cras_direct"] = buscar_cras_module
spec.loader.exec_module(buscar_cras_module)


# =============================================================================
# Unit Tests for buscar_cras function
# =============================================================================
class TestBuscarCrasFunction:
    """Tests for the buscar_cras tool function."""

    def test_buscar_cras_no_params(self):
        """Test error when neither CEP nor IBGE code provided."""
        result = buscar_cras_module.buscar_cras()

        assert result["erro"] is True
        assert result["encontrados"] == 0
        assert "CEP ou codigo IBGE" in result["mensagem"]

    def test_buscar_cras_with_ibge_from_db(self):
        """Test CRAS search by IBGE code with database results."""
        mock_cras_data = [
            {
                "nome": "CRAS Test",
                "endereco": "Rua Test, 123",
                "cidade": "Sao Paulo",
                "telefone": "(11) 1234-5678",
                "horario": "Seg-Sex 8h-17h",
                "servicos": ["CadUnico"],
                "latitude": -23.55,
                "longitude": -46.63,
            }
        ]

        with patch.object(
            buscar_cras_module,
            "_carregar_cras_do_banco",
            return_value=mock_cras_data,
        ):
            result = buscar_cras_module.buscar_cras(ibge_code="3550308")

            assert result["erro"] is False
            assert result["encontrados"] == 1
            assert result["cras"][0]["nome"] == "CRAS Test"
            assert "texto_formatado" in result

    def test_buscar_cras_with_cep(self):
        """Test CRAS search by CEP."""
        mock_cras_data = [
            {
                "nome": "CRAS Vila Mariana",
                "endereco": "Rua Domingos de Morais, 1000",
                "cidade": "Sao Paulo",
                "telefone": "(11) 5573-1515",
                "horario": "Seg-Sex 8h-17h",
                "servicos": ["CadUnico", "BolsaFamilia"],
                "latitude": -23.5889,
                "longitude": -46.6388,
            }
        ]

        with patch.object(
            buscar_cras_module,
            "_obter_ibge_por_cep",
            return_value="3550308",
        ):
            with patch.object(
                buscar_cras_module,
                "_carregar_cras_do_banco",
                return_value=mock_cras_data,
            ):
                result = buscar_cras_module.buscar_cras(cep="04010100")

                assert result["erro"] is False
                assert result["encontrados"] == 1
                assert result["cras"][0]["nome"] == "CRAS Vila Mariana"

    def test_buscar_cras_invalid_cep(self):
        """Test with CEP that doesn't resolve to IBGE."""
        with patch.object(
            buscar_cras_module,
            "_obter_ibge_por_cep",
            return_value=None,
        ):
            result = buscar_cras_module.buscar_cras(cep="00000000")

            assert result["erro"] is True
            assert "Nao foi possivel identificar" in result["mensagem"]

    def test_buscar_cras_fallback_json(self):
        """Test fallback to JSON when database is empty."""
        mock_json_data = {
            "cras": [
                {
                    "nome": "CRAS JSON",
                    "endereco": "Rua JSON, 300",
                    "ibge_code": "3550308",
                    "cidade": "Sao Paulo",
                    "telefone": "(11) 3333-3333",
                    "horario": "Seg-Sex 8h-17h",
                }
            ]
        }

        # Database returns empty, fallback JSON has data
        with patch.object(
            buscar_cras_module,
            "_carregar_cras_do_banco",
            return_value=[],
        ):
            with patch.object(
                buscar_cras_module,
                "_carregar_cras",
                return_value=mock_json_data,
            ):
                result = buscar_cras_module.buscar_cras(ibge_code="3550308")

                assert result["erro"] is False
                assert result["encontrados"] == 1
                assert result["cras"][0]["nome"] == "CRAS JSON"

    def test_buscar_cras_no_data_anywhere(self):
        """Test when no CRAS data found in DB or JSON."""
        with patch.object(
            buscar_cras_module,
            "_carregar_cras_do_banco",
            return_value=[],
        ):
            with patch.object(
                buscar_cras_module,
                "_carregar_cras",
                return_value={"cras": []},
            ):
                result = buscar_cras_module.buscar_cras(ibge_code="9999999")

                assert result["erro"] is False
                assert result["encontrados"] == 0
                # Should mention Disque Social 121
                assert "121" in result["texto_formatado"]

    def test_buscar_cras_limite(self):
        """Test that limite parameter limits results."""
        many_cras = [
            {
                "nome": f"CRAS {i}",
                "endereco": f"Rua {i}",
                "cidade": "Sao Paulo",
                "telefone": "(11) 1111-1111",
                "horario": "Seg-Sex 8h-17h",
                "servicos": [],
            }
            for i in range(10)
        ]

        with patch.object(
            buscar_cras_module,
            "_carregar_cras_do_banco",
            return_value=many_cras,
        ):
            result = buscar_cras_module.buscar_cras(ibge_code="3550308", limite=3)

            assert result["encontrados"] == 3
            assert len(result["cras"]) == 3


# =============================================================================
# Tests for coordinate-based search
# =============================================================================
# Note: These tests require the full app context for relative imports to work.
# They are skipped when running in isolation (without conftest loading full app).
class TestBuscarCrasPorCoordenadas:
    """Tests for coordinate-based CRAS search."""

    @pytest.mark.skip(reason="Requires full app for relative imports (.google_places)")
    @pytest.mark.asyncio
    async def test_buscar_por_coordenadas_success(self):
        """Test successful coordinate search."""
        mock_google_result = {
            "sucesso": True,
            "cras": [
                {
                    "nome": "CRAS Google",
                    "endereco": "Rua Google, 1",
                    "distancia": "1.2 km",
                    "distancia_metros": 1200,
                    "aberto_agora": True,
                    "links": {"direcoes": "https://maps.google.com/..."},
                }
            ],
            "coordenadas_busca": {"lat": -23.55, "lng": -46.63},
        }

        # Patch the import inside the function
        with patch(
            "app.agent.tools.google_places.buscar_cras_proximos",
            new_callable=AsyncMock,
            return_value=mock_google_result,
        ):
            result = await buscar_cras_module.buscar_cras_por_coordenadas(
                latitude=-23.55,
                longitude=-46.63,
                raio_metros=5000,
                limite=3,
            )

            assert result["erro"] is False
            assert result["encontrados"] == 1
            assert result["cras"][0]["nome"] == "CRAS Google"
            assert "texto_formatado" in result

    @pytest.mark.skip(reason="Requires full app for relative imports (.google_places)")
    @pytest.mark.asyncio
    async def test_buscar_por_coordenadas_no_results(self):
        """Test when no CRAS found by coordinates."""
        mock_empty = {"sucesso": True, "cras": []}

        with patch(
            "app.agent.tools.google_places.buscar_cras_proximos",
            new_callable=AsyncMock,
            return_value=mock_empty,
        ):
            result = await buscar_cras_module.buscar_cras_por_coordenadas(
                latitude=-23.55, longitude=-46.63
            )

            assert result["erro"] is False
            assert result["encontrados"] == 0
            # Should mention Disque Social 121
            assert "121" in result["texto_formatado"]

    @pytest.mark.skip(reason="Requires full app for relative imports (.google_places)")
    @pytest.mark.asyncio
    async def test_buscar_por_coordenadas_api_error(self):
        """Test handling Google Places API error."""
        with patch(
            "app.agent.tools.google_places.buscar_cras_proximos",
            new_callable=AsyncMock,
            side_effect=Exception("API Error"),
        ):
            result = await buscar_cras_module.buscar_cras_por_coordenadas(
                latitude=-23.55, longitude=-46.63
            )

            assert result["erro"] is True
            assert result["encontrados"] == 0
            # Should mention Disque Social 121
            assert "121" in result["texto_formatado"]


# =============================================================================
# Tests for ViaCEP integration
# =============================================================================
class TestViaCepIntegration:
    """Tests for ViaCEP integration."""

    def test_obter_ibge_por_cep_valid(self):
        """Test getting IBGE code from valid CEP."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cep": "04010-100",
            "localidade": "São Paulo",
            "ibge": "3550308",
        }

        with patch("httpx.get", return_value=mock_response):
            result = buscar_cras_module._obter_ibge_por_cep("04010-100")

            assert result == "3550308"

    def test_obter_ibge_por_cep_invalid(self):
        """Test with invalid CEP."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"erro": True}

        with patch("httpx.get", return_value=mock_response):
            result = buscar_cras_module._obter_ibge_por_cep("00000000")

            assert result is None

    def test_obter_ibge_por_cep_timeout(self):
        """Test handling ViaCEP timeout."""
        import httpx

        with patch("httpx.get", side_effect=httpx.TimeoutException("timeout")):
            result = buscar_cras_module._obter_ibge_por_cep("04010100")

            assert result is None

    def test_obter_ibge_por_cep_malformed(self):
        """Test with malformed CEP."""
        result = buscar_cras_module._obter_ibge_por_cep("123")  # Too short

        assert result is None


# =============================================================================
# Tests for database integration
# =============================================================================
class TestDatabaseIntegration:
    """Tests for database CRAS lookup."""

    def test_carregar_cras_do_banco_success(self):
        """Test successful database query."""
        # Create mock CRAS with municipality
        mock_municipality = MagicMock()
        mock_municipality.name = "Sao Paulo"

        mock_cras = MagicMock()
        mock_cras.nome = "CRAS DB Test"
        mock_cras.endereco = "Rua Test, 123"
        mock_cras.bairro = "Centro"
        mock_cras.telefone = "(11) 1234-5678"
        mock_cras.horario_funcionamento = "Seg-Sex 8h-17h"
        mock_cras.servicos = ["CadUnico", "BolsaFamilia"]
        mock_cras.latitude = -23.55
        mock_cras.longitude = -46.63
        mock_cras.ibge_code = "3550308"
        mock_cras.municipality = mock_municipality

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_cras]

        # Patch where it's imported inside the function
        with patch("app.database.SessionLocal", return_value=mock_db):
            result = buscar_cras_module._carregar_cras_do_banco("3550308")

            assert len(result) == 1
            assert result[0]["nome"] == "CRAS DB Test"
            assert result[0]["cidade"] == "Sao Paulo"
            mock_db.close.assert_called_once()

    def test_carregar_cras_do_banco_empty(self):
        """Test when database has no results."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        with patch("app.database.SessionLocal", return_value=mock_db):
            result = buscar_cras_module._carregar_cras_do_banco("9999999")

            assert result == []

    def test_carregar_cras_do_banco_error(self):
        """Test handling database errors gracefully."""
        with patch("app.database.SessionLocal", side_effect=Exception("DB Error")):
            result = buscar_cras_module._carregar_cras_do_banco("3550308")

            # Should return empty list on error, not raise
            assert result == []


# =============================================================================
# Tests for fallback JSON loading
# =============================================================================
class TestFallbackLoading:
    """Tests for fallback JSON loading."""

    def test_carregar_cras_from_json(self):
        """Test loading CRAS data from JSON fallback."""
        # Reset cache first
        buscar_cras_module._CRAS_CACHE = None

        result = buscar_cras_module._carregar_cras()

        # Should have loaded data from cras_exemplo.json
        assert "cras" in result
        # Should have at least some CRAS entries
        if result["cras"]:  # Only if file exists
            assert len(result["cras"]) > 0
            first = result["cras"][0]
            assert "nome" in first
            assert "ibge_code" in first


# =============================================================================
# Integration test (uses real DB if available)
# =============================================================================
class TestRealDatabaseQuery:
    """Integration tests with real database (if available)."""

    @pytest.mark.skip(reason="Integration test - run manually with USE_POSTGRES_TESTS=1")
    def test_query_real_db_sao_paulo(self):
        """Test querying real CRAS data for Sao Paulo."""
        result = buscar_cras_module.buscar_cras(ibge_code="3550308")

        # Should find CRAS in Sao Paulo
        assert result["encontrados"] > 0
        assert len(result["cras"]) > 0
        # CRAS names should contain "CRAS"
        assert any("CRAS" in c["nome"] for c in result["cras"])
