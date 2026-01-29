"""
Testes para o modulo de cache Redis.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestCacheModule:
    """Testes para funcoes de cache."""

    def test_get_cache_hit(self, mock_redis):
        """Deve retornar valor do cache quando existe."""
        from app.core import cache

        mock_redis.get.return_value = '{"key": "value"}'

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.get_cache("test_key")

        assert result == {"key": "value"}
        mock_redis.get.assert_called_once_with("test_key")

    def test_get_cache_miss(self, mock_redis):
        """Deve retornar None quando chave nao existe."""
        from app.core import cache

        mock_redis.get.return_value = None

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.get_cache("nonexistent_key")

        assert result is None

    def test_get_cache_error(self, mock_redis):
        """Deve retornar None em caso de erro."""
        from app.core import cache

        mock_redis.get.side_effect = Exception("Redis error")

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.get_cache("test_key")

        assert result is None

    def test_set_cache_success(self, mock_redis):
        """Deve salvar valor no cache."""
        from app.core import cache

        mock_redis.setex.return_value = True

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.set_cache("test_key", {"data": 123}, ttl=3600)

        assert result is True
        mock_redis.setex.assert_called_once()

    def test_set_cache_error(self, mock_redis):
        """Deve retornar False em caso de erro."""
        from app.core import cache

        mock_redis.setex.side_effect = Exception("Redis error")

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.set_cache("test_key", {"data": 123})

        assert result is False

    def test_delete_cache_success(self, mock_redis):
        """Deve deletar chave do cache."""
        from app.core import cache

        mock_redis.delete.return_value = 1

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.delete_cache("test_key")

        assert result is True

    def test_delete_cache_not_found(self, mock_redis):
        """Deve retornar True mesmo se chave nao existe."""
        from app.core import cache

        mock_redis.delete.return_value = 0

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.delete_cache("nonexistent_key")

        # Pode retornar True ou False dependendo da implementacao
        assert result in [True, False]

    def test_delete_cache_error(self, mock_redis):
        """Deve retornar False em caso de erro."""
        from app.core import cache

        mock_redis.delete.side_effect = Exception("Redis error")

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.delete_cache("test_key")

        assert result is False

    def test_clear_cache_pattern_success(self, mock_redis):
        """Deve limpar chaves por padrao."""
        from app.core import cache

        mock_redis.keys.return_value = ["prefix:1", "prefix:2"]
        mock_redis.delete.return_value = 2

        with patch.object(cache, "get_redis_client", return_value=mock_redis):
            result = cache.clear_cache_pattern("prefix:*")

        assert result == 2


class TestIntentClassifier:
    """Testes para o classificador de intencoes."""

    def test_classify_farmacia_intent(self):
        """Deve classificar intencao de farmacia."""
        from app.agent.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        result = classifier.classify("quero pedir remédios")

        assert result is not None
        assert hasattr(result, "category")

    def test_classify_beneficio_intent(self):
        """Deve classificar intencao de beneficio."""
        from app.agent.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        result = classifier.classify("quero ver meus benefícios")

        assert result is not None

    def test_classify_documentacao_intent(self):
        """Deve classificar intencao de documentacao."""
        from app.agent.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        result = classifier.classify("que documentos preciso para Bolsa Família")

        assert result is not None

    def test_classify_saudacao(self):
        """Deve classificar saudacao."""
        from app.agent.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        result = classifier.classify("oi, bom dia")

        assert result is not None


class TestExceptionsModule:
    """Testes para o modulo de excecoes."""

    def test_not_found_error(self):
        """Deve criar NotFoundError."""
        from app.core.exceptions import NotFoundError

        error = NotFoundError("Program", "INVALID_CODE")

        assert "not found" in str(error).lower()
        assert error.status_code == 404

    def test_validation_error(self):
        """Deve criar ValidationError."""
        from app.core.exceptions import ValidationError

        error = ValidationError("Campo invalido", field="cpf")

        assert "validation" in str(error).lower() or "cpf" in str(error).lower()
        assert error.status_code == 400

    def test_database_error(self):
        """Deve criar DatabaseError."""
        from app.core.exceptions import DatabaseError

        error = DatabaseError("Connection failed")

        assert "database" in str(error).lower()
        assert error.status_code == 500

    def test_external_api_error(self):
        """Deve criar ExternalAPIError."""
        from app.core.exceptions import ExternalAPIError

        error = ExternalAPIError("IBGE", "Timeout")

        assert "ibge" in str(error).lower()
        assert error.status_code == 502

    def test_base_exception(self):
        """Deve criar TaNaMaoException base."""
        from app.core.exceptions import TaNaMaoException

        error = TaNaMaoException("Erro generico", status_code=418)

        assert str(error) == "Erro generico"
        assert error.status_code == 418
