"""Service layer for partner operations."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partner import Partner, PartnerConversion


async def get_active_partners(db: AsyncSession) -> list[Partner]:
    """List all active partners ordered by priority."""
    result = await db.execute(
        select(Partner)
        .where(Partner.is_active == True)
        .order_by(Partner.priority.desc())
    )
    return list(result.scalars().all())


async def get_partner_by_slug(db: AsyncSession, slug: str) -> Optional[Partner]:
    """Get a single partner by slug."""
    result = await db.execute(
        select(Partner).where(Partner.slug == slug, Partner.is_active == True)
    )
    return result.scalars().first()


async def get_partner_for_programs(
    db: AsyncSession, program_codes: list[str]
) -> Optional[Partner]:
    """Find the best partner for a set of benefit programs."""
    partners = await get_active_partners(db)
    for partner in partners:
        if partner.target_programs:
            if any(code in partner.target_programs for code in program_codes):
                return partner
    # Fallback to highest priority partner
    return partners[0] if partners else None


async def record_conversion(
    db: AsyncSession,
    partner_slug: str,
    session_id: str,
    event: str,
    source: str,
    metadata: Optional[dict] = None,
) -> Optional[PartnerConversion]:
    """Record a conversion event."""
    partner = await get_partner_by_slug(db, partner_slug)
    if not partner:
        return None

    conversion = PartnerConversion(
        id=uuid4(),
        partner_id=partner.id,
        session_id=session_id,
        event=event,
        source=source,
        extra_data=metadata,
    )
    db.add(conversion)
    return conversion


async def get_conversion_stats(
    db: AsyncSession,
    partner_slug: Optional[str] = None,
    days: int = 30,
) -> list[dict]:
    """Get aggregated conversion stats for dashboard."""
    since = datetime.utcnow() - timedelta(days=days)

    base_query = (
        select(
            Partner.slug,
            Partner.name,
            PartnerConversion.event,
            func.count(PartnerConversion.id).label("count"),
        )
        .join(Partner, Partner.id == PartnerConversion.partner_id)
        .where(PartnerConversion.created_at >= since)
        .group_by(Partner.slug, Partner.name, PartnerConversion.event)
    )

    if partner_slug:
        base_query = base_query.where(Partner.slug == partner_slug)

    result = await db.execute(base_query)
    rows = result.all()

    # Aggregate by partner
    stats_map: dict[str, dict] = {}
    for slug, name, event, count in rows:
        if slug not in stats_map:
            stats_map[slug] = {
                "partner_slug": slug,
                "partner_name": name,
                "impressions": 0,
                "clicks": 0,
                "redirects": 0,
            }
        stats_map[slug][f"{event}s"] = count

    # Calculate rates
    stats = []
    for s in stats_map.values():
        impressions = s["impressions"]
        clicks = s["clicks"]
        s["click_rate"] = round(clicks / impressions, 4) if impressions > 0 else 0.0
        s["redirect_rate"] = round(s["redirects"] / clicks, 4) if clicks > 0 else 0.0
        s["period_start"] = since
        s["period_end"] = datetime.utcnow()
        stats.append(s)

    return stats
