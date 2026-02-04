"""Anjo Social advisory system endpoints."""

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.advisor import (
    CaseCreate,
    CaseUpdate,
    CaseNoteCreate,
    AdvisorCreate,
)
from app.services.advisor_service import (
    create_case,
    get_case,
    update_case,
    add_case_note,
    list_cases,
    get_active_advisors,
    create_advisor,
    get_advisor_dashboard,
)

router = APIRouter()


# --- Cases ---

@router.post("/cases/")
async def create_new_case(
    data: CaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new advisory case (usually from AI escalation)."""
    case = await create_case(
        db=db,
        citizen_session_id=data.citizen_session_id,
        benefits=data.benefits,
        escalation_reason=data.escalation_reason,
        priority=data.priority,
        citizen_context=data.citizen_context,
    )
    return {
        "id": str(case.id),
        "status": case.status,
        "advisorId": str(case.advisor_id) if case.advisor_id else None,
    }


@router.get("/cases/{case_id}")
async def get_case_detail(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get full case details with advisor and notes."""
    case = await get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.to_dict()


@router.patch("/cases/{case_id}")
async def update_case_endpoint(
    case_id: UUID,
    data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update case status, priority, or advisor assignment."""
    case = await update_case(
        db=db,
        case_id=case_id,
        status=data.status,
        priority=data.priority,
        advisor_id=data.advisor_id,
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"id": str(case.id), "status": case.status}


@router.post("/cases/{case_id}/notes")
async def add_note(
    case_id: UUID,
    data: CaseNoteCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a note to a case."""
    note = await add_case_note(
        db=db,
        case_id=case_id,
        author=data.author,
        content=data.content,
    )
    if not note:
        raise HTTPException(status_code=404, detail="Case not found")
    return note.to_dict()


@router.get("/cases/")
async def list_all_cases(
    advisor_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List cases with optional filters and pagination."""
    cases, total = await list_cases(
        db=db,
        advisor_id=advisor_id,
        status=status,
        priority=priority,
        limit=limit,
        offset=offset,
    )
    return {
        "cases": [c.to_dict() for c in cases],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# --- Advisors ---

@router.get("/advisors/")
async def list_advisors(db: AsyncSession = Depends(get_db)):
    """List all active advisors."""
    advisors = await get_active_advisors(db)
    return [a.to_dict() for a in advisors]


@router.post("/advisors/")
async def create_new_advisor(
    data: AdvisorCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new advisor."""
    advisor = await create_advisor(db, data.model_dump())
    return advisor.to_dict()


@router.get("/advisors/{advisor_id}/dashboard")
async def advisor_dashboard(
    advisor_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get advisor dashboard with active cases and stats."""
    dashboard = await get_advisor_dashboard(db, advisor_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Advisor not found")
    return dashboard
