"""BPC/LOAS (Benefício de Prestação Continuada) data ingestion.

Downloads BPC data from Portal da Transparência API.
Requires API token from gov.br (set in PORTAL_TRANSPARENCIA_TOKEN env var).

Sources:
- Portal da Transparência: https://api.portaldatransparencia.gov.br/
- Endpoint: /api-de-dados/bpc-por-municipio
"""

import asyncio
import os
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
import logging

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func
from tenacity import retry, stop_after_attempt, wait_exponential

from app.database import SessionLocal
from app.models import Municipality, Program, BeneficiaryData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Portal da Transparência API
API_BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
API_TOKEN = os.getenv("PORTAL_TRANSPARENCIA_TOKEN", "")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_bpc_by_municipality(
    client: httpx.AsyncClient,
    ibge_code: str,
    year_month: str,
    page: int = 1
) -> List[Dict]:
    """Fetch BPC data for a municipality from Portal da Transparência."""
    url = f"{API_BASE_URL}/bpc-por-municipio"
    params = {
        "mesAno": year_month,
        "codigoIbge": ibge_code,
        "pagina": page,
    }
    headers = {
        "chave-api-dados": API_TOKEN,
        "Accept": "application/json",
    }

    response = await client.get(url, params=params, headers=headers, timeout=30.0)

    if response.status_code == 401:
        logger.error("API authentication failed. Set PORTAL_TRANSPARENCIA_TOKEN env var.")
        return []

    if response.status_code == 404:
        return []

    response.raise_for_status()
    return response.json()


async def fetch_all_municipalities_bpc(year_month: str, db: Session) -> Dict[str, Dict]:
    """Fetch BPC data for all municipalities."""
    municipalities = db.query(Municipality).all()
    logger.info(f"Fetching BPC data for {len(municipalities)} municipalities, month {year_month}")

    results = {}

    async with httpx.AsyncClient() as client:
        # Process in batches to avoid overwhelming the API
        batch_size = 50
        for i in range(0, len(municipalities), batch_size):
            batch = municipalities[i:i + batch_size]

            for mun in batch:
                try:
                    data = await fetch_bpc_by_municipality(
                        client, mun.ibge_code, year_month
                    )

                    if data:
                        # Aggregate data for this municipality
                        total_beneficiaries = 0
                        total_value = 0.0

                        for record in data:
                            total_beneficiaries += record.get("quantidadeBeneficiados", 0)
                            total_value += float(record.get("valor", 0))

                        results[mun.ibge_code] = {
                            "municipality_id": mun.id,
                            "ibge_code": mun.ibge_code,
                            "total_beneficiaries": total_beneficiaries,
                            "total_value_brl": total_value,
                        }

                except Exception as e:
                    logger.warning(f"Error fetching BPC for {mun.ibge_code}: {e}")
                    continue

            logger.info(f"Processed {min(i + batch_size, len(municipalities))}/{len(municipalities)} municipalities")
            await asyncio.sleep(0.5)  # Rate limiting

    return results


def save_bpc_data(db: Session, data: Dict[str, Dict], reference_date: date, program_id: int):
    """Save BPC data to database."""
    records_created = 0

    for ibge_code, mun_data in data.items():
        # Get CadÚnico families for coverage calculation
        from app.models import CadUnicoData

        cadunico = (
            db.query(CadUnicoData)
            .filter(CadUnicoData.municipality_id == mun_data["municipality_id"])
            .order_by(CadUnicoData.reference_date.desc())
            .first()
        )

        cadunico_families = cadunico.total_families if cadunico else 0
        coverage = (
            mun_data["total_beneficiaries"] / cadunico_families
            if cadunico_families > 0 else 0
        )

        # Check if record exists
        existing = db.query(BeneficiaryData).filter(
            BeneficiaryData.municipality_id == mun_data["municipality_id"],
            BeneficiaryData.program_id == program_id,
            BeneficiaryData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_beneficiaries = mun_data["total_beneficiaries"]
            existing.total_families = int(mun_data["total_beneficiaries"] * 0.9)  # Estimate
            existing.total_value_brl = Decimal(str(mun_data["total_value_brl"]))
            existing.coverage_rate = Decimal(str(min(coverage, 1.0)))
            existing.data_source = "PORTAL_TRANSPARENCIA"
        else:
            beneficiary_data = BeneficiaryData(
                municipality_id=mun_data["municipality_id"],
                program_id=program_id,
                reference_date=reference_date,
                total_beneficiaries=mun_data["total_beneficiaries"],
                total_families=int(mun_data["total_beneficiaries"] * 0.9),
                total_value_brl=Decimal(str(mun_data["total_value_brl"])),
                coverage_rate=Decimal(str(min(coverage, 1.0))),
                data_source="PORTAL_TRANSPARENCIA",
                extra_data={"source": "BPC/LOAS"}
            )
            db.add(beneficiary_data)

        records_created += 1

    db.commit()
    logger.info(f"Saved {records_created} BPC records")


async def ingest_bpc_data(year_month: Optional[str] = None):
    """Main function to ingest BPC data."""
    logger.info("Starting BPC/LOAS data ingestion")

    if not API_TOKEN:
        logger.error("PORTAL_TRANSPARENCIA_TOKEN not set. Get token from gov.br")
        logger.info("For now, using simulated data based on CadÚnico distribution")
        await ingest_bpc_simulated()
        return

    # Default to previous month
    if not year_month:
        today = date.today()
        if today.month == 1:
            year_month = f"{today.year - 1}12"
        else:
            year_month = f"{today.year}{today.month - 1:02d}"

    db = SessionLocal()
    try:
        # Get or create BPC program (using PIS_PASEP as placeholder since BPC isn't in enum)
        program = db.query(Program).filter(Program.code == "BPC").first()
        if not program:
            # Create BPC program
            program = Program(
                code="BPC",
                name="Benefício de Prestação Continuada",
                description="BPC/LOAS para idosos e pessoas com deficiência",
                data_source_url="https://portaldatransparencia.gov.br/beneficios/bpc",
                update_frequency="monthly",
                is_active=True,
            )
            db.add(program)
            db.commit()
            db.refresh(program)

        # Fetch data
        data = await fetch_all_municipalities_bpc(year_month, db)
        logger.info(f"Fetched BPC data for {len(data)} municipalities")

        # Parse reference date
        year = int(year_month[:4])
        month = int(year_month[4:])
        ref_date = date(year, month, 1)

        # Save data
        save_bpc_data(db, data, ref_date, program.id)

    finally:
        db.close()

    logger.info("BPC/LOAS data ingestion completed")


async def ingest_bpc_simulated():
    """Simulate BPC data based on CadÚnico distribution when API token is not available."""
    logger.info("Simulating BPC data based on CadÚnico distribution")

    db = SessionLocal()
    try:
        # Get or create BPC program
        program = db.query(Program).filter(Program.code == "BPC").first()
        if not program:
            program = Program(
                code="BPC",
                name="Benefício de Prestação Continuada",
                description="BPC/LOAS para idosos e pessoas com deficiência",
                data_source_url="https://portaldatransparencia.gov.br/beneficios/bpc",
                update_frequency="monthly",
                is_active=True,
            )
            db.add(program)
            db.commit()
            db.refresh(program)

        # BPC national totals (approximate, from public data):
        # ~5.9M beneficiaries total (idosos + PCD)
        # Average benefit: R$ 1,412 (1 minimum wage)
        NATIONAL_BPC_BENEFICIARIES = 5_900_000
        AVERAGE_BENEFIT = 1412.00

        # Get total population
        total_pop = db.query(func.sum(Municipality.population)).scalar() or 1

        municipalities = db.query(Municipality).all()
        reference_date = date(2024, 11, 1)

        records_created = 0
        for mun in municipalities:
            pop = mun.population or 0
            pop_ratio = pop / total_pop if total_pop > 0 else 0

            # Distribute proportionally by population
            beneficiaries = int(NATIONAL_BPC_BENEFICIARIES * pop_ratio)
            if beneficiaries == 0 and pop > 0:
                beneficiaries = 1

            value = beneficiaries * AVERAGE_BENEFIT

            # Calculate coverage
            from app.models import CadUnicoData
            cadunico = (
                db.query(CadUnicoData)
                .filter(CadUnicoData.municipality_id == mun.id)
                .first()
            )
            cadunico_families = cadunico.total_families if cadunico else 0
            coverage = beneficiaries / cadunico_families if cadunico_families > 0 else 0

            # Check if exists
            existing = db.query(BeneficiaryData).filter(
                BeneficiaryData.municipality_id == mun.id,
                BeneficiaryData.program_id == program.id,
                BeneficiaryData.reference_date == reference_date
            ).first()

            if existing:
                existing.total_beneficiaries = beneficiaries
                existing.total_families = int(beneficiaries * 0.95)
                existing.total_value_brl = Decimal(str(value))
                existing.coverage_rate = Decimal(str(min(coverage, 1.0)))
            else:
                data = BeneficiaryData(
                    municipality_id=mun.id,
                    program_id=program.id,
                    reference_date=reference_date,
                    total_beneficiaries=beneficiaries,
                    total_families=int(beneficiaries * 0.95),
                    total_value_brl=Decimal(str(value)),
                    coverage_rate=Decimal(str(min(coverage, 1.0))),
                    data_source="SIMULATED",
                    extra_data={"method": "proportional_by_population"}
                )
                db.add(data)

            records_created += 1

        db.commit()
        logger.info(f"Created {records_created} simulated BPC records")

    finally:
        db.close()


def run_ingestion():
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_bpc_data())


if __name__ == "__main__":
    run_ingestion()
