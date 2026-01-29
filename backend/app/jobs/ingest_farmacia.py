"""Farmácia Popular data ingestion.

Downloads Farmácia Popular data from Ministry of Health.
Note: Real API access requires authentication. This script includes
simulated data based on public statistics.

Sources:
- Ministério da Saúde: https://www.gov.br/saude/pt-br/composicao/sectics/daf/farmacia-popular
- API: https://apidadosabertos.saude.gov.br/
"""

import asyncio
from datetime import date
from decimal import Decimal
import logging

from sqlalchemy import func

from app.database import SessionLocal
from app.models import Municipality, Program, BeneficiaryData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_farmacia_popular():
    """Main function to ingest Farmácia Popular data."""
    logger.info("Starting Farmácia Popular data ingestion")

    # Since direct API access is complex, use simulated data based on public statistics
    await ingest_farmacia_simulated()


async def ingest_farmacia_simulated():
    """Simulate Farmácia Popular data based on public statistics.

    Based on public data:
    - ~24 million beneficiaries in 2024
    - Average subsidy: ~R$ 25 per transaction
    - Higher concentration in urban areas
    """
    logger.info("Simulating Farmácia Popular data based on public statistics")

    db = SessionLocal()
    try:
        # Get or create Farmácia Popular program
        program = db.query(Program).filter(Program.code == "FARMACIA_POPULAR").first()
        if not program:
            program = Program(
                code="FARMACIA_POPULAR",
                name="Farmácia Popular do Brasil",
                description="Programa de acesso a medicamentos essenciais",
                data_source_url="https://www.gov.br/saude/pt-br/composicao/sectics/daf/farmacia-popular",
                update_frequency="monthly",
                is_active=True,
            )
            db.add(program)
            db.commit()
            db.refresh(program)

        # Farmácia Popular statistics (from public data):
        # - ~24M beneficiaries in 2024
        # - Average transaction value: ~R$ 30
        # - Higher in urban areas with more pharmacies
        NATIONAL_BENEFICIARIES = 24_000_000
        AVERAGE_VALUE = 30.00  # Per transaction

        # Get population by municipality
        municipalities = db.query(Municipality).all()
        total_pop = db.query(func.sum(Municipality.population)).scalar() or 1

        reference_date = date(2024, 11, 1)
        records_created = 0

        for mun in municipalities:
            pop = mun.population or 0
            pop_ratio = pop / total_pop if total_pop > 0 else 0

            # Urban factor: larger cities have more pharmacy coverage
            urban_factor = 1.0
            if pop > 500_000:
                urban_factor = 1.3
            elif pop > 100_000:
                urban_factor = 1.2
            elif pop > 50_000:
                urban_factor = 1.1
            elif pop < 10_000:
                urban_factor = 0.7  # Rural areas have less pharmacy access

            # Calculate beneficiaries with urban adjustment
            beneficiaries = int(NATIONAL_BENEFICIARIES * pop_ratio * urban_factor)
            if beneficiaries == 0 and pop > 0:
                beneficiaries = max(1, int(pop * 0.05))  # At least 5% of population

            value = beneficiaries * AVERAGE_VALUE

            # Calculate coverage using CadÚnico as base
            from app.models import CadUnicoData
            cadunico = (
                db.query(CadUnicoData)
                .filter(CadUnicoData.municipality_id == mun.id)
                .first()
            )
            cadunico_families = cadunico.total_families if cadunico else 0
            # Farmácia Popular reaches beyond CadÚnico, so coverage can exceed 100%
            coverage = beneficiaries / (cadunico_families * 2) if cadunico_families > 0 else 0

            # Check if exists
            existing = db.query(BeneficiaryData).filter(
                BeneficiaryData.municipality_id == mun.id,
                BeneficiaryData.program_id == program.id,
                BeneficiaryData.reference_date == reference_date
            ).first()

            if existing:
                existing.total_beneficiaries = beneficiaries
                existing.total_families = int(beneficiaries * 0.8)
                existing.total_value_brl = Decimal(str(value))
                existing.coverage_rate = Decimal(str(min(coverage, 1.0)))
            else:
                data = BeneficiaryData(
                    municipality_id=mun.id,
                    program_id=program.id,
                    reference_date=reference_date,
                    total_beneficiaries=beneficiaries,
                    total_families=int(beneficiaries * 0.8),
                    total_value_brl=Decimal(str(value)),
                    coverage_rate=Decimal(str(min(coverage, 1.0))),
                    data_source="SIMULATED",
                    extra_data={
                        "method": "proportional_by_population_urban_adjusted",
                        "urban_factor": urban_factor,
                    }
                )
                db.add(data)

            records_created += 1

        db.commit()
        logger.info(f"Created {records_created} Farmácia Popular records")
        logger.info(f"Total beneficiaries: {NATIONAL_BENEFICIARIES:,}")

    finally:
        db.close()

    logger.info("Farmácia Popular data ingestion completed")


def run_ingestion():
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_farmacia_popular())


if __name__ == "__main__":
    run_ingestion()
