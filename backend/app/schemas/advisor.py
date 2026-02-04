"""Pydantic schemas for Anjo Social advisory system."""

from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# --- Case Schemas ---

class CaseNoteCreate(BaseModel):
    """Schema for adding a note to a case."""
    author: str = Field(description="Nome do autor (assessor ou 'sistema')")
    content: str = Field(description="Conteúdo da nota")


class CaseNoteResponse(BaseModel):
    """Response schema for case notes."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author: str
    content: str
    created_at: datetime = Field(alias="createdAt")


class CaseCreate(BaseModel):
    """Schema for creating a new case (usually from AI escalation)."""
    citizen_session_id: str = Field(description="Session ID anônimo do cidadão")
    benefits: List[str] = Field(description="Benefícios em questão")
    escalation_reason: str = Field(description="Motivo do escalonamento pela IA")
    priority: Literal["low", "medium", "high", "emergency"] = "medium"
    citizen_context: Optional[dict] = Field(
        None, description="Contexto anônimo (UF, perfil sem PII)"
    )


class CaseUpdate(BaseModel):
    """Schema for updating a case."""
    status: Optional[Literal["open", "assigned", "in_progress", "resolved", "closed"]] = None
    priority: Optional[Literal["low", "medium", "high", "emergency"]] = None
    advisor_id: Optional[UUID] = None


class CaseResponse(BaseModel):
    """Full case response with advisor and notes."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    citizen_session_id: str = Field(alias="citizenSessionId")
    status: str
    priority: str
    benefits: List[str]
    escalation_reason: str = Field(alias="escalationReason")
    citizen_context: Optional[dict] = Field(None, alias="citizenContext")
    advisor: Optional["AdvisorResponse"] = None
    notes: List[CaseNoteResponse] = []
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resolved_at: Optional[datetime] = Field(None, alias="resolvedAt")


class CaseListResponse(BaseModel):
    """Lightweight case for list views."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    priority: str
    benefits: List[str]
    escalation_reason: str = Field(alias="escalationReason")
    advisor_name: Optional[str] = Field(None, alias="advisorName")
    created_at: datetime = Field(alias="createdAt")


# --- Advisor Schemas ---

class AdvisorCreate(BaseModel):
    """Schema for creating an advisor."""
    name: str = Field(description="Nome completo")
    role: str = Field(description="Cargo: Assistente Social, Voluntário, etc.")
    organization: str = Field(description="Organização: CRAS Centro - São Paulo")
    phone: Optional[str] = Field(None, description="WhatsApp")
    email: Optional[str] = None
    max_active_cases: int = Field(10, description="Máximo de casos ativos")
    specialties: List[str] = Field(
        default_factory=list,
        description="Especialidades: BPC, Bolsa Família, MCMV, etc."
    )


class AdvisorResponse(BaseModel):
    """Full advisor response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    role: str
    organization: str
    specialties: List[str] = []
    max_active_cases: int = Field(alias="maxActiveCases")
    total_resolved: int = Field(alias="totalResolved")
    is_active: bool = Field(alias="isActive")


class AdvisorDashboard(BaseModel):
    """Dashboard data for an advisor."""
    advisor: AdvisorResponse
    active_cases: List[CaseListResponse] = Field(alias="activeCases")
    stats: "AdvisorStats"


class AdvisorStats(BaseModel):
    """Aggregated stats for advisor dashboard."""
    open_cases: int = Field(0, alias="openCases")
    in_progress_cases: int = Field(0, alias="inProgressCases")
    resolved_this_month: int = Field(0, alias="resolvedThisMonth")
    total_resolved: int = Field(0, alias="totalResolved")
    avg_resolution_days: Optional[float] = Field(None, alias="avgResolutionDays")


# Fix forward references
CaseResponse.model_rebuild()
