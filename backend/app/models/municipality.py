"""Municipality model with PostGIS geometry."""

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class Municipality(Base):
    """Brazilian municipality model with geometry."""

    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)
    ibge_code = Column(String(7), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False, index=True)

    # Demographics
    population = Column(Integer)
    area_km2 = Column(Numeric(12, 2))

    # PostGIS geometry columns
    geometry = Column(Geometry("MULTIPOLYGON", srid=4326))
    geometry_simplified = Column(Geometry("MULTIPOLYGON", srid=4326))
    centroid = Column(Geometry("POINT", srid=4326))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    state = relationship("State", back_populates="municipalities")
    beneficiary_data = relationship("BeneficiaryData", back_populates="municipality")
    cadunico_data = relationship("CadUnicoData", back_populates="municipality")

    def __repr__(self):
        return f"<Municipality {self.ibge_code} - {self.name}>"

    @property
    def state_code(self) -> str:
        """Return the 2-digit state code from IBGE code."""
        return self.ibge_code[:2] if self.ibge_code else ""

    def to_geojson_feature(self, simplified: bool = True) -> dict:
        """Convert to GeoJSON Feature format."""
        from shapely import wkb
        import json

        geom = self.geometry_simplified if simplified and self.geometry_simplified else self.geometry

        if geom:
            # Convert WKB to GeoJSON
            shape = wkb.loads(bytes(geom.data))
            geometry = json.loads(shape.geojson)
        else:
            geometry = None

        return {
            "type": "Feature",
            "properties": {
                "ibge_code": self.ibge_code,
                "name": self.name,
                "state_id": self.state_id,
                "population": self.population,
                "area_km2": float(self.area_km2) if self.area_km2 else None,
            },
            "geometry": geometry,
        }
