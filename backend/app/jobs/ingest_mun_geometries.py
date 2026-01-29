"""Load municipality geometries from IBGE Malhas API.

Downloads GeoJSON geometries for all municipalities from IBGE API
and updates the database.

Source: https://servicodados.ibge.gov.br/api/v3/malhas/
"""

import asyncio
from typing import Optional
import logging

import httpx
from sqlalchemy.orm import Session
from shapely.geometry import shape, MultiPolygon
from geoalchemy2.shape import from_shape
from tenacity import retry, stop_after_attempt, wait_exponential

from app.database import SessionLocal
from app.models import State, Municipality

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IBGE Malhas API - Get municipalities by state
MALHAS_URL = "https://servicodados.ibge.gov.br/api/v3/malhas/estados/{state_code}?formato=application/vnd.geo+json&resolucao=2&intrarregiao=municipio"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_state_municipalities(client: httpx.AsyncClient, state_code: str) -> Optional[dict]:
    """Fetch municipality geometries for a state from IBGE."""
    url = MALHAS_URL.format(state_code=state_code)
    logger.info(f"Fetching municipalities for state {state_code}")
    try:
        response = await client.get(url, timeout=120.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch state {state_code}: {e}")
        return None


def update_municipality_geometries(db: Session, geojson: dict, state_code: str):
    """Update municipality geometries from GeoJSON."""
    if not geojson or "features" not in geojson:
        logger.warning(f"No features for state {state_code}")
        return 0

    updated = 0
    for feature in geojson["features"]:
        ibge_code = str(feature.get("properties", {}).get("codarea", ""))
        if not ibge_code:
            continue

        geometry = feature.get("geometry")
        if not geometry:
            continue

        # Find municipality in database
        mun = db.query(Municipality).filter(Municipality.ibge_code == ibge_code).first()
        if not mun:
            continue

        try:
            # Convert GeoJSON to Shapely geometry
            shapely_geom = shape(geometry)

            # Convert to MultiPolygon if needed
            if shapely_geom.geom_type == "Polygon":
                shapely_geom = MultiPolygon([shapely_geom])
            elif shapely_geom.geom_type != "MultiPolygon":
                logger.warning(f"Unexpected geometry type for {ibge_code}: {shapely_geom.geom_type}")
                continue

            # Update database
            mun.geometry = from_shape(shapely_geom, srid=4326)
            updated += 1

        except Exception as e:
            logger.warning(f"Failed to process geometry for {ibge_code}: {e}")
            continue

    db.commit()
    return updated


async def ingest_municipality_geometries():
    """Main function to ingest all municipality geometries."""
    logger.info("Starting municipality geometry ingestion")

    db = SessionLocal()
    try:
        # Get all states
        states = db.query(State).all()
        logger.info(f"Loading geometries for {len(states)} states")

        total_updated = 0

        async with httpx.AsyncClient() as client:
            for state in states:
                # Use IBGE code for API call
                geojson = await fetch_state_municipalities(client, state.ibge_code)

                if geojson:
                    updated = update_municipality_geometries(db, geojson, state.ibge_code)
                    total_updated += updated
                    logger.info(f"Updated {updated} municipalities for {state.abbreviation}")

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

        logger.info(f"Total municipalities updated: {total_updated}")

    finally:
        db.close()

    logger.info("Municipality geometry ingestion completed")


def run_ingestion():
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_municipality_geometries())


if __name__ == "__main__":
    run_ingestion()
