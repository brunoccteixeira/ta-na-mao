"""Partner and PartnerConversion models for banking/B2B partnerships."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from app.database import Base


class PartnerType(str, Enum):
    """Type of partner organization."""
    BANK = "bank"
    NGO = "ngo"
    GOVERNMENT = "government"
    EMPLOYER = "employer"


class ConversionEvent(str, Enum):
    """Types of conversion events for tracking."""
    IMPRESSION = "impression"
    CLICK = "click"
    REDIRECT = "redirect"


class Partner(Base):
    """
    Partner model - banks, NGOs, government orgs that sponsor the platform.
    First partner: CAIXA Economica Federal (Caixa Tem).
    """
    __tablename__ = "partners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False)
    slug = Column(String(50), nullable=False, unique=True, index=True)
    type = Column(String(20), nullable=False, default=PartnerType.BANK.value)

    # Display
    logo_url = Column(String(500), nullable=True)
    cta_text = Column(String(200), nullable=False)
    cta_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    benefits_list = Column(ARRAY(String), nullable=False, default=list)

    # Config
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    priority = Column(Integer, nullable=False, default=0)
    color = Column(String(7), nullable=True)  # Hex color for branding, e.g. "#005CA9"

    # Targeting: which benefit programs this partner is relevant for
    target_programs = Column(ARRAY(String), nullable=True)  # e.g. ["BOLSA_FAMILIA", "BPC"]

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Partner(slug='{self.slug}', name='{self.name}')>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "type": self.type,
            "logoUrl": self.logo_url,
            "ctaText": self.cta_text,
            "ctaUrl": self.cta_url,
            "description": self.description,
            "benefits": self.benefits_list,
            "isActive": self.is_active,
            "priority": self.priority,
            "color": self.color,
            "targetPrograms": self.target_programs,
        }


class PartnerConversion(Base):
    """
    Tracks anonymous conversion events (impressions, clicks, redirects).
    No PII stored - only session_id (anonymous UUID).
    """
    __tablename__ = "partner_conversions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)  # Anonymous session UUID
    event = Column(String(20), nullable=False)  # impression, click, redirect
    source = Column(String(50), nullable=False)  # rights_wallet, homepage, chat
    extra_data = Column("metadata", JSONB, nullable=True)  # Extra context (e.g. which benefits were shown)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<PartnerConversion(partner_id='{self.partner_id}', event='{self.event}')>"
