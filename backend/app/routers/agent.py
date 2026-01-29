"""Endpoints da API para o agente conversacional.

Inclui endpoints V1 (legado) e V2 (com orquestrador e A2UI).
"""

import logging
from typing import Dict
from fastapi import APIRouter, HTTPException

from app.schemas.agent import (
    ChatRequest,
    ChatRequestV2,
    ChatResponse,
    ChatResponseV2,
    WelcomeResponse,
    AgentStatus,
    ErrorResponse,
    UIComponentSchema,
    ActionSchema,
)
from app.agent.agent import TaNaMaoAgent, create_agent, GOOGLE_API_KEY
from app.agent.orchestrator import get_orchestrator
from app.agent.response_types import AgentResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Cache de sessões (em produção, usar Redis)
sessions: Dict[str, TaNaMaoAgent] = {}


def get_or_create_agent(session_id: str = None) -> TaNaMaoAgent:
    """Obtém agente existente ou cria um novo.

    Args:
        session_id: ID da sessão existente.

    Returns:
        TaNaMaoAgent: Instância do agente.
    """
    if session_id and session_id in sessions:
        return sessions[session_id]

    agent = create_agent(session_id)
    sessions[agent.session_id] = agent
    return agent


@router.get(
    "/status",
    response_model=AgentStatus,
    summary="Status do Agente",
    description="Verifica se o agente está disponível e configurado."
)
async def get_status():
    """Retorna status do agente."""
    return AgentStatus(
        available=bool(GOOGLE_API_KEY),
        model="gemini-2.0-flash-exp",
        tools=["validar_cpf", "buscar_cep", "consultar_beneficios"]
    )


@router.post(
    "/start",
    response_model=WelcomeResponse,
    summary="Iniciar Conversa",
    description="Inicia uma nova sessão de conversa com o agente."
)
async def start_conversation():
    """Inicia uma nova conversa e retorna mensagem de boas-vindas."""
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Agente não configurado. GOOGLE_API_KEY não definida."
        )

    agent = get_or_create_agent()

    return WelcomeResponse(
        message=agent.get_welcome_message(),
        session_id=agent.session_id
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Mensagem inválida"},
        503: {"model": ErrorResponse, "description": "Agente não disponível"},
    },
    summary="Enviar Mensagem",
    description="Envia uma mensagem para o agente e recebe a resposta."
)
async def chat(request: ChatRequest):
    """Processa mensagem do usuário e retorna resposta do agente."""
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Agente não configurado. GOOGLE_API_KEY não definida."
        )

    try:
        agent = get_or_create_agent(request.session_id)
        response = agent.process_message(request.message)

        return ChatResponse(
            response=response,
            session_id=agent.session_id,
            tools_used=agent.tools_used.copy()
        )

    except Exception as e:
        logger.error(f"Erro ao processar chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )


@router.post(
    "/reset/{session_id}",
    summary="Resetar Conversa",
    description="Reinicia uma sessão de conversa existente."
)
async def reset_conversation(session_id: str):
    """Reinicia uma conversa existente."""
    if session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada"
        )

    sessions[session_id].reset()

    return {"message": "Conversa reiniciada", "session_id": session_id}


@router.delete(
    "/session/{session_id}",
    summary="Encerrar Sessão",
    description="Encerra e remove uma sessão de conversa."
)
async def end_session(session_id: str):
    """Encerra uma sessão."""
    if session_id in sessions:
        del sessions[session_id]

    return {"message": "Sessão encerrada", "session_id": session_id}


# =============================================================================
# V2 Endpoints (com Orquestrador e A2UI)
# =============================================================================

def _convert_to_schema(response: AgentResponse, session_id: str) -> ChatResponseV2:
    """Converte AgentResponse interno para ChatResponseV2 schema."""
    return ChatResponseV2(
        text=response.text,
        session_id=session_id,
        ui_components=[
            UIComponentSchema(type=c.type.value, data=c.data)
            for c in response.ui_components
        ],
        suggested_actions=[
            ActionSchema(
                label=a.label,
                action_type=a.action_type.value,
                payload=a.payload,
                icon=a.icon,
                primary=a.primary
            )
            for a in response.suggested_actions
        ],
        flow_state=response.flow_state,
        tools_used=[]  # Será preenchido pelo context
    )


@router.post(
    "/v2/start",
    response_model=ChatResponseV2,
    summary="Iniciar Conversa (V2)",
    description="Inicia uma nova sessão com resposta estruturada A2UI.",
    tags=["v2"]
)
async def start_conversation_v2():
    """Inicia uma nova conversa com resposta estruturada."""
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Agente não configurado. GOOGLE_API_KEY não definida."
        )

    try:
        orchestrator = get_orchestrator()
        response = orchestrator.get_welcome_message()
        session_id = response.context.get("session_id", "")

        return _convert_to_schema(response, session_id)

    except Exception as e:
        logger.error(f"Erro ao iniciar conversa V2: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao iniciar conversa: {str(e)}"
        )


@router.post(
    "/v2/chat",
    response_model=ChatResponseV2,
    responses={
        400: {"model": ErrorResponse, "description": "Mensagem inválida"},
        503: {"model": ErrorResponse, "description": "Agente não disponível"},
    },
    summary="Enviar Mensagem (V2)",
    description="Envia mensagem e recebe resposta estruturada com componentes A2UI.",
    tags=["v2"]
)
async def chat_v2(request: ChatRequestV2):
    """Processa mensagem com orquestrador e retorna resposta estruturada."""
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Agente não configurado. GOOGLE_API_KEY não definida."
        )

    try:
        orchestrator = get_orchestrator()

        # Atualizar geolocalização no contexto se fornecida
        if request.location and request.session_id:
            session = orchestrator.get_session(request.session_id)
            if session:
                session.citizen.update_from_geolocation(
                    latitude=request.location.latitude,
                    longitude=request.location.longitude,
                    accuracy=request.location.accuracy
                )
                logger.info(
                    f"Localização atualizada: {request.location.latitude}, {request.location.longitude}"
                )

        response = await orchestrator.process_message(
            message=request.message,
            session_id=request.session_id,
            image_base64=request.image_base64
        )

        # Obter session_id do contexto
        session = orchestrator.get_session(request.session_id) if request.session_id else None
        session_id = session.session_id if session else request.session_id or ""

        # Atualizar geolocalização na nova sessão também
        if request.location and session and not session.citizen.has_geolocation():
            session.citizen.update_from_geolocation(
                latitude=request.location.latitude,
                longitude=request.location.longitude,
                accuracy=request.location.accuracy
            )

        # Obter tools usadas
        tools_used = session.tools_used if session else []

        result = _convert_to_schema(response, session_id)
        result.tools_used = tools_used

        return result

    except Exception as e:
        logger.error(f"Erro ao processar chat V2: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )


@router.post(
    "/v2/reset/{session_id}",
    summary="Resetar Conversa (V2)",
    description="Reinicia uma sessão de conversa usando o orquestrador.",
    tags=["v2"]
)
async def reset_conversation_v2(session_id: str):
    """Reinicia uma conversa existente no orquestrador."""
    orchestrator = get_orchestrator()

    if not orchestrator.reset_session(session_id):
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada"
        )

    return {"message": "Conversa reiniciada", "session_id": session_id}


@router.delete(
    "/v2/session/{session_id}",
    summary="Encerrar Sessão (V2)",
    description="Encerra e remove uma sessão do orquestrador.",
    tags=["v2"]
)
async def end_session_v2(session_id: str):
    """Encerra uma sessão no orquestrador."""
    orchestrator = get_orchestrator()
    orchestrator.delete_session(session_id)

    return {"message": "Sessão encerrada", "session_id": session_id}


@router.get(
    "/v2/status",
    response_model=AgentStatus,
    summary="Status do Agente (V2)",
    description="Verifica status do agente com orquestrador.",
    tags=["v2"]
)
async def get_status_v2():
    """Retorna status do agente com orquestrador."""
    return AgentStatus(
        available=bool(GOOGLE_API_KEY),
        model="gemini-2.0-flash-exp",
        tools=[
            "processar_receita",
            "buscar_farmacia",
            "preparar_pedido",
            "consultar_pedido",
            "validar_cpf",
            "buscar_cep",
            "gerar_checklist",
            "buscar_cras",
            "consultar_beneficio"
        ]
    )
