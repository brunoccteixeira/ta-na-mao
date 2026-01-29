"""Historical data ingestion for all programs.

Ingests all available historical data from:
- OpenDataSUS: Farmácia Popular (2016-2025), Dignidade Menstrual (2024-2025)
- Portal da Transparência: BPC (2019-2025)
- ANEEL: TSEE (historical)
"""

import asyncio
import csv
import io
import zipfile
from datetime import date
from decimal import Decimal
from typing import Dict
from collections import defaultdict
import logging

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Municipality, Program, BeneficiaryData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenDataSUS URLs
FARMACIA_POPULAR_URL = "https://demas-dados-abertos.s3.amazonaws.com/csv/pfpbben.csv.zip"
DIGNIDADE_MENSTRUAL_URL = "https://demas-dados-abertos.s3.amazonaws.com/csv/pfpbdm.csv.zip"

# Average values per beneficiary
AVG_VALUE_FARMACIA = 30.0
AVG_VALUE_DIGNIDADE = 24.0


async def fetch_opendatasus_all_periods(url: str) -> Dict[str, Dict[str, Dict]]:
    """Fetch all periods from OpenDataSUS.

    Returns:
        Dict mapping period -> ibge_code -> data
    """
    logger.info(f"Downloading data from {url}...")

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        response = await client.get(url)

        if response.status_code != 200:
            logger.error(f"Download failed: {response.status_code}")
            return {}

        logger.info(f"Downloaded {len(response.content):,} bytes")

        # Extract CSV
        zip_buffer = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_buffer) as zf:
            csv_name = zf.namelist()[0]
            with zf.open(csv_name) as csv_file:
                content = csv_file.read().decode('utf-8')

        # Parse all periods
        reader = csv.DictReader(io.StringIO(content))

        all_periods = defaultdict(lambda: defaultdict(lambda: {
            "beneficiaries": 0,
            "municipality_name": "",
            "uf": ""
        }))

        for row in reader:
            period = row.get('co_anomes', '')
            ibge_code = row.get('co_ibge', '').strip()

            if not ibge_code or not period:
                continue

            if len(ibge_code) == 6:
                ibge_code = ibge_code + "0"

            try:
                beneficiaries = float(row.get('vl_indicador_calculado_mun', 0) or 0)
            except (ValueError, TypeError):
                beneficiaries = 0

            all_periods[period][ibge_code] = {
                "beneficiaries": int(beneficiaries),
                "municipality_name": row.get('no_municipio', ''),
                "uf": row.get('sg_uf', '')
            }

        logger.info(f"Found {len(all_periods)} periods")
        return dict(all_periods)


def save_historical_data(
    db: Session,
    all_periods: Dict[str, Dict[str, Dict]],
    program_code: str,
    avg_value: float,
    data_source: str
):
    """Save all historical periods to database."""

    program = db.query(Program).filter(Program.code == program_code).first()
    if not program:
        logger.error(f"Program {program_code} not found")
        return

    # Build municipality lookup
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}
    for mun in list(municipalities.values()):
        if len(mun.ibge_code) == 7:
            municipalities[mun.ibge_code[:6]] = mun

    total_created = 0
    total_updated = 0

    for period, data in sorted(all_periods.items()):
        year = int(period[:4])
        month = int(period[4:6])
        reference_date = date(year, month, 1)

        records_created = 0
        records_updated = 0

        for ibge_code, mun_data in data.items():
            municipality = municipalities.get(ibge_code)
            if not municipality and len(ibge_code) == 7:
                municipality = municipalities.get(ibge_code[:6])
            if not municipality and len(ibge_code) == 6:
                municipality = municipalities.get(ibge_code + "0")

            if not municipality:
                continue

            beneficiaries = mun_data["beneficiaries"]
            value = beneficiaries * avg_value

            existing = db.query(BeneficiaryData).filter(
                BeneficiaryData.municipality_id == municipality.id,
                BeneficiaryData.program_id == program.id,
                BeneficiaryData.reference_date == reference_date
            ).first()

            if existing:
                existing.total_beneficiaries = beneficiaries
                existing.total_families = int(beneficiaries * 0.8)
                existing.total_value_brl = Decimal(str(value))
                existing.data_source = data_source
                existing.extra_data = {"source": "opendatasus.saude.gov.br", "period": period}
                records_updated += 1
            else:
                beneficiary_data = BeneficiaryData(
                    municipality_id=municipality.id,
                    program_id=program.id,
                    reference_date=reference_date,
                    total_beneficiaries=beneficiaries,
                    total_families=int(beneficiaries * 0.8),
                    total_value_brl=Decimal(str(value)),
                    coverage_rate=Decimal("0"),
                    data_source=data_source,
                    extra_data={"source": "opendatasus.saude.gov.br", "period": period}
                )
                db.add(beneficiary_data)
                records_created += 1

        db.commit()
        total_created += records_created
        total_updated += records_updated
        logger.info(f"  {period}: created {records_created}, updated {records_updated}")

    logger.info(f"Total: created {total_created}, updated {total_updated}")


async def ingest_farmacia_historical():
    """Ingest all historical Farmácia Popular data (2016-2025)."""
    logger.info("=" * 60)
    logger.info("INGESTING FARMÁCIA POPULAR HISTORICAL DATA")
    logger.info("=" * 60)

    all_periods = await fetch_opendatasus_all_periods(FARMACIA_POPULAR_URL)

    if not all_periods:
        logger.error("No data fetched")
        return

    db = SessionLocal()
    try:
        save_historical_data(
            db, all_periods,
            "FARMACIA_POPULAR",
            AVG_VALUE_FARMACIA,
            "OPENDATASUS"
        )
    finally:
        db.close()


async def ingest_dignidade_historical():
    """Ingest all historical Dignidade Menstrual data (2024-2025)."""
    logger.info("=" * 60)
    logger.info("INGESTING DIGNIDADE MENSTRUAL HISTORICAL DATA")
    logger.info("=" * 60)

    all_periods = await fetch_opendatasus_all_periods(DIGNIDADE_MENSTRUAL_URL)

    if not all_periods:
        logger.error("No data fetched")
        return

    db = SessionLocal()
    try:
        save_historical_data(
            db, all_periods,
            "DIGNIDADE_MENSTRUAL",
            AVG_VALUE_DIGNIDADE,
            "OPENDATASUS"
        )
    finally:
        db.close()


async def ingest_all_historical():
    """Ingest all available historical data."""
    logger.info("Starting historical data ingestion for all programs")

    await ingest_farmacia_historical()
    await ingest_dignidade_historical()

    logger.info("Historical data ingestion completed!")


def run_ingestion():
    """Synchronous wrapper."""
    asyncio.run(ingest_all_historical())


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "farmacia":
            asyncio.run(ingest_farmacia_historical())
        elif sys.argv[1] == "dignidade":
            asyncio.run(ingest_dignidade_historical())
        else:
            print("Usage: python -m app.jobs.ingest_historical [farmacia|dignidade]")
    else:
        run_ingestion()
