"""BPC/LOAS real data ingestion from Portal da Transparência CSV downloads.

Downloads BPC data directly from the Portal da Transparência CSV files.
No API token required - uses public download links.

Source: https://portaldatransparencia.gov.br/download-de-dados/bpc
"""

import asyncio
import zipfile
import csv
import io
from pathlib import Path
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

# Portal da Transparência download URLs
# Format: https://portaldatransparencia.gov.br/download-de-dados/bpc/{YYYYMM}
BASE_DOWNLOAD_URL = "https://portaldatransparencia.gov.br/download-de-dados/bpc"

# SIAFI to IBGE mapping
SIAFI_MAPPING_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/abb968cb-3710-4f85-89cf-875c91b9c7f6/resource/eebb3bc6-9eea-4496-8bcf-304f33155282/download/tabmun.csv"
SIAFI_MAPPING_FILE = Path(__file__).parent.parent.parent / "data" / "siafi_ibge_mapping.csv"


async def load_siafi_mapping() -> Dict[str, str]:
    """Load SIAFI to IBGE code mapping."""
    mapping = {}

    # Try to load from local file first
    if SIAFI_MAPPING_FILE.exists():
        logger.info(f"Loading SIAFI mapping from {SIAFI_MAPPING_FILE}")
        with open(SIAFI_MAPPING_FILE, 'r', encoding='latin-1') as f:
            for line in f:
                parts = line.strip().split(';')
                if len(parts) >= 5:
                    siafi = parts[0].strip().zfill(4)  # Pad to 4 digits
                    ibge = parts[4].strip()
                    if siafi and ibge:
                        mapping[siafi] = ibge
        logger.info(f"Loaded {len(mapping)} SIAFI-IBGE mappings from file")
        return mapping

    # Download if not available locally
    logger.info("Downloading SIAFI-IBGE mapping from Tesouro Transparente...")
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        try:
            response = await client.get(SIAFI_MAPPING_URL)
            if response.status_code == 200:
                # Save locally for future use
                SIAFI_MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(SIAFI_MAPPING_FILE, 'wb') as f:
                    f.write(response.content)

                # Parse
                content = response.content.decode('latin-1')
                for line in content.split('\n'):
                    parts = line.strip().split(';')
                    if len(parts) >= 5:
                        siafi = parts[0].strip().zfill(4)
                        ibge = parts[4].strip()
                        if siafi and ibge:
                            mapping[siafi] = ibge

                logger.info(f"Downloaded and cached {len(mapping)} SIAFI-IBGE mappings")
        except Exception as e:
            logger.error(f"Failed to download SIAFI mapping: {e}")

    return mapping


async def download_bpc_csv(year: int, month: int) -> Optional[bytes]:
    """Download BPC CSV file from Portal da Transparência."""
    year_month = f"{year}{month:02d}"
    url = f"{BASE_DOWNLOAD_URL}/{year_month}"

    logger.info(f"Downloading BPC data from {url}")

    async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
        try:
            response = await client.get(url)

            if response.status_code == 200:
                logger.info(f"Downloaded {len(response.content)} bytes")
                return response.content
            else:
                logger.error(f"Download failed with status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Download error: {e}")
            return None


def parse_bpc_csv(zip_content: bytes, siafi_mapping: Dict[str, str]) -> Dict[str, Dict]:
    """Parse BPC CSV from zip file and aggregate by municipality.

    Uses SIAFI to IBGE mapping since BPC data uses SIAFI codes.
    """
    results = defaultdict(lambda: {
        "total_beneficiaries": 0,
        "total_value": 0.0,
        "count": 0
    })

    try:
        # The download is a ZIP file containing CSV
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
            csv_files = [f for f in zf.namelist() if f.endswith('.csv')]

            if not csv_files:
                logger.error("No CSV file found in ZIP")
                return {}

            csv_filename = csv_files[0]
            logger.info(f"Processing {csv_filename}")

            with zf.open(csv_filename) as csv_file:
                # BPC files use latin-1 encoding
                content = csv_file.read().decode('latin-1')

                reader = csv.DictReader(io.StringIO(content), delimiter=';')

                row_count = 0
                siafi_not_found = set()

                for row in reader:
                    row_count += 1

                    # Get SIAFI code
                    siafi_code = row.get('CÓDIGO MUNICÍPIO SIAFI', '').strip()

                    if not siafi_code:
                        continue

                    # Pad SIAFI code to 4 digits for lookup
                    siafi_padded = siafi_code.zfill(4)

                    # Convert SIAFI to IBGE
                    ibge_code = siafi_mapping.get(siafi_padded)

                    if not ibge_code:
                        siafi_not_found.add(siafi_code)
                        continue

                    # Get value
                    value_str = row.get('VALOR PARCELA', '0')
                    try:
                        value = float(value_str.replace(',', '.').replace('"', '').strip() or '0')
                    except:
                        value = 0.0

                    results[ibge_code]["total_beneficiaries"] += 1
                    results[ibge_code]["total_value"] += value
                    results[ibge_code]["count"] += 1

                logger.info(f"Processed {row_count:,} rows, found {len(results)} municipalities")
                if siafi_not_found:
                    logger.warning(f"{len(siafi_not_found)} SIAFI codes not found in mapping")

    except zipfile.BadZipFile:
        logger.error("Invalid ZIP file")
        return {}
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        import traceback
        traceback.print_exc()
        return {}

    return dict(results)


def save_bpc_data(db: Session, data: Dict[str, Dict], reference_date: date, program_id: int):
    """Save real BPC data to database."""

    # Build municipality lookup
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}

    # Also try 6-digit codes (convert to list to avoid modifying dict during iteration)
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

        if not municipality:
            not_found += 1
            continue

        # Get CadÚnico families for coverage calculation
        cadunico = (
            db.query(CadUnicoData)
            .filter(CadUnicoData.municipality_id == municipality.id)
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
            BeneficiaryData.municipality_id == municipality.id,
            BeneficiaryData.program_id == program_id,
            BeneficiaryData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_beneficiaries = mun_data["total_beneficiaries"]
            existing.total_families = int(mun_data["total_beneficiaries"] * 0.95)
            existing.total_value_brl = Decimal(str(mun_data["total_value"]))
            existing.coverage_rate = Decimal(str(min(coverage, 1.0)))
            existing.data_source = "PORTAL_TRANSPARENCIA_CSV"
            records_updated += 1
        else:
            beneficiary_data = BeneficiaryData(
                municipality_id=municipality.id,
                program_id=program_id,
                reference_date=reference_date,
                total_beneficiaries=mun_data["total_beneficiaries"],
                total_families=int(mun_data["total_beneficiaries"] * 0.95),
                total_value_brl=Decimal(str(mun_data["total_value"])),
                coverage_rate=Decimal(str(min(coverage, 1.0))),
                data_source="PORTAL_TRANSPARENCIA_CSV",
                extra_data={"source": "BPC/LOAS", "records_in_csv": mun_data["count"]}
            )
            db.add(beneficiary_data)
            records_created += 1

    db.commit()
    logger.info(f"Created {records_created}, updated {records_updated} records. {not_found} municipalities not found.")


async def ingest_bpc_real(year: Optional[int] = None, month: Optional[int] = None):
    """Main function to ingest real BPC data from CSV downloads."""
    logger.info("Starting BPC/LOAS real data ingestion from Portal da Transparência")

    # Default to previous month
    if year is None or month is None:
        today = date.today()
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1

    # Load SIAFI to IBGE mapping
    siafi_mapping = await load_siafi_mapping()
    if not siafi_mapping:
        logger.error("Failed to load SIAFI-IBGE mapping. Cannot proceed.")
        return

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

        # Download CSV
        zip_content = await download_bpc_csv(year, month)

        if not zip_content:
            logger.error("Failed to download BPC data. Check if the file exists for this period.")
            logger.info("Try accessing manually: https://portaldatransparencia.gov.br/download-de-dados/bpc")
            return

        # Parse CSV with SIAFI mapping
        data = parse_bpc_csv(zip_content, siafi_mapping)

        if not data:
            logger.error("No data parsed from CSV")
            return

        logger.info(f"Parsed BPC data for {len(data)} municipalities")

        # Calculate totals
        total_beneficiaries = sum(d["total_beneficiaries"] for d in data.values())
        total_value = sum(d["total_value"] for d in data.values())
        logger.info(f"Total: {total_beneficiaries:,} beneficiaries, R$ {total_value:,.2f}")

        # Save to database
        reference_date = date(year, month, 1)
        save_bpc_data(db, data, reference_date, program.id)

        logger.info("BPC/LOAS real data ingestion completed!")

    finally:
        db.close()


def run_ingestion(year: Optional[int] = None, month: Optional[int] = None):
    """Synchronous wrapper for running the ingestion."""
    asyncio.run(ingest_bpc_real(year, month))


if __name__ == "__main__":
    import sys

    # Allow passing year and month as arguments
    year = None
    month = None

    if len(sys.argv) >= 3:
        year = int(sys.argv[1])
        month = int(sys.argv[2])

    run_ingestion(year, month)
