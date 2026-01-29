"""Municipalities API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Municipality, State
from app.schemas.municipality import (
    MunicipalityResponse,
    MunicipalityListResponse,
)

router = APIRouter()


@router.get("/", response_model=MunicipalityListResponse)
async def list_municipalities(
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    state_code: Optional[str] = Query(None, description="Filter by state abbreviation (e.g., SP)"),
    search: Optional[str] = Query(None, description="Search by name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    List municipalities with optional filters.

    - **state_id**: Filter by state database ID
    - **state_code**: Filter by state abbreviation (SP, RJ, etc.)
    - **search**: Search municipalities by name (case-insensitive)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 50, max: 200)
    """
    # Build base query
    stmt = select(Municipality)

    # Apply filters
    if state_id:
        stmt = stmt.where(Municipality.state_id == state_id)

    if state_code:
        state_stmt = select(State).where(State.abbreviation == state_code.upper())
        state_result = await db.execute(state_stmt)
        state = state_result.scalar_one_or_none()
        if state:
            stmt = stmt.where(Municipality.state_id == state.id)
        else:
            return MunicipalityListResponse(
                items=[], total=0, page=page, limit=limit, pages=0
            )

    if search:
        stmt = stmt.where(Municipality.name.ilike(f"%{search}%"))

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * limit
    stmt = stmt.order_by(Municipality.name).offset(offset).limit(limit)
    result = await db.execute(stmt)
    municipalities = result.scalars().all()

    return MunicipalityListResponse(
        items=[MunicipalityResponse.model_validate(m) for m in municipalities],
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit,
    )


@router.get("/search")
async def search_municipalities(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=50, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search municipalities by name.

    Returns municipalities matching the search query, ordered by relevance.
    """
    stmt = (
        select(Municipality)
        .where(Municipality.name.ilike(f"%{q}%"))
        .order_by(Municipality.name)
        .limit(limit)
    )
    result = await db.execute(stmt)
    municipalities = result.scalars().all()

    return [
        {
            "ibge_code": m.ibge_code,
            "name": m.name,
            "state_id": m.state_id,
            "population": m.population,
        }
        for m in municipalities
    ]


@router.get("/{ibge_code}")
async def get_municipality(
    ibge_code: str,
    program: Optional[str] = Query(None, description="Filter by program code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get municipality details by IBGE code with optional program filter.

    - **ibge_code**: 7-digit IBGE municipality code
    - **program**: Optional program code to filter beneficiary data (e.g., TSEE)
    """
    from app.models import BeneficiaryData, Program, CadUnicoData

    stmt = select(Municipality).where(Municipality.ibge_code == ibge_code)
    result = await db.execute(stmt)
    municipality = result.scalar_one_or_none()

    if not municipality:
        raise HTTPException(status_code=404, detail="Municipality not found")

    # Get state info
    state_stmt = select(State).where(State.id == municipality.state_id)
    state_result = await db.execute(state_stmt)
    state = state_result.scalar_one_or_none()

    # Get CadÚnico data
    cadunico_stmt = (
        select(CadUnicoData)
        .where(CadUnicoData.municipality_id == municipality.id)
        .order_by(CadUnicoData.reference_date.desc())
        .limit(1)
    )
    cadunico_result = await db.execute(cadunico_stmt)
    cadunico = cadunico_result.scalar_one_or_none()

    # Get beneficiary data
    from sqlalchemy import func

    total_beneficiaries = 0
    total_families = 0
    total_value = 0.0
    avg_coverage = 0.0

    if program:
        # Filter by specific program
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            beneficiary_data_stmt = (
                select(BeneficiaryData)
                .where(
                    BeneficiaryData.municipality_id == municipality.id,
                    BeneficiaryData.program_id == prog.id,
                )
                .order_by(BeneficiaryData.reference_date.desc())
                .limit(1)
            )
            beneficiary_data_result = await db.execute(beneficiary_data_stmt)
            beneficiary_data = beneficiary_data_result.scalar_one_or_none()
            if beneficiary_data:
                total_beneficiaries = beneficiary_data.total_beneficiaries or 0
                total_families = beneficiary_data.total_families or 0
                total_value = float(beneficiary_data.total_value_brl) if beneficiary_data.total_value_brl else 0
                avg_coverage = float(beneficiary_data.coverage_rate) if beneficiary_data.coverage_rate else 0
    else:
        # Aggregate all programs
        agg_stmt = (
            select(
                func.sum(BeneficiaryData.total_beneficiaries).label("total_ben"),
                func.sum(BeneficiaryData.total_families).label("total_fam"),
                func.sum(BeneficiaryData.total_value_brl).label("total_val"),
                func.avg(BeneficiaryData.coverage_rate).label("avg_cov"),
            )
            .where(BeneficiaryData.municipality_id == municipality.id)
        )
        agg_result = await db.execute(agg_stmt)
        agg = agg_result.first()
        if agg:
            total_beneficiaries = agg.total_ben or 0
            total_families = agg.total_fam or 0
            total_value = float(agg.total_val) if agg.total_val else 0
            avg_coverage = float(agg.avg_cov) if agg.avg_cov else 0

    return {
        "ibge_code": municipality.ibge_code,
        "name": municipality.name,
        "state_abbreviation": state.abbreviation if state else None,
        "state_name": state.name if state else None,
        "region": state.region if state else None,
        "population": municipality.population or 0,
        "area_km2": float(municipality.area_km2) if municipality.area_km2 else None,
        "cadunico_families": cadunico.total_families if cadunico else 0,
        "total_beneficiaries": total_beneficiaries,
        "total_families": total_families,
        "total_value_brl": total_value,
        "coverage_rate": avg_coverage,
    }


@router.get("/{ibge_code}/programs")
async def get_municipality_programs(
    ibge_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all program data for a specific municipality.

    Returns beneficiary data for all tracked programs.
    """
    stmt = select(Municipality).where(Municipality.ibge_code == ibge_code)
    result = await db.execute(stmt)
    municipality = result.scalar_one_or_none()

    if not municipality:
        raise HTTPException(status_code=404, detail="Municipality not found")

    # Get latest beneficiary data for each program
    from app.models import BeneficiaryData, Program

    # Subquery to get latest date per program
    latest_dates_subq = (
        select(
            BeneficiaryData.program_id,
            func.max(BeneficiaryData.reference_date).label("max_date"),
        )
        .where(BeneficiaryData.municipality_id == municipality.id)
        .group_by(BeneficiaryData.program_id)
        .subquery()
    )

    # Get latest data for each program
    program_data_stmt = (
        select(BeneficiaryData, Program)
        .join(Program, BeneficiaryData.program_id == Program.id)
        .join(
            latest_dates_subq,
            (BeneficiaryData.program_id == latest_dates_subq.c.program_id)
            & (BeneficiaryData.reference_date == latest_dates_subq.c.max_date),
        )
        .where(BeneficiaryData.municipality_id == municipality.id)
    )
    program_data_result = await db.execute(program_data_stmt)
    program_data = program_data_result.all()

    return {
        "ibge_code": ibge_code,
        "name": municipality.name,
        "programs": [
            {
                "code": prog.code,
                "name": prog.name,
                "total_beneficiaries": data.total_beneficiaries,
                "total_families": data.total_families,
                "total_value_brl": float(data.total_value_brl) if data.total_value_brl else None,
                "coverage_rate": float(data.coverage_rate) if data.coverage_rate else None,
                "reference_date": data.reference_date.isoformat(),
            }
            for data, prog in program_data
        ],
    }
