"""Admin API endpoints for advanced analytics and data export.

Provides endpoints for:
- Penetration rates by municipality (paginated)
- Coverage alerts (low coverage municipalities)
- Data export (CSV, JSON)
"""

from typing import Optional, List
from datetime import datetime
import csv
import io

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, case

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
    db: Session = Depends(get_db),
):
    """
    Get penetration rates by municipality with advanced filtering and pagination.

    Returns detailed coverage data for all municipalities, ideal for admin tables.
    """
    # Base query with municipality data
    query = (
        db.query(
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
        prog = db.query(Program).filter(Program.code == program.upper()).first()
        if prog:
            query = query.filter(BeneficiaryData.program_id == prog.id)

    # State filter
    if state_code:
        query = query.filter(State.abbreviation == state_code.upper())

    # Population filters
    if min_population:
        query = query.filter(Municipality.population >= min_population)
    if max_population:
        query = query.filter(Municipality.population <= max_population)

    # Group by municipality
    query = query.group_by(
        Municipality.ibge_code,
        Municipality.name,
        State.abbreviation,
        State.region,
        Municipality.population,
    )

    # Coverage filters (applied after grouping via HAVING)
    if min_coverage is not None:
        query = query.having(func.avg(BeneficiaryData.coverage_rate) >= min_coverage / 100)
    if max_coverage is not None:
        query = query.having(func.avg(BeneficiaryData.coverage_rate) <= max_coverage / 100)

    # Get total count before pagination
    count_query = query.with_entities(func.count()).scalar_subquery()

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
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))

    # Pagination
    total_count = db.query(Municipality).count()  # Simplified count
    results = query.offset(offset).limit(limit).all()

    # Get CadÚnico data for gap calculation
    cadunico_map = {}
    cadunico_query = (
        db.query(
            Municipality.ibge_code,
            func.sum(CadUnicoData.total_families).label("cadunico_families")
        )
        .join(CadUnicoData, Municipality.id == CadUnicoData.municipality_id)
        .group_by(Municipality.ibge_code)
    )
    for row in cadunico_query.all():
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
    db: Session = Depends(get_db),
):
    """
    Get coverage alerts for municipalities with low coverage.

    Returns municipalities with coverage below thresholds, categorized by severity.
    """
    # Query municipalities with coverage data
    query = (
        db.query(
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
        prog = db.query(Program).filter(Program.code == program.upper()).first()
        if prog:
            query = query.filter(BeneficiaryData.program_id == prog.id)

    if state_code:
        query = query.filter(State.abbreviation == state_code.upper())

    # Group and filter by coverage
    query = (
        query.group_by(
            Municipality.ibge_code,
            Municipality.name,
            State.abbreviation,
            Municipality.population,
        )
        .having(func.avg(BeneficiaryData.coverage_rate) < threshold_warning / 100)
        .order_by(asc(func.avg(BeneficiaryData.coverage_rate)))
        .limit(limit)
    )

    results = query.all()

    # Categorize alerts
    critical_threshold = threshold_critical / 100
    warning_threshold = threshold_warning / 100

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
    gap_query = (
        db.query(
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
        .first()
    )

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
    db: Session = Depends(get_db),
):
    """
    Export beneficiary data in CSV or JSON format.

    Ideal for downloading data for external analysis.
    """
    # Query all municipalities with data
    query = (
        db.query(
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
        prog = db.query(Program).filter(Program.code == program.upper()).first()
        if prog:
            query = query.filter(BeneficiaryData.program_id == prog.id)

    if scope == "state" and state_code:
        query = query.filter(State.abbreviation == state_code.upper())

    # Group by municipality
    query = query.group_by(
        Municipality.ibge_code,
        Municipality.name,
        State.name,
        State.abbreviation,
        State.region,
        Municipality.population,
    ).order_by(State.abbreviation, Municipality.name)

    results = query.all()

    # Get CadÚnico data
    cadunico_map = {}
    cadunico_query = (
        db.query(
            Municipality.ibge_code,
            func.sum(CadUnicoData.total_families).label("cadunico_families")
        )
        .join(CadUnicoData, Municipality.id == CadUnicoData.municipality_id)
        .group_by(Municipality.ibge_code)
    )
    for row in cadunico_query.all():
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
    db: Session = Depends(get_db),
):
    """
    Get quick summary statistics for admin dashboard.

    Returns key metrics and counts for the overview panel.
    """
    # Total municipalities
    total_municipalities = db.query(Municipality).count()

    # Total states
    total_states = db.query(State).count()

    # Total population
    total_population = db.query(func.sum(Municipality.population)).scalar() or 0

    # Total beneficiaries across all programs
    total_beneficiaries = db.query(func.sum(BeneficiaryData.total_beneficiaries)).scalar() or 0

    # Total value
    total_value = db.query(func.sum(BeneficiaryData.total_value_brl)).scalar() or 0

    # Average coverage
    avg_coverage = db.query(func.avg(BeneficiaryData.coverage_rate)).scalar() or 0

    # Critical municipalities (coverage < 20%)
    critical_count = (
        db.query(func.count(func.distinct(Municipality.id)))
        .join(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
        .group_by(Municipality.id)
        .having(func.avg(BeneficiaryData.coverage_rate) < 0.2)
        .count()
    )

    # Programs count
    programs_count = db.query(Program).count()

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
