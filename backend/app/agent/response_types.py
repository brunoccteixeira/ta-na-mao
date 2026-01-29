"""
Tipos de resposta estruturada do agente (A2UI - Agent-to-User Interface).

Este módulo define os tipos para respostas ricas que podem ser renderizadas
como componentes visuais no frontend (cards, listas, botões, etc).

Inspirado em: https://github.com/google/A2UI
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


# =============================================================================
# Tipos de Componentes UI
# =============================================================================

class UIComponentType(str, Enum):
    """Tipos de componentes UI suportados."""

    # Farmácia
    PHARMACY_CARD = "pharmacy_card"
    MEDICATION_LIST = "medication_list"
    ORDER_STATUS = "order_status"

    # Benefícios
    BENEFIT_CARD = "benefit_card"
    ELIGIBILITY_RESULT = "eligibility_result"

    # Documentação
    CHECKLIST = "checklist"
    CRAS_CARD = "cras_card"

    # Genéricos
    INFO_CARD = "info_card"
    MAP_LOCATION = "map_location"
    STATUS_BADGE = "status_badge"
    ALERT = "alert"


class ActionType(str, Enum):
    """Tipos de ações sugeridas."""

    SEND_MESSAGE = "send_message"  # Envia mensagem ao chat
    OPEN_URL = "open_url"          # Abre URL externa
    CALL_PHONE = "call_phone"      # Liga para número
    OPEN_WHATSAPP = "open_whatsapp"  # Abre WhatsApp
    SHARE = "share"                # Compartilha conteúdo
    CAMERA = "camera"              # Abre câmera
    OPEN_MAP = "open_map"          # Abre mapa


# =============================================================================
# Componentes UI Específicos
# =============================================================================

class MedicationItem(BaseModel):
    """Item de medicamento na lista."""

    name: str = Field(..., description="Nome do medicamento")
    dosage: Optional[str] = Field(None, description="Dosagem (ex: 50mg)")
    quantity: Optional[int] = Field(None, description="Quantidade")
    free: bool = Field(False, description="Se é gratuito no Farmácia Popular")
    copay: Optional[float] = Field(None, description="Valor de copagamento se houver")


class MedicationListData(BaseModel):
    """Dados para componente medication_list."""

    medications: List[MedicationItem]
    all_free: bool = Field(False, description="Se todos são gratuitos")
    estimated_savings: Optional[str] = Field(None, description="Economia estimada")
    needs_prescription: bool = Field(True, description="Se precisa de receita")


class PharmacyCardData(BaseModel):
    """Dados para componente pharmacy_card."""

    id: str
    name: str
    address: str
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    distance: Optional[str] = None
    hours: Optional[str] = None
    has_whatsapp: bool = False
    programs: List[str] = Field(default_factory=list, description="Programas disponíveis")


class OrderStep(BaseModel):
    """Etapa do pedido."""

    label: str
    done: bool
    timestamp: Optional[str] = None


class OrderStatusData(BaseModel):
    """Dados para componente order_status."""

    order_number: str
    status: Literal["pending", "confirmed", "preparing", "ready", "picked_up", "cancelled"]
    pharmacy_name: str
    pharmacy_address: Optional[str] = None
    estimated_ready: Optional[str] = None
    steps: List[OrderStep]
    can_cancel: bool = True


class BenefitCardData(BaseModel):
    """Dados para componente benefit_card."""

    code: str
    name: str
    status: Literal["receiving", "eligible", "not_eligible", "pending", "unknown"]
    value: Optional[float] = None
    value_formatted: Optional[str] = None
    last_payment: Optional[str] = None
    next_payment: Optional[str] = None
    description: Optional[str] = None


class ChecklistItem(BaseModel):
    """Item do checklist."""

    text: str
    required: bool = True
    checked: bool = False
    note: Optional[str] = None


class ChecklistData(BaseModel):
    """Dados para componente checklist."""

    title: str
    items: List[ChecklistItem]
    program: Optional[str] = None
    total_required: int = 0
    total_optional: int = 0


class CrasCardData(BaseModel):
    """Dados para componente cras_card."""

    name: str
    address: str
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    hours: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    distance: Optional[str] = None


class MapLocationData(BaseModel):
    """Dados para componente map_location."""

    latitude: float
    longitude: float
    title: str
    address: Optional[str] = None
    zoom: int = 15


class AlertData(BaseModel):
    """Dados para componente alert."""

    type: Literal["info", "success", "warning", "error"]
    title: str
    message: str
    dismissable: bool = True


# =============================================================================
# Componente UI Genérico
# =============================================================================

class UIComponent(BaseModel):
    """
    Componente de UI renderizável.

    O frontend mapeia o `type` para um componente React/Flutter específico
    e passa `data` como props.
    """

    type: UIComponentType = Field(..., description="Tipo do componente")
    data: Dict[str, Any] = Field(..., description="Dados do componente")

    @classmethod
    def medication_list(cls, data: MedicationListData) -> "UIComponent":
        return cls(type=UIComponentType.MEDICATION_LIST, data=data.model_dump())

    @classmethod
    def pharmacy_card(cls, data: PharmacyCardData) -> "UIComponent":
        return cls(type=UIComponentType.PHARMACY_CARD, data=data.model_dump())

    @classmethod
    def order_status(cls, data: OrderStatusData) -> "UIComponent":
        return cls(type=UIComponentType.ORDER_STATUS, data=data.model_dump())

    @classmethod
    def benefit_card(cls, data: BenefitCardData) -> "UIComponent":
        return cls(type=UIComponentType.BENEFIT_CARD, data=data.model_dump())

    @classmethod
    def checklist(cls, data: ChecklistData) -> "UIComponent":
        return cls(type=UIComponentType.CHECKLIST, data=data.model_dump())

    @classmethod
    def cras_card(cls, data: CrasCardData) -> "UIComponent":
        return cls(type=UIComponentType.CRAS_CARD, data=data.model_dump())

    @classmethod
    def alert(cls, data: AlertData) -> "UIComponent":
        return cls(type=UIComponentType.ALERT, data=data.model_dump())


# =============================================================================
# Ações Sugeridas
# =============================================================================

class Action(BaseModel):
    """
    Ação sugerida ao usuário.

    Renderizada como botão/chip clicável no frontend.
    """

    label: str = Field(..., description="Texto do botão")
    action_type: ActionType = Field(..., description="Tipo de ação")
    payload: str = Field(..., description="Dados da ação (mensagem, URL, telefone)")
    icon: Optional[str] = Field(None, description="Ícone opcional")
    primary: bool = Field(False, description="Se é ação principal (destaque)")

    @classmethod
    def send_message(cls, label: str, message: str, primary: bool = False) -> "Action":
        return cls(
            label=label,
            action_type=ActionType.SEND_MESSAGE,
            payload=message,
            primary=primary
        )

    @classmethod
    def call_phone(cls, label: str, phone: str) -> "Action":
        return cls(
            label=label,
            action_type=ActionType.CALL_PHONE,
            payload=phone,
            icon="phone"
        )

    @classmethod
    def open_whatsapp(cls, label: str, phone: str, message: str = "") -> "Action":
        # Formato: 5511999999999|mensagem
        payload = f"{phone}|{message}" if message else phone
        return cls(
            label=label,
            action_type=ActionType.OPEN_WHATSAPP,
            payload=payload,
            icon="whatsapp"
        )

    @classmethod
    def open_camera(cls, label: str = "Tirar foto") -> "Action":
        return cls(
            label=label,
            action_type=ActionType.CAMERA,
            payload="prescription",
            icon="camera"
        )

    @classmethod
    def open_map(cls, label: str, address: str) -> "Action":
        return cls(
            label=label,
            action_type=ActionType.OPEN_MAP,
            payload=address,
            icon="map"
        )


# =============================================================================
# Resposta do Agente
# =============================================================================

class AgentResponse(BaseModel):
    """
    Resposta estruturada do agente.

    Combina texto (para leitura/TTS) com componentes visuais
    e ações sugeridas para interação rica.
    """

    text: str = Field(..., description="Resposta textual principal")
    ui_components: List[UIComponent] = Field(
        default_factory=list,
        description="Componentes visuais para renderizar"
    )
    suggested_actions: List[Action] = Field(
        default_factory=list,
        description="Ações sugeridas (botões)"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Contexto para próxima interação"
    )
    flow_state: Optional[str] = Field(
        None,
        description="Estado do fluxo (ex: 'farmacia:medicamentos')"
    )

    def with_component(self, component: UIComponent) -> "AgentResponse":
        """Adiciona um componente e retorna self (fluent interface)."""
        self.ui_components.append(component)
        return self

    def with_action(self, action: Action) -> "AgentResponse":
        """Adiciona uma ação e retorna self (fluent interface)."""
        self.suggested_actions.append(action)
        return self
