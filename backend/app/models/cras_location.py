"""CRAS location model for social assistance centers."""

from datetime import datetime
from typing import List, Optional
import uuid

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


class CrasLocation(Base):
    """Centro de Referencia de Assistencia Social (CRAS) location.

    CRAS are the primary access points for social assistance in Brazil,
    providing services like CadUnico registration, Bolsa Familia enrollment,
    and BPC/LOAS applications.
    """

    __tablename__ = "cras_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ibge_code = Column(String(7), ForeignKey("municipalities.ibge_code"), nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    endereco = Column(String(500), nullable=True)
    bairro = Column(String(100), nullable=True)
    cep = Column(String(8), nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    servicos = Column(ARRAY(String), nullable=True)  # ["CadUnico", "BolsaFamilia", "BPC"]
    horario_funcionamento = Column(String(100), nullable=True)
    source = Column(String(50), nullable=True)  # "censo_suas", "mapa_social"
    geocode_source = Column(String(50), nullable=True)  # "cnefe", "google", "manual"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    municipality = relationship("Municipality", backref="cras_locations")

    def __repr__(self) -> str:
        return f"<CrasLocation {self.nome} - {self.ibge_code}>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "ibge_code": self.ibge_code,
            "nome": self.nome,
            "endereco": self.endereco,
            "bairro": self.bairro,
            "cep": self.cep,
            "telefone": self.telefone,
            "email": self.email,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "servicos": self.servicos or [],
            "horario_funcionamento": self.horario_funcionamento,
            "source": self.source,
            "geocode_source": self.geocode_source,
        }

    @property
    def has_coordinates(self) -> bool:
        """Check if CRAS has valid coordinates."""
        return self.latitude is not None and self.longitude is not None

    @property
    def endereco_completo(self) -> str:
        """Return complete address string."""
        parts = [self.endereco]
        if self.bairro:
            parts.append(self.bairro)
        return ", ".join(filter(None, parts))
