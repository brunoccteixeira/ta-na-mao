"""Program Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel


class ProgramResponse(BaseModel):
    """Program response schema."""

    code: str
    name: str
    description: Optional[str] = None
    data_source_url: Optional[str] = None
    update_frequency: Optional[str] = None


class ProgramStats(BaseModel):
    """Program statistics."""

    total_beneficiaries: int = 0
    total_families: int = 0
    total_value_brl: float = 0.0
    avg_coverage_rate: float = 0.0
    municipalities_covered: int = 0
    total_municipalities: int = 0


class ProgramWithStats(ProgramResponse):
    """Program with national statistics."""

    national_stats: ProgramStats
