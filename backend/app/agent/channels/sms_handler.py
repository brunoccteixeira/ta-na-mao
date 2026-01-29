"""
Handler para canal SMS/USSD.

Implementa navegação por menu numérico para dispositivos
sem acesso a internet ou smartphones básicos.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from .base import (
    ChannelHandler,
    ChannelResponse,
    ChannelSession,
    ChannelType,
    SMSMenuOption,
    SMSState,
    UnifiedMessage,
    channel_session_manager,
)

logger = logging.getLogger(__name__)


class SMSHandler(ChannelHandler):
    """
    Handler para canal SMS.

    Implementa fluxo de navegação USSD-like com menus numéricos.
    Otimizado para mensagens curtas (< 160 caracteres).
    """

    # Menus por estado
    MENUS: Dict[SMSState, List[SMSMenuOption]] = {
        SMSState.MENU_PRINCIPAL: [
            SMSMenuOption(
                key="1",
                label="Consultar benefícios",
                action="consultar_beneficios",
                next_state=SMSState.AGUARDANDO_CPF
            ),
            SMSMenuOption(
                key="2",
                label="Dinheiro esquecido",
                action="dinheiro_esquecido",
                next_state=SMSState.AGUARDANDO_CPF
            ),
            SMSMenuOption(
                key="3",
                label="Farmácia Popular",
                action="farmacia_popular",
                next_state=SMSState.AGUARDANDO_CPF
            ),
            SMSMenuOption(
                key="4",
                label="CRAS mais próximo",
                action="buscar_cras",
                next_state=SMSState.AGUARDANDO_CEP
            ),
            SMSMenuOption(
                key="5",
                label="Falar com atendente",
                action="transferir_atendente",
                next_state=None
            ),
        ],
        SMSState.MENU_SECUNDARIO: [
            SMSMenuOption(
                key="1",
                label="Ver detalhes",
                action="ver_detalhes",
                next_state=SMSState.RESULTADO
            ),
            SMSMenuOption(
                key="2",
                label="Nova consulta",
                action="nova_consulta",
                next_state=SMSState.MENU_PRINCIPAL
            ),
            SMSMenuOption(
                key="0",
                label="Voltar ao início",
                action="voltar_inicio",
                next_state=SMSState.MENU_PRINCIPAL
            ),
        ],
    }

    def __init__(self, provider: str = "twilio"):
        """
        Inicializa handler SMS.

        Args:
            provider: Provedor SMS (twilio, zenvia, infobip)
        """
        self.provider = provider
        self._client = None

    @property
    def channel_type(self) -> ChannelType:
        return ChannelType.SMS

    async def parse_incoming(self, raw_data: Dict[str, Any]) -> UnifiedMessage:
        """
        Converte webhook do provedor para mensagem unificada.

        Suporta formato Twilio e Zenvia.
        """
        # Detectar formato do provedor
        if "From" in raw_data:
            # Formato Twilio
            return self._parse_twilio(raw_data)
        elif "from" in raw_data:
            # Formato Zenvia/Infobip
            return self._parse_zenvia(raw_data)
        else:
            raise ValueError("Formato de webhook não reconhecido")

    def _parse_twilio(self, data: Dict[str, Any]) -> UnifiedMessage:
        """Parse formato Twilio."""
        phone = data.get("From", "").replace("whatsapp:", "")
        text = data.get("Body", "").strip()
        message_id = data.get("MessageSid", "")

        # Obter ou criar sessão
        session = channel_session_manager.get_or_create(
            user_phone=phone,
            channel=ChannelType.SMS,
            initial_state=SMSState.MENU_PRINCIPAL.value
        )

        return UnifiedMessage(
            channel=ChannelType.SMS,
            message_id=message_id,
            session_id=session.session_id,
            user_id=phone,
            user_phone=phone,
            text=text,
            channel_state=session.state,
            metadata={
                "provider": "twilio",
                "to": data.get("To", ""),
                "num_media": data.get("NumMedia", 0),
            }
        )

    def _parse_zenvia(self, data: Dict[str, Any]) -> UnifiedMessage:
        """Parse formato Zenvia."""
        phone = data.get("from", "")
        text = data.get("body", data.get("text", "")).strip()
        message_id = data.get("id", data.get("message_id", ""))

        session = channel_session_manager.get_or_create(
            user_phone=phone,
            channel=ChannelType.SMS,
            initial_state=SMSState.MENU_PRINCIPAL.value
        )

        return UnifiedMessage(
            channel=ChannelType.SMS,
            message_id=message_id,
            session_id=session.session_id,
            user_id=phone,
            user_phone=phone,
            text=text,
            channel_state=session.state,
            metadata={
                "provider": "zenvia",
                "to": data.get("to", ""),
            }
        )

    async def format_response(
        self,
        agent_response: Dict[str, Any],
        session: ChannelSession
    ) -> ChannelResponse:
        """
        Formata resposta do agente para SMS.

        Otimiza para limite de 160 caracteres.
        """
        text = agent_response.get("text", "")
        state = session.state

        # Simplificar texto para SMS
        text = self._simplify_for_sms(text)

        # Adicionar menu se aplicável
        menu_text = self._get_menu_text(state)
        if menu_text:
            text = f"{text}\n\n{menu_text}"

        response = ChannelResponse(
            text=text,
            next_state=state,
        )

        # Dividir se necessário
        response.split_sms()

        return response

    def _simplify_for_sms(self, text: str) -> str:
        """Simplifica texto para SMS."""
        # Remover markdown
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*(.+?)\*", r"\1", text)  # Italic
        text = re.sub(r"#+ ", "", text)  # Headers

        # Simplificar emojis (manter apenas alguns)
        emoji_map = {
            "✅": "[OK]",
            "❌": "[X]",
            "⚡": "[!]",
            "💰": "R$",
            "📍": "",
            "📞": "Tel:",
        }
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)

        # Remover outros emojis
        text = re.sub(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F]",
            "",
            text
        )

        # Compactar espaços
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"  +", " ", text)

        return text.strip()

    def _get_menu_text(self, state: str) -> str:
        """Gera texto do menu para o estado atual."""
        try:
            state_enum = SMSState(state)
        except ValueError:
            return ""

        menu_options = self.MENUS.get(state_enum, [])
        if not menu_options:
            return ""

        lines = []
        for opt in menu_options:
            lines.append(f"{opt.key}) {opt.label}")

        return "\n".join(lines)

    async def send_response(
        self,
        response: ChannelResponse,
        to: str,
        **kwargs
    ) -> bool:
        """
        Envia SMS através do provedor.

        Args:
            response: Resposta formatada
            to: Número de destino
            **kwargs: from_number, etc.

        Returns:
            bool: True se enviado com sucesso
        """
        from_number = kwargs.get("from_number", "")

        if self.provider == "twilio":
            return await self._send_twilio(response, to, from_number)
        elif self.provider == "zenvia":
            return await self._send_zenvia(response, to, from_number)
        else:
            logger.error(f"Provedor SMS não suportado: {self.provider}")
            return False

    async def _send_twilio(
        self,
        response: ChannelResponse,
        to: str,
        from_number: str
    ) -> bool:
        """Envia via Twilio."""
        try:
            from twilio.rest import Client
            from app.config import settings

            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )

            # Enviar cada parte da mensagem
            parts = response.text_parts or [response.text]
            for part in parts:
                client.messages.create(
                    body=part,
                    from_=from_number or settings.TWILIO_SMS_FROM,
                    to=to
                )

            logger.info(f"SMS enviado via Twilio para {to}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar SMS via Twilio: {e}")
            return False

    async def _send_zenvia(
        self,
        response: ChannelResponse,
        to: str,
        from_number: str
    ) -> bool:
        """Envia via Zenvia."""
        try:
            import httpx
            from app.config import settings

            headers = {
                "X-API-TOKEN": settings.ZENVIA_API_TOKEN,
                "Content-Type": "application/json",
            }

            parts = response.text_parts or [response.text]
            for part in parts:
                payload = {
                    "from": from_number or settings.ZENVIA_SMS_FROM,
                    "to": to,
                    "contents": [{"type": "text", "text": part}]
                }

                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        "https://api.zenvia.com/v2/channels/sms/messages",
                        json=payload,
                        headers=headers
                    )
                    resp.raise_for_status()

            logger.info(f"SMS enviado via Zenvia para {to}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar SMS via Zenvia: {e}")
            return False

    def get_menu_options(self, state: str) -> List[SMSMenuOption]:
        """Retorna opções de menu para o estado."""
        try:
            state_enum = SMSState(state)
            return self.MENUS.get(state_enum, [])
        except ValueError:
            return []

    def validate_input(self, message: UnifiedMessage, session: ChannelSession) -> bool:
        """Valida entrada do usuário."""
        text = message.text.strip().upper()
        state = session.state

        # Validar CPF
        if state == SMSState.AGUARDANDO_CPF.value:
            cpf = re.sub(r"\D", "", text)
            return len(cpf) == 11

        # Validar CEP
        if state == SMSState.AGUARDANDO_CEP.value:
            cep = re.sub(r"\D", "", text)
            return len(cep) == 8

        # Validar opção de menu
        if state in [SMSState.MENU_PRINCIPAL.value, SMSState.MENU_SECUNDARIO.value]:
            options = self.get_menu_options(state)
            valid_keys = [opt.key for opt in options]
            return text in valid_keys

        return True

    async def process_message(
        self,
        message: UnifiedMessage
    ) -> ChannelResponse:
        """
        Processa mensagem SMS e retorna resposta.

        Gerencia máquina de estados do fluxo SMS.
        """
        # Obter sessão
        session = channel_session_manager.get_or_create(
            user_phone=message.user_phone or message.user_id,
            channel=ChannelType.SMS,
            initial_state=SMSState.MENU_PRINCIPAL.value
        )

        text = message.text.strip().upper()

        # Processar baseado no estado atual
        if session.state == SMSState.MENU_PRINCIPAL.value:
            return await self._handle_menu_principal(text, session)

        elif session.state == SMSState.AGUARDANDO_CPF.value:
            return await self._handle_cpf(text, session)

        elif session.state == SMSState.AGUARDANDO_CEP.value:
            return await self._handle_cep(text, session)

        elif session.state == SMSState.RESULTADO.value:
            return await self._handle_resultado(text, session)

        elif session.state == SMSState.MENU_SECUNDARIO.value:
            return await self._handle_menu_secundario(text, session)

        else:
            # Estado desconhecido, voltar ao início
            session.update_state(SMSState.MENU_PRINCIPAL.value)
            channel_session_manager.update(session)
            return self._get_welcome_response()

    async def _handle_menu_principal(
        self,
        text: str,
        session: ChannelSession
    ) -> ChannelResponse:
        """Processa seleção no menu principal."""
        options = self.MENUS[SMSState.MENU_PRINCIPAL]

        for opt in options:
            if text == opt.key:
                session.selected_option = opt.action
                if opt.next_state:
                    session.update_state(opt.next_state.value)
                    channel_session_manager.update(session)

                    if opt.next_state == SMSState.AGUARDANDO_CPF:
                        return ChannelResponse(
                            text="Digite seu CPF (apenas numeros):",
                            next_state=SMSState.AGUARDANDO_CPF.value
                        )
                    elif opt.next_state == SMSState.AGUARDANDO_CEP:
                        return ChannelResponse(
                            text="Digite seu CEP (apenas numeros):",
                            next_state=SMSState.AGUARDANDO_CEP.value
                        )

                # Ação especial (transferir atendente)
                if opt.action == "transferir_atendente":
                    return ChannelResponse(
                        text="Para falar com atendente, ligue 0800-XXX-XXXX (seg-sex 8h-17h).",
                        end_session=True
                    )

        # Opção inválida
        return ChannelResponse(
            text=f"{self.get_error_message('invalid_option')}\n\n{self._get_menu_text(SMSState.MENU_PRINCIPAL.value)}",
            next_state=SMSState.MENU_PRINCIPAL.value
        )

    async def _handle_cpf(
        self,
        text: str,
        session: ChannelSession
    ) -> ChannelResponse:
        """Processa entrada de CPF."""
        cpf = re.sub(r"\D", "", text)

        if len(cpf) != 11:
            return ChannelResponse(
                text=self.get_error_message("invalid_cpf"),
                next_state=SMSState.AGUARDANDO_CPF.value
            )

        # Validar CPF
        if not self._validate_cpf(cpf):
            return ChannelResponse(
                text="CPF invalido. Verifique e tente novamente:",
                next_state=SMSState.AGUARDANDO_CPF.value
            )

        # Salvar CPF na sessão
        session.cpf = cpf
        session.update_state(SMSState.RESULTADO.value)
        channel_session_manager.update(session)

        # Consultar baseado na opção selecionada
        result = await self._query_by_option(session)

        return ChannelResponse(
            text=f"{result}\n\nDigite M para mais opcoes ou 0 para voltar.",
            next_state=SMSState.MENU_SECUNDARIO.value
        )

    async def _handle_cep(
        self,
        text: str,
        session: ChannelSession
    ) -> ChannelResponse:
        """Processa entrada de CEP."""
        cep = re.sub(r"\D", "", text)

        if len(cep) != 8:
            return ChannelResponse(
                text="CEP invalido. Digite 8 numeros:",
                next_state=SMSState.AGUARDANDO_CEP.value
            )

        session.cep = cep
        session.update_state(SMSState.RESULTADO.value)
        channel_session_manager.update(session)

        # Buscar CRAS
        result = await self._query_cras(cep)

        return ChannelResponse(
            text=f"{result}\n\nDigite 0 para voltar ao inicio.",
            next_state=SMSState.MENU_SECUNDARIO.value
        )

    async def _handle_resultado(
        self,
        text: str,
        session: ChannelSession
    ) -> ChannelResponse:
        """Processa interação após resultado."""
        if text in ["0", "VOLTAR", "INICIO"]:
            session.update_state(SMSState.MENU_PRINCIPAL.value)
            channel_session_manager.update(session)
            return self._get_welcome_response()

        return ChannelResponse(
            text="Digite 0 para voltar ao inicio.",
            next_state=SMSState.RESULTADO.value
        )

    async def _handle_menu_secundario(
        self,
        text: str,
        session: ChannelSession
    ) -> ChannelResponse:
        """Processa menu secundário."""
        if text in ["0", "VOLTAR", "INICIO"]:
            session.update_state(SMSState.MENU_PRINCIPAL.value)
            session.cpf = None
            session.cep = None
            session.selected_option = None
            channel_session_manager.update(session)
            return self._get_welcome_response()

        if text == "M":
            return ChannelResponse(
                text=self._get_menu_text(SMSState.MENU_SECUNDARIO.value),
                next_state=SMSState.MENU_SECUNDARIO.value
            )

        return ChannelResponse(
            text="Opcao invalida. Digite M para opcoes ou 0 para voltar.",
            next_state=SMSState.MENU_SECUNDARIO.value
        )

    async def _query_by_option(self, session: ChannelSession) -> str:
        """Executa consulta baseado na opção selecionada."""
        from app.agent.orchestrator import get_orchestrator

        option = session.selected_option
        cpf = session.cpf

        try:
            orchestrator = get_orchestrator()

            if option == "consultar_beneficios":
                # Simular consulta de benefícios
                response = await orchestrator.process_message(
                    f"Consultar benefícios do CPF {cpf}",
                    session_id=session.session_id
                )
                return self._simplify_for_sms(response.text)

            elif option == "dinheiro_esquecido":
                response = await orchestrator.process_message(
                    f"Verificar dinheiro esquecido para CPF {cpf}",
                    session_id=session.session_id
                )
                return self._simplify_for_sms(response.text)

            elif option == "farmacia_popular":
                return "Farmacia Popular: envie foto da receita pelo WhatsApp para numero (11) 99999-9999"

            else:
                return "Consulta realizada. Sem resultados."

        except Exception as e:
            logger.error(f"Erro na consulta: {e}")
            return "Erro na consulta. Tente novamente."

    async def _query_cras(self, cep: str) -> str:
        """Busca CRAS pelo CEP."""
        from app.agent.orchestrator import get_orchestrator

        try:
            orchestrator = get_orchestrator()
            response = await orchestrator.process_message(
                f"Buscar CRAS próximo ao CEP {cep}",
            )
            return self._simplify_for_sms(response.text)

        except Exception as e:
            logger.error(f"Erro ao buscar CRAS: {e}")
            return "Erro ao buscar CRAS. Tente pelo 0800."

    def _validate_cpf(self, cpf: str) -> bool:
        """Valida CPF."""
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        # Primeiro dígito
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        d1 = 0 if resto < 2 else 11 - resto

        if int(cpf[9]) != d1:
            return False

        # Segundo dígito
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        d2 = 0 if resto < 2 else 11 - resto

        return int(cpf[10]) == d2

    def _get_welcome_response(self) -> ChannelResponse:
        """Retorna mensagem de boas-vindas com menu."""
        menu = self._get_menu_text(SMSState.MENU_PRINCIPAL.value)
        return ChannelResponse(
            text=f"Ta na Mao - Beneficios Sociais\n\n{menu}",
            next_state=SMSState.MENU_PRINCIPAL.value
        )


# Singleton
_sms_handler: Optional[SMSHandler] = None


def get_sms_handler(provider: str = "twilio") -> SMSHandler:
    """Obtém instância singleton do handler SMS."""
    global _sms_handler
    if _sms_handler is None:
        _sms_handler = SMSHandler(provider=provider)
    return _sms_handler
