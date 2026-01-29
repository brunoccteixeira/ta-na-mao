"""
Interface base para handlers de canal.

Define a estrutura comum que todos os handlers de canal
(SMS, Voice, WhatsApp, Web) devem implementar.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChannelType(str, Enum):
    """Tipos de canal suportados."""

    WHATSAPP = "whatsapp"
    SMS = "sms"
    VOICE = "voice"
    WEB = "web"
    USSD = "ussd"


class SMSState(str, Enum):
    """Estados do fluxo SMS/USSD."""

    MENU_PRINCIPAL = "menu_principal"
    AGUARDANDO_CPF = "aguardando_cpf"
    AGUARDANDO_CEP = "aguardando_cep"
    AGUARDANDO_OPCAO = "aguardando_opcao"
    RESULTADO = "resultado"
    MENU_SECUNDARIO = "menu_secundario"
    AGUARDANDO_CONFIRMACAO = "aguardando_confirmacao"


class VoiceState(str, Enum):
    """Estados do fluxo de voz/URA."""

    BOAS_VINDAS = "boas_vindas"
    MENU_PRINCIPAL = "menu_principal"
    COLETANDO_CPF = "coletando_cpf"
    PROCESSANDO = "processando"
    RESULTADO = "resultado"
    MENU_OPCOES = "menu_opcoes"
    TRANSFERINDO = "transferindo"
    DESPEDIDA = "despedida"
    ERRO = "erro"


@dataclass
class UnifiedMessage:
    """
    Mensagem unificada entre canais.

    Normaliza mensagens de diferentes canais para um formato comum
    que pode ser processado pelo orquestrador.
    """

    # Identificação
    channel: ChannelType
    message_id: str
    session_id: str

    # Remetente
    user_id: str  # Telefone normalizado ou ID único
    user_phone: Optional[str] = None

    # Conteúdo
    text: str = ""
    dtmf_digits: Optional[str] = None  # Para voz
    media_url: Optional[str] = None
    media_type: Optional[str] = None

    # Contexto
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Estado (para canais stateful como SMS/Voz)
    channel_state: Optional[str] = None

    def normalize_phone(self) -> str:
        """Normaliza número de telefone para formato E.164."""
        if not self.user_phone:
            return self.user_id

        phone = "".join(filter(str.isdigit, self.user_phone))

        # Adiciona código do país se necessário
        if len(phone) == 11:  # Celular BR: DDD + 9 dígitos
            phone = f"55{phone}"
        elif len(phone) == 10:  # Fixo BR: DDD + 8 dígitos
            phone = f"55{phone}"

        return f"+{phone}"


@dataclass
class ChannelResponse:
    """
    Resposta formatada para um canal específico.

    Contém o conteúdo e metadados necessários para
    enviar a resposta através do canal apropriado.
    """

    # Conteúdo
    text: str

    # Para SMS: mensagem pode ser dividida em partes
    text_parts: List[str] = field(default_factory=list)

    # Para voz: TTS e configurações
    ssml: Optional[str] = None
    voice: str = "Polly.Camila"
    language: str = "pt-BR"

    # Ações de navegação
    gather_digits: bool = False
    num_digits: int = 1
    action_url: Optional[str] = None

    # Estado
    next_state: Optional[str] = None
    end_session: bool = False

    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)

    def split_sms(self, max_length: int = 160) -> List[str]:
        """Divide texto em partes para SMS (limite de 160 caracteres)."""
        if len(self.text) <= max_length:
            return [self.text]

        parts = []
        current = ""
        words = self.text.split()

        for word in words:
            if len(current) + len(word) + 1 <= max_length:
                current = f"{current} {word}".strip()
            else:
                if current:
                    parts.append(current)
                current = word

        if current:
            parts.append(current)

        self.text_parts = parts
        return parts


class SMSMenuOption(BaseModel):
    """Opção de menu para SMS/USSD."""

    key: str  # "1", "2", etc.
    label: str
    action: str  # Texto que será enviado ao agente
    next_state: Optional[SMSState] = None


class VoiceMenuOption(BaseModel):
    """Opção de menu para URA."""

    digit: str  # "1", "2", etc.
    label: str  # Texto lido pelo TTS
    action: str
    next_state: Optional[VoiceState] = None


class ChannelSession(BaseModel):
    """
    Sessão de canal.

    Mantém estado específico do canal entre interações.
    """

    session_id: str
    channel: ChannelType
    user_phone: str
    state: str  # SMSState ou VoiceState

    # Dados coletados durante a sessão
    cpf: Optional[str] = None
    cep: Optional[str] = None
    selected_option: Optional[str] = None

    # Histórico simplificado
    interaction_count: int = 0
    last_message: Optional[str] = None

    # Timestamps
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    # Metadados
    metadata: Dict[str, Any] = {}

    def update_state(self, new_state: str) -> None:
        """Atualiza estado da sessão."""
        self.state = new_state
        self.updated_at = datetime.now()
        self.interaction_count += 1


class ChannelHandler(ABC):
    """
    Interface base para handlers de canal.

    Cada canal (SMS, Voice, etc.) deve implementar esta interface
    para garantir compatibilidade com o orquestrador.
    """

    @property
    @abstractmethod
    def channel_type(self) -> ChannelType:
        """Retorna tipo do canal."""
        pass

    @abstractmethod
    async def parse_incoming(self, raw_data: Dict[str, Any]) -> UnifiedMessage:
        """
        Converte mensagem do canal para formato unificado.

        Args:
            raw_data: Dados brutos recebidos do webhook

        Returns:
            UnifiedMessage: Mensagem normalizada
        """
        pass

    @abstractmethod
    async def format_response(
        self,
        agent_response: Dict[str, Any],
        session: ChannelSession
    ) -> ChannelResponse:
        """
        Converte resposta do agente para formato do canal.

        Args:
            agent_response: Resposta do orquestrador
            session: Sessão atual do canal

        Returns:
            ChannelResponse: Resposta formatada para o canal
        """
        pass

    @abstractmethod
    async def send_response(
        self,
        response: ChannelResponse,
        to: str,
        **kwargs
    ) -> bool:
        """
        Envia resposta através do canal.

        Args:
            response: Resposta formatada
            to: Destinatário (telefone, ID, etc.)
            **kwargs: Parâmetros específicos do canal

        Returns:
            bool: True se enviado com sucesso
        """
        pass

    @abstractmethod
    def get_menu_options(self, state: str) -> List[Any]:
        """
        Retorna opções de menu para o estado atual.

        Args:
            state: Estado atual da sessão

        Returns:
            Lista de opções (SMSMenuOption ou VoiceMenuOption)
        """
        pass

    def validate_input(self, message: UnifiedMessage, session: ChannelSession) -> bool:
        """
        Valida entrada do usuário baseado no estado atual.

        Args:
            message: Mensagem recebida
            session: Sessão atual

        Returns:
            bool: True se entrada é válida
        """
        # Implementação padrão - pode ser sobrescrita
        return True

    def get_error_message(self, error_type: str) -> str:
        """
        Retorna mensagem de erro apropriada.

        Args:
            error_type: Tipo do erro

        Returns:
            str: Mensagem de erro
        """
        errors = {
            "invalid_cpf": "CPF inválido. Digite apenas os 11 números.",
            "invalid_option": "Opção inválida. Escolha uma das opções disponíveis.",
            "timeout": "Tempo esgotado. Digite qualquer tecla para continuar.",
            "generic": "Erro no sistema. Tente novamente.",
        }
        return errors.get(error_type, errors["generic"])


class ChannelSessionManager:
    """
    Gerenciador de sessões de canal.

    Mantém estado das sessões SMS/Voice entre interações.
    Em produção, usar Redis para persistência.
    """

    def __init__(self):
        self._sessions: Dict[str, ChannelSession] = {}

    def get_or_create(
        self,
        user_phone: str,
        channel: ChannelType,
        initial_state: str = "menu_principal"
    ) -> ChannelSession:
        """
        Obtém ou cria sessão para usuário.

        Args:
            user_phone: Telefone do usuário
            channel: Tipo do canal
            initial_state: Estado inicial se criar nova sessão

        Returns:
            ChannelSession: Sessão do usuário
        """
        import uuid

        key = f"{channel.value}:{user_phone}"

        if key not in self._sessions:
            self._sessions[key] = ChannelSession(
                session_id=str(uuid.uuid4()),
                channel=channel,
                user_phone=user_phone,
                state=initial_state
            )

        session = self._sessions[key]
        session.updated_at = datetime.now()
        return session

    def get(self, user_phone: str, channel: ChannelType) -> Optional[ChannelSession]:
        """Obtém sessão existente."""
        key = f"{channel.value}:{user_phone}"
        return self._sessions.get(key)

    def update(self, session: ChannelSession) -> None:
        """Atualiza sessão."""
        key = f"{session.channel.value}:{session.user_phone}"
        self._sessions[key] = session

    def delete(self, user_phone: str, channel: ChannelType) -> bool:
        """Remove sessão."""
        key = f"{channel.value}:{user_phone}"
        if key in self._sessions:
            del self._sessions[key]
            return True
        return False

    def cleanup_expired(self, max_age_minutes: int = 30) -> int:
        """Remove sessões expiradas."""
        from datetime import timedelta

        now = datetime.now()
        expired = []

        for key, session in self._sessions.items():
            age = now - session.updated_at
            if age > timedelta(minutes=max_age_minutes):
                expired.append(key)

        for key in expired:
            del self._sessions[key]

        return len(expired)


# Singleton para gerenciamento de sessões
channel_session_manager = ChannelSessionManager()
