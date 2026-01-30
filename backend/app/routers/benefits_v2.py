"""
Benefits API v2 endpoints.
Unified benefits catalog with eligibility evaluation.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.benefit import Benefit
from app.schemas.benefit import (
    BenefitResponse,
    BenefitSummary,
    BenefitListResponse,
    BenefitStatsResponse,
    CitizenProfile,
    EligibilityRequest,
    EligibilityResponse,
    EstimatedValue,
)
from app.services.eligibility_service import (
    evaluate_all_benefits,
    get_benefits_for_location,
)

router = APIRouter()


@router.get("/", response_model=BenefitListResponse)
async def list_benefits(
    scope: Optional[str] = Query(None, description="Filter by scope: federal, state, municipal, sectoral"),
    state: Optional[str] = Query(None, description="Filter by state code (e.g., SP, RJ)"),
    municipality_ibge: Optional[str] = Query(None, description="Filter by municipality IBGE code"),
    sector: Optional[str] = Query(None, description="Filter by sector (e.g., pescador, agricultor)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    status: Optional[str] = Query("active", description="Filter by status: active, suspended, ended"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all benefits with optional filters.

    Returns a paginated list of benefits from the unified catalog.
    Includes federal, state, municipal, and sectoral benefits.

    Examples:
    - GET /api/v2/benefits?scope=federal
    - GET /api/v2/benefits?state=SP&scope=state
    - GET /api/v2/benefits?municipality_ibge=3550308
    - GET /api/v2/benefits?search=bolsa
    """
    # Build base query
    stmt = select(Benefit)

    # Apply filters
    if scope:
        stmt = stmt.where(Benefit.scope == scope.lower())

    if state:
        stmt = stmt.where(Benefit.state == state.upper())

    if municipality_ibge:
        stmt = stmt.where(Benefit.municipality_ibge == municipality_ibge)

    if sector:
        stmt = stmt.where(Benefit.sector == sector.lower())

    if category:
        stmt = stmt.where(Benefit.category.ilike(f"%{category}%"))

    if status:
        stmt = stmt.where(Benefit.status == status.lower())

    if search:
        search_filter = f"%{search.lower()}%"
        stmt = stmt.where(
            (Benefit.name.ilike(search_filter)) |
            (Benefit.short_description.ilike(search_filter))
        )

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * limit
    stmt = stmt.order_by(Benefit.name).offset(offset).limit(limit)
    result = await db.execute(stmt)
    benefits = result.scalars().all()

    # Convert to response format
    items = []
    for b in benefits:
        est_value = None
        if b.estimated_value:
            est_value = EstimatedValue(
                type=b.estimated_value.get("type", "monthly"),
                min=b.estimated_value.get("min"),
                max=b.estimated_value.get("max"),
                description=b.estimated_value.get("description"),
            )
        items.append(BenefitSummary(
            id=b.id,
            name=b.name,
            shortDescription=b.short_description,
            scope=b.scope,
            state=b.state,
            municipalityIbge=b.municipality_ibge,
            estimatedValue=est_value,
            status=b.status,
            icon=b.icon,
            category=b.category,
        ))

    return BenefitListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 0,
    )


@router.get("/stats", response_model=BenefitStatsResponse)
async def get_benefits_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics about the benefits catalog.

    Returns total counts by scope, category, and geographic coverage.
    """
    # Total benefits
    total_stmt = select(func.count()).select_from(Benefit)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar() or 0

    # By scope
    scope_stmt = select(
        Benefit.scope,
        func.count().label("count")
    ).group_by(Benefit.scope)
    scope_result = await db.execute(scope_stmt)
    by_scope = {row.scope: row.count for row in scope_result}

    # By category
    category_stmt = select(
        Benefit.category,
        func.count().label("count")
    ).where(Benefit.category.isnot(None)).group_by(Benefit.category)
    category_result = await db.execute(category_stmt)
    by_category = {row.category: row.count for row in category_result}

    # States covered
    states_stmt = select(func.count(func.distinct(Benefit.state))).where(
        Benefit.state.isnot(None)
    )
    states_result = await db.execute(states_stmt)
    states_covered = states_result.scalar() or 0

    # Municipalities covered
    muni_stmt = select(func.count(func.distinct(Benefit.municipality_ibge))).where(
        Benefit.municipality_ibge.isnot(None)
    )
    muni_result = await db.execute(muni_stmt)
    municipalities_covered = muni_result.scalar() or 0

    return BenefitStatsResponse(
        totalBenefits=total,
        byScope=by_scope,
        byCategory=by_category,
        statesCovered=states_covered,
        municipalitiesCovered=municipalities_covered,
    )


@router.get("/by-location/{state_code}")
async def get_benefits_by_location(
    state_code: str,
    municipality_ibge: Optional[str] = Query(None, description="IBGE code for municipal benefits"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all applicable benefits for a specific location.

    Returns federal + state + municipal benefits for the given location.

    Examples:
    - GET /api/v2/benefits/by-location/SP (federal + SP state benefits)
    - GET /api/v2/benefits/by-location/SP?municipality_ibge=3550308 (includes São Paulo city benefits)
    """
    benefits = await get_benefits_for_location(
        db,
        state_code=state_code.upper(),
        ibge_code=municipality_ibge,
    )

    # Group by scope
    federal = []
    state = []
    municipal = []
    sectoral = []

    for b in benefits:
        item = b.to_dict()
        if b.scope == "federal":
            federal.append(item)
        elif b.scope == "state":
            state.append(item)
        elif b.scope == "municipal":
            municipal.append(item)
        elif b.scope == "sectoral":
            sectoral.append(item)

    return {
        "state": state_code.upper(),
        "municipality_ibge": municipality_ibge,
        "total": len(benefits),
        "federal": federal,
        "state": state,
        "municipal": municipal,
        "sectoral": sectoral,
    }


@router.get("/{benefit_id}")
async def get_benefit(
    benefit_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get full details of a specific benefit.

    Examples:
    - GET /api/v2/benefits/federal-bolsa-familia
    - GET /api/v2/benefits/sp-bolsa-povo
    """
    stmt = select(Benefit).where(Benefit.id == benefit_id)
    result = await db.execute(stmt)
    benefit = result.scalar_one_or_none()

    if not benefit:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")

    return benefit.to_dict()


@router.post("/eligibility/check", response_model=EligibilityResponse)
async def check_eligibility(
    request: EligibilityRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate eligibility for all benefits based on citizen profile.

    Receives a CitizenProfile and returns eligibility status for all
    applicable benefits, grouped by status (eligible, likely_eligible,
    maybe, not_eligible, not_applicable, already_receiving).

    Also returns:
    - Total potential monthly/annual/one-time values
    - Priority steps (what to do first)
    - Documents needed

    Example request:
    ```json
    {
      "profile": {
        "estado": "SP",
        "municipioIbge": "3550308",
        "pessoasNaCasa": 4,
        "rendaFamiliarMensal": 800,
        "cadastradoCadunico": true
      }
    }
    ```
    """
    response = await evaluate_all_benefits(
        db=db,
        profile=request.profile,
        scope=request.scope,
        include_not_applicable=request.include_not_applicable,
    )

    return response


@router.post("/eligibility/quick")
async def quick_eligibility_check(
    estado: str = Query(..., description="UF code (e.g., SP)"),
    renda_familiar: float = Query(..., ge=0, description="Monthly family income"),
    pessoas_na_casa: int = Query(1, ge=1, description="Number of people in household"),
    cadastrado_cadunico: bool = Query(False, description="Registered in CadÚnico?"),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick eligibility check with minimal parameters.

    Useful for a simplified initial assessment.
    For full evaluation, use POST /eligibility/check.
    """
    profile = CitizenProfile(
        estado=estado.upper(),
        pessoasNaCasa=pessoas_na_casa,
        rendaFamiliarMensal=renda_familiar,
        cadastradoCadunico=cadastrado_cadunico,
        quantidadeFilhos=0,
        temIdoso65Mais=False,
        temGestante=False,
        temPcd=False,
        temCrianca0a6=False,
        trabalhoFormal=False,
        temCasaPropria=False,
        moradiaZonaRural=False,
        recebeBolsaFamilia=False,
        recebeBpc=False,
        temMei=False,
        trabalhaAplicativo=False,
        agricultorFamiliar=False,
        pescadorArtesanal=False,
        catadorReciclavel=False,
        estudante=False,
        redePublica=False,
    )

    request = EligibilityRequest(
        profile=profile,
        scope=None,
        includeNotApplicable=False,
    )

    response = await evaluate_all_benefits(
        db=db,
        profile=profile,
        scope=None,
        include_not_applicable=False,
    )

    # Return simplified response
    return {
        "estado": estado.upper(),
        "rendaPerCapita": renda_familiar / pessoas_na_casa,
        "totalEligible": len(response.summary.eligible),
        "totalLikelyEligible": len(response.summary.likely_eligible),
        "totalPotentialMonthly": response.summary.total_potential_monthly,
        "topBenefits": [
            {
                "id": r.benefit.id,
                "name": r.benefit.name,
                "estimatedValue": r.estimated_value,
            }
            for r in (response.summary.eligible + response.summary.likely_eligible)[:5]
        ],
        "nextStep": response.summary.priority_steps[0] if response.summary.priority_steps else None,
    }
