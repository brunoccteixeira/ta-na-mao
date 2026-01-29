"""Beneficiary data models for tracking program penetration."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class BeneficiaryData(Base):
    """Time-series data for beneficiaries per municipality/program."""

    __tablename__ = "beneficiary_data"

    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(
        Integer, ForeignKey("municipalities.id"), nullable=False, index=True
    )
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    reference_date = Column(Date, nullable=False, index=True)

    # Common metrics
    total_beneficiaries = Column(Integer)
    total_families = Column(Integer)
    total_value_brl = Column(Numeric(15, 2))
    coverage_rate = Column(Numeric(5, 4))  # 0.0000 to 1.0000

    # Program-specific data (flexible JSON)
    extra_data = Column(JSONB)

    # Data quality
    data_source = Column(String(100))
    ingested_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    municipality = relationship("Municipality", back_populates="beneficiary_data")
    program = relationship("Program", back_populates="beneficiary_data")

    def __repr__(self):
        return f"<BeneficiaryData {self.municipality_id}/{self.program_id} @ {self.reference_date}>"

    @property
    def coverage_percentage(self) -> float:
        """Return coverage rate as percentage."""
        return float(self.coverage_rate * 100) if self.coverage_rate else 0.0


class CadUnicoData(Base):
    """CadÚnico-specific data with detailed demographics."""

    __tablename__ = "cadunico_data"

    id = Column(Integer, primary_key=True, index=True)
    municipality_id = Column(
        Integer, ForeignKey("municipalities.id"), nullable=False, index=True
    )
    reference_date = Column(Date, nullable=False, index=True)

    # Totals
    total_families = Column(Integer)
    total_persons = Column(Integer)

    # Income brackets
    families_extreme_poverty = Column(Integer)  # < R$105/capita
    families_poverty = Column(Integer)  # R$105 - R$218/capita
    families_low_income = Column(Integer)  # up to 1/2 min wage

    # Demographics by age
    persons_0_5_years = Column(Integer)
    persons_6_14_years = Column(Integer)
    persons_15_17_years = Column(Integer)
    persons_18_64_years = Column(Integer)
    persons_65_plus = Column(Integer)

    # Timestamps
    ingested_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    municipality = relationship("Municipality", back_populates="cadunico_data")

    def __repr__(self):
        return f"<CadUnicoData {self.municipality_id} @ {self.reference_date}>"

    @property
    def total_vulnerable_families(self) -> int:
        """Sum of all vulnerable families."""
        return (
            (self.families_extreme_poverty or 0)
            + (self.families_poverty or 0)
            + (self.families_low_income or 0)
        )
