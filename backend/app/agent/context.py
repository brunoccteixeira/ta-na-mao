"""
Contexto de conversa compartilhado entre orquestrador e sub-agentes.

Este módulo gerencia o estado da conversa, perfil do cidadão,
e dados do fluxo atual.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


# =============================================================================
# Enums
# =============================================================================

class FlowType(str, Enum):
    """Tipos de fluxo de conversa."""

    FARMACIA = "farmacia"
    BENEFICIO = "beneficio"
    DOCUMENTACAO = "documentacao"
    PROTECAO = "protecao"
    GERAL = "geral"


class FarmaciaState(str, Enum):
    """Estados do fluxo de farmácia."""

    INICIO = "inicio"
    RECEITA = "receita"
    MEDICAMENTOS = "medicamentos"
    LOCALIZACAO = "localizacao"
    FARMACIA = "farmacia"
    DADOS_CIDADAO = "dados_cidadao"
    CONFIRMACAO = "confirmacao"
    PEDIDO_ENVIADO = "pedido_enviado"


class BeneficioState(str, Enum):
    """Estados do fluxo de benefícios."""

    INICIO = "inicio"
    CONSULTA_CPF = "consulta_cpf"
    RESULTADO = "resultado"
    ELEGIBILIDADE = "elegibilidade"
    ORIENTACAO = "orientacao"


class DocumentacaoState(str, Enum):
    """Estados do fluxo de documentação."""

    INICIO = "inicio"
    PROGRAMA = "programa"
    CHECKLIST = "checklist"
    LOCALIZACAO = "localizacao"
    CRAS = "cras"


# =============================================================================
# Perfil do Cidadão
# =============================================================================

class BeneficioInfo(BaseModel):
    """Informações de um benefício recebido."""

    ativo: bool = False
    valor: Optional[float] = None
    data_referencia: Optional[str] = None
    tipo: Optional[str] = None  # Para BPC: IDOSO, PCD_LEVE, etc


class CitizenProfile(BaseModel):
    """
    Perfil do cidadão extraído durante a conversa.

    Preenchido progressivamente conforme o agente coleta informações.
    """

    # Identificação
    cpf: Optional[str] = None
    cpf_masked: Optional[str] = None
    nome: Optional[str] = None
    nis: Optional[str] = None

    # Localização
    cep: Optional[str] = None
    ibge_code: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    bairro: Optional[str] = None
    endereco: Optional[str] = None

    # Geolocalização (GPS)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geo_accuracy: Optional[float] = None

    # Contato
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None

    # Benefícios atuais
    bolsa_familia: Optional[BeneficioInfo] = None
    bpc: Optional[BeneficioInfo] = None
    cadunico_ativo: bool = False
    faixa_renda: Optional[str] = None  # EXTREMA_POBREZA, POBREZA, BAIXA_RENDA

    # Situação familiar (para checklist personalizado)
    tem_filhos: bool = False
    quantidade_filhos: int = 0
    gestante: bool = False
    idoso: bool = False
    deficiencia: bool = False

    def update_from_cep_result(self, cep_data: Dict[str, Any]) -> None:
        """Atualiza localização a partir de resultado de busca de CEP."""
        self.cep = cep_data.get("cep")
        self.ibge_code = cep_data.get("ibge")
        self.cidade = cep_data.get("localidade")
        self.uf = cep_data.get("uf")
        self.bairro = cep_data.get("bairro")
        self.endereco = cep_data.get("logradouro")

    def update_from_geolocation(
        self,
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = None
    ) -> None:
        """Atualiza geolocalização a partir de coordenadas GPS."""
        self.latitude = latitude
        self.longitude = longitude
        self.geo_accuracy = accuracy

    def has_geolocation(self) -> bool:
        """Verifica se tem coordenadas GPS."""
        return self.latitude is not None and self.longitude is not None

    def update_from_beneficio_result(self, beneficio_data: Dict[str, Any]) -> None:
        """Atualiza benefícios a partir de resultado de consulta."""
        if "bolsa_familia" in beneficio_data:
            bf = beneficio_data["bolsa_familia"]
            self.bolsa_familia = BeneficioInfo(
                ativo=bf.get("ativo", False),
                valor=bf.get("valor"),
                data_referencia=bf.get("parcela_mes")
            )

        if "bpc" in beneficio_data:
            bpc = beneficio_data["bpc"]
            self.bpc = BeneficioInfo(
                ativo=bpc.get("ativo", False),
                valor=bpc.get("valor"),
                tipo=bpc.get("tipo")
            )

        if "cadunico" in beneficio_data:
            cad = beneficio_data["cadunico"]
            self.cadunico_ativo = cad.get("ativo", False)
            self.faixa_renda = cad.get("faixa_renda")


# =============================================================================
# Mensagem de Histórico
# =============================================================================

class MessageRole(str, Enum):
    """Papel do autor da mensagem."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Message(BaseModel):
    """Mensagem no histórico da conversa."""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_name: Optional[str] = None  # Se role == TOOL
    tool_result: Optional[Dict[str, Any]] = None


# =============================================================================
# Dados de Fluxo
# =============================================================================

class FarmaciaFlowData(BaseModel):
    """Dados específicos do fluxo de farmácia."""

    state: FarmaciaState = FarmaciaState.INICIO
    medicamentos: List[Dict[str, Any]] = Field(default_factory=list)
    receita_url: Optional[str] = None
    farmacia_selecionada: Optional[Dict[str, Any]] = None
    farmacias_encontradas: List[Dict[str, Any]] = Field(default_factory=list)
    pedido_numero: Optional[str] = None
    pedido_id: Optional[str] = None


class BeneficioFlowData(BaseModel):
    """Dados específicos do fluxo de benefícios."""

    state: BeneficioState = BeneficioState.INICIO
    programa_consultado: Optional[str] = None
    resultado_consulta: Optional[Dict[str, Any]] = None


class DocumentacaoFlowData(BaseModel):
    """Dados específicos do fluxo de documentação."""

    state: DocumentacaoState = DocumentacaoState.INICIO
    programa_selecionado: Optional[str] = None
    checklist_gerado: Optional[Dict[str, Any]] = None
    cras_encontrados: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Contexto Principal
# =============================================================================

class ConversationContext(BaseModel):
    """
    Contexto completo da conversa.

    Compartilhado entre orquestrador e sub-agentes.
    Persiste durante toda a sessão.
    """

    # Identificação da sessão
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)

    # Perfil do cidadão (preenchido progressivamente)
    citizen: CitizenProfile = Field(default_factory=CitizenProfile)

    # Fluxo atual
    active_flow: Optional[FlowType] = None
    flow_data: Dict[str, Any] = Field(default_factory=dict)

    # Histórico de mensagens (últimas N para contexto do LLM)
    history: List[Message] = Field(default_factory=list)
    max_history_size: int = 20

    # Tools utilizadas na sessão
    tools_used: List[str] = Field(default_factory=list)

    def add_message(self, role: MessageRole, content: str, **kwargs) -> None:
        """Adiciona mensagem ao histórico."""
        self.history.append(Message(role=role, content=content, **kwargs))
        self.last_activity = datetime.now()

        # Limita tamanho do histórico
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]

    def add_tool_usage(self, tool_name: str) -> None:
        """Registra uso de tool."""
        if tool_name not in self.tools_used:
            self.tools_used.append(tool_name)

    def start_flow(self, flow_type: FlowType) -> None:
        """Inicia um novo fluxo."""
        self.active_flow = flow_type
        self.flow_data = {}

    def end_flow(self) -> None:
        """Encerra o fluxo atual."""
        self.active_flow = None
        self.flow_data = {}

    def get_farmacia_flow(self) -> FarmaciaFlowData:
        """Retorna dados do fluxo de farmácia (cria se não existir)."""
        if self.active_flow != FlowType.FARMACIA:
            self.start_flow(FlowType.FARMACIA)

        if not self.flow_data:
            self.flow_data = FarmaciaFlowData().model_dump()

        return FarmaciaFlowData(**self.flow_data)

    def set_farmacia_flow(self, data: FarmaciaFlowData) -> None:
        """Atualiza dados do fluxo de farmácia."""
        self.flow_data = data.model_dump()

    def get_beneficio_flow(self) -> BeneficioFlowData:
        """Retorna dados do fluxo de benefícios."""
        if self.active_flow != FlowType.BENEFICIO:
            self.start_flow(FlowType.BENEFICIO)

        if not self.flow_data:
            self.flow_data = BeneficioFlowData().model_dump()

        return BeneficioFlowData(**self.flow_data)

    def set_beneficio_flow(self, data: BeneficioFlowData) -> None:
        """Atualiza dados do fluxo de benefícios."""
        self.flow_data = data.model_dump()

    def get_documentacao_flow(self) -> DocumentacaoFlowData:
        """Retorna dados do fluxo de documentação."""
        if self.active_flow != FlowType.DOCUMENTACAO:
            self.start_flow(FlowType.DOCUMENTACAO)

        if not self.flow_data:
            self.flow_data = DocumentacaoFlowData().model_dump()

        return DocumentacaoFlowData(**self.flow_data)

    def set_documentacao_flow(self, data: DocumentacaoFlowData) -> None:
        """Atualiza dados do fluxo de documentação."""
        self.flow_data = data.model_dump()

    def reset(self) -> None:
        """Reseta o contexto (mantém session_id)."""
        self.citizen = CitizenProfile()
        self.active_flow = None
        self.flow_data = {}
        self.history = []
        self.tools_used = []
        self.last_activity = datetime.now()


# =============================================================================
# Gerenciador de Sessões
# =============================================================================

class SessionManager:
    """
    Gerenciador de sessões de conversa.

    Em produção, usar Redis para persistência.
    """

    def __init__(self):
        self._sessions: Dict[str, ConversationContext] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> ConversationContext:
        """Obtém sessão existente ou cria nova."""
        if session_id and session_id in self._sessions:
            context = self._sessions[session_id]
            context.last_activity = datetime.now()
            return context

        # Cria nova sessão
        context = ConversationContext(session_id=session_id or str(uuid.uuid4()))
        self._sessions[context.session_id] = context
        return context

    def get(self, session_id: str) -> Optional[ConversationContext]:
        """Obtém sessão existente."""
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        """Remove sessão."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def reset(self, session_id: str) -> bool:
        """Reseta sessão (mantém ID)."""
        if session_id in self._sessions:
            self._sessions[session_id].reset()
            return True
        return False

    def cleanup_expired(self, max_age_hours: int = 24) -> int:
        """Remove sessões expiradas."""
        from datetime import timedelta

        now = datetime.now()
        expired = []

        for session_id, context in self._sessions.items():
            age = now - context.last_activity
            if age > timedelta(hours=max_age_hours):
                expired.append(session_id)

        for session_id in expired:
            del self._sessions[session_id]

        return len(expired)


# =============================================================================
# Factory de Session Manager
# =============================================================================

def get_session_manager():
    """
    Factory que retorna SessionManager apropriado baseado no ambiente.

    - Produção: RedisSessionManager (persistente)
    - Desenvolvimento: SessionManager em memória (mais rápido)

    A escolha é feita automaticamente baseada em settings.ENVIRONMENT.
    """
    from app.config import settings

    if settings.ENVIRONMENT == "production":
        try:
            from .session_redis import RedisSessionManager
            return RedisSessionManager()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"Falha ao criar RedisSessionManager: {e}. Usando fallback em memória."
            )
            return SessionManager()
    else:
        return SessionManager()


# Singleton para uso global
# Usa factory para escolher implementação apropriada
session_manager = get_session_manager()
