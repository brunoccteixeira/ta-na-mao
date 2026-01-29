"""Programs API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.database import get_db
from app.models import Program, BeneficiaryData, Municipality

router = APIRouter()


@router.get("/")
async def list_programs(db: AsyncSession = Depends(get_db)):
    """
    List all tracked social programs.

    Returns program metadata and national statistics.

    **Example Response:**
    ```json
    [
      {
        "code": "BOLSA_FAMILIA",
        "name": "Bolsa Família",
        "description": "Programa de transferência de renda",
        "national_stats": {
          "total_beneficiaries": 20600000,
          "total_families": 15000000,
          "total_value_brl": 12000000000.0,
          "latest_data_date": "2024-01-01"
        }
      }
    ]
    ```
    """
    # Query all active programs
    stmt = select(Program).where(Program.is_active is True)
    result = await db.execute(stmt)
    programs = result.scalars().all()

    result_list = []
    for prog in programs:
        # Get national totals for latest date
        latest_data_stmt = (
            select(
                func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
                func.sum(BeneficiaryData.total_families).label("total_families"),
                func.sum(BeneficiaryData.total_value_brl).label("total_value"),
                func.max(BeneficiaryData.reference_date).label("latest_date"),
            )
            .where(BeneficiaryData.program_id == prog.id)
        )
        latest_data_result = await db.execute(latest_data_stmt)
        latest_data = latest_data_result.first()

        result_list.append({
            "code": prog.code,
            "name": prog.name,
            "description": prog.description,
            "data_source_url": prog.data_source_url,
            "update_frequency": prog.update_frequency,
            "national_stats": {
                "total_beneficiaries": latest_data.total_beneficiaries or 0,
                "total_families": latest_data.total_families or 0,
                "total_value_brl": float(latest_data.total_value or 0),
                "latest_data_date": latest_data.latest_date.isoformat() if latest_data.latest_date else None,
            },
        })

    return result_list


@router.get("/{code}")
async def get_program(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get program details and national statistics.

    - **code**: Program code (TSEE, FARMACIA_POPULAR, etc.)
    """
    stmt = select(Program).where(Program.code == code.upper())
    result = await db.execute(stmt)
    program = result.scalar_one_or_none()

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    # Get national totals
    totals_stmt = (
        select(
            func.sum(BeneficiaryData.total_beneficiaries).label("total_beneficiaries"),
            func.sum(BeneficiaryData.total_families).label("total_families"),
            func.sum(BeneficiaryData.total_value_brl).label("total_value"),
            func.avg(BeneficiaryData.coverage_rate).label("avg_coverage"),
            func.count(func.distinct(BeneficiaryData.municipality_id)).label("municipalities_covered"),
        )
        .where(BeneficiaryData.program_id == program.id)
    )
    totals_result = await db.execute(totals_stmt)
    totals = totals_result.first()

    # Get total municipalities count
    mun_count_stmt = select(func.count(Municipality.id))
    mun_count_result = await db.execute(mun_count_stmt)
    total_municipalities = mun_count_result.scalar() or 0

    return {
        "code": program.code,
        "name": program.name,
        "description": program.description,
        "data_source_url": program.data_source_url,
        "update_frequency": program.update_frequency,
        "national_stats": {
            "total_beneficiaries": totals.total_beneficiaries or 0,
            "total_families": totals.total_families or 0,
            "total_value_brl": float(totals.total_value or 0),
            "avg_coverage_rate": float(totals.avg_coverage or 0),
            "municipalities_covered": totals.municipalities_covered or 0,
            "total_municipalities": total_municipalities,
            "coverage_percentage": (
                (totals.municipalities_covered or 0) / total_municipalities * 100
                if total_municipalities > 0
                else 0
            ),
        },
    }


@router.get("/{code}/ranking")
async def get_program_ranking(
    code: str,
    state_code: Optional[str] = Query(None, description="Filter by state abbreviation"),
    order_by: str = Query("beneficiaries", description="Order by: beneficiaries, coverage, value"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get municipality ranking for a specific program.

    Returns top municipalities ordered by beneficiaries, coverage, or value.
    """
    stmt = select(Program).where(Program.code == code.upper())
    result = await db.execute(stmt)
    program = result.scalar_one_or_none()

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    # Build query
    stmt = (
        select(BeneficiaryData, Municipality)
        .join(Municipality)
        .where(BeneficiaryData.program_id == program.id)
    )

    # Filter by state if provided
    if state_code:
        from app.models import State
        state_stmt = select(State).where(State.abbreviation == state_code.upper())
        state_result = await db.execute(state_stmt)
        state = state_result.scalar_one_or_none()
        if state:
            stmt = stmt.where(Municipality.state_id == state.id)

    # Order by selected metric
    order_column = {
        "beneficiaries": BeneficiaryData.total_beneficiaries.desc(),
        "coverage": BeneficiaryData.coverage_rate.desc(),
        "value": BeneficiaryData.total_value_brl.desc(),
    }.get(order_by, BeneficiaryData.total_beneficiaries.desc())

    stmt = stmt.order_by(order_column).limit(limit)
    result = await db.execute(stmt)
    results = result.all()

    return {
        "program_code": program.code,
        "program_name": program.name,
        "order_by": order_by,
        "ranking": [
            {
                "rank": idx + 1,
                "ibge_code": mun.ibge_code,
                "name": mun.name,
                "total_beneficiaries": data.total_beneficiaries,
                "total_families": data.total_families,
                "coverage_rate": float(data.coverage_rate) if data.coverage_rate else None,
                "total_value_brl": float(data.total_value_brl) if data.total_value_brl else None,
                "reference_date": data.reference_date.isoformat(),
            }
            for idx, (data, mun) in enumerate(results)
        ],
    }
