"""Aggregation API endpoints for national, state, and regional statistics."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.database import get_db
from app.models import State, Municipality, Program, BeneficiaryData

router = APIRouter()


@router.get("/national")
async def get_national_aggregation(
    program: Optional[str] = Query(None, description="Filter by program code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get national-level aggregated statistics.

    Returns totals across all municipalities for all or a specific program.
    """
    stmt = select(
        func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
        func.sum(BeneficiaryData.total_families).label("total_families"),
        func.sum(BeneficiaryData.total_value_brl).label("total_value"),
        func.avg(BeneficiaryData.coverage_rate).label("avg_coverage"),
    )

    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            stmt = stmt.where(BeneficiaryData.program_id == prog.id)

    result = await db.execute(stmt)
    stats = result.first()

    # Get population total
    pop_stmt = select(func.sum(Municipality.population))
    pop_result = await db.execute(pop_stmt)
    pop_total = pop_result.scalar() or 0

    # Get CadÚnico families
    from app.models import CadUnicoData
    cadunico_stmt = select(func.sum(CadUnicoData.total_families))
    cadunico_result = await db.execute(cadunico_stmt)
    cadunico_total = cadunico_result.scalar() or 0

    # Get counts
    mun_count_stmt = select(func.count(Municipality.id))
    mun_count_result = await db.execute(mun_count_stmt)
    total_municipalities = mun_count_result.scalar() or 0

    state_count_stmt = select(func.count(State.id))
    state_count_result = await db.execute(state_count_stmt)
    total_states = state_count_result.scalar() or 0

    return {
        "level": "national",
        "population": pop_total,
        "cadunico_families": cadunico_total,
        "total_municipalities": total_municipalities,
        "total_states": total_states,
        "program_stats": {
            "total_beneficiaries": stats.total_beneficiaries or 0,
            "total_families": stats.total_families or 0,
            "total_value_brl": float(stats.total_value or 0),
            "avg_coverage_rate": float(stats.avg_coverage or 0),
        },
    }


@router.get("/states")
async def get_states_aggregation(
    program: Optional[str] = Query(None, description="Filter by program code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get state-level aggregated statistics.

    Returns aggregated data for all 27 Brazilian states.
    """
    from app.models import CadUnicoData

    # Base query joining states with municipalities and beneficiary data
    stmt = (
        select(
            State.id,
            State.ibge_code,
            State.name,
            State.abbreviation,
            State.region,
            func.sum(Municipality.population).label("population"),
            func.count(func.distinct(Municipality.id)).label("municipality_count"),
            func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
            func.sum(BeneficiaryData.total_families).label("total_families"),
            func.sum(BeneficiaryData.total_value_brl).label("total_value"),
            func.avg(BeneficiaryData.coverage_rate).label("avg_coverage"),
        )
        .select_from(State)
        .join(Municipality, State.id == Municipality.state_id)
        .outerjoin(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
    )

    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            stmt = stmt.where(BeneficiaryData.program_id == prog.id)

    stmt = stmt.group_by(
        State.id, State.ibge_code, State.name, State.abbreviation, State.region
    )

    result = await db.execute(stmt)
    results = result.all()

    # Get CadÚnico families per state
    cadunico_by_state = {}
    cadunico_stmt = (
        select(
            State.id,
            func.sum(CadUnicoData.total_families).label("cadunico_families")
        )
        .select_from(State)
        .join(Municipality, State.id == Municipality.state_id)
        .join(CadUnicoData, Municipality.id == CadUnicoData.municipality_id)
        .group_by(State.id)
    )
    cadunico_result = await db.execute(cadunico_stmt)
    for row in cadunico_result.all():
        cadunico_by_state[row.id] = row.cadunico_families or 0

    return {
        "level": "states",
        "count": len(results),
        "states": [
            {
                "ibge_code": r.ibge_code,
                "name": r.name,
                "abbreviation": r.abbreviation,
                "region": r.region,
                "population": r.population or 0,
                "municipality_count": r.municipality_count or 0,
                "total_beneficiaries": r.total_beneficiaries or 0,
                "total_families": r.total_families or 0,
                "cadunico_families": cadunico_by_state.get(r.id, 0),
                "total_value_brl": float(r.total_value or 0),
                "avg_coverage_rate": float(r.avg_coverage or 0) if r.avg_coverage else 0,
            }
            for r in results
        ],
    }


@router.get("/states/{state_code}")
async def get_state_detail(
    state_code: str,
    program: Optional[str] = Query(None, description="Filter by program code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed statistics for a specific state.

    Includes all municipalities within the state.
    """
    state_stmt = select(State).where(State.abbreviation == state_code.upper())
    state_result = await db.execute(state_stmt)
    state = state_result.scalar_one_or_none()

    if not state:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="State not found")

    # Get municipalities with their data
    stmt = (
        select(
            Municipality.ibge_code,
            Municipality.name,
            Municipality.population,
            func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
            func.sum(BeneficiaryData.total_families).label("total_families"),
            func.avg(BeneficiaryData.coverage_rate).label("avg_coverage"),
        )
        .select_from(Municipality)
        .outerjoin(BeneficiaryData)
        .where(Municipality.state_id == state.id)
    )

    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            stmt = stmt.where(BeneficiaryData.program_id == prog.id)

    stmt = stmt.group_by(
        Municipality.ibge_code, Municipality.name, Municipality.population
    )

    result = await db.execute(stmt)
    municipalities = result.all()

    return {
        "level": "state",
        "state": {
            "ibge_code": state.ibge_code,
            "name": state.name,
            "abbreviation": state.abbreviation,
            "region": state.region,
        },
        "municipality_count": len(municipalities),
        "municipalities": [
            {
                "ibge_code": m.ibge_code,
                "name": m.name,
                "population": m.population or 0,
                "total_beneficiaries": m.total_beneficiaries or 0,
                "total_families": m.total_families or 0,
                "avg_coverage_rate": float(m.avg_coverage or 0) if m.avg_coverage else 0,
            }
            for m in municipalities
        ],
    }


@router.get("/demographics")
async def get_demographics(
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get demographic breakdown from CadÚnico data.

    Returns income brackets and age distribution.
    """
    from app.models import CadUnicoData

    stmt = select(
        func.sum(CadUnicoData.total_families).label("total_families"),
        func.sum(CadUnicoData.total_persons).label("total_persons"),
        func.sum(CadUnicoData.families_extreme_poverty).label("extreme_poverty"),
        func.sum(CadUnicoData.families_poverty).label("poverty"),
        func.sum(CadUnicoData.families_low_income).label("low_income"),
        func.sum(CadUnicoData.persons_0_5_years).label("age_0_5"),
        func.sum(CadUnicoData.persons_6_14_years).label("age_6_14"),
        func.sum(CadUnicoData.persons_15_17_years).label("age_15_17"),
        func.sum(CadUnicoData.persons_18_64_years).label("age_18_64"),
        func.sum(CadUnicoData.persons_65_plus).label("age_65_plus"),
    ).select_from(CadUnicoData)

    if state_code:
        state_stmt = select(State).where(State.abbreviation == state_code.upper())
        state_result = await db.execute(state_stmt)
        state = state_result.scalar_one_or_none()
        if state:
            stmt = stmt.join(Municipality).where(Municipality.state_id == state.id)

    db_result = await db.execute(stmt)
    result = db_result.first()

    total_families = result.total_families or 0
    total_persons = result.total_persons or 0

    return {
        "level": "demographics",
        "total_families": total_families,
        "total_persons": total_persons,
        "income_brackets": {
            "extreme_poverty": result.extreme_poverty or 0,
            "poverty": result.poverty or 0,
            "low_income": result.low_income or 0,
        },
        "age_distribution": {
            "0_5": result.age_0_5 or 0,
            "6_14": result.age_6_14 or 0,
            "15_17": result.age_15_17 or 0,
            "18_64": result.age_18_64 or 0,
            "65_plus": result.age_65_plus or 0,
        },
    }


@router.get("/time-series")
async def get_time_series(
    program: Optional[str] = Query(None, description="Filter by program code"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get time-series data for beneficiaries aggregated by month.

    Returns monthly totals for charting trends over time.
    """
    stmt = (
        select(
            BeneficiaryData.reference_date,
            func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
            func.sum(BeneficiaryData.total_families).label("total_families"),
            func.sum(BeneficiaryData.total_value_brl).label("total_value"),
            func.avg(BeneficiaryData.coverage_rate).label("avg_coverage"),
        )
        .select_from(BeneficiaryData)
    )

    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            stmt = stmt.where(BeneficiaryData.program_id == prog.id)

    if state_code:
        state_stmt = select(State).where(State.abbreviation == state_code.upper())
        state_result = await db.execute(state_stmt)
        state = state_result.scalar_one_or_none()
        if state:
            stmt = stmt.join(Municipality).where(Municipality.state_id == state.id)

    stmt = stmt.group_by(BeneficiaryData.reference_date).order_by(BeneficiaryData.reference_date)

    db_result = await db.execute(stmt)
    results = db_result.all()

    return {
        "level": "time_series",
        "count": len(results),
        "data": [
            {
                "date": r.reference_date.isoformat(),
                "month": r.reference_date.strftime("%b/%y"),
                "total_beneficiaries": r.total_beneficiaries or 0,
                "total_families": r.total_families or 0,
                "total_value_brl": float(r.total_value or 0),
                "avg_coverage_rate": float(r.avg_coverage or 0) if r.avg_coverage else 0,
            }
            for r in results
        ],
    }


@router.get("/regions")
async def get_regions_aggregation(
    program: Optional[str] = Query(None, description="Filter by program code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get region-level aggregated statistics.

    Returns data aggregated by Brazilian regions (Norte, Nordeste, Centro-Oeste, Sudeste, Sul).
    """
    stmt = (
        select(
            State.region,
            func.sum(Municipality.population).label("population"),
            func.count(func.distinct(State.id)).label("state_count"),
            func.count(Municipality.id).label("municipality_count"),
            func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
            func.sum(BeneficiaryData.total_families).label("total_families"),
            func.sum(BeneficiaryData.total_value_brl).label("total_value"),
            func.avg(BeneficiaryData.coverage_rate).label("avg_coverage"),
        )
        .select_from(State)
        .join(Municipality, State.id == Municipality.state_id)
        .outerjoin(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
    )

    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            stmt = stmt.where(BeneficiaryData.program_id == prog.id)

    stmt = stmt.group_by(State.region)

    db_result = await db.execute(stmt)
    results = db_result.all()

    region_names = {
        "N": "Norte",
        "NE": "Nordeste",
        "CO": "Centro-Oeste",
        "SE": "Sudeste",
        "S": "Sul",
    }

    return {
        "level": "regions",
        "count": len(results),
        "regions": [
            {
                "code": r.region,
                "name": region_names.get(r.region, r.region),
                "population": r.population or 0,
                "state_count": r.state_count or 0,
                "municipality_count": r.municipality_count or 0,
                "total_beneficiaries": r.total_beneficiaries or 0,
                "total_families": r.total_families or 0,
                "total_value_brl": float(r.total_value or 0),
                "avg_coverage_rate": float(r.avg_coverage or 0) if r.avg_coverage else 0,
            }
            for r in results
        ],
    }
