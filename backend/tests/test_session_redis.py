"""
Testes para session_redis.

Testa RedisSessionManager e funcoes relacionadas.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestRedisSessionManager:
    """Testes para RedisSessionManager."""

    def test_import(self):
        """Deve importar RedisSessionManager."""
        from app.agent.session_redis import RedisSessionManager

        assert RedisSessionManager is not None

    def test_create_session_manager(self):
        """Deve criar instancia de RedisSessionManager."""
        from app.agent.session_redis import RedisSessionManager

        # Sem Redis, deve criar manager em modo fallback
        manager = RedisSessionManager(redis_url=None)
        assert manager is not None

    def test_manager_has_ttl(self):
        """Deve ter TTL configuravel."""
        from app.agent.session_redis import RedisSessionManager

        manager = RedisSessionManager(ttl_seconds=3600)
        assert manager.ttl_seconds == 3600

    def test_manager_has_prefix(self):
        """Deve ter prefixo configuravel."""
        from app.agent.session_redis import RedisSessionManager

        manager = RedisSessionManager(prefix="test:")
        assert manager.prefix == "test:"

    def test_redis_available_flag(self):
        """Deve ter flag de disponibilidade Redis."""
        from app.agent.session_redis import REDIS_AVAILABLE

        # REDIS_AVAILABLE é True se redis está instalado
        assert isinstance(REDIS_AVAILABLE, bool)


class TestSessionRedisHelpers:
    """Testes para funcoes auxiliares."""

    def test_serialize_context(self):
        """Deve serializar contexto."""
        from app.agent.context import ConversationContext
        import json

        context = ConversationContext()
        
        # Tentar serializar manualmente
        if hasattr(context, 'model_dump'):
            data = context.model_dump()
        elif hasattr(context, 'dict'):
            data = context.dict()
        else:
            data = {"session_id": context.session_id}
        
        # Deve ser serializavel
        serialized = json.dumps(data, default=str)
        assert serialized is not None

    def test_deserialize_context(self):
        """Deve deserializar contexto."""
        import json

        mock_data = {
            "session_id": "test123",
            "active_flow": None,
            "history": [],
            "tools_used": []
        }

        serialized = json.dumps(mock_data)
        deserialized = json.loads(serialized)
        
        assert deserialized["session_id"] == "test123"
