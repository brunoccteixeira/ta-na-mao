"""
Gerenciador de fluxos interativos para WhatsApp.

Implementa menus numerados, deteccao de selecao e formatacao
otimizada para WhatsApp (emojis, texto estruturado).

Funciona como pre-processing layer no webhook, antes do orchestrator.
"""

import re
import logging
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# Menu Principal
# =============================================================================

class WhatsAppMenuOption(str, Enum):
    """Opcoes do menu principal WhatsApp."""
    CONSULTAR_BENEFICIOS = "1"
    FARMACIA_POPULAR = "2"
    DOCUMENTOS = "3"
    ATUALIZAR_CADUNICO = "4"
    OUTRO_ASSUNTO = "5"


# Mapeamento de opcao numerica para intencao textual
_MENU_PRINCIPAL_MAP = {
    "1": "quero consultar meus beneficios",
    "2": "quero pedir remedio pelo farmacia popular",
    "3": "quero saber quais documentos preciso",
    "4": "preciso atualizar meu cadunico",
    "5": None,  # None = deixar texto original passar pro orchestrator
}

# Mapeamento de palavras-chave de menu de retorno
_MENU_RETORNO_KEYWORDS = [
    "menu", "voltar", "inicio", "início",
    "começar", "comecar", "opcoes", "opções",
]


# =============================================================================
# Formatacao WhatsApp
# =============================================================================

def formatar_menu_principal() -> str:
    """Gera o menu principal formatado para WhatsApp."""
    return (
        "Oi! Sou o *Ta na Mao* \U0001F44B\n\n"
        "Como posso te ajudar hoje?\n\n"
        "\U0001F4B0 *1* - Consultar meus beneficios\n"
        "\U0001F48A *2* - Farmacia Popular (remedios)\n"
        "\U0001F4CB *3* - Documentos necessarios\n"
        "\U0001F4DD *4* - Atualizar CadUnico\n"
        "\U0001F4AC *5* - Falar sobre outro assunto\n\n"
        "Manda o *numero* da opcao!"
    )


def formatar_menu_retorno() -> str:
    """Gera o menu de retorno apos conclusao de fluxo."""
    return (
        "Posso te ajudar com mais alguma coisa?\n\n"
        "\U0001F4B0 *1* - Consultar beneficios\n"
        "\U0001F48A *2* - Farmacia Popular\n"
        "\U0001F4CB *3* - Documentos\n"
        "\U0001F4DD *4* - Atualizar CadUnico\n"
        "\U0001F4AC *5* - Outro assunto\n\n"
        "Manda o *numero* ou escreve o que precisa!"
    )


def formatar_resposta_whatsapp(texto: str) -> str:
    """Formata texto de resposta para WhatsApp.

    Converte markdown basico para formatacao WhatsApp:
    - **texto** -> *texto* (negrito)
    - Adiciona emojis de contexto
    - Limita tamanho da mensagem

    Args:
        texto: Texto da resposta do agente

    Returns:
        Texto formatado para WhatsApp
    """
    # Converter markdown bold para WhatsApp bold
    texto = re.sub(r'\*\*(.+?)\*\*', r'*\1*', texto)

    # Limitar tamanho (WhatsApp tem limite de ~4096 chars)
    if len(texto) > 4000:
        texto = texto[:3950] + "\n\n_Mensagem resumida. Pergunte mais detalhes._"

    return texto


# =============================================================================
# Pre-processamento de mensagens
# =============================================================================

class WhatsAppFlowManager:
    """Gerenciador de fluxos WhatsApp.

    Intercepta mensagens antes do orchestrator para:
    1. Detectar selecao numerica de menus
    2. Mapear para intencao textual
    3. Gerar menus de retorno
    """

    def __init__(self):
        self._sessions_aguardando_menu: set = set()

    def pre_process_message(
        self,
        message: str,
        session_id: str,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Pre-processa mensagem WhatsApp antes do orchestrator.

        Args:
            message: Texto da mensagem recebida
            session_id: ID da sessao (telefone normalizado)

        Returns:
            Tupla (mensagem_transformada, menu_resposta):
            - mensagem_transformada: None se deve usar mensagem original,
              ou texto transformado para o orchestrator
            - menu_resposta: None se nao precisa de menu extra,
              ou texto do menu para enviar junto com a resposta
        """
        message_stripped = message.strip()

        # 1. Verificar se eh selecao numerica de menu
        mapped = self._mapear_selecao_numerica(message_stripped)
        if mapped is not None:
            logger.info(f"WhatsApp: opcao '{message_stripped}' mapeada para intencao")
            return mapped, None

        # 2. Verificar se quer ver o menu
        if self._quer_menu(message_stripped):
            logger.info(f"WhatsApp: cidadao pediu menu")
            return None, formatar_menu_principal()

        # 3. Mensagem normal - deixar passar
        return None, None

    def _mapear_selecao_numerica(self, message: str) -> Optional[str]:
        """Mapeia selecao numerica para intencao textual.

        Args:
            message: Mensagem do cidadao (ex: "1", "2")

        Returns:
            Texto da intencao mapeada, ou None se nao eh selecao numerica
        """
        # Aceitar formatos: "1", " 1 ", "1.", "opcao 1", "opção 1"
        match = re.match(r'^(?:op[cç][aã]o\s*)?(\d)\s*\.?\s*$', message.lower())
        if not match:
            return None

        numero = match.group(1)
        return _MENU_PRINCIPAL_MAP.get(numero)

    def _quer_menu(self, message: str) -> bool:
        """Verifica se cidadao quer ver o menu."""
        message_lower = message.lower().strip()
        return any(kw in message_lower for kw in _MENU_RETORNO_KEYWORDS)

    def should_show_return_menu(self, response_text: str) -> bool:
        """Verifica se deve mostrar menu de retorno apos a resposta.

        Heuristica: mostra menu de retorno quando a resposta parece
        ser uma conclusao de fluxo.

        Args:
            response_text: Texto da resposta do agente

        Returns:
            True se deve anexar menu de retorno
        """
        conclusao_keywords = [
            "mais alguma coisa",
            "precisa de mais",
            "posso ajudar com",
            "espero ter ajudado",
            "qualquer duvida",
            "estou aqui",
        ]
        response_lower = response_text.lower()
        return any(kw in response_lower for kw in conclusao_keywords)


# Singleton
_flow_manager: Optional[WhatsAppFlowManager] = None


def get_whatsapp_flow_manager() -> WhatsAppFlowManager:
    """Retorna instancia singleton do gerenciador de fluxos WhatsApp."""
    global _flow_manager
    if _flow_manager is None:
        _flow_manager = WhatsAppFlowManager()
    return _flow_manager
