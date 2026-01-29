"""Municipality Pydantic schemas."""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class MunicipalityResponse(BaseModel):
    """Basic municipality response."""

    model_config = ConfigDict(from_attributes=True)

    ibge_code: str
    name: str
    state_id: int
    population: Optional[int] = None
    area_km2: Optional[float] = None


class MunicipalityListResponse(BaseModel):
    """Paginated list of municipalities."""

    items: List[MunicipalityResponse]
    total: int
    page: int
    limit: int
    pages: int


class MunicipalityDetailResponse(BaseModel):
    """Detailed municipality response with state info."""

    ibge_code: str
    name: str
    state_abbreviation: Optional[str] = None
    state_name: Optional[str] = None
    region: Optional[str] = None
    population: Optional[int] = None
    area_km2: Optional[float] = None


class ProgramDataSummary(BaseModel):
    """Program data summary for a municipality."""

    program_code: str
    program_name: str
    total_beneficiaries: Optional[int] = None
    total_families: Optional[int] = None
    total_value_brl: Optional[float] = None
    coverage_rate: Optional[float] = None
    reference_date: Optional[str] = None


class MunicipalityWithPrograms(MunicipalityDetailResponse):
    """Municipality with all program data."""

    programs: List[ProgramDataSummary] = []
