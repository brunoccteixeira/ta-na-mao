"""
Endpoints para webhook de Voz (0800/URA).

Recebe chamadas de voz do Twilio e processa através do handler de voz,
retornando TwiML para controle da chamada.
"""

import logging

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel

from app.agent.channels import (
    ChannelType,
    VoiceState,
    channel_session_manager,
)
from app.agent.channels.voice_handler import get_voice_handler
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class VoiceSessionResponse(BaseModel):
    """Response com estado da sessão de voz."""

    session_id: str
    call_sid: str
    phone: str
    state: str
    interaction_count: int
    cpf_provided: bool
    last_activity: str


def twiml_response(content: str) -> Response:
    """Retorna resposta TwiML."""
    return Response(
        content=content,
        media_type="application/xml"
    )


# =============================================================================
# Webhooks Twilio Voice
# =============================================================================

@router.post(
    "/webhook",
    summary="Webhook Principal de Voz",
    description="Recebe chamadas de voz do Twilio.",
    tags=["Voice"]
)
async def voice_webhook(
    request: Request,
    CallSid: str = Form(...),
    Caller: str = Form(None),
    From: str = Form(None),
    To: str = Form(None),
    CallStatus: str = Form(None),
    Direction: str = Form(None),
):
    """
    Webhook principal para chamadas de voz.

    Retorna TwiML com menu de boas-vindas.
    """
    try:
        handler = get_voice_handler()
        caller = Caller or From or ""

        logger.info(
            f"Chamada recebida: {CallSid} de {caller}",
            extra={
                "call_sid": CallSid,
                "caller": caller,
                "status": CallStatus,
                "direction": Direction,
            }
        )

        # Criar ou obter sessão
        session = channel_session_manager.get_or_create(
            user_phone=caller,
            channel=ChannelType.VOICE,
            initial_state=VoiceState.BOAS_VINDAS.value
        )

        # Atualizar metadados da sessão
        session.metadata["call_sid"] = CallSid
        session.metadata["to"] = To
        channel_session_manager.update(session)

        # Retornar TwiML de boas-vindas
        twiml = handler.get_twiml_welcome()

        # Atualizar estado
        session.update_state(VoiceState.MENU_PRINCIPAL.value)
        channel_session_manager.update(session)

        return twiml_response(twiml)

    except Exception as e:
        logger.error(f"Erro no webhook de voz: {e}", exc_info=True)
        handler = get_voice_handler()
        return twiml_response(handler.get_twiml_error())


@router.post(
    "/dtmf",
    summary="Processar DTMF",
    description="Processa dígitos pressionados pelo usuário.",
    tags=["Voice"]
)
async def process_dtmf(
    request: Request,
    CallSid: str = Form(...),
    Caller: str = Form(None),
    From: str = Form(None),
    Digits: str = Form(""),
):
    """
    Processa entrada DTMF (teclas do telefone).

    Retorna TwiML apropriado baseado no estado da sessão.
    """
    try:
        handler = get_voice_handler()
        caller = Caller or From or ""

        logger.info(
            f"DTMF recebido: {Digits} da chamada {CallSid}",
            extra={"call_sid": CallSid, "digits": Digits, "caller": caller}
        )

        # Obter sessão
        session = channel_session_manager.get(caller, ChannelType.VOICE)

        if not session:
            # Sessão não encontrada, voltar ao início
            session = channel_session_manager.get_or_create(
                user_phone=caller,
                channel=ChannelType.VOICE,
                initial_state=VoiceState.MENU_PRINCIPAL.value
            )

        # Processar DTMF
        twiml = await handler.process_dtmf(Digits, session)

        return twiml_response(twiml)

    except Exception as e:
        logger.error(f"Erro ao processar DTMF: {e}", exc_info=True)
        handler = get_voice_handler()
        return twiml_response(handler.get_twiml_error())


@router.post(
    "/cpf",
    summary="Processar CPF",
    description="Processa CPF digitado pelo usuário.",
    tags=["Voice"]
)
async def process_cpf(
    request: Request,
    CallSid: str = Form(...),
    Caller: str = Form(None),
    From: str = Form(None),
    Digits: str = Form(""),
):
    """
    Processa entrada de CPF (11 dígitos).

    Valida o CPF e executa a consulta apropriada.
    """
    try:
        handler = get_voice_handler()
        caller = Caller or From or ""

        logger.info(
            f"CPF recebido: ***{Digits[-4:] if len(Digits) >= 4 else '****'} da chamada {CallSid}"
        )

        session = channel_session_manager.get(caller, ChannelType.VOICE)

        if not session:
            session = channel_session_manager.get_or_create(
                user_phone=caller,
                channel=ChannelType.VOICE,
                initial_state=VoiceState.COLETANDO_CPF.value
            )

        # Processar CPF (é tratado como DTMF no estado COLETANDO_CPF)
        session.state = VoiceState.COLETANDO_CPF.value
        channel_session_manager.update(session)

        twiml = await handler.process_dtmf(Digits, session)

        return twiml_response(twiml)

    except Exception as e:
        logger.error(f"Erro ao processar CPF: {e}", exc_info=True)
        handler = get_voice_handler()
        return twiml_response(
            handler.get_twiml_gather_cpf("Ocorreu um erro. Vamos tentar novamente.")
        )


@router.post(
    "/gather-cpf",
    summary="Solicitar CPF",
    description="Retorna TwiML para coletar CPF do usuário.",
    tags=["Voice"]
)
async def gather_cpf():
    """
    Retorna TwiML para coletar CPF.

    Usado para redirect após timeout ou erro.
    """
    handler = get_voice_handler()
    return twiml_response(handler.get_twiml_gather_cpf())


@router.post(
    "/status",
    summary="Status da Chamada",
    description="Recebe callbacks de status da chamada.",
    tags=["Voice"]
)
async def call_status_callback(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    CallDuration: str = Form(None),
    Caller: str = Form(None),
    From: str = Form(None),
):
    """
    Callback de status da chamada.

    Registra métricas e limpa sessões quando a chamada termina.
    """
    caller = Caller or From or ""

    logger.info(
        f"Call Status: {CallSid} -> {CallStatus}",
        extra={
            "call_sid": CallSid,
            "status": CallStatus,
            "duration": CallDuration,
            "caller": caller,
        }
    )

    # Se a chamada terminou, limpar sessão
    if CallStatus in ["completed", "busy", "failed", "no-answer", "canceled"]:
        channel_session_manager.delete(caller, ChannelType.VOICE)
        logger.info(f"Sessão de voz encerrada para {caller}")

    # TODO: Registrar métricas de duração e status

    return {"status": "received"}


@router.post(
    "/fallback",
    summary="Fallback de Erro",
    description="Endpoint de fallback para erros na chamada.",
    tags=["Voice"]
)
async def voice_fallback(
    ErrorCode: str = Form(None),
    ErrorUrl: str = Form(None),
):
    """
    Fallback para erros de aplicação.

    Retorna mensagem de erro genérica.
    """
    logger.error(
        f"Voice fallback acionado: {ErrorCode}",
        extra={"error_code": ErrorCode, "error_url": ErrorUrl}
    )

    handler = get_voice_handler()
    return twiml_response(handler.get_twiml_error(
        "Desculpe, estamos com problemas técnicos. Por favor, tente novamente mais tarde."
    ))


# =============================================================================
# Gestão de Sessões
# =============================================================================

@router.get(
    "/session/{call_sid}",
    response_model=VoiceSessionResponse,
    summary="Estado da Sessão de Voz",
    description="Retorna estado atual da sessão de uma chamada.",
    tags=["Voice"]
)
async def get_voice_session(call_sid: str):
    """
    Retorna estado da sessão de voz.

    Args:
        call_sid: ID da chamada Twilio
    """
    # Buscar sessão pelo call_sid nos metadados
    # Isso é ineficiente, mas funciona para desenvolvimento
    for key in list(channel_session_manager._sessions.keys()):
        if key.startswith("voice:"):
            session = channel_session_manager._sessions[key]
            if session.metadata.get("call_sid") == call_sid:
                return VoiceSessionResponse(
                    session_id=session.session_id,
                    call_sid=call_sid,
                    phone=session.user_phone,
                    state=session.state,
                    interaction_count=session.interaction_count,
                    cpf_provided=session.cpf is not None,
                    last_activity=session.updated_at.isoformat(),
                )

    raise HTTPException(
        status_code=404,
        detail="Sessão não encontrada"
    )


@router.delete(
    "/session/{phone}",
    summary="Encerrar Sessão de Voz",
    description="Encerra e remove sessão de voz de um telefone.",
    tags=["Voice"]
)
async def delete_voice_session(phone: str):
    """
    Encerra sessão de voz.

    Args:
        phone: Número de telefone
    """
    phone = "".join(filter(str.isdigit, phone))

    deleted = channel_session_manager.delete(phone, ChannelType.VOICE)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada"
        )

    return {"message": "Sessão encerrada", "phone": phone}


# =============================================================================
# Endpoints de Teste
# =============================================================================

@router.get(
    "/test/welcome",
    summary="TwiML de Boas-Vindas",
    description="Retorna TwiML de boas-vindas para teste.",
    tags=["Voice", "Test"]
)
async def test_welcome_twiml():
    """Retorna TwiML de boas-vindas para debug."""
    handler = get_voice_handler()
    return twiml_response(handler.get_twiml_welcome())


@router.get(
    "/test/gather-cpf",
    summary="TwiML Coletar CPF",
    description="Retorna TwiML para coletar CPF.",
    tags=["Voice", "Test"]
)
async def test_gather_cpf_twiml():
    """Retorna TwiML de coleta de CPF para debug."""
    handler = get_voice_handler()
    return twiml_response(handler.get_twiml_gather_cpf())


@router.get(
    "/test/transfer",
    summary="TwiML Transferência",
    description="Retorna TwiML de transferência.",
    tags=["Voice", "Test"]
)
async def test_transfer_twiml():
    """Retorna TwiML de transferência para debug."""
    handler = get_voice_handler()
    return twiml_response(handler.get_twiml_transfer())


@router.get(
    "/test/goodbye",
    summary="TwiML Despedida",
    description="Retorna TwiML de despedida.",
    tags=["Voice", "Test"]
)
async def test_goodbye_twiml():
    """Retorna TwiML de despedida para debug."""
    handler = get_voice_handler()
    return twiml_response(handler.get_twiml_goodbye())


@router.post(
    "/test/simulate",
    summary="Simular Fluxo de Voz",
    description="Simula interação de voz para teste.",
    tags=["Voice", "Test"]
)
async def simulate_voice_flow(
    phone: str = Query(..., description="Número de telefone"),
    digits: str = Query(..., description="Dígitos a simular"),
):
    """
    Simula fluxo de voz.

    Apenas para ambiente de desenvolvimento.
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=403,
            detail="Endpoint de teste não disponível em produção"
        )

    handler = get_voice_handler()

    # Obter ou criar sessão
    session = channel_session_manager.get_or_create(
        user_phone=phone,
        channel=ChannelType.VOICE,
        initial_state=VoiceState.MENU_PRINCIPAL.value
    )

    # Processar DTMF
    twiml = await handler.process_dtmf(digits, session)

    return {
        "phone": phone,
        "digits": digits,
        "current_state": session.state,
        "twiml": twiml,
    }
