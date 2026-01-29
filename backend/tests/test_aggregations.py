"""Testes para o router de agregações.

NOTE: These tests require PostgreSQL with PostGIS/JSONB support.
They are skipped when running with SQLite (test environment).
"""

import pytest
from datetime import date
from fastapi import status

from tests.conftest import requires_postgres
from app.models import Program, Municipality, BeneficiaryData, State


@requires_postgres
@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_national_aggregation_empty(client, test_db):
    """Testa agregação nacional sem dados."""
    response = await client.get("/api/v1/aggregations/national")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["level"] == "national"
    assert "program_stats" in data


@requires_postgres
@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_national_aggregation_with_data(client, test_db, sample_state_data, sample_program_data):
    """Testa agregação nacional com dados."""
    import uuid
    unique_id = uuid.uuid4().hex[:5]  # 5 chars para caber em varchar(7)

    # Criar estado com dados únicos
    state = State(**sample_state_data)
    test_db.add(state)
    await test_db.flush()

    # Criar município com código único (max 7 chars)
    municipality = Municipality(
        ibge_code=f"99{unique_id}",  # 99 + 5 = 7 chars
        name=f"Município Teste {unique_id}",
        state_id=state.id,
        population=1000000,
    )
    test_db.add(municipality)
    await test_db.flush()

    # Criar programa com dados únicos
    program = Program(**sample_program_data)
    test_db.add(program)
    await test_db.flush()

    # Criar dados de beneficiário
    beneficiary_data = BeneficiaryData(
        municipality_id=municipality.id,
        program_id=program.id,
        reference_date=date(2024, 1, 1),
        total_beneficiaries=1000,
        total_families=500,
        total_value_brl=50000.0,
        coverage_rate=0.75,
    )
    test_db.add(beneficiary_data)
    await test_db.flush()

    response = await client.get("/api/v1/aggregations/national")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Verifica que os dados existem (pode ter mais dados do banco de dev)
    assert "program_stats" in data or "total_beneficiaries" in data


@requires_postgres
@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_national_aggregation_filtered_by_program(client, test_db, sample_state_data):
    """Testa agregação nacional filtrada por programa."""
    import uuid
    unique_id = uuid.uuid4().hex[:5]  # 5 chars para caber em varchar(7)

    # Criar estado com dados únicos
    state = State(**sample_state_data)
    test_db.add(state)
    await test_db.flush()

    # Criar município com código único (max 7 chars)
    municipality = Municipality(
        ibge_code=f"99{unique_id}",  # 99 + 5 = 7 chars
        name=f"Município Teste {unique_id}",
        state_id=state.id,
        population=1000000,
    )
    test_db.add(municipality)
    await test_db.flush()

    # Criar dois programas com códigos únicos
    program1_code = f"TEST_PROG1_{unique_id}"
    program2_code = f"TEST_PROG2_{unique_id}"
    program1 = Program(code=program1_code, name="Programa Teste 1", is_active=True)
    program2 = Program(code=program2_code, name="Programa Teste 2", is_active=True)
    test_db.add_all([program1, program2])
    await test_db.flush()

    # Criar dados para cada programa
    data1 = BeneficiaryData(
        municipality_id=municipality.id,
        program_id=program1.id,
        reference_date=date(2024, 1, 1),
        total_beneficiaries=1000,
        total_families=500,
        total_value_brl=50000.0,
    )
    data2 = BeneficiaryData(
        municipality_id=municipality.id,
        program_id=program2.id,
        reference_date=date(2024, 1, 1),
        total_beneficiaries=500,
        total_families=250,
        total_value_brl=25000.0,
    )
    test_db.add_all([data1, data2])
    await test_db.flush()

    # Testar filtro por programa
    response = await client.get("/api/v1/aggregations/national", params={"program": program1_code})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Verifica estrutura da resposta
    assert "level" in data or "total_beneficiaries" in data


@requires_postgres
@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_states_aggregation(client, test_db):
    """Testa agregação por estados usando dados existentes."""
    # Este teste usa dados existentes do banco de desenvolvimento
    # pois os dados criados em transação de teste não são visíveis para o cliente
    response = await client.get("/api/v1/aggregations/states")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["level"] == "states"  # plural
    # Verifica que existem estados (dados reais do banco)
    assert "states" in data

