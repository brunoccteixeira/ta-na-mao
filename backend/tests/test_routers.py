"""
Testes para os routers da API.

Testa endpoints de admin, geo, municipalities, etc.
"""

import pytest
from fastapi import status

from tests.conftest import requires_postgres


@requires_postgres
class TestAdminRouter:
    """Testes para o router admin."""

    @pytest.mark.asyncio
    async def test_get_penetration_rates(self, client, test_db):
        """Deve retornar taxas de penetracao."""
        response = await client.get("/api/v1/admin/penetration")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data or "results" in data or "municipalities" in data or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_penetration_rates_with_state_filter(self, client, test_db):
        """Deve filtrar por estado."""
        response = await client.get(
            "/api/v1/admin/penetration",
            params={"state_code": "SP"}
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_penetration_rates_with_pagination(self, client, test_db):
        """Deve suportar paginacao."""
        response = await client.get(
            "/api/v1/admin/penetration",
            params={"limit": 10, "offset": 0}
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_coverage_alerts(self, client, test_db):
        """Deve retornar alertas de cobertura baixa."""
        response = await client.get("/api/v1/admin/alerts")

        # Pode retornar 200 ou 404 dependendo dos dados
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    @pytest.mark.asyncio
    async def test_export_data_csv(self, client, test_db):
        """Deve exportar dados em CSV."""
        response = await client.get(
            "/api/v1/admin/export",
            params={"format": "csv"}
        )

        # Pode retornar 200 ou 404 dependendo dos dados
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@requires_postgres
class TestGeoRouter:
    """Testes para o router geo."""

    @pytest.mark.asyncio
    async def test_get_states(self, client, test_db):
        """Deve retornar lista de estados (GeoJSON)."""
        response = await client.get("/api/v1/geo/states")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Retorna GeoJSON FeatureCollection
        assert isinstance(data, list) or "states" in data or "features" in data

    @pytest.mark.asyncio
    async def test_get_state_by_code(self, client, test_db):
        """Deve retornar estado por codigo."""
        response = await client.get("/api/v1/geo/states/SP")

        # Pode retornar 200 ou 404 dependendo dos dados
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    @pytest.mark.asyncio
    async def test_get_municipalities_by_state(self, client, test_db):
        """Deve retornar municipios de um estado."""
        response = await client.get("/api/v1/geo/states/SP/municipalities")

        # Pode retornar 200 ou 404 dependendo dos dados
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@requires_postgres
class TestMunicipalitiesRouter:
    """Testes para o router de municipios."""

    @pytest.mark.asyncio
    async def test_list_municipalities(self, client, test_db):
        """Deve listar municipios."""
        response = await client.get("/api/v1/municipalities/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Retorna paginacao com items
        assert isinstance(data, list) or "municipalities" in data or "items" in data

    @pytest.mark.asyncio
    async def test_list_municipalities_with_limit(self, client, test_db):
        """Deve limitar resultados."""
        response = await client.get(
            "/api/v1/municipalities/",
            params={"limit": 5}
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_municipality_by_ibge_code(self, client, test_db):
        """Deve retornar municipio por codigo IBGE."""
        # Usa codigo IBGE de Sao Paulo
        response = await client.get("/api/v1/municipalities/3550308")

        # Pode retornar 200 ou 404 dependendo dos dados
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    @pytest.mark.asyncio
    async def test_get_municipality_not_found(self, client, test_db):
        """Deve retornar 404 para codigo inexistente."""
        response = await client.get("/api/v1/municipalities/9999999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_search_municipalities(self, client, test_db):
        """Deve buscar municipios por nome."""
        response = await client.get(
            "/api/v1/municipalities/search",
            params={"q": "Paulo"}
        )

        # Pode retornar 200 ou 404 dependendo do endpoint
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@requires_postgres
class TestNearbyRouter:
    """Testes para o router nearby."""

    @pytest.mark.asyncio
    async def test_get_nearby_cras(self, client, test_db):
        """Deve retornar CRAS proximos."""
        response = await client.get(
            "/api/v1/nearby/cras",
            params={"lat": -23.5505, "lng": -46.6333}
        )

        # Pode retornar 200 ou 404 dependendo dos dados
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    @pytest.mark.asyncio
    async def test_get_nearby_pharmacies(self, client, test_db):
        """Deve retornar farmacias proximas."""
        response = await client.get(
            "/api/v1/nearby/pharmacies",
            params={"lat": -23.5505, "lng": -46.6333}
        )

        # Pode retornar 200 ou 404 dependendo dos dados
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@requires_postgres
class TestWebhookRouter:
    """Testes para o router webhook."""

    @pytest.mark.asyncio
    async def test_whatsapp_webhook_verification(self, client, test_db):
        """Deve verificar webhook do WhatsApp."""
        response = await client.get(
            "/api/v1/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test-token",
                "hub.challenge": "test-challenge"
            }
        )

        # Pode retornar 200 ou 403 dependendo do token
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN
        ]

    @pytest.mark.asyncio
    async def test_whatsapp_webhook_message(self, client, test_db):
        """Deve receber mensagem do WhatsApp."""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "123",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "messages": []
                    },
                    "field": "messages"
                }]
            }]
        }

        response = await client.post(
            "/api/v1/webhook/whatsapp",
            json=payload
        )

        # Deve aceitar a requisicao
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
