"""Dignidade Menstrual (Menstrual Dignity) data ingestion.

Downloads Dignidade Menstrual data from OpenDataSUS.
This program distributes free sanitary pads through Farmácia Popular.

Sources:
- OpenDataSUS: https://opendatasus.saude.gov.br/dataset/mgdi-programa-farmacia-popular-do-brasil
- Ministério da Saúde: https://www.gov.br/saude/pt-br/campanhas-da-saude/2024/dignidade-menstrual
- Law 14.214/2021, Decree 11.432/2023, Portaria GM/MS 3.076/2024
"""

import asyncio
import csv
import io
import zipfile
from datetime import date
from decimal import Decimal
from typing import Dict, Optional, Tuple
from collections import defaultdict
import logging

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models import Municipality, Program, BeneficiaryData, CadUnicoData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenDataSUS - absorventes higiênicos
OPENDATASUS_URL = "https://demas-dados-abertos.s3.amazonaws.com/csv/pfpbdm.csv.zip"

# Average value per beneficiary (2 packs/month * R$ 12/pack = R$ 24/month)
AVG_VALUE_PER_BENEFICIARY = 24.0


async def fetch_opendatasus_dignidade(period: Optional[str] = None) -> Tuple[Dict[str, Dict], Optional[str]]:
    """Fetch real Dignidade Menstrual data from OpenDataSUS.

    Args:
        period: Optional period in format YYYYMM. If None, uses most recent.

    Returns:
        Tuple of (data dict, selected period).
    """
    logger.info("Downloading Dignidade Menstrual data from OpenDataSUS...")

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        try:
            response = await client.get(OPENDATASUS_URL)

            if response.status_code != 200:
                logger.error(f"OpenDataSUS download failed: {response.status_code}")
                return {}, None

            logger.info(f"Downloaded {len(response.content):,} bytes from OpenDataSUS")

            # Extract CSV from ZIP
            zip_buffer = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_buffer) as zf:
                csv_name = zf.namelist()[0]
                with zf.open(csv_name) as csv_file:
                    content = csv_file.read().decode('utf-8')

            # Parse CSV
            reader = csv.DictReader(io.StringIO(content))

            # Group by period
            periods_data = defaultdict(lambda: defaultdict(lambda: {
                "beneficiaries": 0,
                "municipality_name": "",
                "uf": ""
            }))

            for row in reader:
                row_period = row.get('co_anomes', '')
                ibge_code = row.get('co_ibge', '').strip()

                if not ibge_code or not row_period:
                    continue

                # Normalize IBGE code to 7 digits
                if len(ibge_code) == 6:
                    ibge_code = ibge_code + "0"

                try:
                    beneficiaries = float(row.get('vl_indicador_calculado_mun', 0) or 0)
                except (ValueError, TypeError):
                    beneficiaries = 0

                periods_data[row_period][ibge_code] = {
                    "beneficiaries": int(beneficiaries),
                    "municipality_name": row.get('no_municipio', ''),
                    "uf": row.get('sg_uf', '')
                }

            # Select period
            if period and period in periods_data:
                selected_period = period
            else:
                selected_period = max(periods_data.keys()) if periods_data else None

            if not selected_period:
                logger.error("No data found in OpenDataSUS response")
                return {}, None

            data = periods_data[selected_period]
            total_beneficiaries = sum(d["beneficiaries"] for d in data.values())

            logger.info(f"Selected period: {selected_period}")
            logger.info(f"Found {len(data):,} municipalities with {total_beneficiaries:,} beneficiaries")

            return dict(data), selected_period

        except Exception as e:
            logger.error(f"Error fetching OpenDataSUS data: {e}")
            import traceback
            traceback.print_exc()
            return {}, None


def save_dignidade_real_data(
    db: Session,
    data: Dict[str, Dict],
    period: str,
    program_id: int
):
    """Save real Dignidade Menstrual data to database."""

    # Parse period to date
    year = int(period[:4])
    month = int(period[4:6])
    reference_date = date(year, month, 1)

    # Build municipality lookup
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}
    for mun in list(municipalities.values()):
        if len(mun.ibge_code) == 7:
            municipalities[mun.ibge_code[:6]] = mun

    records_created = 0
    records_updated = 0
    not_found = 0

    for ibge_code, mun_data in data.items():
        municipality = municipalities.get(ibge_code)
        if not municipality and len(ibge_code) == 7:
            municipality = municipalities.get(ibge_code[:6])
        if not municipality and len(ibge_code) == 6:
            municipality = municipalities.get(ibge_code + "0")

        if not municipality:
            not_found += 1
            continue

        beneficiaries = mun_data["beneficiaries"]
        value = beneficiaries * AVG_VALUE_PER_BENEFICIARY

        # Get CadÚnico for coverage
        cadunico = (
            db.query(CadUnicoData)
            .filter(CadUnicoData.municipality_id == municipality.id)
            .order_by(CadUnicoData.reference_date.desc())
            .first()
        )

        cadunico_families = cadunico.total_families if cadunico else 0
        coverage = beneficiaries / cadunico_families if cadunico_families > 0 else 0

        existing = db.query(BeneficiaryData).filter(
            BeneficiaryData.municipality_id == municipality.id,
            BeneficiaryData.program_id == program_id,
            BeneficiaryData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_beneficiaries = beneficiaries
            existing.total_families = int(beneficiaries * 0.9)
            existing.total_value_brl = Decimal(str(value))
            existing.coverage_rate = Decimal(str(min(coverage, 1.0)))
            existing.data_source = "OPENDATASUS"
            existing.extra_data = {"source": "opendatasus.saude.gov.br", "period": period}
            records_updated += 1
        else:
            beneficiary_data = BeneficiaryData(
                municipality_id=municipality.id,
                program_id=program_id,
                reference_date=reference_date,
                total_beneficiaries=beneficiaries,
                total_families=int(beneficiaries * 0.9),
                total_value_brl=Decimal(str(value)),
                coverage_rate=Decimal(str(min(coverage, 1.0))),
                data_source="OPENDATASUS",
                extra_data={"source": "opendatasus.saude.gov.br", "period": period}
            )
            db.add(beneficiary_data)
            records_created += 1

    db.commit()
    logger.info(f"Created {records_created}, updated {records_updated} records. {not_found} not found.")


async def ingest_dignidade_menstrual(use_real_data: bool = True):
    """Main function to ingest Dignidade Menstrual data.

    Args:
        use_real_data: If True, tries OpenDataSUS first. If False, uses simulated.
    """
    logger.info("Starting Dignidade Menstrual data ingestion")

    db = SessionLocal()
    try:
        # Get or create program
        program = db.query(Program).filter(Program.code == "DIGNIDADE_MENSTRUAL").first()
        if not program:
            program = Program(
                code="DIGNIDADE_MENSTRUAL",
                name="Programa Dignidade Menstrual",
                description="Distribuição gratuita de absorventes higiênicos",
                data_source_url="https://opendatasus.saude.gov.br/dataset/mgdi-programa-farmacia-popular-do-brasil",
                update_frequency="monthly",
                is_active=True,
            )
            db.add(program)
            db.commit()
            db.refresh(program)

        if use_real_data:
            data, period = await fetch_opendatasus_dignidade()

            if data and period:
                total = sum(d["beneficiaries"] for d in data.values())
                logger.info(f"Total: {total:,} beneficiaries in {len(data)} municipalities")
                save_dignidade_real_data(db, data, period, program.id)
                logger.info("Dignidade Menstrual real data ingestion completed!")
                return

            logger.warning("OpenDataSUS failed, falling back to simulated data...")

        # Fallback to simulated
        await ingest_dignidade_simulated()

    finally:
        db.close()


async def ingest_dignidade_simulated():
    """Simulate Dignidade Menstrual data based on CadÚnico demographics.

    Based on public data:
    - Target population: ~24 million women aged 10-49 in CadÚnico
    - Started distribution in January 2024
    - Distributed through Farmácia Popular network
    """
    logger.info("Simulating Dignidade Menstrual data based on CadÚnico demographics")

    db = SessionLocal()
    try:
        # Get or create Dignidade Menstrual program
        program = db.query(Program).filter(Program.code == "DIGNIDADE_MENSTRUAL").first()
        if not program:
            program = Program(
                code="DIGNIDADE_MENSTRUAL",
                name="Programa Dignidade Menstrual",
                description="Distribuição gratuita de absorventes higiênicos",
                data_source_url="https://www.gov.br/saude/pt-br/campanhas-da-saude/2024/dignidade-menstrual",
                update_frequency="monthly",
                is_active=True,
            )
            db.add(program)
            db.commit()
            db.refresh(program)

        # Dignidade Menstrual statistics (from public data):
        # - Target: ~24M women aged 10-49 in vulnerable situation
        # - Estimated reach in 2024: ~8-10M (program ramping up)
        # - Value: ~R$ 12/package (2 packages/month = R$ 24)
        ESTIMATED_BENEFICIARIES = 8_000_000
        MONTHLY_VALUE = 24.00  # Average per beneficiary

        # Get municipalities with CadÚnico data
        from app.models import CadUnicoData

        municipalities = db.query(Municipality).all()

        # Get total eligible population (women 10-49 in CadÚnico)
        # Use age groups from CadÚnico: 6-14, 15-17, 18-64
        # We'll estimate ~40% of CadÚnico persons are eligible women
        db.query(func.sum(CadUnicoData.total_persons)).scalar() or 1

        reference_date = date(2024, 11, 1)
        records_created = 0

        # Get total population
        total_pop = db.query(func.sum(Municipality.population)).scalar() or 1

        for mun in municipalities:
            pop = mun.population or 0
            if pop == 0:
                continue

            # Get CadÚnico data for this municipality
            cadunico = (
                db.query(CadUnicoData)
                .filter(CadUnicoData.municipality_id == mun.id)
                .first()
            )

            cadunico_families = cadunico.total_families if cadunico else 0

            # Estimate eligible women based on population
            # ~20% of population are women aged 10-49 in vulnerable situation
            eligible_women = int(pop * 0.20 * 0.15)  # 15% of women 10-49 are in CadÚnico
            if eligible_women == 0:
                eligible_women = max(1, int(cadunico_families * 0.3) if cadunico_families else 1)

            # Calculate beneficiaries based on population distribution
            pop_ratio = pop / total_pop if total_pop > 0 else 0
            beneficiaries = int(ESTIMATED_BENEFICIARIES * pop_ratio)

            if beneficiaries == 0:
                beneficiaries = 1

            value = beneficiaries * MONTHLY_VALUE

            # Coverage rate relative to eligible women
            coverage = beneficiaries / eligible_women if eligible_women > 0 else 0

            # Check if exists
            existing = db.query(BeneficiaryData).filter(
                BeneficiaryData.municipality_id == mun.id,
                BeneficiaryData.program_id == program.id,
                BeneficiaryData.reference_date == reference_date
            ).first()

            if existing:
                existing.total_beneficiaries = beneficiaries
                existing.total_families = int(beneficiaries * 0.9)
                existing.total_value_brl = Decimal(str(value))
                existing.coverage_rate = Decimal(str(min(coverage, 1.0)))
            else:
                data = BeneficiaryData(
                    municipality_id=mun.id,
                    program_id=program.id,
                    reference_date=reference_date,
                    total_beneficiaries=beneficiaries,
                    total_families=int(beneficiaries * 0.9),
                    total_value_brl=Decimal(str(value)),
                    coverage_rate=Decimal(str(min(coverage, 1.0))),
                    data_source="SIMULATED",
                    extra_data={
                        "method": "cadunico_demographics",
                        "eligible_women": eligible_women,
                    }
                )
                db.add(data)

            records_created += 1

        db.commit()
        logger.info(f"Created {records_created} Dignidade Menstrual records")

    finally:
        db.close()

    logger.info("Dignidade Menstrual data ingestion completed")


def run_ingestion():
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_dignidade_menstrual())


if __name__ == "__main__":
    run_ingestion()
