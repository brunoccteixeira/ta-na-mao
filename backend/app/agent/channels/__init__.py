"""
Módulo de canais de comunicação.

Fornece handlers para diferentes canais de comunicação:
- SMS/USSD
- Voz (0800/URA)
- WhatsApp (via webhook)
- Web

Todos os handlers implementam a interface ChannelHandler
para garantir compatibilidade com o orquestrador.
"""

from .base import (
    ChannelType,
    ChannelHandler,
    ChannelResponse,
    ChannelSession,
    ChannelSessionManager,
    UnifiedMessage,
    SMSState,
    VoiceState,
    SMSMenuOption,
    VoiceMenuOption,
    channel_session_manager,
)

from .sms_handler import SMSHandler
from .voice_handler import VoiceHandler

__all__ = [
    # Tipos
    "ChannelType",
    "SMSState",
    "VoiceState",
    # Classes base
    "ChannelHandler",
    "ChannelResponse",
    "ChannelSession",
    "ChannelSessionManager",
    "UnifiedMessage",
    # Menu options
    "SMSMenuOption",
    "VoiceMenuOption",
    # Handlers
    "SMSHandler",
    "VoiceHandler",
    # Singletons
    "channel_session_manager",
]
