"""
Gerenciador de sessões com Redis.

Alternativa ao SessionManager em memória para uso em produção.
Persiste ConversationContext entre reinicializações do servidor.
"""

import uuid
import logging
from typing import Optional
from datetime import datetime

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from .context import ConversationContext

logger = logging.getLogger(__name__)


class RedisSessionManager:
    """
    Gerenciador de sessões usando Redis.

    Características:
    - TTL de 24h para sessões inativas (configurável)
    - Serialização automática via Pydantic
    - Renovação automática de TTL a cada acesso
    - Fallback gracioso se Redis não estiver disponível
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        ttl_seconds: int = 86400,  # 24 horas
        prefix: str = "tanamao:session:"
    ):
        """
        Inicializa o gerenciador de sessões.

        Args:
            redis_url: URL de conexão Redis (padrão: de settings)
            ttl_seconds: Tempo de vida das sessões em segundos
            prefix: Prefixo para chaves no Redis
        """
        self.ttl_seconds = ttl_seconds
        self.prefix = prefix
        self._redis: Optional[redis.Redis] = None
        self._fallback_sessions: dict = {}  # Fallback se Redis falhar

        if not REDIS_AVAILABLE:
            logger.warning(
                "Redis não instalado. Usando fallback em memória. "
                "Instale com: pip install redis"
            )
            return

        try:
            if redis_url is None:
                from app.config import settings
                redis_url = settings.REDIS_URL

            self._redis = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )

            # Testar conexão
            self._redis.ping()
            logger.info(f"Redis conectado: {redis_url}")

        except Exception as e:
            logger.error(f"Erro ao conectar Redis: {e}. Usando fallback em memória.")
            self._redis = None

    def _key(self, session_id: str) -> str:
        """Gera chave Redis para a sessão."""
        return f"{self.prefix}{session_id}"

    def _is_redis_available(self) -> bool:
        """Verifica se Redis está disponível."""
        if self._redis is None:
            return False

        try:
            self._redis.ping()
            return True
        except Exception:
            return False

    def get_or_create(self, session_id: Optional[str] = None) -> ConversationContext:
        """
        Obtém sessão existente ou cria nova.

        Args:
            session_id: ID da sessão (opcional, gera UUID se não fornecido)

        Returns:
            ConversationContext da sessão
        """
        # Tentar obter sessão existente
        if session_id:
            existing = self.get(session_id)
            if existing:
                return existing

        # Criar nova sessão
        new_session_id = session_id or str(uuid.uuid4())
        context = ConversationContext(session_id=new_session_id)

        # Salvar no Redis
        self.save(context)

        return context

    def get(self, session_id: str) -> Optional[ConversationContext]:
        """
        Obtém sessão existente.

        Args:
            session_id: ID da sessão

        Returns:
            ConversationContext ou None se não existir
        """
        if self._is_redis_available():
            try:
                data = self._redis.get(self._key(session_id))
                if data:
                    context = ConversationContext.model_validate_json(data)
                    context.last_activity = datetime.now()

                    # Renovar TTL
                    self._redis.expire(self._key(session_id), self.ttl_seconds)

                    return context
            except Exception as e:
                logger.error(f"Erro ao obter sessão do Redis: {e}")

        # Fallback para memória
        return self._fallback_sessions.get(session_id)

    def save(self, context: ConversationContext) -> bool:
        """
        Salva sessão no Redis.

        Args:
            context: ConversationContext para salvar

        Returns:
            True se salvou com sucesso
        """
        context.last_activity = datetime.now()

        if self._is_redis_available():
            try:
                self._redis.setex(
                    self._key(context.session_id),
                    self.ttl_seconds,
                    context.model_dump_json()
                )
                return True
            except Exception as e:
                logger.error(f"Erro ao salvar sessão no Redis: {e}")

        # Fallback para memória
        self._fallback_sessions[context.session_id] = context
        return True

    def delete(self, session_id: str) -> bool:
        """
        Remove sessão.

        Args:
            session_id: ID da sessão

        Returns:
            True se removeu com sucesso
        """
        if self._is_redis_available():
            try:
                result = self._redis.delete(self._key(session_id))
                return result > 0
            except Exception as e:
                logger.error(f"Erro ao deletar sessão do Redis: {e}")

        # Fallback
        if session_id in self._fallback_sessions:
            del self._fallback_sessions[session_id]
            return True

        return False

    def reset(self, session_id: str) -> bool:
        """
        Reseta sessão (mantém ID mas limpa dados).

        Args:
            session_id: ID da sessão

        Returns:
            True se resetou com sucesso
        """
        context = self.get(session_id)
        if context:
            context.reset()
            return self.save(context)
        return False

    def cleanup_expired(self) -> int:
        """
        Limpa sessões expiradas.

        No Redis, isso é automático via TTL.
        Aqui limpamos apenas o fallback em memória.

        Returns:
            Número de sessões removidas
        """
        if not self._fallback_sessions:
            return 0

        from datetime import timedelta

        now = datetime.now()
        expired = []

        for session_id, context in self._fallback_sessions.items():
            age = now - context.last_activity
            if age > timedelta(seconds=self.ttl_seconds):
                expired.append(session_id)

        for session_id in expired:
            del self._fallback_sessions[session_id]

        if expired:
            logger.info(f"Limpeza: {len(expired)} sessões expiradas removidas")

        return len(expired)

    def count_sessions(self) -> int:
        """
        Conta número de sessões ativas.

        Returns:
            Número de sessões
        """
        if self._is_redis_available():
            try:
                keys = self._redis.keys(f"{self.prefix}*")
                return len(keys)
            except Exception as e:
                logger.error(f"Erro ao contar sessões no Redis: {e}")

        return len(self._fallback_sessions)

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """
        Obtém informações resumidas da sessão.

        Args:
            session_id: ID da sessão

        Returns:
            Dict com info da sessão ou None
        """
        context = self.get(session_id)
        if not context:
            return None

        return {
            "session_id": context.session_id,
            "created_at": context.created_at.isoformat(),
            "last_activity": context.last_activity.isoformat(),
            "active_flow": context.active_flow.value if context.active_flow else None,
            "messages_count": len(context.history),
            "tools_used": context.tools_used,
            "has_cpf": context.citizen.cpf is not None,
            "has_location": context.citizen.has_geolocation(),
        }
