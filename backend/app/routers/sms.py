"""
Endpoints para webhook SMS.

Recebe mensagens SMS de provedores (Twilio, Zenvia, Infobip)
e processa através do handler SMS.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from app.agent.channels import (
    ChannelType,
    channel_session_manager,
)
from app.agent.channels.sms_handler import get_sms_handler
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class SMSWebhookRequest(BaseModel):
    """Request body para webhook SMS (formato JSON)."""

    from_number: str
    to_number: str
    body: str
    message_id: Optional[str] = None
    provider: Optional[str] = "generic"


class SMSStatusRequest(BaseModel):
    """Request body para status de entrega SMS."""

    message_id: str
    status: str  # sent, delivered, failed
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class SMSSessionResponse(BaseModel):
    """Response com estado da sessão SMS."""

    session_id: str
    phone: str
    state: str
    interaction_count: int
    cpf_provided: bool
    last_activity: str


# =============================================================================
# Webhooks Twilio
# =============================================================================

@router.post(
    "/webhook/twilio",
    response_class=PlainTextResponse,
    summary="Webhook Twilio SMS",
    description="Recebe mensagens SMS do Twilio e retorna resposta.",
    tags=["SMS"]
)
async def twilio_sms_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    MessageSid: str = Form(None),
    NumMedia: int = Form(0),
):
    """
    Webhook para receber SMS do Twilio.

    Processa a mensagem e retorna TwiML com resposta.
    """
    try:
        handler = get_sms_handler(provider="twilio")

        # Parsear mensagem
        raw_data = {
            "Body": Body,
            "From": From,
            "To": To,
            "MessageSid": MessageSid or "",
            "NumMedia": NumMedia,
        }

        message = await handler.parse_incoming(raw_data)
        logger.info(
            f"SMS recebido de {message.user_phone}: {message.text[:50]}..."
        )

        # Processar mensagem
        response = await handler.process_message(message)

        # Enviar resposta via Twilio
        success = await handler.send_response(
            response=response,
            to=message.user_phone,
            from_number=To,
        )

        if not success:
            logger.warning(f"Falha ao enviar resposta SMS para {message.user_phone}")

        # Retornar TwiML vazio (resposta já enviada via API)
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>"""

    except Exception as e:
        logger.error(f"Erro no webhook Twilio SMS: {e}", exc_info=True)
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Erro no sistema. Tente novamente.</Message>
</Response>"""


@router.post(
    "/webhook/twilio/status",
    summary="Status de entrega Twilio",
    description="Recebe callbacks de status de entrega do Twilio.",
    tags=["SMS"]
)
async def twilio_status_callback(
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    To: str = Form(None),
    ErrorCode: str = Form(None),
    ErrorMessage: str = Form(None),
):
    """
    Callback de status de entrega do Twilio.

    Registra status para métricas e debugging.
    """
    logger.info(
        f"SMS Status: {MessageSid} -> {MessageStatus}",
        extra={
            "message_sid": MessageSid,
            "status": MessageStatus,
            "to": To,
            "error_code": ErrorCode,
            "error_message": ErrorMessage,
        }
    )

    # TODO: Registrar métricas de entrega

    return {"status": "received"}


# =============================================================================
# Webhooks Zenvia
# =============================================================================

@router.post(
    "/webhook/zenvia",
    summary="Webhook Zenvia SMS",
    description="Recebe mensagens SMS da Zenvia.",
    tags=["SMS"]
)
async def zenvia_sms_webhook(request: Request):
    """
    Webhook para receber SMS da Zenvia.

    Formato esperado:
    {
        "id": "message-id",
        "from": "+5511999999999",
        "to": "28282",
        "contents": [{"type": "text", "text": "mensagem"}]
    }
    """
    try:
        data = await request.json()
        handler = get_sms_handler(provider="zenvia")

        # Extrair texto
        contents = data.get("contents", [])
        text = ""
        for content in contents:
            if content.get("type") == "text":
                text = content.get("text", "")
                break

        raw_data = {
            "from": data.get("from", ""),
            "to": data.get("to", ""),
            "body": text,
            "id": data.get("id", ""),
        }

        message = await handler.parse_incoming(raw_data)
        logger.info(
            f"SMS Zenvia de {message.user_phone}: {message.text[:50]}..."
        )

        # Processar mensagem
        response = await handler.process_message(message)

        # Enviar resposta
        await handler.send_response(
            response=response,
            to=message.user_phone,
        )

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"Erro no webhook Zenvia SMS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/webhook/zenvia/status",
    summary="Status de entrega Zenvia",
    description="Recebe callbacks de status da Zenvia.",
    tags=["SMS"]
)
async def zenvia_status_callback(request: Request):
    """Callback de status da Zenvia."""
    data = await request.json()

    logger.info(
        f"Zenvia Status: {data.get('id')} -> {data.get('status')}",
        extra=data
    )

    return {"status": "received"}


# =============================================================================
# Webhook Genérico
# =============================================================================

@router.post(
    "/webhook",
    summary="Webhook SMS Genérico",
    description="Webhook genérico para qualquer provedor SMS.",
    tags=["SMS"]
)
async def generic_sms_webhook(request: SMSWebhookRequest):
    """
    Webhook genérico para SMS.

    Aceita formato JSON padronizado.
    """
    try:
        provider = request.provider or "twilio"
        handler = get_sms_handler(provider=provider)

        raw_data = {
            "From" if provider == "twilio" else "from": request.from_number,
            "To" if provider == "twilio" else "to": request.to_number,
            "Body" if provider == "twilio" else "body": request.body,
            "MessageSid" if provider == "twilio" else "id": request.message_id or "",
        }

        message = await handler.parse_incoming(raw_data)
        response = await handler.process_message(message)

        await handler.send_response(
            response=response,
            to=message.user_phone,
        )

        return {
            "status": "processed",
            "session_id": message.session_id,
            "response_text": response.text[:100],
        }

    except Exception as e:
        logger.error(f"Erro no webhook SMS genérico: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Gestão de Sessões
# =============================================================================

@router.get(
    "/session/{phone}",
    response_model=SMSSessionResponse,
    summary="Estado da Sessão SMS",
    description="Retorna estado atual da sessão SMS de um telefone.",
    tags=["SMS"]
)
async def get_sms_session(phone: str):
    """
    Retorna estado da sessão SMS.

    Args:
        phone: Número de telefone (formato E.164 ou nacional)
    """
    # Normalizar telefone
    phone = "".join(filter(str.isdigit, phone))

    session = channel_session_manager.get(phone, ChannelType.SMS)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada"
        )

    return SMSSessionResponse(
        session_id=session.session_id,
        phone=session.user_phone,
        state=session.state,
        interaction_count=session.interaction_count,
        cpf_provided=session.cpf is not None,
        last_activity=session.updated_at.isoformat(),
    )


@router.delete(
    "/session/{phone}",
    summary="Encerrar Sessão SMS",
    description="Encerra e remove sessão SMS de um telefone.",
    tags=["SMS"]
)
async def delete_sms_session(phone: str):
    """
    Encerra sessão SMS.

    Args:
        phone: Número de telefone
    """
    phone = "".join(filter(str.isdigit, phone))

    deleted = channel_session_manager.delete(phone, ChannelType.SMS)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada"
        )

    return {"message": "Sessão encerrada", "phone": phone}


@router.post(
    "/sessions/cleanup",
    summary="Limpar Sessões Expiradas",
    description="Remove sessões SMS inativas há mais de N minutos.",
    tags=["SMS"]
)
async def cleanup_sms_sessions(
    max_age_minutes: int = Query(30, ge=5, le=1440)
):
    """
    Remove sessões expiradas.

    Args:
        max_age_minutes: Idade máxima em minutos (padrão: 30)
    """
    removed = channel_session_manager.cleanup_expired(max_age_minutes)

    return {
        "message": f"{removed} sessões removidas",
        "max_age_minutes": max_age_minutes
    }


# =============================================================================
# Endpoints de Teste
# =============================================================================

@router.post(
    "/test/send",
    summary="Enviar SMS de Teste",
    description="Endpoint para testar envio de SMS (desenvolvimento).",
    tags=["SMS", "Test"]
)
async def test_send_sms(
    to: str = Query(..., description="Número de destino"),
    message: str = Query(..., description="Mensagem a enviar"),
    provider: str = Query("twilio", description="Provedor SMS"),
):
    """
    Envia SMS de teste.

    Apenas para ambiente de desenvolvimento.
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=403,
            detail="Endpoint de teste não disponível em produção"
        )

    from app.agent.channels.base import ChannelResponse

    handler = get_sms_handler(provider=provider)
    response = ChannelResponse(text=message)

    success = await handler.send_response(response, to)

    return {
        "success": success,
        "to": to,
        "message": message[:50],
        "provider": provider,
    }


@router.get(
    "/test/menu",
    summary="Ver Menu SMS",
    description="Retorna texto do menu principal SMS.",
    tags=["SMS", "Test"]
)
async def get_sms_menu():
    """Retorna menu SMS para debug."""
    handler = get_sms_handler()
    welcome = handler._get_welcome_response()

    return {
        "menu_text": welcome.text,
        "state": welcome.next_state,
    }
