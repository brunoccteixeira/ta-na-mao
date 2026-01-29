"""Update coverage rates based on CadÚnico eligible families.

This script recalculates coverage_rate for all beneficiary_data records
using the CadÚnico total families as the denominator.

Coverage = program_beneficiaries / total_cadunico_families

The script matches CadÚnico data by municipality and reference_date.
If exact date not found, uses the closest available CadÚnico date.
"""

import logging
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import BeneficiaryData, CadUnicoData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_coverage_rates(db: Session):
    """Update coverage rates for all beneficiary data records."""
    logger.info("Updating coverage rates based on CadÚnico data")

    # Build CadÚnico lookup: {municipality_id: {date: total_families}}
    cadunico_data = db.query(CadUnicoData).all()
    cadunico_by_mun = defaultdict(dict)
    for c in cadunico_data:
        cadunico_by_mun[c.municipality_id][c.reference_date] = c.total_families

    logger.info(f"Loaded CadÚnico data for {len(cadunico_by_mun)} municipalities")

    # Get all available CadÚnico dates sorted
    all_dates = sorted(set(c.reference_date for c in cadunico_data))
    logger.info(f"CadÚnico dates available: {all_dates[0]} to {all_dates[-1]}")

    def find_closest_cadunico(mun_id, ref_date):
        """Find CadÚnico data for municipality, matching by date or closest."""
        mun_data = cadunico_by_mun.get(mun_id, {})
        if not mun_data:
            return None

        # Exact match
        if ref_date in mun_data:
            return mun_data[ref_date]

        # Find closest date
        available = sorted(mun_data.keys())
        closest = min(available, key=lambda d: abs((d - ref_date).days))
        return mun_data[closest]

    # Update beneficiary data
    beneficiary_records = db.query(BeneficiaryData).all()
    updated = 0
    no_cadunico = 0

    for record in beneficiary_records:
        eligible = find_closest_cadunico(record.municipality_id, record.reference_date)

        if eligible and eligible > 0:
            # For Bolsa Família, use families; for others use beneficiaries
            numerator = record.total_families or record.total_beneficiaries or 0
            coverage = numerator / eligible
            # Cap at 1.0 (100%)
            coverage = min(coverage, 1.0)
            record.coverage_rate = Decimal(str(round(coverage, 4)))
            updated += 1
        else:
            record.coverage_rate = Decimal("0")
            no_cadunico += 1

    db.commit()
    logger.info(f"Updated coverage for {updated} records")
    logger.info(f"Records without CadÚnico data: {no_cadunico}")


def main():
    """Main function to update coverage rates."""
    logger.info("Starting coverage rate update")

    db = SessionLocal()
    try:
        update_coverage_rates(db)

        # Print summary statistics
        from sqlalchemy import func
        stats = db.query(
            func.count(BeneficiaryData.id),
            func.avg(BeneficiaryData.coverage_rate),
            func.min(BeneficiaryData.coverage_rate),
            func.max(BeneficiaryData.coverage_rate),
        ).first()

        logger.info(f"Total records: {stats[0]}")
        logger.info(f"Avg coverage: {float(stats[1]):.2%}")
        logger.info(f"Min coverage: {float(stats[2]):.2%}")
        logger.info(f"Max coverage: {float(stats[3]):.2%}")

    finally:
        db.close()

    logger.info("Coverage rate update completed")


if __name__ == "__main__":
    main()
