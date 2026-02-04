"""Partners API endpoints."""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.partner import (
    PartnerResponse,
    ConversionCreate,
    ConversionResponse,
    ConversionStats,
)
from app.services.partner_service import (
    get_active_partners,
    get_partner_by_slug,
    record_conversion,
    get_conversion_stats,
)

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_partners(db: AsyncSession = Depends(get_db)):
    """List all active partners."""
    partners = await get_active_partners(db)
    return [p.to_dict() for p in partners]


@router.get("/{slug}")
async def get_partner(slug: str, db: AsyncSession = Depends(get_db)):
    """Get partner details by slug."""
    partner = await get_partner_by_slug(db, slug)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner.to_dict()


@router.post("/conversions", response_model=ConversionResponse)
async def track_conversion(
    data: ConversionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Record a conversion event (impression, click, redirect)."""
    conversion = await record_conversion(
        db=db,
        partner_slug=data.partner_slug,
        session_id=data.session_id,
        event=data.event,
        source=data.source,
        metadata=data.metadata,
    )
    if not conversion:
        raise HTTPException(status_code=404, detail="Partner not found")
    return ConversionResponse(id=conversion.id)


@router.get("/conversions/stats", response_model=List[ConversionStats])
async def conversion_stats(
    partner_slug: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get conversion statistics (admin)."""
    stats = await get_conversion_stats(db, partner_slug=partner_slug, days=days)
    return stats
