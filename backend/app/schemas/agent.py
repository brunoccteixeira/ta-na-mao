"""Schemas para endpoints do agente conversacional."""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# =============================================================================
# A2UI Components (Agent-to-User Interface)
# =============================================================================

class UIComponentSchema(BaseModel):
    """Componente de UI renderizável pelo frontend."""

    type: str = Field(
        ...,
        description="Tipo do componente (pharmacy_card, medication_list, checklist, etc)"
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Dados do componente para renderização"
    )


class ActionSchema(BaseModel):
    """Ação sugerida (botão clicável)."""

    label: str = Field(..., description="Texto do botão")
    action_type: Literal[
        "send_message", "open_url", "call_phone",
        "open_whatsapp", "share", "camera", "open_map"
    ] = Field(..., description="Tipo de ação")
    payload: str = Field(..., description="Dados da ação")
    icon: Optional[str] = Field(None, description="Ícone opcional")
    primary: bool = Field(False, description="Se é ação principal (destaque)")


# =============================================================================
# Request/Response Schemas
# =============================================================================

class ChatRequest(BaseModel):
    """Requisição de chat (v1 - legado)."""

    message: str = Field(..., description="Mensagem do usuário", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="ID da sessão para manter contexto")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Olá, quero saber sobre o Bolsa Família",
                    "session_id": "abc123"
                }
            ]
        }
    }


class LocationData(BaseModel):
    """Dados de localização do usuário."""

    latitude: float = Field(..., description="Latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude", ge=-180, le=180)
    accuracy: Optional[float] = Field(None, description="Precisão em metros")


class ChatRequestV2(BaseModel):
    """Requisição de chat (v2 - com suporte a imagem e localização)."""

    message: str = Field(..., description="Mensagem do usuário", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="ID da sessão para manter contexto")
    image_base64: Optional[str] = Field(None, description="Imagem em base64 (ex: receita médica)")
    location: Optional[LocationData] = Field(None, description="Localização do usuário")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Quero pedir esses remédios",
                    "session_id": "abc123",
                    "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
                    "location": {
                        "latitude": -23.5505,
                        "longitude": -46.6333,
                        "accuracy": 10.0
                    }
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Resposta do chat (v1 - legado)."""

    response: str = Field(..., description="Resposta do agente")
    session_id: str = Field(..., description="ID da sessão (use para manter contexto)")
    tools_used: List[str] = Field(default_factory=list, description="Lista de tools utilizadas")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response": "Olá! Sou o assistente Tá na Mão...",
                    "session_id": "abc123",
                    "tools_used": ["validar_cpf"]
                }
            ]
        }
    }


class ChatResponseV2(BaseModel):
    """Resposta do chat (v2 - com componentes A2UI)."""

    text: str = Field(..., description="Resposta textual do agente")
    session_id: str = Field(..., description="ID da sessão")
    ui_components: List[UIComponentSchema] = Field(
        default_factory=list,
        description="Componentes visuais para renderizar (cards, listas, etc)"
    )
    suggested_actions: List[ActionSchema] = Field(
        default_factory=list,
        description="Ações sugeridas (botões clicáveis)"
    )
    flow_state: Optional[str] = Field(
        None,
        description="Estado do fluxo atual (ex: 'farmacia:medicamentos')"
    )
    tools_used: List[str] = Field(
        default_factory=list,
        description="Tools utilizadas nesta resposta"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Encontrei 2 remédios na sua receita!",
                    "session_id": "abc123",
                    "ui_components": [
                        {
                            "type": "medication_list",
                            "data": {
                                "medications": [
                                    {"name": "Losartana", "dosage": "50mg", "free": True}
                                ],
                                "all_free": True
                            }
                        }
                    ],
                    "suggested_actions": [
                        {
                            "label": "Confirmar",
                            "action_type": "send_message",
                            "payload": "sim",
                            "primary": True
                        }
                    ],
                    "flow_state": "farmacia:medicamentos",
                    "tools_used": ["processar_receita"]
                }
            ]
        }
    }


class WelcomeResponse(BaseModel):
    """Resposta de boas-vindas."""

    message: str = Field(..., description="Mensagem de boas-vindas")
    session_id: str = Field(..., description="ID da nova sessão")


class AgentStatus(BaseModel):
    """Status do agente."""

    available: bool = Field(..., description="Se o agente está disponível")
    model: str = Field(..., description="Modelo sendo usado")
    tools: List[str] = Field(..., description="Tools disponíveis")


class ErrorResponse(BaseModel):
    """Resposta de erro."""

    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes adicionais")
