"""Admin API endpoints for advanced analytics and data export.

Provides endpoints for:
- Penetration rates by municipality (paginated)
- Coverage alerts (low coverage municipalities)
- Data export (CSV, JSON)
"""

from typing import Optional
from datetime import datetime
import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, asc, select

from app.database import get_db
from app.models import State, Municipality, Program, BeneficiaryData, CadUnicoData

router = APIRouter()


@router.get("/penetration")
async def get_penetration_rates(
    state_code: Optional[str] = Query(None, description="Filter by state code (e.g., SP, RJ)"),
    program: Optional[str] = Query(None, description="Filter by program code"),
    min_population: Optional[int] = Query(None, description="Minimum population filter"),
    max_population: Optional[int] = Query(None, description="Maximum population filter"),
    min_coverage: Optional[float] = Query(None, description="Minimum coverage rate (0-100)"),
    max_coverage: Optional[float] = Query(None, description="Maximum coverage rate (0-100)"),
    order_by: str = Query("coverage", description="Order by: coverage, gap, population, value, name"),
    order_dir: str = Query("asc", description="Order direction: asc, desc"),
    limit: int = Query(50, ge=1, le=500, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get penetration rates by municipality with advanced filtering and pagination.

    Returns detailed coverage data for all municipalities, ideal for admin tables.
    """
    # Base query with municipality data
    stmt = (
        select(
            Municipality.ibge_code,
            Municipality.name.label("municipality_name"),
            State.abbreviation.label("state"),
            State.region,
            Municipality.population,
            func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
            func.sum(BeneficiaryData.total_families).label("total_families"),
            func.sum(BeneficiaryData.total_value_brl).label("total_value"),
            func.avg(BeneficiaryData.coverage_rate).label("coverage_rate"),
        )
        .join(State, Municipality.state_id == State.id)
        .outerjoin(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
    )

    # Program filter
    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            stmt = stmt.where(BeneficiaryData.program_id == prog.id)

    # State filter
    if state_code:
        stmt = stmt.where(State.abbreviation == state_code.upper())

    # Population filters
    if min_population:
        stmt = stmt.where(Municipality.population >= min_population)
    if max_population:
        stmt = stmt.where(Municipality.population <= max_population)

    # Group by municipality
    stmt = stmt.group_by(
        Municipality.ibge_code,
        Municipality.name,
        State.abbreviation,
        State.region,
        Municipality.population,
    )

    # Coverage filters (applied after grouping via HAVING)
    if min_coverage is not None:
        stmt = stmt.having(func.avg(BeneficiaryData.coverage_rate) >= min_coverage / 100)
    if max_coverage is not None:
        stmt = stmt.having(func.avg(BeneficiaryData.coverage_rate) <= max_coverage / 100)

    # Ordering
    order_map = {
        "coverage": func.avg(BeneficiaryData.coverage_rate),
        "gap": Municipality.population - func.sum(BeneficiaryData.total_beneficiaries),
        "population": Municipality.population,
        "value": func.sum(BeneficiaryData.total_value_brl),
        "name": Municipality.name,
        "beneficiaries": func.sum(BeneficiaryData.total_beneficiaries),
    }

    order_col = order_map.get(order_by, order_map["coverage"])
    if order_dir == "desc":
        stmt = stmt.order_by(desc(order_col))
    else:
        stmt = stmt.order_by(asc(order_col))

    # Get total count before pagination (simplified)
    total_count_stmt = select(func.count(Municipality.id))
    total_count_result = await db.execute(total_count_stmt)
    total_count = total_count_result.scalar() or 0

    # Pagination
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    results = result.all()

    # Get CadÚnico data for gap calculation
    cadunico_map = {}
    cadunico_stmt = (
        select(
            Municipality.ibge_code,
            func.sum(CadUnicoData.total_families).label("cadunico_families")
        )
        .join(CadUnicoData, Municipality.id == CadUnicoData.municipality_id)
        .group_by(Municipality.ibge_code)
    )
    cadunico_result = await db.execute(cadunico_stmt)
    for row in cadunico_result.all():
        cadunico_map[row.ibge_code] = row.cadunico_families or 0

    return {
        "level": "penetration",
        "total_count": total_count,
        "page_size": limit,
        "offset": offset,
        "filters": {
            "state": state_code,
            "program": program,
            "min_population": min_population,
            "max_population": max_population,
            "min_coverage": min_coverage,
            "max_coverage": max_coverage,
        },
        "data": [
            {
                "ibge_code": r.ibge_code,
                "municipality": r.municipality_name,
                "state": r.state,
                "region": r.region,
                "population": r.population or 0,
                "cadunico_families": cadunico_map.get(r.ibge_code, 0),
                "total_beneficiaries": r.total_beneficiaries or 0,
                "total_families": r.total_families or 0,
                "total_value_brl": float(r.total_value or 0),
                "coverage_rate": float(r.coverage_rate or 0) * 100,  # Convert to percentage
                "gap": max(0, cadunico_map.get(r.ibge_code, 0) - (r.total_families or 0)),
            }
            for r in results
        ],
    }


@router.get("/alerts")
async def get_coverage_alerts(
    threshold_critical: float = Query(20.0, description="Critical threshold (%)"),
    threshold_warning: float = Query(40.0, description="Warning threshold (%)"),
    program: Optional[str] = Query(None, description="Filter by program code"),
    state_code: Optional[str] = Query(None, description="Filter by state code"),
    limit: int = Query(50, ge=1, le=200, description="Max alerts to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get coverage alerts for municipalities with low coverage.

    Returns municipalities with coverage below thresholds, categorized by severity.
    """
    # Query municipalities with coverage data
    stmt = (
        select(
            Municipality.ibge_code,
            Municipality.name.label("municipality_name"),
            State.abbreviation.label("state"),
            Municipality.population,
            func.avg(BeneficiaryData.coverage_rate).label("coverage_rate"),
            func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
        )
        .join(State, Municipality.state_id == State.id)
        .join(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
    )

    # Filters
    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            stmt = stmt.where(BeneficiaryData.program_id == prog.id)

    if state_code:
        stmt = stmt.where(State.abbreviation == state_code.upper())

    # Group and filter by coverage
    stmt = (
        stmt.group_by(
            Municipality.ibge_code,
            Municipality.name,
            State.abbreviation,
            Municipality.population,
        )
        .having(func.avg(BeneficiaryData.coverage_rate) < threshold_warning / 100)
        .order_by(asc(func.avg(BeneficiaryData.coverage_rate)))
        .limit(limit)
    )

    result = await db.execute(stmt)
    results = result.all()

    # Categorize alerts
    critical_threshold = threshold_critical / 100
    threshold_warning / 100

    alerts = []
    critical_count = 0
    warning_count = 0

    for r in results:
        coverage = r.coverage_rate or 0
        if coverage < critical_threshold:
            alert_type = "critical"
            critical_count += 1
        else:
            alert_type = "warning"
            warning_count += 1

        alerts.append({
            "type": alert_type,
            "ibge_code": r.ibge_code,
            "municipality": r.municipality_name,
            "state": r.state,
            "population": r.population or 0,
            "coverage_rate": float(coverage * 100),
            "total_beneficiaries": r.total_beneficiaries or 0,
            "message": f"Cobertura de {coverage*100:.1f}% - {'CRÍTICO' if alert_type == 'critical' else 'Alerta'}",
        })

    # Get biggest gap municipality
    gap_stmt = (
        select(
            Municipality.name.label("municipality_name"),
            State.abbreviation.label("state"),
            Municipality.population,
            func.sum(CadUnicoData.total_families).label("cadunico_families"),
            func.sum(BeneficiaryData.total_families).label("beneficiary_families"),
        )
        .join(State, Municipality.state_id == State.id)
        .outerjoin(CadUnicoData, Municipality.id == CadUnicoData.municipality_id)
        .outerjoin(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
        .group_by(Municipality.name, State.abbreviation, Municipality.population)
        .order_by(desc(func.sum(CadUnicoData.total_families) - func.sum(BeneficiaryData.total_families)))
        .limit(1)
    )
    gap_result = await db.execute(gap_stmt)
    gap_query = gap_result.first()

    biggest_gap = None
    if gap_query:
        gap_value = (gap_query.cadunico_families or 0) - (gap_query.beneficiary_families or 0)
        if gap_value > 0:
            biggest_gap = {
                "municipality": gap_query.municipality_name,
                "state": gap_query.state,
                "gap": gap_value,
            }

    return {
        "summary": {
            "critical_count": critical_count,
            "warning_count": warning_count,
            "thresholds": {
                "critical": threshold_critical,
                "warning": threshold_warning,
            },
            "biggest_gap": biggest_gap,
        },
        "alerts": alerts,
    }


@router.get("/export")
async def export_data(
    format: str = Query("csv", description="Export format: csv, json"),
    scope: str = Query("national", description="Scope: national, state"),
    state_code: Optional[str] = Query(None, description="State code for state scope"),
    program: Optional[str] = Query(None, description="Filter by program code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Export beneficiary data in CSV or JSON format.

    Ideal for downloading data for external analysis.
    """
    # Query all municipalities with data
    stmt = (
        select(
            Municipality.ibge_code,
            Municipality.name.label("municipality_name"),
            State.name.label("state_name"),
            State.abbreviation.label("state"),
            State.region,
            Municipality.population,
            func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
            func.sum(BeneficiaryData.total_families).label("total_families"),
            func.sum(BeneficiaryData.total_value_brl).label("total_value"),
            func.avg(BeneficiaryData.coverage_rate).label("coverage_rate"),
        )
        .join(State, Municipality.state_id == State.id)
        .outerjoin(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
    )

    # Apply filters
    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            stmt = stmt.where(BeneficiaryData.program_id == prog.id)

    if scope == "state" and state_code:
        stmt = stmt.where(State.abbreviation == state_code.upper())

    # Group by municipality
    stmt = stmt.group_by(
        Municipality.ibge_code,
        Municipality.name,
        State.name,
        State.abbreviation,
        State.region,
        Municipality.population,
    ).order_by(State.abbreviation, Municipality.name)

    result = await db.execute(stmt)
    results = result.all()

    # Get CadÚnico data
    cadunico_map = {}
    cadunico_stmt = (
        select(
            Municipality.ibge_code,
            func.sum(CadUnicoData.total_families).label("cadunico_families")
        )
        .join(CadUnicoData, Municipality.id == CadUnicoData.municipality_id)
        .group_by(Municipality.ibge_code)
    )
    cadunico_result = await db.execute(cadunico_stmt)
    for row in cadunico_result.all():
        cadunico_map[row.ibge_code] = row.cadunico_families or 0

    # Prepare data
    data = []
    for r in results:
        cadunico = cadunico_map.get(r.ibge_code, 0)
        families = r.total_families or 0
        data.append({
            "ibge_code": r.ibge_code,
            "municipality": r.municipality_name,
            "state": r.state,
            "state_name": r.state_name,
            "region": r.region,
            "population": r.population or 0,
            "cadunico_families": cadunico,
            "total_beneficiaries": r.total_beneficiaries or 0,
            "total_families": families,
            "total_value_brl": float(r.total_value or 0),
            "coverage_rate": float((r.coverage_rate or 0) * 100),
            "gap": max(0, cadunico - families),
        })

    if format == "json":
        return {
            "export_date": datetime.now().isoformat(),
            "scope": scope,
            "state": state_code,
            "program": program,
            "total_rows": len(data),
            "data": data,
        }

    # CSV format
    output = io.StringIO()
    if data:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    content = output.getvalue()
    filename = f"tanamao_export_{scope}"
    if state_code:
        filename += f"_{state_code}"
    if program:
        filename += f"_{program}"
    filename += f"_{datetime.now().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/summary")
async def get_admin_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Get quick summary statistics for admin dashboard.

    Returns key metrics and counts for the overview panel.
    """
    # Total municipalities
    total_mun_stmt = select(func.count(Municipality.id))
    total_mun_result = await db.execute(total_mun_stmt)
    total_municipalities = total_mun_result.scalar() or 0

    # Total states
    total_states_stmt = select(func.count(State.id))
    total_states_result = await db.execute(total_states_stmt)
    total_states = total_states_result.scalar() or 0

    # Total population
    total_pop_stmt = select(func.sum(Municipality.population))
    total_pop_result = await db.execute(total_pop_stmt)
    total_population = total_pop_result.scalar() or 0

    # Total beneficiaries across all programs
    total_ben_stmt = select(func.sum(BeneficiaryData.total_beneficiaries))
    total_ben_result = await db.execute(total_ben_stmt)
    total_beneficiaries = total_ben_result.scalar() or 0

    # Total value
    total_val_stmt = select(func.sum(BeneficiaryData.total_value_brl))
    total_val_result = await db.execute(total_val_stmt)
    total_value = total_val_result.scalar() or 0

    # Average coverage
    avg_cov_stmt = select(func.avg(BeneficiaryData.coverage_rate))
    avg_cov_result = await db.execute(avg_cov_stmt)
    avg_coverage = avg_cov_result.scalar() or 0

    # Critical municipalities (coverage < 20%) - simplified count
    critical_stmt = (
        select(func.count(func.distinct(Municipality.id)))
        .join(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
        .group_by(Municipality.id)
        .having(func.avg(BeneficiaryData.coverage_rate) < 0.2)
    )
    # Note: This is a simplified count - for exact count, would need subquery
    critical_result = await db.execute(select(func.count()).select_from(critical_stmt.subquery()))
    critical_count = critical_result.scalar() or 0

    # Programs count
    programs_stmt = select(func.count(Program.id))
    programs_result = await db.execute(programs_stmt)
    programs_count = programs_result.scalar() or 0

    return {
        "total_municipalities": total_municipalities,
        "total_states": total_states,
        "total_population": total_population,
        "total_beneficiaries": total_beneficiaries,
        "total_value_brl": float(total_value),
        "avg_coverage_rate": float(avg_coverage * 100),
        "critical_municipalities": critical_count,
        "programs_tracked": programs_count,
    }
