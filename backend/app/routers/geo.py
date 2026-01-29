"""GeoJSON API endpoints for map rendering."""

from typing import Optional
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.database import get_db
from app.models import State, Municipality, BeneficiaryData, Program

router = APIRouter()


@router.get("/states")
async def get_states_geojson(
    simplified: bool = Query(True, description="Use simplified geometry"),
    program: Optional[str] = Query(None, description="Include program data"),
    metric: Optional[str] = Query(None, description="Metric for choropleth: beneficiaries, coverage, gap"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get GeoJSON FeatureCollection of all Brazilian states.

    Returns simplified or full geometry with optional program statistics.
    """
    # Build query with geometry
    if simplified:
        # Simplify geometry (tolerance in degrees, ~0.01 = ~1km)
        geom_column = func.ST_AsGeoJSON(func.ST_Simplify(State.geometry, 0.01))
    else:
        geom_column = func.ST_AsGeoJSON(State.geometry)

    stmt = select(
        State.id,
        State.ibge_code,
        State.name,
        State.abbreviation,
        State.region,
        geom_column.label("geometry"),
    )

    result = await db.execute(stmt)
    states = result.all()

    # Get program data if requested
    program_data = {}
    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            # Aggregate beneficiary data by state
            state_stats_stmt = (
                select(
                    Municipality.state_id,
                    func.sum(BeneficiaryData.total_beneficiaries).label("beneficiaries"),
                    func.sum(BeneficiaryData.total_families).label("families"),
                    func.avg(BeneficiaryData.coverage_rate).label("coverage"),
                )
                .join(BeneficiaryData, Municipality.id == BeneficiaryData.municipality_id)
                .where(BeneficiaryData.program_id == prog.id)
                .group_by(Municipality.state_id)
            )
            state_stats_result = await db.execute(state_stats_stmt)
            state_stats = state_stats_result.all()

            for stat in state_stats:
                program_data[stat.state_id] = {
                    "beneficiaries": stat.beneficiaries or 0,
                    "families": stat.families or 0,
                    "coverage": float(stat.coverage or 0),
                }

    # Build GeoJSON
    features = []
    for state in states:
        properties = {
            "ibge_code": state.ibge_code,
            "name": state.name,
            "abbreviation": state.abbreviation,
            "region": state.region,
        }

        # Add program data if available
        if state.id in program_data:
            properties.update(program_data[state.id])

        feature = {
            "type": "Feature",
            "properties": properties,
            "geometry": json.loads(state.geometry) if state.geometry else None,
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.get("/municipalities")
async def get_municipalities_geojson(
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    state_code: Optional[str] = Query(None, description="Filter by state abbreviation"),
    simplified: bool = Query(True, description="Use simplified geometry"),
    program: Optional[str] = Query(None, description="Include program data"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get GeoJSON FeatureCollection of municipalities.

    **Important**: For performance, always filter by state when rendering maps.
    Loading all 5,570 municipalities at once is not recommended.
    """
    # Resolve state filter
    state_filter = None
    if state_code:
        state_stmt = select(State).where(State.abbreviation == state_code.upper())
        state_result = await db.execute(state_stmt)
        state = state_result.scalar_one_or_none()
        if state:
            state_filter = state.id
        else:
            raise HTTPException(status_code=404, detail="State not found")
    elif state_id:
        state_filter = state_id

    # Build geometry column
    if simplified:
        geom_column = func.ST_AsGeoJSON(
            func.coalesce(
                Municipality.geometry_simplified,
                func.ST_Simplify(Municipality.geometry, 0.005)
            )
        )
    else:
        geom_column = func.ST_AsGeoJSON(Municipality.geometry)

    stmt = select(
        Municipality.id,
        Municipality.ibge_code,
        Municipality.name,
        Municipality.state_id,
        Municipality.population,
        geom_column.label("geometry"),
    )

    if state_filter:
        stmt = stmt.where(Municipality.state_id == state_filter)
    else:
        # Limit to prevent memory issues
        stmt = stmt.limit(500)

    result = await db.execute(stmt)
    municipalities = result.all()

    # Get program data if requested
    program_data = {}
    if program:
        prog_stmt = select(Program).where(Program.code == program.upper())
        prog_result = await db.execute(prog_stmt)
        prog = prog_result.scalar_one_or_none()
        if prog:
            mun_ids = [m.id for m in municipalities]
            stats_stmt = (
                select(
                    BeneficiaryData.municipality_id,
                    BeneficiaryData.total_beneficiaries,
                    BeneficiaryData.total_families,
                    BeneficiaryData.coverage_rate,
                )
                .where(BeneficiaryData.program_id == prog.id)
                .where(BeneficiaryData.municipality_id.in_(mun_ids))
            )
            stats_result = await db.execute(stats_stmt)
            stats = stats_result.all()

            for stat in stats:
                program_data[stat.municipality_id] = {
                    "beneficiaries": stat.total_beneficiaries or 0,
                    "families": stat.total_families or 0,
                    "coverage": float(stat.coverage_rate or 0),
                }

    # Build GeoJSON
    features = []
    for mun in municipalities:
        properties = {
            "ibge_code": mun.ibge_code,
            "name": mun.name,
            "state_id": mun.state_id,
            "population": mun.population,
        }

        if mun.id in program_data:
            properties.update(program_data[mun.id])

        feature = {
            "type": "Feature",
            "properties": properties,
            "geometry": json.loads(mun.geometry) if mun.geometry else None,
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "count": len(features),
            "state_id": state_filter,
            "simplified": simplified,
        },
    }


@router.get("/municipalities/{ibge_code}")
async def get_municipality_geojson(
    ibge_code: str,
    simplified: bool = Query(False, description="Use simplified geometry"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get GeoJSON Feature for a single municipality.
    """
    if simplified:
        geom_column = func.ST_AsGeoJSON(
            func.coalesce(
                Municipality.geometry_simplified,
                Municipality.geometry
            )
        )
    else:
        geom_column = func.ST_AsGeoJSON(Municipality.geometry)

    stmt = select(
        Municipality.ibge_code,
        Municipality.name,
        Municipality.state_id,
        Municipality.population,
        Municipality.area_km2,
        geom_column.label("geometry"),
    ).where(Municipality.ibge_code == ibge_code)

    result_exec = await db.execute(stmt)
    result = result_exec.first()

    if not result:
        raise HTTPException(status_code=404, detail="Municipality not found")

    return {
        "type": "Feature",
        "properties": {
            "ibge_code": result.ibge_code,
            "name": result.name,
            "state_id": result.state_id,
            "population": result.population,
            "area_km2": float(result.area_km2) if result.area_km2 else None,
        },
        "geometry": json.loads(result.geometry) if result.geometry else None,
    }


@router.get("/bounds")
async def get_bounds(
    state_code: Optional[str] = Query(None, description="Get bounds for specific state"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get bounding box for Brazil or a specific state.

    Returns [minLng, minLat, maxLng, maxLat] for Leaflet fitBounds.
    """
    if state_code:
        state_stmt = select(State).where(State.abbreviation == state_code.upper())
        state_result = await db.execute(state_stmt)
        state = state_result.scalar_one_or_none()
        if not state:
            raise HTTPException(status_code=404, detail="State not found")

        # Get envelope of state geometry
        bounds_stmt = select(
            func.ST_XMin(func.ST_Envelope(State.geometry)).label("min_lng"),
            func.ST_YMin(func.ST_Envelope(State.geometry)).label("min_lat"),
            func.ST_XMax(func.ST_Envelope(State.geometry)).label("max_lng"),
            func.ST_YMax(func.ST_Envelope(State.geometry)).label("max_lat"),
        ).where(State.id == state.id)
        bounds_result = await db.execute(bounds_stmt)
        bounds = bounds_result.first()
    else:
        # Brazil bounds (approximate)
        return {
            "bounds": [-73.99, -33.75, -28.85, 5.27],
            "center": [-51.92, -14.24],
        }

    return {
        "bounds": [bounds.min_lng, bounds.min_lat, bounds.max_lng, bounds.max_lat],
        "center": [
            (bounds.min_lng + bounds.max_lng) / 2,
            (bounds.min_lat + bounds.max_lat) / 2,
        ],
    }
