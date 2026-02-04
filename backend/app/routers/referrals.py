"""Referral tracking endpoints - anonymous member-get-member program."""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


# In-memory tracking (em produção, usar Redis ou tabela dedicada)
# Estrutura simples: registrar eventos de compartilhamento e conversões
_referral_events: list[dict] = []


class ReferralEvent(BaseModel):
    """Schema for tracking a referral share event."""
    referral_code: str
    method: str  # whatsapp, copy, sms


class ReferralConversion(BaseModel):
    """Schema for tracking when a referred user completes the wizard."""
    referral_code: str


@router.post("/")
async def track_referral_share(data: ReferralEvent):
    """Record when a user shares their referral link."""
    _referral_events.append({
        "type": "share",
        "code": data.referral_code,
        "method": data.method,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return {"recorded": True}


@router.post("/conversion")
async def track_referral_conversion(data: ReferralConversion):
    """Record when a referred user arrives and completes the wizard."""
    _referral_events.append({
        "type": "conversion",
        "code": data.referral_code,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return {"recorded": True}


@router.get("/stats")
async def referral_stats(days: int = Query(30, ge=1, le=365)):
    """Get referral program statistics (admin)."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    cutoff_str = cutoff.isoformat()

    recent = [e for e in _referral_events if e["timestamp"] >= cutoff_str]

    shares = [e for e in recent if e["type"] == "share"]
    conversions = [e for e in recent if e["type"] == "conversion"]

    # Breakdown por método
    by_method: dict[str, int] = {}
    for s in shares:
        method = s.get("method", "unknown")
        by_method[method] = by_method.get(method, 0) + 1

    # Códigos únicos
    unique_sharers = len(set(e["code"] for e in shares))
    unique_conversions = len(set(e["code"] for e in conversions))

    return {
        "period_days": days,
        "total_shares": len(shares),
        "total_conversions": len(conversions),
        "unique_sharers": unique_sharers,
        "unique_conversions": unique_conversions,
        "conversion_rate": round(unique_conversions / unique_sharers, 4) if unique_sharers > 0 else 0,
        "by_method": by_method,
    }
