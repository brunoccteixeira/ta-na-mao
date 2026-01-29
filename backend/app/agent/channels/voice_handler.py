"""
Handler para canal de Voz (0800/URA).

Implementa navegação por DTMF (teclas do telefone) e
respostas via TTS (Text-to-Speech).
"""

import logging
import re
from typing import Any, Dict, List, Optional

from .base import (
    ChannelHandler,
    ChannelResponse,
    ChannelSession,
    ChannelType,
    VoiceMenuOption,
    VoiceState,
    UnifiedMessage,
    channel_session_manager,
)

logger = logging.getLogger(__name__)


class VoiceHandler(ChannelHandler):
    """
    Handler para canal de voz.

    Implementa fluxo URA (IVR) com navegação por DTMF
    e respostas via TTS.
    """

    # Configurações de voz
    DEFAULT_VOICE = "Polly.Camila"
    DEFAULT_LANGUAGE = "pt-BR"

    # Menus por estado
    MENUS: Dict[VoiceState, List[VoiceMenuOption]] = {
        VoiceState.MENU_PRINCIPAL: [
            VoiceMenuOption(
                digit="1",
                label="consultar seus benefícios",
                action="consultar_beneficios",
                next_state=VoiceState.COLETANDO_CPF
            ),
            VoiceMenuOption(
                digit="2",
                label="verificar dinheiro esquecido",
                action="dinheiro_esquecido",
                next_state=VoiceState.COLETANDO_CPF
            ),
            VoiceMenuOption(
                digit="3",
                label="informações sobre Farmácia Popular",
                action="farmacia_popular",
                next_state=VoiceState.RESULTADO
            ),
            VoiceMenuOption(
                digit="4",
                label="encontrar o CRAS mais próximo",
                action="buscar_cras",
                next_state=VoiceState.COLETANDO_CPF
            ),
            VoiceMenuOption(
                digit="9",
                label="falar com um atendente",
                action="transferir_atendente",
                next_state=VoiceState.TRANSFERINDO
            ),
        ],
        VoiceState.MENU_OPCOES: [
            VoiceMenuOption(
                digit="1",
                label="ouvir novamente",
                action="repetir",
                next_state=VoiceState.RESULTADO
            ),
            VoiceMenuOption(
                digit="2",
                label="fazer nova consulta",
                action="nova_consulta",
                next_state=VoiceState.MENU_PRINCIPAL
            ),
            VoiceMenuOption(
                digit="9",
                label="falar com atendente",
                action="transferir_atendente",
                next_state=VoiceState.TRANSFERINDO
            ),
            VoiceMenuOption(
                digit="0",
                label="encerrar",
                action="encerrar",
                next_state=VoiceState.DESPEDIDA
            ),
        ],
    }

    def __init__(self, provider: str = "twilio"):
        """
        Inicializa handler de voz.

        Args:
            provider: Provedor de voz (twilio, etc.)
        """
        self.provider = provider
        self.voice = self.DEFAULT_VOICE
        self.language = self.DEFAULT_LANGUAGE

    @property
    def channel_type(self) -> ChannelType:
        return ChannelType.VOICE

    async def parse_incoming(self, raw_data: Dict[str, Any]) -> UnifiedMessage:
        """
        Converte webhook de voz para mensagem unificada.

        Suporta formato Twilio.
        """
        # Formato Twilio Voice
        call_sid = raw_data.get("CallSid", "")
        caller = raw_data.get("Caller", raw_data.get("From", ""))
        digits = raw_data.get("Digits", "")
        speech_result = raw_data.get("SpeechResult", "")

        # Normalizar telefone
        caller = self._normalize_phone(caller)

        # Obter ou criar sessão
        session = channel_session_manager.get_or_create(
            user_phone=caller,
            channel=ChannelType.VOICE,
            initial_state=VoiceState.BOAS_VINDAS.value
        )

        # Texto é DTMF ou resultado de speech-to-text
        text = digits or speech_result

        return UnifiedMessage(
            channel=ChannelType.VOICE,
            message_id=call_sid,
            session_id=session.session_id,
            user_id=caller,
            user_phone=caller,
            text=text,
            dtmf_digits=digits,
            channel_state=session.state,
            metadata={
                "provider": "twilio",
                "call_sid": call_sid,
                "call_status": raw_data.get("CallStatus", ""),
                "direction": raw_data.get("Direction", ""),
            }
        )

    def _normalize_phone(self, phone: str) -> str:
        """Normaliza número de telefone."""
        phone = re.sub(r"\D", "", phone)
        if len(phone) == 11 and not phone.startswith("55"):
            phone = f"55{phone}"
        return phone

    async def format_response(
        self,
        agent_response: Dict[str, Any],
        session: ChannelSession
    ) -> ChannelResponse:
        """
        Formata resposta do agente para TTS.

        Gera SSML otimizado para leitura em voz.
        """
        text = agent_response.get("text", "")
        state = session.state

        # Converter para fala natural
        speech_text = self._text_to_speech(text)

        # Gerar SSML
        ssml = self._generate_ssml(speech_text, state)

        return ChannelResponse(
            text=speech_text,
            ssml=ssml,
            voice=self.voice,
            language=self.language,
            gather_digits=self._should_gather(state),
            num_digits=self._get_num_digits(state),
            next_state=state,
        )

    def _text_to_speech(self, text: str) -> str:
        """Converte texto para formato adequado para TTS."""
        # Remover markdown
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"#+ ", "", text)

        # Converter símbolos
        text = text.replace("R$", "reais ")
        text = text.replace("%", " por cento")
        text = text.replace("&", " e ")

        # Remover emojis
        text = re.sub(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]",
            "",
            text
        )

        # Converter listas em frases
        text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)

        # Limpar espaços extras
        text = re.sub(r"\n{2,}", ". ", text)
        text = re.sub(r"\n", ", ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _generate_ssml(self, text: str, state: str) -> str:
        """Gera SSML para o texto."""
        # Adicionar pausas naturais
        text = text.replace(". ", '. <break time="500ms"/> ')
        text = text.replace(", ", ', <break time="200ms"/> ')

        ssml = f"""<speak>
    <prosody rate="95%">
        {text}
    </prosody>
</speak>"""

        return ssml

    def _should_gather(self, state: str) -> bool:
        """Verifica se deve coletar DTMF."""
        gathering_states = [
            VoiceState.MENU_PRINCIPAL.value,
            VoiceState.COLETANDO_CPF.value,
            VoiceState.MENU_OPCOES.value,
        ]
        return state in gathering_states

    def _get_num_digits(self, state: str) -> int:
        """Retorna número de dígitos esperados."""
        if state == VoiceState.COLETANDO_CPF.value:
            return 11
        return 1

    async def send_response(
        self,
        response: ChannelResponse,
        to: str,
        **kwargs
    ) -> bool:
        """
        Envia resposta de voz.

        Note: Para voz, geralmente retornamos TwiML em vez de enviar.
        Este método é para chamadas outbound.
        """
        logger.info(f"Voice response prepared for {to}")
        return True

    def get_menu_options(self, state: str) -> List[VoiceMenuOption]:
        """Retorna opções de menu para o estado."""
        try:
            state_enum = VoiceState(state)
            return self.MENUS.get(state_enum, [])
        except ValueError:
            return []

    def get_twiml_welcome(self) -> str:
        """Gera TwiML para boas-vindas."""
        menu_text = self._get_menu_speech(VoiceState.MENU_PRINCIPAL)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{self.voice}" language="{self.language}">
        <prosody rate="95%">
            Bem-vindo ao Tá na Mão, seu assistente de benefícios sociais.
            <break time="500ms"/>
        </prosody>
    </Say>
    <Gather numDigits="1" action="/api/v1/voice/dtmf" method="POST" timeout="10">
        <Say voice="{self.voice}" language="{self.language}">
            <prosody rate="95%">
                {menu_text}
            </prosody>
        </Say>
    </Gather>
    <Say voice="{self.voice}" language="{self.language}">
        Não recebi sua resposta. Por favor, ligue novamente.
    </Say>
    <Hangup/>
</Response>"""

    def get_twiml_gather_cpf(self, prompt: str = None) -> str:
        """Gera TwiML para coletar CPF."""
        if not prompt:
            prompt = "Por favor, digite os 11 números do seu C P F usando o teclado do telefone."

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="11" action="/api/v1/voice/cpf" method="POST" timeout="15">
        <Say voice="{self.voice}" language="{self.language}">
            <prosody rate="90%">
                {prompt}
            </prosody>
        </Say>
    </Gather>
    <Say voice="{self.voice}" language="{self.language}">
        Não recebi o C P F. Vou repetir.
    </Say>
    <Redirect>/api/v1/voice/gather-cpf</Redirect>
</Response>"""

    def get_twiml_result(self, result_text: str, session: ChannelSession) -> str:
        """Gera TwiML para exibir resultado."""
        speech = self._text_to_speech(result_text)
        menu_text = self._get_menu_speech(VoiceState.MENU_OPCOES)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{self.voice}" language="{self.language}">
        <prosody rate="95%">
            {speech}
            <break time="1s"/>
        </prosody>
    </Say>
    <Gather numDigits="1" action="/api/v1/voice/dtmf" method="POST" timeout="10">
        <Say voice="{self.voice}" language="{self.language}">
            <prosody rate="95%">
                {menu_text}
            </prosody>
        </Say>
    </Gather>
    <Say voice="{self.voice}" language="{self.language}">
        Obrigado por usar o Tá na Mão. Até logo.
    </Say>
    <Hangup/>
</Response>"""

    def get_twiml_transfer(self) -> str:
        """Gera TwiML para transferência para atendente."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{self.voice}" language="{self.language}">
        <prosody rate="95%">
            Vou transferir você para um atendente.
            <break time="500ms"/>
            Por favor, aguarde na linha.
        </prosody>
    </Say>
    <Dial timeout="30">
        <Number>+5508001234567</Number>
    </Dial>
    <Say voice="{self.voice}" language="{self.language}">
        Não foi possível completar a transferência. Por favor, ligue novamente.
    </Say>
    <Hangup/>
</Response>"""

    def get_twiml_goodbye(self) -> str:
        """Gera TwiML para despedida."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{self.voice}" language="{self.language}">
        <prosody rate="95%">
            Obrigado por usar o Tá na Mão.
            <break time="300ms"/>
            Lembre-se: você tem direitos!
            <break time="300ms"/>
            Até logo.
        </prosody>
    </Say>
    <Hangup/>
</Response>"""

    def get_twiml_error(self, message: str = None) -> str:
        """Gera TwiML para erro."""
        if not message:
            message = "Desculpe, ocorreu um erro. Por favor, tente novamente."

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{self.voice}" language="{self.language}">
        {message}
    </Say>
    <Redirect>/api/v1/voice/webhook</Redirect>
</Response>"""

    def get_twiml_invalid_input(self, state: str) -> str:
        """Gera TwiML para entrada inválida."""
        if state == VoiceState.COLETANDO_CPF.value:
            return self.get_twiml_gather_cpf(
                "C P F inválido. Por favor, digite novamente os 11 números."
            )

        menu_text = self._get_menu_speech(VoiceState.MENU_PRINCIPAL)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{self.voice}" language="{self.language}">
        Opção inválida.
        <break time="300ms"/>
    </Say>
    <Gather numDigits="1" action="/api/v1/voice/dtmf" method="POST" timeout="10">
        <Say voice="{self.voice}" language="{self.language}">
            <prosody rate="95%">
                {menu_text}
            </prosody>
        </Say>
    </Gather>
    <Hangup/>
</Response>"""

    def _get_menu_speech(self, state: VoiceState) -> str:
        """Gera texto do menu para TTS."""
        options = self.MENUS.get(state, [])
        if not options:
            return ""

        parts = []
        for opt in options:
            parts.append(f"Para {opt.label}, digite {opt.digit}.")

        return " <break time='300ms'/> ".join(parts)

    async def process_dtmf(
        self,
        digits: str,
        session: ChannelSession
    ) -> str:
        """
        Processa entrada DTMF e retorna TwiML.

        Args:
            digits: Dígitos pressionados
            session: Sessão do usuário

        Returns:
            str: TwiML para resposta
        """
        state = session.state

        # Menu principal
        if state == VoiceState.BOAS_VINDAS.value or state == VoiceState.MENU_PRINCIPAL.value:
            return await self._handle_menu_principal(digits, session)

        # Coletando CPF
        if state == VoiceState.COLETANDO_CPF.value:
            return await self._handle_cpf(digits, session)

        # Menu de opções
        if state == VoiceState.MENU_OPCOES.value:
            return await self._handle_menu_opcoes(digits, session)

        # Estado desconhecido
        session.update_state(VoiceState.MENU_PRINCIPAL.value)
        channel_session_manager.update(session)
        return self.get_twiml_welcome()

    async def _handle_menu_principal(
        self,
        digits: str,
        session: ChannelSession
    ) -> str:
        """Processa seleção no menu principal."""
        options = self.MENUS[VoiceState.MENU_PRINCIPAL]

        for opt in options:
            if digits == opt.digit:
                session.selected_option = opt.action

                if opt.next_state == VoiceState.COLETANDO_CPF:
                    session.update_state(VoiceState.COLETANDO_CPF.value)
                    channel_session_manager.update(session)
                    return self.get_twiml_gather_cpf()

                elif opt.next_state == VoiceState.RESULTADO:
                    session.update_state(VoiceState.RESULTADO.value)
                    channel_session_manager.update(session)
                    # Resposta genérica para Farmácia Popular
                    return self.get_twiml_result(
                        "Para usar o Farmácia Popular, vá a uma farmácia credenciada "
                        "com receita médica e documento com C P F. "
                        "Medicamentos para hipertensão, diabetes e asma são gratuitos.",
                        session
                    )

                elif opt.next_state == VoiceState.TRANSFERINDO:
                    return self.get_twiml_transfer()

        # Opção inválida
        return self.get_twiml_invalid_input(VoiceState.MENU_PRINCIPAL.value)

    async def _handle_cpf(self, digits: str, session: ChannelSession) -> str:
        """Processa entrada de CPF."""
        cpf = re.sub(r"\D", "", digits)

        if len(cpf) != 11 or not self._validate_cpf(cpf):
            return self.get_twiml_gather_cpf(
                "C P F inválido. Por favor, digite novamente os 11 números."
            )

        session.cpf = cpf
        session.update_state(VoiceState.RESULTADO.value)
        channel_session_manager.update(session)

        # Executar consulta
        result = await self._query_by_option(session)

        return self.get_twiml_result(result, session)

    async def _handle_menu_opcoes(
        self,
        digits: str,
        session: ChannelSession
    ) -> str:
        """Processa menu de opções após resultado."""
        if digits == "1":
            # Repetir resultado
            result = await self._query_by_option(session)
            return self.get_twiml_result(result, session)

        elif digits == "2":
            # Nova consulta
            session.update_state(VoiceState.MENU_PRINCIPAL.value)
            session.cpf = None
            session.selected_option = None
            channel_session_manager.update(session)
            return self.get_twiml_welcome()

        elif digits == "9":
            return self.get_twiml_transfer()

        elif digits == "0":
            return self.get_twiml_goodbye()

        return self.get_twiml_invalid_input(VoiceState.MENU_OPCOES.value)

    async def _query_by_option(self, session: ChannelSession) -> str:
        """Executa consulta baseado na opção selecionada."""
        from app.agent.orchestrator import get_orchestrator

        option = session.selected_option
        cpf = session.cpf

        try:
            orchestrator = get_orchestrator()

            if option == "consultar_beneficios":
                response = await orchestrator.process_message(
                    f"Consultar benefícios do CPF {cpf}",
                    session_id=session.session_id
                )
                return self._text_to_speech(response.text)

            elif option == "dinheiro_esquecido":
                response = await orchestrator.process_message(
                    f"Verificar dinheiro esquecido para CPF {cpf}",
                    session_id=session.session_id
                )
                return self._text_to_speech(response.text)

            elif option == "buscar_cras":
                response = await orchestrator.process_message(
                    f"Buscar CRAS para o CPF {cpf}",
                    session_id=session.session_id
                )
                return self._text_to_speech(response.text)

            else:
                return "Consulta realizada. Não encontramos informações."

        except Exception as e:
            logger.error(f"Erro na consulta por voz: {e}")
            return "Desculpe, ocorreu um erro na consulta. Por favor, tente novamente."

    def _validate_cpf(self, cpf: str) -> bool:
        """Valida CPF."""
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        d1 = 0 if resto < 2 else 11 - resto

        if int(cpf[9]) != d1:
            return False

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        d2 = 0 if resto < 2 else 11 - resto

        return int(cpf[10]) == d2


# Singleton
_voice_handler: Optional[VoiceHandler] = None


def get_voice_handler(provider: str = "twilio") -> VoiceHandler:
    """Obtém instância singleton do handler de voz."""
    global _voice_handler
    if _voice_handler is None:
        _voice_handler = VoiceHandler(provider=provider)
    return _voice_handler
