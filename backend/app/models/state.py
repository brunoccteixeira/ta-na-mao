"""State model with PostGIS geometry."""

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class State(Base):
    """Brazilian state (UF) model."""

    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    ibge_code = Column(String(2), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(2), nullable=False, index=True)
    region = Column(String(20), nullable=False, index=True)

    # PostGIS geometry column
    geometry = Column(Geometry("MULTIPOLYGON", srid=4326))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    municipalities = relationship("Municipality", back_populates="state")

    def __repr__(self):
        return f"<State {self.abbreviation} - {self.name}>"

    @property
    def region_name(self) -> str:
        """Return full region name."""
        regions = {
            "N": "Norte",
            "NE": "Nordeste",
            "CO": "Centro-Oeste",
            "SE": "Sudeste",
            "S": "Sul",
        }
        return regions.get(self.region, self.region)
