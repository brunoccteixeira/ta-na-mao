"""Advisor and Case models for the Anjo Social human advisory system."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


class CaseStatus(str, Enum):
    """Status workflow for advisory cases."""
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CasePriority(str, Enum):
    """Priority levels for cases."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


class Advisor(Base):
    """
    Assessor social - agente de CRAS, voluntário ou assistente social
    que acompanha casos complexos escalados pela IA.
    """
    __tablename__ = "advisors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False)
    role = Column(String(100), nullable=False)  # "Assistente Social", "Voluntário"
    organization = Column(String(200), nullable=False)  # "CRAS Centro - São Paulo"
    phone = Column(String(20), nullable=True)  # WhatsApp
    email = Column(String(200), nullable=True)
    max_active_cases = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    specialties = Column(ARRAY(String), nullable=False, default=list)  # ["BPC", "Bolsa Família"]

    # Stats
    total_resolved = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cases = relationship("Case", back_populates="advisor")

    def __repr__(self) -> str:
        return f"<Advisor(name='{self.name}', org='{self.organization}')>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "role": self.role,
            "organization": self.organization,
            "specialties": self.specialties or [],
            "maxActiveCases": self.max_active_cases,
            "totalResolved": self.total_resolved,
            "isActive": self.is_active,
        }


class CaseNote(Base):
    """Notes/interactions on a case, from either the advisor or the system."""
    __tablename__ = "case_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    author = Column(String(100), nullable=False)  # advisor name or "sistema"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="notes")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "author": self.author,
            "content": self.content,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Case(Base):
    """
    Caso de assessoria - escalado pela IA quando detecta situação complexa.
    Sem PII: usa session_id anônimo para identificar o cidadão.
    """
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    citizen_session_id = Column(String(100), nullable=False, index=True)
    advisor_id = Column(UUID(as_uuid=True), ForeignKey("advisors.id"), nullable=True, index=True)

    # Status & Priority
    status = Column(String(20), nullable=False, default=CaseStatus.OPEN.value, index=True)
    priority = Column(String(20), nullable=False, default=CasePriority.MEDIUM.value, index=True)

    # Context
    benefits = Column(ARRAY(String), nullable=False, default=list)  # Benefícios em questão
    escalation_reason = Column(Text, nullable=False)  # Por que a IA escalou
    citizen_context = Column(JSONB, nullable=True)  # Contexto anônimo (UF, perfil sem PII)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    advisor = relationship("Advisor", back_populates="cases")
    notes = relationship("CaseNote", back_populates="case", order_by="CaseNote.created_at")

    def __repr__(self) -> str:
        return f"<Case(id='{self.id}', status='{self.status}', priority='{self.priority}')>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "citizenSessionId": self.citizen_session_id,
            "advisor": self.advisor.to_dict() if self.advisor else None,
            "status": self.status,
            "priority": self.priority,
            "benefits": self.benefits or [],
            "escalationReason": self.escalation_reason,
            "citizenContext": self.citizen_context,
            "notes": [n.to_dict() for n in (self.notes or [])],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "resolvedAt": self.resolved_at.isoformat() if self.resolved_at else None,
        }
