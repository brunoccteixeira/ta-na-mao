"""PNAE data ingestion from FNDE OData API.

Downloads official PNAE (Programa Nacional de Alimentacao Escolar) data.
Source: https://www.fnde.gov.br/olinda-ide/servico/PNAE_Recursos_Repassados_Pck_3/versao/v1/odata

PNAE: Programa Nacional de Alimentacao Escolar - provides federal funds
for school meals in public schools. Municipalities must spend at least
30% of PNAE funds purchasing from family farmers (Agricultura Familiar).
"""

import asyncio
from datetime import date
from decimal import Decimal
from typing import Dict, List
import logging
from collections import defaultdict

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Municipality, Program, BeneficiaryData, State
from app.models.program import ProgramCode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FNDE OData API endpoint
ODATA_BASE_URL = "https://www.fnde.gov.br/olinda-ide/servico/PNAE_Recursos_Repassados_Pck_3/versao/v1/odata"


def build_municipality_name_mapping(db: Session) -> Dict[str, Municipality]:
    """Build a mapping from municipality name (normalized) to Municipality object."""
    mapping = {}

    municipalities = (
        db.query(Municipality, State.abbreviation)
        .join(State, Municipality.state_id == State.id)
        .all()
    )

    for mun, uf in municipalities:
        # Create normalized name key (uppercase, no accents, no special chars)
        name_normalized = normalize_name(mun.name)
        key = f"{name_normalized}_{uf}"
        mapping[key] = mun

        # Also map without UF for fallback
        if name_normalized not in mapping:
            mapping[name_normalized] = mun

    logger.info(f"Built name mapping with {len(mapping)} entries")
    return mapping


def normalize_name(name: str) -> str:
    """Normalize municipality name for matching."""
    import unicodedata

    # Remove accents
    normalized = unicodedata.normalize('NFD', name)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')

    # Uppercase and remove special chars
    normalized = normalized.upper()
    normalized = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in normalized)
    normalized = ' '.join(normalized.split())  # Normalize whitespace

    return normalized


async def fetch_pnae_data(year: int, skip: int = 0, top: int = 10000) -> List[Dict]:
    """Fetch PNAE data from FNDE OData API."""
    url = f"{ODATA_BASE_URL}/RecursosRepassados"
    params = {
        "$filter": f"Ano eq '{year}'",
        "$skip": skip,
        "$top": top,
        "$format": "json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return data.get("value", [])
            else:
                logger.error(f"API request failed: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"API error: {e}")
            return []


async def download_pnae_year(year: int) -> List[Dict]:
    """Download all PNAE data for a given year."""
    all_data = []
    skip = 0
    page_size = 10000

    logger.info(f"Downloading PNAE data for {year}...")

    while True:
        logger.info(f"Fetching records {skip} to {skip + page_size}...")
        page_data = await fetch_pnae_data(year, skip=skip, top=page_size)

        if not page_data:
            break

        all_data.extend(page_data)
        logger.info(f"Got {len(page_data)} records. Total: {len(all_data)}")

        if len(page_data) < page_size:
            break

        skip += page_size

        # Small delay to be nice to the API
        await asyncio.sleep(0.5)

    logger.info(f"Downloaded {len(all_data)} total records for {year}")
    return all_data


def parse_value(value_str: str) -> float:
    """Parse Brazilian currency value string to float."""
    if not value_str:
        return 0.0

    # Remove currency symbols and spaces
    value_str = value_str.strip()

    # Handle Brazilian number format (1.234,56 -> 1234.56)
    # First remove thousand separators (dots)
    value_str = value_str.replace('.', '')
    # Then replace decimal comma with dot
    value_str = value_str.replace(',', '.')

    try:
        return float(value_str)
    except ValueError:
        return 0.0


def aggregate_pnae_data(records: List[Dict]) -> Dict[str, Dict]:
    """Aggregate PNAE data by municipality."""
    aggregated = defaultdict(lambda: {
        "total_value": 0.0,
        "record_count": 0,
        "modalidades": set(),
        "esfera": None,
        "uf": None,
    })

    for record in records:
        estado = record.get("Estado", "").strip().upper()
        municipio = record.get("Municipio", "").strip().upper()
        esfera = record.get("Esfera_governo", "").strip()
        modalidade = record.get("Modalidade_ensino", "").strip()
        valor = parse_value(record.get("Vl_total_escolas", "0"))

        # Skip state-level records (we want municipal)
        if esfera.upper() != "MUNICIPAL":
            continue

        # Create unique key
        municipio_normalized = normalize_name(municipio)
        key = f"{municipio_normalized}_{estado}"

        aggregated[key]["total_value"] += valor
        aggregated[key]["record_count"] += 1
        aggregated[key]["modalidades"].add(modalidade)
        aggregated[key]["esfera"] = esfera
        aggregated[key]["uf"] = estado

    logger.info(f"Aggregated data for {len(aggregated)} municipalities")
    return dict(aggregated)


def save_pnae_data(db: Session, data: Dict[str, Dict], reference_date: date, name_mapping: Dict[str, Municipality]):
    """Save PNAE data to database."""
    program = db.query(Program).filter(Program.code == ProgramCode.PNAE).first()
    if not program:
        logger.error("PNAE program not found in database. Run seed_programs first.")
        return 0, 0

    records_created = 0
    records_updated = 0
    not_found = 0
    not_found_names = []

    total_value = 0.0

    for key, mun_data in data.items():
        # Try to find municipality
        municipality = name_mapping.get(key)

        if not municipality:
            # Try without UF
            name_only = key.rsplit('_', 1)[0]
            municipality = name_mapping.get(name_only)

        if not municipality:
            not_found += 1
            if len(not_found_names) < 20:  # Log first 20
                not_found_names.append(key)
            continue

        valor = mun_data["total_value"]
        total_value += valor

        # PNAE is a program that benefits all students, so we estimate based on value
        # Average daily value per student is ~R$ 0.36 to R$ 2.00 depending on modality
        # For a rough estimate, use average of R$ 0.50 x 200 school days = R$ 100/student/year
        estimated_students = int(valor / 100) if valor > 0 else 0

        existing = db.query(BeneficiaryData).filter(
            BeneficiaryData.municipality_id == municipality.id,
            BeneficiaryData.program_id == program.id,
            BeneficiaryData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_beneficiaries = estimated_students
            existing.total_families = estimated_students  # Students, not families
            existing.total_value_brl = Decimal(str(valor))
            records_updated += 1
        else:
            beneficiary_data = BeneficiaryData(
                municipality_id=municipality.id,
                program_id=program.id,
                reference_date=reference_date,
                total_beneficiaries=estimated_students,
                total_families=estimated_students,
                total_value_brl=Decimal(str(valor)),
                coverage_rate=0.0,  # Will be updated by coverage script
            )
            db.add(beneficiary_data)
            records_created += 1

    db.commit()

    logger.info(f"Created {records_created}, updated {records_updated} records")
    logger.info(f"Not found: {not_found} municipalities")
    if not_found_names:
        logger.info(f"Sample not found: {not_found_names[:10]}")
    logger.info(f"Total value: R$ {total_value:,.2f}")

    return records_created + records_updated, total_value


async def ingest_pnae(year: int):
    """Main function to ingest PNAE data for a year."""
    logger.info("=" * 60)
    logger.info(f"INGESTING PNAE DATA - {year}")
    logger.info("=" * 60)

    # Download data
    records = await download_pnae_year(year)

    if not records:
        logger.error("No data downloaded")
        return

    logger.info("Aggregating data by municipality...")
    data = aggregate_pnae_data(records)

    if not data:
        logger.error("No data after aggregation")
        return

    # Reference date is last day of year for annual data
    reference_date = date(year, 12, 31)

    db = SessionLocal()
    try:
        logger.info("Building municipality name mapping...")
        name_mapping = build_municipality_name_mapping(db)

        records_saved, total_value = save_pnae_data(db, data, reference_date, name_mapping)

        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE!")
        logger.info(f"PNAE records saved: {records_saved}")
        logger.info(f"Total value: R$ {total_value:,.2f}")
        logger.info("=" * 60)

    finally:
        db.close()


def run_ingestion():
    """Synchronous wrapper with default parameters."""
    from datetime import datetime
    # Use previous year as data is usually complete
    year = datetime.now().year - 1
    asyncio.run(ingest_pnae(year))


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2:
        if sys.argv[1] == "--help":
            print("Usage: python -m app.jobs.ingest_pnae [YEAR]")
            print("")
            print("Examples:")
            print("  python -m app.jobs.ingest_pnae 2023")
            print("  python -m app.jobs.ingest_pnae 2024")
            print("")
            print("Data source: FNDE OData API - PNAE Recursos Repassados")
            print("URL: https://www.fnde.gov.br/olinda-ide/servico/PNAE_Recursos_Repassados_Pck_3/versao/v1/odata")
            print("")
            print("PNAE provides federal funds for school meals in public schools.")
            print("Municipalities must spend at least 30% buying from family farmers.")
        else:
            year = int(sys.argv[1])
            asyncio.run(ingest_pnae(year))
    else:
        run_ingestion()
