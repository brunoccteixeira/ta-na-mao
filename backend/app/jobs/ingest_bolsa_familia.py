"""Bolsa Família data ingestion from Portal da Transparência.

Downloads official Bolsa Família beneficiary data and saves as a separate
social program (BOLSA_FAMILIA). No longer used as CadÚnico proxy.

Source: https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia
"""

import asyncio
import csv
import io
import os
import zipfile
from datetime import date
from decimal import Decimal
from typing import Dict, Optional
import logging

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Municipality, Program, BeneficiaryData
from app.models.program import ProgramCode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Portal da Transparência URLs
BASE_URL = "https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia"
DIRECT_URL = "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/novo-bolsa-familia"

# SIAFI to IBGE mapping file
SIAFI_MAPPING_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "siafi_ibge_mapping.csv"
)


def load_siafi_mapping() -> Dict[str, str]:
    """Load SIAFI to IBGE code mapping.

    File format (no header): SIAFI;CNPJ;MUNICIPALITY;UF;IBGE
    """
    mapping = {}

    if not os.path.exists(SIAFI_MAPPING_FILE):
        logger.warning(f"SIAFI mapping file not found: {SIAFI_MAPPING_FILE}")
        return mapping

    with open(SIAFI_MAPPING_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 5:
                siafi = row[0].strip()  # First column is SIAFI
                ibge = row[4].strip()   # Fifth column is IBGE
                if siafi and ibge:
                    mapping[siafi] = ibge

    logger.info(f"Loaded {len(mapping)} SIAFI to IBGE mappings")
    return mapping


async def download_bolsa_familia(year: int, month: int) -> Optional[bytes]:
    """Download Bolsa Família ZIP file for a specific month."""
    period = f"{year}{month:02d}"
    url = f"{DIRECT_URL}/{period}_NovoBolsaFamilia.zip"

    logger.info(f"Downloading Bolsa Família data for {period}...")
    logger.info(f"URL: {url}")

    async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
        try:
            response = await client.get(url)

            if response.status_code == 200:
                logger.info(f"Downloaded {len(response.content):,} bytes")
                return response.content
            else:
                logger.error(f"Download failed: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Download error: {e}")
            return None


def parse_bolsa_familia_csv(zip_content: bytes, siafi_mapping: Dict[str, str]) -> Dict[str, Dict]:
    """Parse Bolsa Família CSV from ZIP and aggregate by municipality.

    Returns dict mapping IBGE code to aggregated data.
    OPTIMIZED: Uses csv.reader and streaming for better performance.
    """
    # Pre-allocate results dict
    results = {}

    zip_buffer = io.BytesIO(zip_content)

    with zipfile.ZipFile(zip_buffer) as zf:
        csv_files = [f for f in zf.namelist() if f.endswith('.csv')]

        if not csv_files:
            logger.error("No CSV file found in ZIP")
            return {}

        csv_name = csv_files[0]
        logger.info(f"Processing {csv_name}...")

        with zf.open(csv_name) as csv_file:
            # Wrap in TextIOWrapper for streaming
            import codecs
            text_stream = codecs.getreader('latin-1')(csv_file)

            # Read header to find column indices
            reader = csv.reader(text_stream, delimiter=';')
            header = next(reader)

            # Find column indices
            siafi_idx = None
            valor_idx = None
            nome_idx = None
            uf_idx = None

            for i, col in enumerate(header):
                col_upper = col.upper()
                if 'SIAFI' in col_upper:
                    siafi_idx = i
                elif 'VALOR PARCELA' in col_upper:
                    valor_idx = i
                elif 'NOME MUNIC' in col_upper:
                    nome_idx = i
                elif col_upper == 'UF':
                    uf_idx = i

            if siafi_idx is None:
                logger.error(f"SIAFI column not found. Headers: {header[:10]}")
                return {}

            logger.info(f"Column indices: SIAFI={siafi_idx}, VALOR={valor_idx}, NOME={nome_idx}, UF={uf_idx}")

            row_count = 0
            for row in reader:
                row_count += 1

                if len(row) <= siafi_idx:
                    continue

                # Get SIAFI code and convert to IBGE
                siafi_code = row[siafi_idx].strip()
                ibge_code = siafi_mapping.get(siafi_code)

                if not ibge_code:
                    # Try to use the code directly if it looks like IBGE
                    if len(siafi_code) == 7:
                        ibge_code = siafi_code
                    elif len(siafi_code) == 6:
                        ibge_code = siafi_code + "0"
                    else:
                        continue

                # Parse value
                valor = 0.0
                if valor_idx is not None and len(row) > valor_idx:
                    valor_str = row[valor_idx].replace('.', '').replace(',', '.')
                    try:
                        valor = float(valor_str)
                    except:
                        valor = 0.0

                # Aggregate by municipality
                if ibge_code not in results:
                    results[ibge_code] = {
                        "families": 0,
                        "beneficiaries": 0,
                        "total_value": 0.0,
                        "municipality_name": row[nome_idx] if nome_idx and len(row) > nome_idx else "",
                        "uf": row[uf_idx] if uf_idx and len(row) > uf_idx else ""
                    }

                results[ibge_code]["families"] += 1
                results[ibge_code]["beneficiaries"] += 1
                results[ibge_code]["total_value"] += valor

                if row_count % 5000000 == 0:
                    logger.info(f"Processed {row_count:,} rows... ({len(results)} municipalities)")

            logger.info(f"Total rows processed: {row_count:,}")
            logger.info(f"Unique municipalities: {len(results)}")

    return results


def save_as_cadunico(db: Session, data: Dict[str, Dict], reference_date: date):
    """Save Bolsa Família data as CadÚnico proxy data.

    Since all BF beneficiaries are in CadÚnico, this provides a baseline
    for the most vulnerable population.
    """
    # Build municipality lookup
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}
    for mun in list(municipalities.values()):
        if len(mun.ibge_code) == 7:
            municipalities[mun.ibge_code[:6]] = mun

    records_created = 0
    records_updated = 0
    not_found = 0

    total_families = 0
    total_persons = 0

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

        families = mun_data["families"]
        # Estimate persons: average family size ~3.3 persons
        persons = int(families * 3.3)

        total_families += families
        total_persons += persons

        # Estimate income brackets based on BF eligibility
        # BF: 100% in poverty or extreme poverty
        # ~60% extreme poverty, ~40% poverty
        int(families * 0.60)
        int(families * 0.40)

        # Get or create Bolsa Família program
        program = db.query(Program).filter(Program.code == ProgramCode.BOLSA_FAMILIA).first()
        if not program:
            logger.error("Bolsa Família program not found in database")
            continue

        # Check if exists
        existing = db.query(BeneficiaryData).filter(
            BeneficiaryData.municipality_id == municipality.id,
            BeneficiaryData.program_id == program.id,
            BeneficiaryData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_beneficiaries = families  # BF = families, not persons
            existing.total_families = families
            existing.total_value_brl = Decimal(str(mun_data["total_value"]))
            # Coverage is calculated as families / total families in CadÚnico
            # This will be updated later when we have real CadÚnico data
            records_updated += 1
        else:
            beneficiary_data = BeneficiaryData(
                municipality_id=municipality.id,
                program_id=program.id,
                reference_date=reference_date,
                total_beneficiaries=families,  # BF = families, not persons
                total_families=families,
                total_value_brl=Decimal(str(mun_data["total_value"])),
                coverage_rate=0.0,  # Will be calculated later with real CadÚnico data
            )
            db.add(beneficiary_data)
            records_created += 1

    db.commit()

    logger.info(f"Created {records_created}, updated {records_updated} records")
    logger.info(f"Not found: {not_found} municipalities")
    logger.info(f"Total families: {total_families:,}")
    logger.info(f"Total persons (estimated): {total_persons:,}")

    return total_families, total_persons


async def ingest_bolsa_familia(year: int, month: int):
    """Main function to ingest Bolsa Família data."""
    logger.info("=" * 60)
    logger.info(f"INGESTING BOLSA FAMÍLIA DATA - {year}/{month:02d}")
    logger.info("=" * 60)

    # Load SIAFI mapping
    siafi_mapping = load_siafi_mapping()

    # Download data
    zip_content = await download_bolsa_familia(year, month)

    if not zip_content:
        logger.error("Failed to download data")
        return

    # Parse CSV
    logger.info("Parsing CSV data...")
    data = parse_bolsa_familia_csv(zip_content, siafi_mapping)

    if not data:
        logger.error("No data parsed")
        return

    # Save to database
    reference_date = date(year, month, 1)

    db = SessionLocal()
    try:
        total_families, total_persons = save_as_cadunico(db, data, reference_date)

        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE!")
        logger.info(f"Bolsa Família families: {total_families:,}")
        logger.info(f"Estimated persons: {total_persons:,}")
        logger.info("=" * 60)

    finally:
        db.close()


def run_ingestion():
    """Synchronous wrapper with default parameters."""
    # Default to most recent available month
    from datetime import datetime
    now = datetime.now()
    # Data usually has 1-2 month lag
    year = now.year
    month = now.month - 2
    if month <= 0:
        month += 12
        year -= 1

    asyncio.run(ingest_bolsa_familia(year, month))


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        asyncio.run(ingest_bolsa_familia(year, month))
    elif len(sys.argv) == 2 and sys.argv[1] == "--help":
        print("Usage: python -m app.jobs.ingest_bolsa_familia [YEAR] [MONTH]")
        print("")
        print("Examples:")
        print("  python -m app.jobs.ingest_bolsa_familia 2024 10")
        print("  python -m app.jobs.ingest_bolsa_familia 2024 11")
        print("")
        print("Data source: Portal da Transparência - Novo Bolsa Família")
        print("URL: https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia")
    else:
        run_ingestion()
