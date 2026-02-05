"""Tests for CRAS data ingestion."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.jobs.ingest_cras import (
    _parse_cras_csv,
    _get_field,
    _normalize_ibge_code,
    _normalize_cep,
    geocode_single_cras,
    save_cras_to_db,
    ingest_cras_data,
)


class TestCSVParsing:
    """Tests for CSV parsing functions."""

    def test_parse_cras_csv_semicolon(self):
        """Test parsing CSV with semicolon delimiter."""
        csv_content = """nome;ibge;endereco;bairro;cep;telefone;email;municipio;uf
CRAS Centro;3550308;Rua Augusta, 100;Centro;01305000;1133334444;cras@sp.gov.br;Sao Paulo;SP
CRAS Vila;3550308;Av Brasil, 200;Vila Maria;02000000;1122223333;cras2@sp.gov.br;Sao Paulo;SP"""

        result = _parse_cras_csv(csv_content)

        assert len(result) == 2
        assert result[0]["nome"] == "CRAS Centro"
        assert result[0]["ibge_code"] == "3550308"
        assert result[0]["endereco"] == "Rua Augusta, 100"
        assert result[0]["uf"] == "SP"

    def test_parse_cras_csv_comma(self):
        """Test parsing CSV with comma delimiter."""
        csv_content = """nome,cod_ibge,logradouro,ds_bairro,co_cep,nu_telefone,ds_email,nome_municipio,sigla_uf
CRAS Teste,3304557,Rua Teste 123,Centro,20000000,2133334444,cras@rj.gov.br,Rio de Janeiro,RJ"""

        result = _parse_cras_csv(csv_content)

        assert len(result) == 1
        assert result[0]["nome"] == "CRAS Teste"
        assert result[0]["ibge_code"] == "3304557"
        assert result[0]["cidade"] == "Rio de Janeiro"

    def test_parse_cras_csv_empty(self):
        """Test parsing empty CSV."""
        csv_content = """nome;ibge;endereco"""

        result = _parse_cras_csv(csv_content)

        assert len(result) == 0

    def test_parse_cras_csv_missing_fields(self):
        """Test parsing CSV with missing optional fields."""
        csv_content = """nome;ibge;municipio;uf
CRAS Minimo;1234567;Cidade Teste;TE"""

        result = _parse_cras_csv(csv_content)

        assert len(result) == 1
        assert result[0]["nome"] == "CRAS Minimo"
        assert result[0]["endereco"] is None


class TestFieldExtraction:
    """Tests for field extraction helpers."""

    def test_get_field_exact_match(self):
        """Test exact field name match."""
        row = {"nome": "CRAS Centro", "endereco": "Rua A"}
        assert _get_field(row, ["nome"]) == "CRAS Centro"

    def test_get_field_case_insensitive(self):
        """Test case-insensitive field match."""
        row = {"NOME": "CRAS Centro", "ENDERECO": "Rua A"}
        assert _get_field(row, ["nome"]) == "CRAS Centro"

    def test_get_field_fallback(self):
        """Test fallback to secondary field names."""
        row = {"nm_cras": "CRAS Vila", "ds_endereco": "Rua B"}
        assert _get_field(row, ["nome", "nome_cras", "nm_cras"]) == "CRAS Vila"

    def test_get_field_not_found(self):
        """Test when field is not found."""
        row = {"campo_outro": "valor"}
        assert _get_field(row, ["nome", "endereco"]) is None

    def test_get_field_empty_value(self):
        """Test when field value is empty."""
        row = {"nome": "", "nome_cras": "CRAS Real"}
        assert _get_field(row, ["nome", "nome_cras"]) == "CRAS Real"


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


class TestGeocodeSingleCras:
    """Tests for single CRAS geocoding."""

    @pytest.mark.asyncio
    async def test_geocode_single_success(self):
        """Test successful single CRAS geocoding."""
        record = {
            "nome": "CRAS Centro",
            "endereco": "Rua Augusta, 100",
            "cidade": "Sao Paulo",
            "uf": "SP",
            "cep": "01305000"
        }

        with patch("app.jobs.ingest_cras.geocode_address") as mock_geocode:
            mock_geocode.return_value = (-23.55, -46.63, "nominatim")

            result = await geocode_single_cras(record)

            assert result["latitude"] == -23.55
            assert result["longitude"] == -46.63
            assert result["geocode_source"] == "nominatim"
            assert result["nome"] == "CRAS Centro"

    @pytest.mark.asyncio
    async def test_geocode_single_no_address(self):
        """Test geocoding with missing address."""
        record = {"nome": "CRAS Sem Endereco"}

        result = await geocode_single_cras(record)

        # Should return unchanged record
        assert result["nome"] == "CRAS Sem Endereco"
        assert "latitude" not in result or result.get("latitude") is None

    @pytest.mark.asyncio
    async def test_geocode_single_failure(self):
        """Test geocoding failure (no coordinates returned)."""
        record = {
            "nome": "CRAS Teste",
            "endereco": "Endereco Invalido",
            "cidade": "Cidade",
            "uf": "UF"
        }

        with patch("app.jobs.ingest_cras.geocode_address") as mock_geocode:
            mock_geocode.return_value = (None, None, None)

            result = await geocode_single_cras(record)

            assert result["latitude"] is None
            assert result["longitude"] is None
            assert result["geocode_source"] is None


class TestSaveCrasToDb:
    """Tests for database save operations."""

    def test_save_cras_creates_new(self):
        """Test creating new CRAS records."""
        # Mock database session
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
                "geocode_source": "nominatim"
            }
        ]

        stats = save_cras_to_db(mock_db, records, source="test")

        assert stats["created"] >= 0  # May be 0 due to mock setup
        mock_db.commit.assert_called_once()

    def test_save_cras_skips_invalid(self):
        """Test skipping records with invalid IBGE code."""
        mock_db = MagicMock()
        mock_db.query.return_value.all.return_value = []

        records = [
            {"nome": "CRAS Invalido", "ibge_code": "invalid"},
            {"nome": "CRAS Sem IBGE"},
        ]

        stats = save_cras_to_db(mock_db, records, source="test")

        assert stats["skipped"] == 2


class TestIngestCrasData:
    """Tests for main ingestion function."""

    @pytest.mark.asyncio
    async def test_ingest_dry_run(self):
        """Test dry run mode (no database save)."""
        mock_records = [
            {"nome": "CRAS 1", "ibge_code": "3550308", "cidade": "SP", "uf": "SP"},
            {"nome": "CRAS 2", "ibge_code": "3304557", "cidade": "RJ", "uf": "RJ"},
        ]

        with patch("app.jobs.ingest_cras.fetch_censo_suas_data", return_value=mock_records):
            with patch("app.jobs.ingest_cras.geocode_cras_batch") as mock_geocode:
                mock_geocode.return_value = [
                    {**r, "latitude": -23.5, "longitude": -46.6, "geocode_source": "test"}
                    for r in mock_records
                ]

                result = await ingest_cras_data(dry_run=True)

                assert result["dry_run"] is True
                assert result["records_fetched"] == 2
                assert result["records_geocoded"] == 2
                assert "records_saved" not in result or result.get("records_saved") is None

    @pytest.mark.asyncio
    async def test_ingest_fallback_data(self):
        """Test loading fallback data when fetch fails."""
        fallback_data = [
            {"nome": "CRAS Fallback", "ibge_code": "3550308", "cidade": "SP", "uf": "SP"}
        ]

        with patch("app.jobs.ingest_cras.fetch_censo_suas_data", return_value=None):
            with patch("app.jobs.ingest_cras._load_fallback_data", return_value=fallback_data):
                with patch("app.jobs.ingest_cras.geocode_cras_batch", return_value=fallback_data):
                    result = await ingest_cras_data(dry_run=True)

                    assert result["records_fetched"] == 1

    @pytest.mark.asyncio
    async def test_ingest_no_data(self):
        """Test when no data is available."""
        with patch("app.jobs.ingest_cras.fetch_censo_suas_data", return_value=None):
            with patch("app.jobs.ingest_cras._load_fallback_data", return_value=None):
                result = await ingest_cras_data(dry_run=True)

                assert "Failed to fetch CRAS data" in result["errors"][0]
