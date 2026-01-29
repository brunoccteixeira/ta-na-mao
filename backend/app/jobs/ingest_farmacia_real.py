"""Farmácia Popular real data ingestion.

Downloads beneficiary data from:
1. OpenDataSUS (primary - real beneficiary counts)
2. i3geo.saude.gov.br (GeoJSON via WFS - establishment counts)
3. dados.gov.br (CSV fallback)

Sources:
- OpenDataSUS: https://opendatasus.saude.gov.br/dataset/mgdi-programa-farmacia-popular-do-brasil
- SAGE/MS: http://sage.saude.gov.br/
- i3geo: http://i3geo.saude.gov.br/i3geo/ogc.htm?temaOgc=farmacia_popular_estabelecimento
"""

import asyncio
import csv
import io
from datetime import date
from decimal import Decimal
from typing import Dict, Optional
from collections import defaultdict
import logging

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Municipality, Program, BeneficiaryData, CadUnicoData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenDataSUS - Primary source (real beneficiary data)
OPENDATASUS_URL = "https://demas-dados-abertos.s3.amazonaws.com/csv/pfpbben.csv.zip"

# WFS endpoint for Farmácia Popular establishments (fallback)
WFS_URL = "http://i3geo.saude.gov.br/i3geo/ogc.php"

# Average value per beneficiary (R$ ~30/month based on program data)
AVG_VALUE_PER_BENEFICIARY = 30.0


async def fetch_opendatasus_data(period: Optional[str] = None) -> Dict[str, Dict]:
    """Fetch real Farmácia Popular data from OpenDataSUS.

    Args:
        period: Optional period in format YYYYMM (e.g., '202510').
                If None, uses most recent available.

    Returns:
        Dict mapping IBGE code to beneficiary data.
    """
    import zipfile

    logger.info("Downloading Farmácia Popular data from OpenDataSUS...")

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        try:
            response = await client.get(OPENDATASUS_URL)

            if response.status_code != 200:
                logger.error(f"OpenDataSUS download failed: {response.status_code}")
                return {}

            logger.info(f"Downloaded {len(response.content):,} bytes from OpenDataSUS")

            # Extract CSV from ZIP
            zip_buffer = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_buffer) as zf:
                csv_name = zf.namelist()[0]
                with zf.open(csv_name) as csv_file:
                    content = csv_file.read().decode('utf-8')

            # Parse CSV
            reader = csv.DictReader(io.StringIO(content))

            # Group by period to find the most recent
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
                # Use most recent period
                selected_period = max(periods_data.keys()) if periods_data else None

            if not selected_period:
                logger.error("No data found in OpenDataSUS response")
                return {}

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


async def fetch_wfs_geojson() -> Optional[Dict]:
    """Fetch Farmácia Popular data via WFS service."""
    logger.info("Fetching Farmácia Popular data from i3geo WFS...")

    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typename": "farmacia_popular_estabelecimento",
        "outputFormat": "application/json",
        "srsname": "EPSG:4326"
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.get(WFS_URL, params=params)

            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                logger.info(f"Fetched {len(features)} establishments from WFS")
                return data
            else:
                logger.warning(f"WFS request failed with status {response.status_code}")
                return None

        except Exception as e:
            logger.warning(f"WFS request error: {e}")
            return None


def aggregate_by_municipality(geojson_data: Dict) -> Dict[str, Dict]:
    """Aggregate establishment data by municipality."""
    results = defaultdict(lambda: {
        "count": 0,
        "names": [],
    })

    features = geojson_data.get("features", [])

    for feature in features:
        props = feature.get("properties", {})

        # Get municipality code - check various field names
        mun_code = None
        for field in ["cd_geocodm", "geocodigo", "codmun", "cod_municipio", "ibge"]:
            if field in props and props[field]:
                mun_code = str(props[field]).strip()
                break

        if not mun_code:
            # Try to extract from other fields or coordinates
            continue

        # Normalize to 7 digits
        if len(mun_code) == 6:
            mun_code = mun_code + "0"

        results[mun_code]["count"] += 1

        # Get establishment name if available
        name = props.get("nome", props.get("razao_social", ""))
        if name:
            results[mun_code]["names"].append(name)

    logger.info(f"Aggregated data for {len(results)} municipalities")
    return dict(results)


def estimate_beneficiaries_from_establishments(
    establishment_count: int,
    municipality_population: int
) -> int:
    """Estimate beneficiaries based on number of establishments.

    Based on national statistics:
    - ~31,000 establishments serve ~25M people
    - Average: ~800 beneficiaries per establishment
    - Adjusted by population density
    """
    AVG_BENEFICIARIES_PER_ESTABLISHMENT = 800

    # Base estimate
    estimated = establishment_count * AVG_BENEFICIARIES_PER_ESTABLISHMENT

    # Cap at reasonable percentage of population (max ~15% of population)
    max_beneficiaries = int(municipality_population * 0.15) if municipality_population else estimated

    return min(estimated, max_beneficiaries)


def save_farmacia_data(
    db: Session,
    data: Dict[str, Dict],
    reference_date: date,
    program_id: int
):
    """Save Farmácia Popular data to database."""

    # Build municipality lookup
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}

    # Also try 6-digit codes
    for mun in list(municipalities.values()):
        if len(mun.ibge_code) == 7:
            municipalities[mun.ibge_code[:6]] = mun

    records_created = 0
    records_updated = 0
    not_found = 0

    # Get national average value per beneficiary (R$ ~30/month based on program data)
    AVG_VALUE_PER_BENEFICIARY = 30.0

    for ibge_code, mun_data in data.items():
        # Find municipality
        municipality = municipalities.get(ibge_code)
        if not municipality and len(ibge_code) == 7:
            municipality = municipalities.get(ibge_code[:6])
        if not municipality and len(ibge_code) == 6:
            municipality = municipalities.get(ibge_code + "0")

        if not municipality:
            not_found += 1
            continue

        # Estimate beneficiaries from establishment count
        beneficiaries = estimate_beneficiaries_from_establishments(
            mun_data["count"],
            municipality.population or 0
        )

        value = beneficiaries * AVG_VALUE_PER_BENEFICIARY

        # Get CadÚnico families for coverage calculation
        cadunico = (
            db.query(CadUnicoData)
            .filter(CadUnicoData.municipality_id == municipality.id)
            .order_by(CadUnicoData.reference_date.desc())
            .first()
        )

        cadunico_families = cadunico.total_families if cadunico else 0
        coverage = (
            beneficiaries / cadunico_families
            if cadunico_families > 0 else 0
        )

        # Check if record exists
        existing = db.query(BeneficiaryData).filter(
            BeneficiaryData.municipality_id == municipality.id,
            BeneficiaryData.program_id == program_id,
            BeneficiaryData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_beneficiaries = beneficiaries
            existing.total_families = int(beneficiaries * 0.8)  # Estimate families
            existing.total_value_brl = Decimal(str(value))
            existing.coverage_rate = Decimal(str(min(coverage, 1.0)))
            existing.data_source = "SAGE_WFS"
            existing.extra_data = {
                "establishments": mun_data["count"],
                "source": "i3geo.saude.gov.br"
            }
            records_updated += 1
        else:
            beneficiary_data = BeneficiaryData(
                municipality_id=municipality.id,
                program_id=program_id,
                reference_date=reference_date,
                total_beneficiaries=beneficiaries,
                total_families=int(beneficiaries * 0.8),
                total_value_brl=Decimal(str(value)),
                coverage_rate=Decimal(str(min(coverage, 1.0))),
                data_source="SAGE_WFS",
                extra_data={
                    "establishments": mun_data["count"],
                    "source": "i3geo.saude.gov.br"
                }
            )
            db.add(beneficiary_data)
            records_created += 1

    db.commit()
    logger.info(f"Created {records_created}, updated {records_updated} records. {not_found} municipalities not found.")


def save_opendatasus_data(
    db: Session,
    data: Dict[str, Dict],
    period: str,
    program_id: int
):
    """Save OpenDataSUS Farmácia Popular data to database."""

    # Parse period (YYYYMM) to date
    year = int(period[:4])
    month = int(period[4:6])
    reference_date = date(year, month, 1)

    # Build municipality lookup
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}

    # Also map 6-digit codes
    for mun in list(municipalities.values()):
        if len(mun.ibge_code) == 7:
            municipalities[mun.ibge_code[:6]] = mun

    records_created = 0
    records_updated = 0
    not_found = 0

    for ibge_code, mun_data in data.items():
        # Find municipality
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

        # Get CadÚnico families for coverage calculation
        cadunico = (
            db.query(CadUnicoData)
            .filter(CadUnicoData.municipality_id == municipality.id)
            .order_by(CadUnicoData.reference_date.desc())
            .first()
        )

        cadunico_families = cadunico.total_families if cadunico else 0
        coverage = (
            beneficiaries / cadunico_families
            if cadunico_families > 0 else 0
        )

        # Check if record exists
        existing = db.query(BeneficiaryData).filter(
            BeneficiaryData.municipality_id == municipality.id,
            BeneficiaryData.program_id == program_id,
            BeneficiaryData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_beneficiaries = beneficiaries
            existing.total_families = int(beneficiaries * 0.8)
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
                total_families=int(beneficiaries * 0.8),
                total_value_brl=Decimal(str(value)),
                coverage_rate=Decimal(str(min(coverage, 1.0))),
                data_source="OPENDATASUS",
                extra_data={"source": "opendatasus.saude.gov.br", "period": period}
            )
            db.add(beneficiary_data)
            records_created += 1

    db.commit()
    logger.info(f"Created {records_created}, updated {records_updated} records. {not_found} municipalities not found.")


async def ingest_farmacia_real(period: Optional[str] = None):
    """Main function to ingest real Farmácia Popular data.

    Args:
        period: Optional period in format YYYYMM (e.g., '202510').
                If None, uses most recent available.
    """
    logger.info("Starting Farmácia Popular real data ingestion")

    db = SessionLocal()
    try:
        # Get or create Farmácia Popular program
        program = db.query(Program).filter(Program.code == "FARMACIA_POPULAR").first()
        if not program:
            program = Program(
                code="FARMACIA_POPULAR",
                name="Farmácia Popular do Brasil",
                description="Programa de acesso a medicamentos essenciais",
                data_source_url="https://opendatasus.saude.gov.br/dataset/mgdi-programa-farmacia-popular-do-brasil",
                update_frequency="monthly",
                is_active=True,
            )
            db.add(program)
            db.commit()
            db.refresh(program)

        # Try OpenDataSUS first (primary source with real beneficiary data)
        data, selected_period = await fetch_opendatasus_data(period)

        if data and selected_period:
            total_beneficiaries = sum(d["beneficiaries"] for d in data.values())
            logger.info(f"Total: {total_beneficiaries:,} beneficiaries in {len(data)} municipalities")

            save_opendatasus_data(db, data, selected_period, program.id)
            logger.info("Farmácia Popular real data ingestion completed!")
            return

        # Fallback to WFS (establishment counts)
        logger.warning("OpenDataSUS failed, trying WFS...")
        geojson_data = await fetch_wfs_geojson()

        if geojson_data and geojson_data.get("features"):
            data = aggregate_by_municipality(geojson_data)
            if data:
                total_establishments = sum(d["count"] for d in data.values())
                logger.info(f"Total: {total_establishments:,} establishments in {len(data)} municipalities")
                reference_date = date.today().replace(day=1)
                save_farmacia_data(db, data, reference_date, program.id)
                logger.info("Farmácia Popular data ingestion completed (from WFS)!")
                return

        logger.error("All data sources failed")
        logger.info("Please try again later or download data manually from:")
        logger.info("  https://opendatasus.saude.gov.br/dataset/mgdi-programa-farmacia-popular-do-brasil")

    finally:
        db.close()


async def ingest_from_csv(csv_path: str):
    """Ingest Farmácia Popular data from a downloaded CSV file.

    Usage:
        python -m app.jobs.ingest_farmacia_real --csv /path/to/file.csv
    """
    logger.info(f"Reading Farmácia Popular data from {csv_path}")

    results = defaultdict(lambda: {"count": 0, "names": []})

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Try to detect delimiter
        sample = f.read(1024)
        f.seek(0)

        delimiter = ';' if ';' in sample else ','

        reader = csv.DictReader(f, delimiter=delimiter)

        for row in reader:
            # Find municipality code
            mun_code = None
            for col in reader.fieldnames:
                if 'ibge' in col.lower() or 'geocod' in col.lower() or 'municipio' in col.lower():
                    val = row.get(col, '').strip()
                    if val and val.isdigit() and len(val) >= 6:
                        mun_code = val
                        break

            if mun_code:
                if len(mun_code) == 6:
                    mun_code = mun_code + "0"
                results[mun_code]["count"] += 1

    logger.info(f"Parsed {sum(d['count'] for d in results.values())} establishments from CSV")

    db = SessionLocal()
    try:
        program = db.query(Program).filter(Program.code == "FARMACIA_POPULAR").first()
        if program:
            reference_date = date.today().replace(day=1)
            save_farmacia_data(db, dict(results), reference_date, program.id)
    finally:
        db.close()


def run_ingestion():
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_farmacia_real())


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--csv" and len(sys.argv) > 2:
        asyncio.run(ingest_from_csv(sys.argv[2]))
    else:
        run_ingestion()
