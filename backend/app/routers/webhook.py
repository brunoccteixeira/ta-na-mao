"""Webhook endpoints para integracoes externas.

Recebe callbacks de:
- Twilio WhatsApp (respostas das farmacias)
- Twilio WhatsApp Chat (conversas com cidadaos)
"""

import re
import logging
import httpx
import base64
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.pedido import Pedido, StatusPedido
from app.agent.tools.enviar_whatsapp import (
    enviar_confirmacao_cidadao,
    enviar_pedido_recusado
)
from app.agent.orchestrator import get_orchestrator
from app.agent.whatsapp_formatter import format_response_for_whatsapp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


def _extrair_numero_pedido(mensagem: str) -> Optional[str]:
    """Extrai numero do pedido da mensagem.

    Formatos aceitos:
    - "SIM PED-12345"
    - "NAO PED-12345"
    - "OK PED-12345"
    - "PED-12345"

    Returns:
        "PED-12345" ou None
    """
    match = re.search(r'(PED-\d{5})', mensagem.upper())
    if match:
        return match.group(1)
    return None


def _interpretar_resposta(mensagem: str) -> tuple[str, Optional[str]]:
    """Interpreta resposta da farmacia.

    Returns:
        (acao, motivo)
        acao: "CONFIRMAR" | "RECUSAR" | "DESCONHECIDO"
    """
    msg = mensagem.upper().strip()

    # Respostas positivas
    if any(p in msg for p in ["SIM", "OK", "CONFIRMO", "CONFIRMADO", "PODE", "PRONTO"]):
        return "CONFIRMAR", None

    # Respostas negativas
    if any(p in msg for p in ["NAO", "NÃO", "RECUSO", "FALTA", "SEM ESTOQUE", "INDISPONIVEL"]):
        # Tentar extrair motivo
        motivo = None
        if "FALTA" in msg or "SEM ESTOQUE" in msg:
            motivo = "Medicamento em falta"
        elif "FECHADO" in msg:
            motivo = "Farmacia fechada"
        return "RECUSAR", motivo

    return "DESCONHECIDO", None


@router.post("/whatsapp")
async def webhook_whatsapp(
    request: Request,
    From: str = Form(None),
    Body: str = Form(None),
    MessageSid: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Recebe mensagens WhatsApp via Twilio.

    Quando farmacia responde:
    - "SIM PED-12345" → Confirma pedido, notifica cidadao
    - "NAO PED-12345" → Recusa pedido, notifica cidadao

    Twilio espera resposta TwiML ou status 200.
    """
    try:
        logger.info(f"Webhook WhatsApp: From={From}, Body={Body}, SID={MessageSid}")

        if not Body:
            return Response(status_code=200)

        # Extrair numero do pedido
        pedido_numero = _extrair_numero_pedido(Body)
        if not pedido_numero:
            logger.warning(f"Mensagem sem numero de pedido: {Body}")
            # Responder pedindo o numero
            return Response(
                content="""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Por favor, inclua o numero do pedido na resposta (ex: SIM PED-12345)</Message>
</Response>""",
                media_type="application/xml"
            )

        # Buscar pedido no banco
        stmt = select(Pedido).where(Pedido.numero == pedido_numero)
        result = await db.execute(stmt)
        pedido = result.scalar_one_or_none()

        if not pedido:
            logger.warning(f"Pedido nao encontrado: {pedido_numero}")
            return Response(
                content=f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Pedido {pedido_numero} nao encontrado. Verifique o numero.</Message>
</Response>""",
                media_type="application/xml"
            )

        # Verificar se pedido ainda esta pendente
        if pedido.status != StatusPedido.PENDENTE.value:
            logger.info(f"Pedido {pedido_numero} ja processado: {pedido.status}")
            return Response(
                content=f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Pedido {pedido_numero} ja foi processado (status: {pedido.status}).</Message>
</Response>""",
                media_type="application/xml"
            )

        # Interpretar resposta
        acao, motivo = _interpretar_resposta(Body)

        if acao == "CONFIRMAR":
            # Atualizar status para PRONTO (farmacia preparou)
            pedido.atualizar_status(StatusPedido.PRONTO)
            await db.commit()

            # Notificar cidadao
            if pedido.telefone_cidadao:
                # Gerar link do Maps se tiver coordenadas
                link_maps = None
                # TODO: Buscar coordenadas da farmacia

                resultado = enviar_confirmacao_cidadao(
                    cidadao_whatsapp=pedido.telefone_cidadao,
                    pedido_numero=pedido.numero,
                    farmacia_nome=pedido.farmacia_nome,
                    farmacia_endereco="",  # TODO: Buscar endereco
                    link_maps=link_maps
                )

                if resultado.get("enviado"):
                    pedido.twilio_sid_cidadao = resultado.get("sid")
                    await db.commit()

            logger.info(f"Pedido {pedido_numero} CONFIRMADO pela farmacia")

            return Response(
                content=f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Obrigado! Pedido {pedido_numero} confirmado. O cidadao foi notificado.</Message>
</Response>""",
                media_type="application/xml"
            )

        elif acao == "RECUSAR":
            # Atualizar status para CANCELADO
            pedido.atualizar_status(StatusPedido.CANCELADO)
            pedido.observacoes = f"Recusado pela farmacia: {motivo or 'Motivo nao informado'}"
            await db.commit()

            # Notificar cidadao
            if pedido.telefone_cidadao:
                resultado = enviar_pedido_recusado(
                    cidadao_whatsapp=pedido.telefone_cidadao,
                    pedido_numero=pedido.numero,
                    farmacia_nome=pedido.farmacia_nome,
                    motivo=motivo
                )

                if resultado.get("enviado"):
                    pedido.twilio_sid_cidadao = resultado.get("sid")
                    await db.commit()

            logger.info(f"Pedido {pedido_numero} RECUSADO pela farmacia: {motivo}")

            return Response(
                content=f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Entendido. Pedido {pedido_numero} cancelado. O cidadao foi notificado.</Message>
</Response>""",
                media_type="application/xml"
            )

        else:
            # Resposta nao compreendida
            return Response(
                content=f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Nao entendi sua resposta. Para confirmar: SIM {pedido_numero}. Para recusar: NAO {pedido_numero}</Message>
</Response>""",
                media_type="application/xml"
            )

    except Exception as e:
        logger.error(f"Erro no webhook WhatsApp: {e}")
        return Response(status_code=200)  # Sempre retornar 200 para Twilio


@router.get("/whatsapp")
async def webhook_whatsapp_verify(request: Request):
    """Verificacao do webhook (Twilio pode fazer GET para verificar)."""
    return {"status": "ok", "message": "Webhook WhatsApp ativo"}


@router.post("/whatsapp/status")
async def webhook_whatsapp_status(
    MessageSid: str = Form(None),
    MessageStatus: str = Form(None),
    To: str = Form(None)
):
    """Recebe atualizacoes de status de mensagens.

    Status possiveis: queued, sent, delivered, read, failed, undelivered
    """
    logger.info(f"Status WhatsApp: SID={MessageSid}, Status={MessageStatus}, To={To}")

    # TODO: Atualizar status no banco se necessario
    # Util para saber se mensagem foi entregue/lida

    return Response(status_code=200)


# =============================================================================
# WhatsApp Chat (Conversa com cidadaos via Orchestrator)
# =============================================================================

def _normalize_phone(phone: str) -> str:
    """Normaliza numero de telefone para uso como session_id.

    Args:
        phone: Numero no formato "whatsapp:+5511999999999"

    Returns:
        Numero limpo: "5511999999999"
    """
    if not phone:
        return ""

    # Remove prefixo whatsapp:
    phone = phone.replace("whatsapp:", "")

    # Remove caracteres nao numericos (exceto +)
    phone = re.sub(r"[^\d+]", "", phone)

    # Remove + inicial
    phone = phone.lstrip("+")

    return phone


async def _fetch_media_base64(media_url: str) -> Optional[str]:
    """Baixa media do Twilio e converte para base64.

    Args:
        media_url: URL da media no Twilio

    Returns:
        String base64 da imagem ou None se falhar
    """
    if not media_url:
        return None

    try:
        from app.config import settings

        # Twilio requer autenticacao para baixar medias
        async with httpx.AsyncClient() as client:
            response = await client.get(
                media_url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                timeout=30.0,
                follow_redirects=True
            )

            if response.status_code == 200:
                # Detectar content type
                content_type = response.headers.get("content-type", "image/jpeg")

                # Converter para base64
                b64_content = base64.b64encode(response.content).decode("utf-8")

                # Retornar como data URL
                return f"data:{content_type};base64,{b64_content}"

    except Exception as e:
        logger.error(f"Erro ao baixar media do Twilio: {e}")

    return None


@router.post("/whatsapp/chat")
async def webhook_whatsapp_chat(
    request: Request,
    From: str = Form(None),
    To: str = Form(None),
    Body: str = Form(None),
    MessageSid: str = Form(None),
    NumMedia: str = Form("0"),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None),
    Latitude: str = Form(None),
    Longitude: str = Form(None),
    ProfileName: str = Form(None),
):
    """Recebe mensagens de cidadaos via WhatsApp e processa com Orchestrator.

    Este endpoint permite conversas completas com o agente Ta na Mao via WhatsApp.
    O numero de telefone e usado como identificador de sessao.

    Parametros Twilio:
        From: Numero do remetente (whatsapp:+5511999999999)
        To: Numero do destinatario (nosso numero)
        Body: Texto da mensagem
        MessageSid: ID unico da mensagem
        NumMedia: Quantidade de arquivos de media
        MediaUrl0: URL da primeira media (imagem)
        MediaContentType0: Tipo da media (image/jpeg, etc)
        Latitude/Longitude: Localizacao compartilhada
        ProfileName: Nome do perfil WhatsApp

    Retorna:
        TwiML com resposta do agente formatada para WhatsApp
    """
    try:
        logger.info(
            f"WhatsApp Chat: From={From}, Body={Body[:50] if Body else 'N/A'}..., "
            f"NumMedia={NumMedia}, ProfileName={ProfileName}"
        )

        # Validar entrada
        if not From:
            logger.warning("Webhook chamado sem numero de origem")
            return Response(status_code=200)

        if not Body and NumMedia == "0":
            logger.warning("Webhook chamado sem mensagem ou media")
            return Response(
                content="""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Oi! Manda uma mensagem ou foto da receita que eu te ajudo!</Message>
</Response>""",
                media_type="application/xml"
            )

        # Normalizar telefone para usar como session_id
        phone = _normalize_phone(From)
        session_id = f"whatsapp:{phone}"

        # Obter orchestrator
        orchestrator = get_orchestrator()

        # Atualizar contexto com geolocalizacao se disponivel
        if Latitude and Longitude:
            try:
                session = orchestrator.get_session(session_id)
                if session:
                    session.citizen.update_from_geolocation(
                        latitude=float(Latitude),
                        longitude=float(Longitude)
                    )
                    logger.info(f"Geolocalizacao atualizada: {Latitude}, {Longitude}")
            except Exception as e:
                logger.warning(f"Erro ao atualizar geolocalizacao: {e}")

        # Baixar imagem se houver
        image_base64 = None
        if int(NumMedia) > 0 and MediaUrl0:
            image_base64 = await _fetch_media_base64(MediaUrl0)
            if image_base64:
                logger.info(f"Imagem baixada com sucesso: {MediaContentType0}")

        # Mensagem padrao se so enviou imagem
        message = Body or "Enviando imagem..."

        # Processar mensagem com orchestrator
        response = await orchestrator.process_message(
            message=message,
            session_id=session_id,
            image_base64=image_base64
        )

        # Converter resposta A2UI para TwiML
        twiml = format_response_for_whatsapp(response)

        logger.info(f"Resposta enviada para {phone}")

        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Erro no webhook WhatsApp Chat: {e}", exc_info=True)

        # Resposta de erro amigavel
        return Response(
            content="""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Ops, tive um probleminha. Tenta de novo em alguns segundos?</Message>
</Response>""",
            media_type="application/xml"
        )


@router.get("/whatsapp/chat")
async def webhook_whatsapp_chat_verify(request: Request):
    """Verificacao do webhook de chat (Twilio pode fazer GET para verificar)."""
    return {
        "status": "ok",
        "message": "Webhook WhatsApp Chat ativo",
        "version": "v2"
    }
