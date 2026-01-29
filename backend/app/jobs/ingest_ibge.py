"""IBGE data ingestion script.

Downloads and imports:
- All 27 Brazilian states with geometries
- All ~5,570 municipalities with geometries
- Population and area data

Sources:
- IBGE Localidades API: https://servicodados.ibge.gov.br/api/v1/localidades/
- IBGE Malhas API v3: https://servicodados.ibge.gov.br/api/v3/malhas/
"""

import asyncio
from typing import Dict, List, Optional
import logging

import httpx
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential
from shapely.geometry import shape, MultiPolygon
from geoalchemy2.shape import from_shape

from app.database import SessionLocal
from app.models import State, Municipality

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IBGE API endpoints
LOCALIDADES_BASE = "https://servicodados.ibge.gov.br/api/v1/localidades"
MALHAS_BASE = "https://servicodados.ibge.gov.br/api/v3/malhas"

# Brazilian regions mapping
REGIONS = {
    "11": "N", "12": "N", "13": "N", "14": "N", "15": "N", "16": "N", "17": "N",  # Norte
    "21": "NE", "22": "NE", "23": "NE", "24": "NE", "25": "NE", "26": "NE", "27": "NE", "28": "NE", "29": "NE",  # Nordeste
    "31": "SE", "32": "SE", "33": "SE", "35": "SE",  # Sudeste
    "41": "S", "42": "S", "43": "S",  # Sul
    "50": "CO", "51": "CO", "52": "CO", "53": "CO",  # Centro-Oeste
}

# State abbreviations
STATE_ABBREVS = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA",
    "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS",
    "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_json(client: httpx.AsyncClient, url: str) -> dict:
    """Fetch JSON from URL with retry logic."""
    response = await client.get(url, timeout=60.0)
    response.raise_for_status()
    return response.json()


async def fetch_states() -> List[dict]:
    """Fetch all Brazilian states from IBGE API."""
    async with httpx.AsyncClient() as client:
        url = f"{LOCALIDADES_BASE}/estados"
        logger.info(f"Fetching states from {url}")
        return await fetch_json(client, url)


async def fetch_municipalities() -> List[dict]:
    """Fetch all Brazilian municipalities from IBGE API."""
    async with httpx.AsyncClient() as client:
        url = f"{LOCALIDADES_BASE}/municipios"
        logger.info(f"Fetching municipalities from {url}")
        return await fetch_json(client, url)


async def fetch_state_geometry(state_code: str, resolution: int = 2) -> Optional[dict]:
    """
    Fetch GeoJSON geometry for a state.

    Resolution levels:
    - 0: Lowest detail
    - 1: Low detail
    - 2: Medium detail (recommended for web)
    - 3: High detail
    - 4: Highest detail
    """
    async with httpx.AsyncClient() as client:
        url = f"{MALHAS_BASE}/estados/{state_code}?formato=application/vnd.geo+json&resolucao={resolution}"
        logger.info(f"Fetching geometry for state {state_code}")
        try:
            return await fetch_json(client, url)
        except Exception as e:
            logger.error(f"Failed to fetch geometry for state {state_code}: {e}")
            return None


async def fetch_municipality_geometries(state_code: str, resolution: int = 2) -> Optional[dict]:
    """
    Fetch GeoJSON geometries for all municipalities in a state.
    """
    async with httpx.AsyncClient() as client:
        url = f"{MALHAS_BASE}/estados/{state_code}/municipios?formato=application/vnd.geo+json&resolucao={resolution}"
        logger.info(f"Fetching municipality geometries for state {state_code}")
        try:
            return await fetch_json(client, url)
        except Exception as e:
            logger.error(f"Failed to fetch municipality geometries for state {state_code}: {e}")
            return None


def insert_states(db: Session, states_data: List[dict], geometries: Dict[str, dict]):
    """Insert states into database."""
    logger.info(f"Inserting {len(states_data)} states")

    for state_data in states_data:
        state_code = str(state_data["id"])
        geometry = geometries.get(state_code)

        state = State(
            ibge_code=state_code,
            name=state_data["nome"],
            abbreviation=state_data["sigla"],
            region=REGIONS.get(state_code, ""),
        )

        if geometry and "features" in geometry and len(geometry["features"]) > 0:
            geom_dict = geometry["features"][0]["geometry"]
            try:
                shapely_geom = shape(geom_dict)
                # Convert Polygon to MultiPolygon if needed
                if shapely_geom.geom_type == "Polygon":
                    shapely_geom = MultiPolygon([shapely_geom])
                state.geometry = from_shape(shapely_geom, srid=4326)
            except Exception as e:
                logger.warning(f"Failed to parse geometry for state {state_code}: {e}")

        db.merge(state)

    db.commit()
    logger.info("States inserted successfully")


def insert_municipalities(
    db: Session,
    municipalities_data: List[dict],
    geometries: Dict[str, dict],
):
    """Insert municipalities into database."""
    logger.info(f"Processing {len(municipalities_data)} municipalities")

    # Get state ID mapping
    states = db.query(State).all()
    state_id_map = {s.ibge_code: s.id for s in states}

    # Process in batches
    batch_size = 500
    processed = 0

    for i in range(0, len(municipalities_data), batch_size):
        batch = municipalities_data[i : i + batch_size]

        for mun_data in batch:
            mun_code = str(mun_data["id"])
            state_code = mun_code[:2]

            if state_code not in state_id_map:
                logger.warning(f"Unknown state for municipality {mun_code}")
                continue

            municipality = Municipality(
                ibge_code=mun_code,
                name=mun_data["nome"],
                state_id=state_id_map[state_code],
            )

            # Find geometry in state's geometries
            state_geoms = geometries.get(state_code, {})
            if state_geoms and "features" in state_geoms:
                for feature in state_geoms["features"]:
                    if str(feature.get("properties", {}).get("codarea")) == mun_code:
                        geom_dict = feature["geometry"]
                        try:
                            shapely_geom = shape(geom_dict)
                            # Convert Polygon to MultiPolygon if needed
                            if shapely_geom.geom_type == "Polygon":
                                shapely_geom = MultiPolygon([shapely_geom])
                            municipality.geometry = from_shape(shapely_geom, srid=4326)
                        except Exception as e:
                            logger.warning(f"Failed to parse geometry for municipality {mun_code}: {e}")
                        break

            db.merge(municipality)
            processed += 1

        db.commit()
        logger.info(f"Processed {processed}/{len(municipalities_data)} municipalities")

    logger.info("Municipalities inserted successfully")


async def ingest_ibge_data():
    """
    Main function to ingest all IBGE data.

    Run this to populate the database with:
    - 27 states with geometries
    - ~5,570 municipalities with geometries
    """
    logger.info("Starting IBGE data ingestion")

    # Fetch states
    states_data = await fetch_states()
    logger.info(f"Fetched {len(states_data)} states")

    # Fetch municipalities
    municipalities_data = await fetch_municipalities()
    logger.info(f"Fetched {len(municipalities_data)} municipalities")

    # Fetch geometries for each state
    state_geometries = {}
    municipality_geometries = {}

    for state in states_data:
        state_code = str(state["id"])

        # Fetch state geometry
        state_geom = await fetch_state_geometry(state_code)
        if state_geom:
            state_geometries[state_code] = state_geom

        # Fetch municipality geometries for this state
        mun_geoms = await fetch_municipality_geometries(state_code)
        if mun_geoms:
            municipality_geometries[state_code] = mun_geoms

        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)

    # Insert into database
    db = SessionLocal()
    try:
        insert_states(db, states_data, state_geometries)
        insert_municipalities(db, municipalities_data, municipality_geometries)
    finally:
        db.close()

    logger.info("IBGE data ingestion completed")


def run_ingestion():
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_ibge_data())


if __name__ == "__main__":
    run_ingestion()
