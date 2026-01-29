"""Tool para enviar mensagens WhatsApp via Twilio.

Usado para:
- Notificar farmacias sobre pedidos
- Notificar cidadaos quando pedido esta pronto
"""

import os
import logging
from typing import Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)

# Configuracao Twilio (lazy loading)
_TWILIO_CLIENT = None


def _get_twilio_client() -> Client:
    """Retorna cliente Twilio configurado."""
    global _TWILIO_CLIENT

    if _TWILIO_CLIENT is None:
        try:
            from app.config import settings
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
        except (ImportError, AttributeError):
            account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")

        if not account_sid or not auth_token:
            raise ValueError("Credenciais Twilio nao configuradas (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)")

        _TWILIO_CLIENT = Client(account_sid, auth_token)

    return _TWILIO_CLIENT


def _get_twilio_from_number() -> str:
    """Retorna numero WhatsApp do Twilio."""
    try:
        from app.config import settings
        return settings.TWILIO_WHATSAPP_FROM
    except (ImportError, AttributeError):
        # Sandbox padrao Twilio
        return os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")


def _formatar_numero(telefone: str) -> str:
    """Formata numero para formato WhatsApp Twilio.

    Args:
        telefone: Numero em qualquer formato
            - "11999999999"
            - "+5511999999999"
            - "(11) 99999-9999"

    Returns:
        "whatsapp:+5511999999999"
    """
    # Remove tudo que nao eh numero
    numero = "".join(c for c in telefone if c.isdigit())

    # Adiciona codigo do Brasil se nao tiver
    if len(numero) == 11:  # DDD + 9 digitos
        numero = "55" + numero
    elif len(numero) == 10:  # DDD + 8 digitos (fixo)
        numero = "55" + numero

    return f"whatsapp:+{numero}"


def enviar_whatsapp(
    para: str,
    mensagem: str,
    media_url: Optional[str] = None
) -> dict:
    """Envia mensagem WhatsApp via Twilio.

    Esta tool envia mensagens WhatsApp usando a API do Twilio.
    Pode ser usada para:
    - Enviar pedido para farmacia
    - Notificar cidadao sobre status do pedido
    - Enviar documentos e checklists

    Args:
        para: Numero do destinatario
            Formatos aceitos:
            - "11999999999"
            - "+5511999999999"
            - "(11) 99999-9999"
        mensagem: Texto da mensagem (max 1600 caracteres)
        media_url: URL de midia para anexar (imagem, PDF)

    Returns:
        dict: {
            "enviado": True/False,
            "sid": "SM...",  # ID da mensagem no Twilio
            "para": "whatsapp:+5511999999999",
            "erro": "mensagem de erro se falhar"
        }

    Example:
        >>> enviar_whatsapp(
        ...     para="11999999999",
        ...     mensagem="Seu pedido #123 esta pronto para retirada!"
        ... )
        {"enviado": True, "sid": "SM1234567890"}
    """
    try:
        client = _get_twilio_client()
        from_number = _get_twilio_from_number()
        to_number = _formatar_numero(para)

        # Truncar mensagem se muito longa
        if len(mensagem) > 1600:
            mensagem = mensagem[:1597] + "..."
            logger.warning("Mensagem truncada para 1600 caracteres")

        # Preparar parametros
        params = {
            "from_": from_number,
            "to": to_number,
            "body": mensagem
        }

        # Adicionar midia se fornecida
        if media_url:
            params["media_url"] = [media_url]

        # Enviar mensagem
        message = client.messages.create(**params)

        logger.info(f"WhatsApp enviado: {message.sid} para {to_number}")

        return {
            "enviado": True,
            "sid": message.sid,
            "para": to_number,
            "status": message.status
        }

    except TwilioRestException as e:
        logger.error(f"Erro Twilio ao enviar WhatsApp: {e}")
        return {
            "enviado": False,
            "erro": f"Erro Twilio: {e.msg}",
            "codigo": e.code
        }
    except ValueError as e:
        logger.error(f"Erro de configuracao: {e}")
        return {
            "enviado": False,
            "erro": str(e)
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar WhatsApp: {e}")
        return {
            "enviado": False,
            "erro": f"Erro inesperado: {str(e)}"
        }


def enviar_pedido_farmacia(
    farmacia_whatsapp: str,
    pedido_numero: str,
    cidadao_nome: str,
    cidadao_cpf_mascarado: str,
    medicamentos_texto: str
) -> dict:
    """Envia pedido de medicamentos para farmacia.

    Mensagem formatada para farmacia confirmar preparo.

    Args:
        farmacia_whatsapp: WhatsApp da farmacia
        pedido_numero: Numero do pedido (ex: "PED-12345")
        cidadao_nome: Nome do cidadao
        cidadao_cpf_mascarado: CPF mascarado (ex: "***456789**")
        medicamentos_texto: Lista de medicamentos formatada

    Returns:
        dict com status do envio
    """
    mensagem = f"""📋 *NOVO PEDIDO - Ta na Mao*

*Pedido:* {pedido_numero}
*Cidadao:* {cidadao_nome}
*CPF:* {cidadao_cpf_mascarado}

*Medicamentos:*
{medicamentos_texto}

Para *CONFIRMAR* que pode preparar, responda:
✅ *SIM {pedido_numero}*

Para *RECUSAR* (falta estoque), responda:
❌ *NAO {pedido_numero}*

---
_Farmacia Popular - Ta na Mao_"""

    return enviar_whatsapp(para=farmacia_whatsapp, mensagem=mensagem)


def enviar_confirmacao_cidadao(
    cidadao_whatsapp: str,
    pedido_numero: str,
    farmacia_nome: str,
    farmacia_endereco: str,
    link_maps: Optional[str] = None
) -> dict:
    """Notifica cidadao que pedido esta pronto.

    Args:
        cidadao_whatsapp: WhatsApp do cidadao
        pedido_numero: Numero do pedido
        farmacia_nome: Nome da farmacia
        farmacia_endereco: Endereco da farmacia
        link_maps: Link para Google Maps (opcional)

    Returns:
        dict com status do envio
    """
    mensagem = f"""🎉 *SEU PEDIDO ESTA PRONTO!*

*Pedido:* {pedido_numero}

Seus medicamentos estao separados e prontos para retirada!

📍 *Onde retirar:*
{farmacia_nome}
{farmacia_endereco}
"""

    if link_maps:
        mensagem += f"\n🗺️ *Ver no mapa:*\n{link_maps}\n"

    mensagem += """
⏰ *Importante:* Retire em ate 24 horas.

Leve:
- Documento com foto (RG ou CNH)
- Receita medica (se aplicavel)

---
_Farmacia Popular - Ta na Mao_"""

    return enviar_whatsapp(para=cidadao_whatsapp, mensagem=mensagem)


def enviar_pedido_recusado(
    cidadao_whatsapp: str,
    pedido_numero: str,
    farmacia_nome: str,
    motivo: Optional[str] = None
) -> dict:
    """Notifica cidadao que pedido foi recusado.

    Args:
        cidadao_whatsapp: WhatsApp do cidadao
        pedido_numero: Numero do pedido
        farmacia_nome: Nome da farmacia
        motivo: Motivo da recusa (opcional)

    Returns:
        dict com status do envio
    """
    mensagem = f"""⚠️ *PEDIDO NAO DISPONIVEL*

*Pedido:* {pedido_numero}

Infelizmente a farmacia {farmacia_nome} nao pode atender seu pedido no momento."""

    if motivo:
        mensagem += f"\n\n*Motivo:* {motivo}"

    mensagem += """

💡 *O que fazer:*
Posso buscar outra farmacia perto de voce.
Basta responder "buscar farmacia" que te ajudo!

---
_Farmacia Popular - Ta na Mao_"""

    return enviar_whatsapp(para=cidadao_whatsapp, mensagem=mensagem)
