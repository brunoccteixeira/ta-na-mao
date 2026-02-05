"""Tests for geocoding service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.geocoding_service import (
    geocode_address,
    _normalize_address,
    _is_valid_brazil_coords,
    _try_nominatim,
    _try_google,
    batch_geocode,
    GeocodingResult,
)


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_normalize_address_basic(self):
        """Test basic address normalization."""
        result = _normalize_address("R. das Flores, 123", "Sao Paulo", "SP")
        assert "Rua das Flores" in result
        assert "Sao Paulo" in result
        assert "SP" in result
        assert "Brasil" in result

    def test_normalize_address_av(self):
        """Test avenue abbreviation expansion."""
        result = _normalize_address("Av. Paulista, 1000", "Sao Paulo", "SP")
        assert "Avenida Paulista" in result

    def test_normalize_address_multiple_spaces(self):
        """Test multiple space normalization."""
        result = _normalize_address("Rua   Teste   123", "Cidade", "UF")
        assert "  " not in result

    def test_is_valid_brazil_coords_valid(self):
        """Test valid Brazil coordinates."""
        # Sao Paulo
        assert _is_valid_brazil_coords(-23.55, -46.63) is True
        # Rio de Janeiro
        assert _is_valid_brazil_coords(-22.90, -43.17) is True
        # Manaus
        assert _is_valid_brazil_coords(-3.10, -60.02) is True

    def test_is_valid_brazil_coords_invalid(self):
        """Test invalid coordinates (outside Brazil)."""
        # New York
        assert _is_valid_brazil_coords(40.71, -74.00) is False
        # Buenos Aires
        assert _is_valid_brazil_coords(-34.60, -58.38) is False
        # Pacific Ocean
        assert _is_valid_brazil_coords(0, -150) is False


class TestNominatimGeocoding:
    """Tests for Nominatim geocoding."""

    @pytest.mark.asyncio
    async def test_nominatim_success(self):
        """Test successful Nominatim geocoding."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "lat": "-23.5505",
                "lon": "-46.6333",
                "display_name": "Sao Paulo, SP, Brasil"
            }
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await _try_nominatim("Rua Augusta", "Sao Paulo", "SP")

            assert result is not None
            assert result.source == "nominatim"
            assert -24 < result.latitude < -23
            assert -47 < result.longitude < -46

    @pytest.mark.asyncio
    async def test_nominatim_no_results(self):
        """Test Nominatim with no results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await _try_nominatim("Endereco Inexistente", "Cidade Fake", "XX")

            assert result is None


class TestGoogleGeocoding:
    """Tests for Google Geocoding API."""

    @pytest.mark.asyncio
    async def test_google_no_api_key(self):
        """Test Google geocoding without API key."""
        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.GOOGLE_GEOCODING_KEY = ""

            result = await _try_google("Rua Augusta", "Sao Paulo", "SP")

            assert result is None

    @pytest.mark.asyncio
    async def test_google_success(self):
        """Test successful Google geocoding."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "geometry": {
                        "location": {"lat": -23.5505, "lng": -46.6333},
                        "location_type": "ROOFTOP"
                    },
                    "formatted_address": "Rua Augusta, Sao Paulo - SP, Brasil"
                }
            ]
        }

        with patch("app.services.geocoding_service.settings") as mock_settings:
            mock_settings.GOOGLE_GEOCODING_KEY = "test-key"

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_instance.get = AsyncMock(return_value=mock_response)
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_client.return_value = mock_instance

                result = await _try_google("Rua Augusta", "Sao Paulo", "SP")

                assert result is not None
                assert result.source == "google"
                assert result.confidence == 1.0  # ROOFTOP
                assert -24 < result.latitude < -23


class TestGeocodeAddress:
    """Tests for main geocode_address function."""

    @pytest.mark.asyncio
    async def test_geocode_nominatim_first(self):
        """Test that Nominatim is tried first."""
        nominatim_result = GeocodingResult(
            latitude=-23.55,
            longitude=-46.63,
            source="nominatim",
            confidence=0.7
        )

        with patch("app.services.geocoding_service._try_nominatim", return_value=nominatim_result):
            with patch("app.services.geocoding_service._try_google") as mock_google:
                lat, lon, source = await geocode_address(
                    "Rua Augusta", "Sao Paulo", "SP"
                )

                assert source == "nominatim"
                assert lat == -23.55
                assert lon == -46.63
                # Google should not be called if Nominatim succeeds
                mock_google.assert_not_called()

    @pytest.mark.asyncio
    async def test_geocode_google_fallback(self):
        """Test Google fallback when Nominatim fails."""
        google_result = GeocodingResult(
            latitude=-23.55,
            longitude=-46.63,
            source="google",
            confidence=1.0
        )

        with patch("app.services.geocoding_service._try_nominatim", return_value=None):
            with patch("app.services.geocoding_service._try_viacep_coords", return_value=None):
                with patch("app.services.geocoding_service._try_google", return_value=google_result):
                    lat, lon, source = await geocode_address(
                        "Rua Augusta", "Sao Paulo", "SP"
                    )

                    assert source == "google"
                    assert lat == -23.55

    @pytest.mark.asyncio
    async def test_geocode_all_fail(self):
        """Test when all geocoding strategies fail."""
        with patch("app.services.geocoding_service._try_nominatim", return_value=None):
            with patch("app.services.geocoding_service._try_viacep_coords", return_value=None):
                with patch("app.services.geocoding_service._try_google", return_value=None):
                    lat, lon, source = await geocode_address(
                        "Endereco Inexistente", "Cidade Fake", "XX"
                    )

                    assert lat is None
                    assert lon is None
                    assert source is None


class TestBatchGeocode:
    """Tests for batch geocoding."""

    @pytest.mark.asyncio
    async def test_batch_geocode_multiple(self):
        """Test batch geocoding multiple addresses."""
        addresses = [
            {"endereco": "Rua A", "cidade": "Sao Paulo", "uf": "SP"},
            {"endereco": "Rua B", "cidade": "Rio de Janeiro", "uf": "RJ"},
        ]

        async def mock_geocode(endereco, cidade, uf, cep=None):
            if cidade == "Sao Paulo":
                return (-23.55, -46.63, "nominatim")
            elif cidade == "Rio de Janeiro":
                return (-22.90, -43.17, "nominatim")
            return (None, None, None)

        with patch("app.services.geocoding_service.geocode_address", side_effect=mock_geocode):
            results = await batch_geocode(addresses, max_concurrent=2)

            assert len(results) == 2
            assert results[0]["latitude"] == -23.55
            assert results[1]["latitude"] == -22.90
            assert all(r.get("geocode_source") == "nominatim" for r in results)

    @pytest.mark.asyncio
    async def test_batch_geocode_empty(self):
        """Test batch geocoding with empty list."""
        results = await batch_geocode([])
        assert results == []
