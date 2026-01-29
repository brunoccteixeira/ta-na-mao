"""
Formatador de respostas A2UI para WhatsApp/TwiML.

Converte AgentResponse estruturado para formato compatível com WhatsApp:
- Texto formatado com emojis
- UIComponents viram blocos de texto
- Actions viram sugestões no final
"""

import html
from typing import List, Dict, Any
from .response_types import AgentResponse, UIComponent, Action, UIComponentType, ActionType


def escape_xml(text: str) -> str:
    """Escapa caracteres especiais para XML."""
    return html.escape(text)


def format_pharmacy_card(data: Dict[str, Any]) -> str:
    """Formata card de farmácia para texto."""
    lines = []

    name = data.get("name", data.get("nome", "Farmácia"))
    address = data.get("address", data.get("endereco", ""))
    distance = data.get("distance", data.get("distancia", ""))
    phone = data.get("phone", data.get("telefone", ""))
    hours = data.get("hours", data.get("horario", ""))

    lines.append(f"*{name}*")

    if address:
        lines.append(f"  {address}")

    if distance:
        lines.append(f"  {distance}")

    if phone:
        lines.append(f"  Tel: {phone}")

    if hours:
        lines.append(f"  Horário: {hours}")

    # Links
    links = data.get("links", {})
    if links.get("direcoes"):
        lines.append(f"  Como chegar: {links['direcoes']}")

    return "\n".join(lines)


def format_medication_list(data: Dict[str, Any]) -> str:
    """Formata lista de medicamentos para texto."""
    lines = ["*Medicamentos:*"]

    medications = data.get("medications", data.get("medicamentos", []))

    for med in medications:
        name = med.get("name", med.get("nome", ""))
        dosage = med.get("dosage", med.get("dosagem", ""))
        quantity = med.get("quantity", med.get("quantidade", ""))
        free = med.get("free", med.get("gratuito", False))

        emoji = "" if free else ""
        med_text = f"  {emoji} {name}"

        if dosage:
            med_text += f" {dosage}"

        if quantity:
            med_text += f" (x{quantity})"

        lines.append(med_text)

    # Resumo
    all_free = data.get("all_free", data.get("todos_gratuitos", False))
    savings = data.get("estimated_savings", data.get("economia_estimada", ""))

    if all_free:
        lines.append("\n*Todos GRATUITOS pelo Farmácia Popular!*")

    if savings:
        lines.append(f"Economia estimada: {savings}")

    return "\n".join(lines)


def format_checklist(data: Dict[str, Any]) -> str:
    """Formata checklist de documentos para texto."""
    title = data.get("title", data.get("titulo", "Documentos Necessários"))
    items = data.get("items", data.get("itens", []))

    lines = [f"*{title}*"]

    for item in items:
        if isinstance(item, dict):
            text = item.get("text", item.get("texto", ""))
            required = item.get("required", item.get("obrigatorio", True))
            checked = item.get("checked", item.get("marcado", False))
        else:
            text = str(item)
            required = True
            checked = False

        # Emoji baseado no status
        if checked:
            emoji = ""
        elif required:
            emoji = ""
        else:
            emoji = ""

        lines.append(f"  {emoji} {text}")

    return "\n".join(lines)


def format_benefit_card(data: Dict[str, Any]) -> str:
    """Formata card de benefício para texto."""
    name = data.get("name", data.get("nome", "Benefício"))
    status = data.get("status", "unknown")
    value = data.get("value", data.get("valor", ""))

    # Emoji baseado no status
    if status in ["active", "ativo", "receiving"]:
        emoji = ""
    elif status in ["eligible", "elegivel"]:
        emoji = ""
    elif status in ["pending", "pendente"]:
        emoji = ""
    else:
        emoji = ""

    lines = [f"{emoji} *{name}*"]

    if value:
        lines.append(f"   Valor: {value}")

    # Detalhes adicionais
    details = data.get("details", data.get("detalhes", ""))
    if details:
        lines.append(f"   {details}")

    return "\n".join(lines)


def format_cras_card(data: Dict[str, Any]) -> str:
    """Formata card de CRAS para texto."""
    name = data.get("name", data.get("nome", "CRAS"))
    address = data.get("address", data.get("endereco", ""))
    distance = data.get("distance", data.get("distancia", ""))
    phone = data.get("phone", data.get("telefone", ""))
    hours = data.get("hours", data.get("horario", "Seg-Sex 8h-17h"))

    lines = [f"*{name}*"]

    if address:
        lines.append(f"   {address}")

    if distance:
        lines.append(f"   {distance}")

    if phone:
        lines.append(f"   Tel: {phone}")

    if hours:
        lines.append(f"   Horário: {hours}")

    # Links
    links = data.get("links", {})
    if links.get("direcoes"):
        lines.append(f"   Como chegar: {links['direcoes']}")

    return "\n".join(lines)


def format_order_status(data: Dict[str, Any]) -> str:
    """Formata status do pedido para texto."""
    order_number = data.get("order_number", data.get("numero_pedido", ""))
    status = data.get("status", "pending")
    pharmacy = data.get("pharmacy", data.get("farmacia", ""))
    estimated_ready = data.get("estimated_ready", data.get("previsao", ""))

    # Emoji baseado no status
    status_emoji = {
        "pending": "",
        "pendente": "",
        "confirmed": "",
        "confirmado": "",
        "preparing": "",
        "preparando": "",
        "ready": "",
        "pronto": "",
        "cancelled": "",
        "cancelado": "",
    }.get(status, "")

    lines = [f"{status_emoji} *Pedido {order_number}*"]

    if pharmacy:
        lines.append(f"   Farmácia: {pharmacy}")

    # Steps
    steps = data.get("steps", data.get("etapas", []))
    if steps:
        lines.append("")
        for step in steps:
            step_label = step.get("label", step.get("texto", ""))
            done = step.get("done", step.get("concluido", False))
            emoji = "" if done else ""
            lines.append(f"   {emoji} {step_label}")

    if estimated_ready:
        lines.append(f"\n   Previsão: {estimated_ready}")

    return "\n".join(lines)


def format_alert(data: Dict[str, Any]) -> str:
    """Formata alerta para texto."""
    alert_type = data.get("type", data.get("tipo", "info"))
    title = data.get("title", data.get("titulo", ""))
    message = data.get("message", data.get("mensagem", ""))

    # Emoji baseado no tipo
    type_emoji = {
        "success": "",
        "sucesso": "",
        "warning": "",
        "aviso": "",
        "error": "",
        "erro": "",
        "info": "",
    }.get(alert_type, "")

    lines = []

    if title:
        lines.append(f"{type_emoji} *{title}*")

    if message:
        lines.append(message)

    return "\n".join(lines)


def format_ui_component(component: UIComponent) -> str:
    """Formata um UIComponent para texto."""
    component_type = component.type
    data = component.data

    # Mapear tipos para formatadores
    formatters = {
        UIComponentType.PHARMACY_CARD: format_pharmacy_card,
        UIComponentType.MEDICATION_LIST: format_medication_list,
        UIComponentType.CHECKLIST: format_checklist,
        UIComponentType.BENEFIT_CARD: format_benefit_card,
        UIComponentType.CRAS_CARD: format_cras_card,
        UIComponentType.ORDER_STATUS: format_order_status,
        UIComponentType.ALERT: format_alert,
    }

    formatter = formatters.get(component_type)

    if formatter:
        return formatter(data)

    # Fallback: tentar formatar como texto genérico
    return str(data)


def format_actions_text(actions: List[Action]) -> str:
    """Formata ações sugeridas para texto."""
    if not actions:
        return ""

    lines = ["\n*O que você quer fazer?*"]

    for i, action in enumerate(actions[:5], 1):  # Max 5 opções
        label = action.label

        # Adicionar emoji baseado no tipo
        if action.action_type == ActionType.CALL_PHONE:
            emoji = ""
        elif action.action_type == ActionType.OPEN_URL:
            emoji = ""
        elif action.action_type == ActionType.SHARE:
            emoji = ""
        elif action.action_type == ActionType.CAMERA:
            emoji = ""
        else:
            emoji = f"{i}."

        lines.append(f"{emoji} {label}")

    lines.append("\n_Digite o número ou o que você quer fazer_")

    return "\n".join(lines)


def format_response_for_whatsapp(response: AgentResponse) -> str:
    """
    Converte AgentResponse completo para TwiML.

    Args:
        response: Resposta estruturada do agente

    Returns:
        String TwiML para envio via Twilio
    """
    # Construir texto da mensagem
    parts = []

    # Texto principal
    if response.text:
        parts.append(response.text)

    # UIComponents
    for component in response.ui_components:
        formatted = format_ui_component(component)
        if formatted:
            parts.append(formatted)

    # Ações sugeridas
    if response.suggested_actions:
        actions_text = format_actions_text(response.suggested_actions)
        if actions_text:
            parts.append(actions_text)

    # Juntar com separadores
    message_text = "\n\n".join(parts)

    # Limitar tamanho (WhatsApp tem limite de ~4096 caracteres)
    if len(message_text) > 4000:
        message_text = message_text[:3997] + "..."

    # Montar TwiML
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{escape_xml(message_text)}</Message>
</Response>'''

    return twiml


def format_response_text_only(response: AgentResponse) -> str:
    """
    Converte AgentResponse para texto simples (sem TwiML).

    Útil para envio via API do Twilio diretamente.
    """
    parts = []

    if response.text:
        parts.append(response.text)

    for component in response.ui_components:
        formatted = format_ui_component(component)
        if formatted:
            parts.append(formatted)

    if response.suggested_actions:
        actions_text = format_actions_text(response.suggested_actions)
        if actions_text:
            parts.append(actions_text)

    message_text = "\n\n".join(parts)

    if len(message_text) > 4000:
        message_text = message_text[:3997] + "..."

    return message_text
