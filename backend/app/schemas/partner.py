"""Pydantic schemas for partners API."""

from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PartnerResponse(BaseModel):
    """Partner response for public API."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    type: Literal["bank", "ngo", "government", "employer"]
    logo_url: Optional[str] = Field(None, alias="logoUrl")
    cta_text: str = Field(alias="ctaText")
    cta_url: str = Field(alias="ctaUrl")
    description: Optional[str] = None
    benefits_list: List[str] = Field(alias="benefits")
    color: Optional[str] = None
    target_programs: Optional[List[str]] = Field(None, alias="targetPrograms")


class ConversionCreate(BaseModel):
    """Schema for creating a conversion event."""
    partner_slug: str = Field(description="Partner slug identifier")
    session_id: str = Field(description="Anonymous session UUID")
    event: Literal["impression", "click", "redirect"]
    source: str = Field(description="Where the event occurred: rights_wallet, homepage, chat")
    metadata: Optional[dict] = None


class ConversionResponse(BaseModel):
    """Response after recording a conversion."""
    id: UUID
    recorded: bool = True


class ConversionStats(BaseModel):
    """Aggregated conversion statistics for admin dashboard."""
    partner_slug: str
    partner_name: str
    impressions: int = 0
    clicks: int = 0
    redirects: int = 0
    click_rate: float = 0.0  # clicks / impressions
    redirect_rate: float = 0.0  # redirects / clicks
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
