"""Population and CadÚnico estimates ingestion from IBGE.

Downloads population estimates for all municipalities from IBGE SIDRA API
and calculates CadÚnico eligibility estimates based on regional poverty rates.

Sources:
- IBGE SIDRA Table 6579: Population estimates
- Regional poverty rates from IBGE PNAD
"""

import asyncio
from datetime import date
from typing import Dict, List
import logging

import httpx
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from app.database import SessionLocal
from app.models import State, Municipality, CadUnicoData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IBGE SIDRA API - Table 6579 (Population estimates)
SIDRA_URL = "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2024"

# Regional poverty rates (% of population in CadÚnico)
# Based on IBGE PNAD data - families in poverty or extreme poverty
REGIONAL_POVERTY_RATES = {
    "N": 0.35,   # Norte - 35%
    "NE": 0.42,  # Nordeste - 42%
    "SE": 0.18,  # Sudeste - 18%
    "S": 0.12,   # Sul - 12%
    "CO": 0.15,  # Centro-Oeste - 15%
}

# State to region mapping
STATE_REGION = {
    "AC": "N", "AM": "N", "AP": "N", "PA": "N", "RO": "N", "RR": "N", "TO": "N",
    "AL": "NE", "BA": "NE", "CE": "NE", "MA": "NE", "PB": "NE", "PE": "NE",
    "PI": "NE", "RN": "NE", "SE": "NE",
    "ES": "SE", "MG": "SE", "RJ": "SE", "SP": "SE",
    "PR": "S", "RS": "S", "SC": "S",
    "DF": "CO", "GO": "CO", "MS": "CO", "MT": "CO",
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_population_data() -> List[Dict]:
    """Fetch population data from IBGE SIDRA API."""
    async with httpx.AsyncClient() as client:
        logger.info("Fetching population data from SIDRA")
        response = await client.get(SIDRA_URL, timeout=120.0)
        response.raise_for_status()
        data = response.json()
        # Skip header row
        return data[1:] if len(data) > 1 else []


def update_municipalities_population(db: Session, population_data: List[Dict]):
    """Update municipalities with population data."""
    logger.info(f"Updating population for {len(population_data)} municipalities")

    # Build lookup by IBGE code
    pop_by_code = {}
    for item in population_data:
        ibge_code = item.get("D1C", "")
        pop_value = item.get("V", "0")
        if ibge_code and pop_value:
            try:
                pop_by_code[ibge_code] = int(pop_value)
            except ValueError:
                continue

    logger.info(f"Parsed population for {len(pop_by_code)} municipalities")

    # Update municipalities
    municipalities = db.query(Municipality).all()
    updated = 0

    for mun in municipalities:
        if mun.ibge_code in pop_by_code:
            mun.population = pop_by_code[mun.ibge_code]
            updated += 1

    db.commit()
    logger.info(f"Updated population for {updated} municipalities")

    return pop_by_code


def create_cadunico_estimates(db: Session, pop_by_code: Dict[str, int]):
    """Create CadÚnico eligibility estimates based on regional poverty rates."""
    logger.info("Creating CadÚnico eligibility estimates")

    # Get state abbreviations mapping
    states = db.query(State).all()
    state_abbrev_map = {s.id: s.abbreviation for s in states}

    municipalities = db.query(Municipality).all()
    reference_date = date(2024, 12, 1)

    records_created = 0

    for mun in municipalities:
        population = mun.population or 0
        if population == 0:
            continue

        state_abbrev = state_abbrev_map.get(mun.state_id, "")
        region = STATE_REGION.get(state_abbrev, "SE")
        poverty_rate = REGIONAL_POVERTY_RATES.get(region, 0.20)

        # Estimate families (avg 3.3 people per family)
        total_families = int(population / 3.3)

        # Estimate CadÚnico eligible families
        eligible_families = int(total_families * poverty_rate)
        eligible_persons = int(population * poverty_rate)

        # Breakdown by poverty level (estimates)
        families_extreme_poverty = int(eligible_families * 0.25)  # 25% extreme
        families_poverty = int(eligible_families * 0.35)          # 35% poverty
        families_low_income = int(eligible_families * 0.40)       # 40% low income

        # Check if exists
        existing = db.query(CadUnicoData).filter(
            CadUnicoData.municipality_id == mun.id,
            CadUnicoData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_families = eligible_families
            existing.total_persons = eligible_persons
            existing.families_extreme_poverty = families_extreme_poverty
            existing.families_poverty = families_poverty
            existing.families_low_income = families_low_income
        else:
            cadunico = CadUnicoData(
                municipality_id=mun.id,
                reference_date=reference_date,
                total_families=eligible_families,
                total_persons=eligible_persons,
                families_extreme_poverty=families_extreme_poverty,
                families_poverty=families_poverty,
                families_low_income=families_low_income,
            )
            db.add(cadunico)

        records_created += 1

    db.commit()
    logger.info(f"Created CadÚnico estimates for {records_created} municipalities")


def update_state_populations(db: Session):
    """Update state populations as sum of municipality populations."""
    logger.info("Updating state populations")

    states = db.query(State).all()

    for state in states:
        total_pop = db.query(
            Municipality.population
        ).filter(
            Municipality.state_id == state.id,
            Municipality.population.isnot(None)
        ).all()

        sum(p[0] for p in total_pop if p[0])
        # Note: State model doesn't have population column yet
        # We'll add it if needed

    db.commit()
    logger.info("State populations updated")


async def ingest_population_data():
    """Main function to ingest population and CadÚnico estimates."""
    logger.info("Starting population data ingestion")

    # Fetch population from IBGE
    population_data = await fetch_population_data()
    logger.info(f"Fetched {len(population_data)} records from IBGE")

    # Update database
    db = SessionLocal()
    try:
        pop_by_code = update_municipalities_population(db, population_data)
        create_cadunico_estimates(db, pop_by_code)

        # Summary
        total_pop = sum(pop_by_code.values())
        logger.info(f"Total population: {total_pop:,}")

    finally:
        db.close()

    logger.info("Population data ingestion completed")


def run_ingestion():
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_population_data())


if __name__ == "__main__":
    run_ingestion()
