"""Benefit model for the unified benefits catalog."""

from datetime import datetime, date
from typing import Optional, List, Any
from enum import Enum

from sqlalchemy import Column, String, Text, Date, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from app.database import Base


class BenefitScope(str, Enum):
    """Benefit scope enum."""
    FEDERAL = "federal"
    STATE = "state"
    MUNICIPAL = "municipal"
    SECTORAL = "sectoral"


class BenefitStatus(str, Enum):
    """Benefit status enum."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ENDED = "ended"


class Benefit(Base):
    """
    Unified benefit model for the entire catalog.
    Stores federal, state, municipal, and sectoral benefits.
    """
    __tablename__ = "benefits"

    # Primary key - uses string ID like 'federal-bolsa-familia'
    id = Column(String(100), primary_key=True)

    # Basic info
    name = Column(String(200), nullable=False)
    short_description = Column(Text, nullable=False)

    # Scope - determines which level of government/sector
    scope = Column(String(20), nullable=False, index=True)
    state = Column(String(2), nullable=True, index=True)  # UF code for state benefits
    municipality_ibge = Column(String(7), nullable=True, index=True)  # IBGE code for municipal
    sector = Column(String(50), nullable=True, index=True)  # Sector for sectoral benefits

    # Value information (stored as JSON)
    # Format: {"type": "monthly"|"annual"|"one_time", "min": number, "max": number, "description": string}
    estimated_value = Column(JSONB, nullable=True)

    # Eligibility rules (stored as JSON array)
    # Format: [{"field": string, "operator": string, "value": any, "description": string}]
    eligibility_rules = Column(JSONB, nullable=False, default=list)

    # Practical information
    where_to_apply = Column(Text, nullable=False)
    documents_required = Column(ARRAY(String), nullable=False, default=list)
    how_to_apply = Column(ARRAY(String), nullable=True)

    # Metadata
    source_url = Column(String(500), nullable=True)
    last_updated = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="active", index=True)

    # UI elements
    icon = Column(String(10), nullable=True)  # Emoji
    category = Column(String(100), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # Composite index for location-based queries
        # Index('ix_benefits_location', 'scope', 'state', 'municipality_ibge'),  # Already created in migration
    )

    def __repr__(self) -> str:
        return f"<Benefit(id='{self.id}', name='{self.name}', scope='{self.scope}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "shortDescription": self.short_description,
            "scope": self.scope,
            "state": self.state,
            "municipalityIbge": self.municipality_ibge,
            "sector": self.sector,
            "estimatedValue": self.estimated_value,
            "eligibilityRules": self.eligibility_rules,
            "whereToApply": self.where_to_apply,
            "documentsRequired": self.documents_required,
            "howToApply": self.how_to_apply,
            "sourceUrl": self.source_url,
            "lastUpdated": self.last_updated.isoformat() if self.last_updated else None,
            "status": self.status,
            "icon": self.icon,
            "category": self.category,
        }

    @classmethod
    def from_json(cls, data: dict) -> "Benefit":
        """Create a Benefit instance from JSON data (frontend format)."""
        # Parse date string to date object
        last_updated = data.get("lastUpdated")
        if isinstance(last_updated, str):
            last_updated = date.fromisoformat(last_updated)
        elif last_updated is None:
            last_updated = date.today()

        return cls(
            id=data["id"],
            name=data["name"],
            short_description=data.get("shortDescription", ""),
            scope=data.get("scope", "federal"),
            state=data.get("state"),
            municipality_ibge=data.get("municipalityIbge"),
            sector=data.get("sector"),
            estimated_value=data.get("estimatedValue"),
            eligibility_rules=data.get("eligibilityRules", []),
            where_to_apply=data.get("whereToApply", ""),
            documents_required=data.get("documentsRequired", []),
            how_to_apply=data.get("howToApply"),
            source_url=data.get("sourceUrl"),
            last_updated=last_updated,
            status=data.get("status", "active"),
            icon=data.get("icon"),
            category=data.get("category"),
        )

    def get_estimated_value_range(self) -> tuple[Optional[float], Optional[float]]:
        """Get min and max estimated values."""
        if not self.estimated_value:
            return None, None
        return (
            self.estimated_value.get("min"),
            self.estimated_value.get("max"),
        )

    def get_value_type(self) -> Optional[str]:
        """Get value type (monthly, annual, one_time)."""
        if not self.estimated_value:
            return None
        return self.estimated_value.get("type")
