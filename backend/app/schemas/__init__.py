"""Pydantic schemas for API validation."""

from app.schemas.municipality import (
    MunicipalityResponse,
    MunicipalityListResponse,
    MunicipalityDetailResponse,
)
from app.schemas.program import ProgramResponse
from app.schemas.geojson import GeoJSONFeature, GeoJSONFeatureCollection
from app.schemas.benefit import (
    BenefitResponse,
    BenefitSummary,
    BenefitListResponse,
    BenefitStatsResponse,
    CitizenProfile,
    EligibilityRequest,
    EligibilityResponse,
    EligibilitySummary,
    BenefitEligibilityResult,
)

__all__ = [
    "MunicipalityResponse",
    "MunicipalityListResponse",
    "MunicipalityDetailResponse",
    "ProgramResponse",
    "GeoJSONFeature",
    "GeoJSONFeatureCollection",
    "BenefitResponse",
    "BenefitSummary",
    "BenefitListResponse",
    "BenefitStatsResponse",
    "CitizenProfile",
    "EligibilityRequest",
    "EligibilityResponse",
    "EligibilitySummary",
    "BenefitEligibilityResult",
]
