"""Testes para o router do agente IA.

NOTE: Tests that require PostgreSQL features are skipped in SQLite test mode.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

from tests.conftest import requires_postgres


@requires_postgres
@pytest.mark.agent
@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_agent_session(client):
    """Testa início de sessão do agente."""
    response = await client.post("/api/v1/agent/start")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    data = response.json()
    assert "session_id" in data or "message" in data


@requires_postgres
@pytest.mark.agent
@pytest.mark.unit
@pytest.mark.asyncio
@patch("app.routers.agent.get_or_create_agent")
async def test_agent_chat(mock_get_agent, client):
    """Testa envio de mensagem ao agente."""
    # Mock do agente com atributos necessários
    mock_agent = MagicMock()
    mock_agent.session_id = "test-session-123"
    mock_agent.tools_used = []
    mock_agent.process_message.return_value = "Olá! Como posso ajudar?"
    mock_get_agent.return_value = mock_agent

    response = await client.post(
        "/api/v1/agent/chat",
        json={
            "message": "Olá",
            "session_id": "test-session-123",
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "response" in data
    assert data["response"] == "Olá! Como posso ajudar?"


@requires_postgres
@pytest.mark.agent
@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_status(client):
    """Testa status do agente."""
    response = await client.get("/api/v1/agent/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # AgentStatus retorna: available, model, tools
    assert "available" in data
    assert "model" in data
    assert "tools" in data






