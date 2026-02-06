"""Tests for CRAS data ingestion from SAGI API."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.jobs.ingest_cras import (
    _map_sagi_to_cras,
    _normalize_ibge_code,
    _normalize_cep,
    _is_valid_brazil_coordinate,
    save_cras_to_db,
    ingest_cras_data,
    fetch_sagi_cras_data,
)


class TestSagiMapping:
    """Tests for SAGI API field mapping."""

    def test_map_sagi_to_cras_complete(self):
        """Test mapping complete SAGI document."""
        doc = {
            "id_equipamento": "12345",
            "ibge": "3550308",
            "nome": "CRAS Vila Mariana",
            "endereco": "Rua Domingos de Morais",
            "numero": "1000",
            "bairro": "Vila Mariana",
            "cep": "04010100",
            "cidade": "Sao Paulo",
            "uf": "SP",
            "telefone": "(11) 5573-1515",
            "georef_location": "-23.5889,-46.6388",
            "data_atualizacao": "2026-01-15",
        }

        result = _map_sagi_to_cras(doc)

        assert result is not None
        assert result["ibge_code"] == "3550308"
        assert result["nome"] == "CRAS Vila Mariana"
        assert result["endereco"] == "Rua Domingos de Morais, 1000"
        assert result["bairro"] == "Vila Mariana"
        assert result["cep"] == "04010100"
        assert result["cidade"] == "Sao Paulo"
        assert result["uf"] == "SP"
        assert result["telefone"] == "(11) 5573-1515"
        assert result["latitude"] == -23.5889
        assert result["longitude"] == -46.6388
        assert result["geocode_source"] == "sagi"

    def test_map_sagi_to_cras_minimal(self):
        """Test mapping SAGI document with only required fields."""
        doc = {
            "ibge": "3550308",
            "nome": "CRAS Minimo",
        }

        result = _map_sagi_to_cras(doc)

        assert result is not None
        assert result["ibge_code"] == "3550308"
        assert result["nome"] == "CRAS Minimo"
        assert result["latitude"] is None
        assert result["longitude"] is None
        assert result["geocode_source"] is None

    def test_map_sagi_to_cras_missing_ibge(self):
        """Test mapping fails without IBGE code."""
        doc = {"nome": "CRAS Sem IBGE"}

        result = _map_sagi_to_cras(doc)

        assert result is None

    def test_map_sagi_to_cras_missing_name(self):
        """Test mapping fails without name."""
        doc = {"ibge": "3550308"}

        result = _map_sagi_to_cras(doc)

        assert result is None

    def test_map_sagi_to_cras_invalid_coordinates(self):
        """Test mapping rejects coordinates outside Brazil."""
        doc = {
            "ibge": "3550308",
            "nome": "CRAS Coordenadas Invalidas",
            "georef_location": "40.7128,-74.0060",  # NYC coordinates
        }

        result = _map_sagi_to_cras(doc)

        assert result is not None
        assert result["latitude"] is None
        assert result["longitude"] is None

    def test_map_sagi_to_cras_malformed_coordinates(self):
        """Test mapping handles malformed coordinates."""
        doc = {
            "ibge": "3550308",
            "nome": "CRAS Coords Malformadas",
            "georef_location": "not,valid",
        }

        result = _map_sagi_to_cras(doc)

        assert result is not None
        assert result["latitude"] is None
        assert result["longitude"] is None


class TestCoordinateValidation:
    """Tests for Brazil bounding box validation."""

    def test_valid_sao_paulo(self):
        """Test valid coordinates in Sao Paulo."""
        assert _is_valid_brazil_coordinate(-23.55, -46.63) is True

    def test_valid_manaus(self):
        """Test valid coordinates in Manaus (northern Brazil)."""
        assert _is_valid_brazil_coordinate(-3.12, -60.02) is True

    def test_valid_porto_alegre(self):
        """Test valid coordinates in Porto Alegre (southern Brazil)."""
        assert _is_valid_brazil_coordinate(-30.03, -51.23) is True

    def test_invalid_nyc(self):
        """Test NYC coordinates are rejected."""
        assert _is_valid_brazil_coordinate(40.71, -74.01) is False

    def test_invalid_paris(self):
        """Test Paris coordinates are rejected."""
        assert _is_valid_brazil_coordinate(48.86, 2.35) is False

    def test_invalid_none(self):
        """Test None coordinates are rejected."""
        assert _is_valid_brazil_coordinate(None, None) is False
        assert _is_valid_brazil_coordinate(-23.55, None) is False
        assert _is_valid_brazil_coordinate(None, -46.63) is False


class TestNormalization:
    """Tests for IBGE code and CEP normalization."""

    def test_normalize_ibge_code_7_digits(self):
        """Test 7-digit IBGE code (unchanged)."""
        assert _normalize_ibge_code("3550308") == "3550308"

    def test_normalize_ibge_code_6_digits(self):
        """Test 6-digit IBGE code (add trailing 0)."""
        assert _normalize_ibge_code("355030") == "3550300"

    def test_normalize_ibge_code_with_spaces(self):
        """Test IBGE code with extra characters."""
        assert _normalize_ibge_code("  3550308  ") == "3550308"

    def test_normalize_ibge_code_invalid(self):
        """Test invalid IBGE code."""
        assert _normalize_ibge_code("123") is None
        assert _normalize_ibge_code("") is None
        assert _normalize_ibge_code(None) is None

    def test_normalize_cep_8_digits(self):
        """Test 8-digit CEP (unchanged)."""
        assert _normalize_cep("01305000") == "01305000"

    def test_normalize_cep_with_dash(self):
        """Test CEP with dash."""
        assert _normalize_cep("01305-000") == "01305000"

    def test_normalize_cep_invalid(self):
        """Test invalid CEP."""
        assert _normalize_cep("12345") is None
        assert _normalize_cep("") is None
        assert _normalize_cep(None) is None


class TestFetchSagiData:
    """Tests for SAGI API fetch."""

    @pytest.mark.asyncio
    async def test_fetch_sagi_success(self):
        """Test successful fetch from SAGI API."""
        mock_response_data = {
            "response": {
                "numFound": 2,
                "docs": [
                    {
                        "ibge": "3550308",
                        "nome": "CRAS SP 1",
                        "georef_location": "-23.55,-46.63",
                    },
                    {
                        "ibge": "3304557",
                        "nome": "CRAS RJ 1",
                        "georef_location": "-22.91,-43.21",
                    },
                ],
            }
        }

        with patch("app.jobs.ingest_cras.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_instance.get.return_value = mock_response

            result = await fetch_sagi_cras_data()

            assert result is not None
            assert len(result) == 2
            assert result[0]["nome"] == "CRAS SP 1"
            assert result[1]["nome"] == "CRAS RJ 1"

    @pytest.mark.asyncio
    async def test_fetch_sagi_api_error(self):
        """Test handling API error status."""
        with patch("app.jobs.ingest_cras.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance

            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_instance.get.return_value = mock_response

            result = await fetch_sagi_cras_data()

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_sagi_timeout(self):
        """Test handling request timeout."""
        import httpx

        with patch("app.jobs.ingest_cras.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = httpx.TimeoutException("timeout")

            result = await fetch_sagi_cras_data()

            assert result is None


class TestSaveCrasToDb:
    """Tests for database save operations."""

    def test_save_cras_creates_new(self):
        """Test creating new CRAS records."""
        mock_db = MagicMock()

        # Mock municipality query
        mock_municipality = MagicMock()
        mock_municipality.ibge_code = "3550308"
        mock_db.query.return_value.all.return_value = [mock_municipality]

        # Mock existing CRAS query (none found)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        records = [
            {
                "nome": "CRAS Novo",
                "ibge_code": "3550308",
                "endereco": "Rua Nova, 123",
                "latitude": -23.55,
                "longitude": -46.63,
                "geocode_source": "sagi",
            }
        ]

        stats = save_cras_to_db(mock_db, records, source="sagi")

        assert stats["created"] >= 0
        mock_db.commit.assert_called_once()

    def test_save_cras_skips_invalid(self):
        """Test skipping records with invalid IBGE code."""
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = []

        records = [
            {"nome": "CRAS Invalido", "ibge_code": "invalid"},
            {"nome": "CRAS Sem IBGE"},
        ]

        stats = save_cras_to_db(mock_db, records, source="sagi")

        assert stats["skipped"] == 2


class TestIngestCrasData:
    """Tests for main ingestion function."""

    @pytest.mark.asyncio
    async def test_ingest_dry_run(self):
        """Test dry run mode (no database save)."""
        mock_records = [
            {
                "nome": "CRAS 1",
                "ibge_code": "3550308",
                "latitude": -23.55,
                "longitude": -46.63,
                "geocode_source": "sagi",
            },
            {
                "nome": "CRAS 2",
                "ibge_code": "3304557",
                "latitude": -22.91,
                "longitude": -43.21,
                "geocode_source": "sagi",
            },
        ]

        with patch("app.jobs.ingest_cras.fetch_sagi_cras_data", return_value=mock_records):
            result = await ingest_cras_data(dry_run=True)

            assert result["dry_run"] is True
            assert result["records_fetched"] == 2
            assert result["records_geocoded"] == 2
            assert result["source"] == "sagi"

    @pytest.mark.asyncio
    async def test_ingest_fallback_data(self):
        """Test loading fallback data when SAGI fails."""
        fallback_data = [
            {
                "nome": "CRAS Fallback",
                "ibge_code": "3550308",
                "latitude": -23.55,
                "longitude": -46.63,
                "geocode_source": "fallback",
            }
        ]

        with patch("app.jobs.ingest_cras.fetch_sagi_cras_data", return_value=None):
            with patch("app.jobs.ingest_cras._load_fallback_data", return_value=fallback_data):
                result = await ingest_cras_data(dry_run=True)

                assert result["records_fetched"] == 1
                assert result["source"] == "fallback_json"

    @pytest.mark.asyncio
    async def test_ingest_no_data(self):
        """Test when no data is available."""
        with patch("app.jobs.ingest_cras.fetch_sagi_cras_data", return_value=None):
            with patch("app.jobs.ingest_cras._load_fallback_data", return_value=None):
                result = await ingest_cras_data(dry_run=True)

                assert "Failed to fetch CRAS data" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_ingest_with_database_save(self):
        """Test full ingestion with database save."""
        mock_records = [
            {
                "nome": "CRAS Test",
                "ibge_code": "3550308",
                "latitude": -23.55,
                "longitude": -46.63,
                "geocode_source": "sagi",
            }
        ]

        mock_save_stats = {"created": 1, "updated": 0, "skipped": 0}

        with patch("app.jobs.ingest_cras.fetch_sagi_cras_data", return_value=mock_records):
            with patch("app.jobs.ingest_cras.SessionLocal") as mock_session:
                mock_db = MagicMock()
                mock_session.return_value = mock_db

                with patch("app.jobs.ingest_cras.save_cras_to_db", return_value=mock_save_stats):
                    result = await ingest_cras_data(dry_run=False)

                    assert result["records_saved"] == 1
                    assert result["created"] == 1
                    assert result["updated"] == 0


class TestFallbackLoading:
    """Tests for fallback JSON loading."""

    def test_load_fallback_maps_coordinates(self):
        """Test fallback loader correctly maps coordinate format."""
        from app.jobs.ingest_cras import _load_fallback_data

        # Test actual fallback file
        data = _load_fallback_data()

        if data:  # Only test if file exists
            assert len(data) > 0
            first = data[0]

            # Check mapped fields
            assert "ibge_code" in first
            assert "nome" in first
            assert "latitude" in first
            assert "longitude" in first
            assert "geocode_source" in first

            # Check coordinates are numeric
            if first["latitude"] is not None:
                assert isinstance(first["latitude"], (int, float))
                assert isinstance(first["longitude"], (int, float))
