"""Seguro Defeso data ingestion from Portal da Transparência.

Downloads official Seguro Defeso beneficiary data.
Source: https://portaldatransparencia.gov.br/download-de-dados/seguro-defeso

Seguro Defeso: Benefício de um salário mínimo para pescadores artesanais
durante o período de defeso (reprodução das espécies). O período varia
conforme a espécie e região.
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

# Portal da Transparência URL
DIRECT_URL = "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/seguro-defeso"

# SIAFI to IBGE mapping file
SIAFI_MAPPING_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "siafi_ibge_mapping.csv"
)


def load_siafi_mapping() -> Dict[str, str]:
    """Load SIAFI to IBGE code mapping."""
    mapping = {}

    if not os.path.exists(SIAFI_MAPPING_FILE):
        logger.warning(f"SIAFI mapping file not found: {SIAFI_MAPPING_FILE}")
        return mapping

    with open(SIAFI_MAPPING_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 5:
                siafi = row[0].strip()
                ibge = row[4].strip()
                if siafi and ibge:
                    mapping[siafi] = ibge

    logger.info(f"Loaded {len(mapping)} SIAFI to IBGE mappings")
    return mapping


async def download_seguro_defeso(year: int, month: int) -> Optional[bytes]:
    """Download Seguro Defeso ZIP file for a specific month."""
    period = f"{year}{month:02d}"
    url = f"{DIRECT_URL}/{period}_SeguroDefeso.zip"

    logger.info(f"Downloading Seguro Defeso data for {period}...")
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


def parse_seguro_defeso_csv(zip_content: bytes, siafi_mapping: Dict[str, str]) -> Dict[str, Dict]:
    """Parse Seguro Defeso CSV from ZIP and aggregate by municipality."""
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
            import codecs
            text_stream = codecs.getreader('latin-1')(csv_file)

            reader = csv.reader(text_stream, delimiter=';')
            header = next(reader)

            # Find column indices
            siafi_idx = None
            valor_idx = None
            nome_idx = None
            uf_idx = None

            for i, col in enumerate(header):
                col_upper = col.upper()
                if 'SIAFI' in col_upper or 'CÓDIGO MUNICÍPIO' in col_upper or 'COD_MUNICIPIO' in col_upper:
                    siafi_idx = i
                elif 'VALOR' in col_upper and ('PARCELA' in col_upper or 'BENEFICIO' in col_upper):
                    valor_idx = i
                elif 'NOME' in col_upper and 'MUNIC' in col_upper:
                    nome_idx = i
                elif col_upper == 'UF':
                    uf_idx = i

            if siafi_idx is None:
                # Try alternative: look for any column with municipality code
                for i, col in enumerate(header):
                    if 'MUNICIPIO' in col.upper() and 'CODIGO' in col.upper():
                        siafi_idx = i
                        break

            if siafi_idx is None:
                logger.error(f"Municipality code column not found. Headers: {header}")
                return {}

            logger.info(f"Column indices: SIAFI={siafi_idx}, VALOR={valor_idx}")

            row_count = 0
            for row in reader:
                row_count += 1

                if len(row) <= siafi_idx:
                    continue

                siafi_code = row[siafi_idx].strip()
                ibge_code = siafi_mapping.get(siafi_code)

                if not ibge_code:
                    if len(siafi_code) == 7:
                        ibge_code = siafi_code
                    elif len(siafi_code) == 6:
                        ibge_code = siafi_code + "0"
                    else:
                        continue

                valor = 0.0
                if valor_idx is not None and len(row) > valor_idx:
                    valor_str = row[valor_idx].replace('.', '').replace(',', '.')
                    try:
                        valor = float(valor_str)
                    except:
                        valor = 0.0

                if ibge_code not in results:
                    results[ibge_code] = {
                        "beneficiaries": 0,
                        "total_value": 0.0,
                        "municipality_name": row[nome_idx] if nome_idx and len(row) > nome_idx else "",
                        "uf": row[uf_idx] if uf_idx and len(row) > uf_idx else ""
                    }

                results[ibge_code]["beneficiaries"] += 1
                results[ibge_code]["total_value"] += valor

                if row_count % 500000 == 0:
                    logger.info(f"Processed {row_count:,} rows...")

            logger.info(f"Total rows processed: {row_count:,}")
            logger.info(f"Unique municipalities: {len(results)}")

    return results


def save_seguro_defeso_data(db: Session, data: Dict[str, Dict], reference_date: date):
    """Save Seguro Defeso data to database."""
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}
    for mun in list(municipalities.values()):
        if len(mun.ibge_code) == 7:
            municipalities[mun.ibge_code[:6]] = mun

    program = db.query(Program).filter(Program.code == ProgramCode.SEGURO_DEFESO).first()
    if not program:
        logger.error("Seguro Defeso program not found in database. Run seed_programs first.")
        return 0, 0

    records_created = 0
    records_updated = 0
    not_found = 0

    total_beneficiaries = 0
    total_value = 0.0

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
        total_beneficiaries += beneficiaries
        total_value += mun_data["total_value"]

        existing = db.query(BeneficiaryData).filter(
            BeneficiaryData.municipality_id == municipality.id,
            BeneficiaryData.program_id == program.id,
            BeneficiaryData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_beneficiaries = beneficiaries
            existing.total_families = beneficiaries  # Individual benefit
            existing.total_value_brl = Decimal(str(mun_data["total_value"]))
            records_updated += 1
        else:
            beneficiary_data = BeneficiaryData(
                municipality_id=municipality.id,
                program_id=program.id,
                reference_date=reference_date,
                total_beneficiaries=beneficiaries,
                total_families=beneficiaries,  # Individual benefit
                total_value_brl=Decimal(str(mun_data["total_value"])),
                coverage_rate=0.0,
            )
            db.add(beneficiary_data)
            records_created += 1

    db.commit()

    logger.info(f"Created {records_created}, updated {records_updated} records")
    logger.info(f"Not found: {not_found} municipalities")
    logger.info(f"Total beneficiaries: {total_beneficiaries:,}")
    logger.info(f"Total value: R$ {total_value:,.2f}")

    return total_beneficiaries, total_value


async def ingest_seguro_defeso(year: int, month: int):
    """Main function to ingest Seguro Defeso data."""
    logger.info("=" * 60)
    logger.info(f"INGESTING SEGURO DEFESO DATA - {year}/{month:02d}")
    logger.info("=" * 60)

    siafi_mapping = load_siafi_mapping()

    zip_content = await download_seguro_defeso(year, month)

    if not zip_content:
        logger.error("Failed to download data")
        return

    logger.info("Parsing CSV data...")
    data = parse_seguro_defeso_csv(zip_content, siafi_mapping)

    if not data:
        logger.error("No data parsed")
        return

    reference_date = date(year, month, 1)

    db = SessionLocal()
    try:
        total_beneficiaries, total_value = save_seguro_defeso_data(db, data, reference_date)

        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE!")
        logger.info(f"Seguro Defeso beneficiaries: {total_beneficiaries:,}")
        logger.info(f"Total value: R$ {total_value:,.2f}")
        logger.info("=" * 60)

    finally:
        db.close()


def run_ingestion():
    """Synchronous wrapper with default parameters."""
    from datetime import datetime
    now = datetime.now()
    year = now.year
    month = now.month - 2
    if month <= 0:
        month += 12
        year -= 1

    asyncio.run(ingest_seguro_defeso(year, month))


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        asyncio.run(ingest_seguro_defeso(year, month))
    elif len(sys.argv) == 2 and sys.argv[1] == "--help":
        print("Usage: python -m app.jobs.ingest_seguro_defeso [YEAR] [MONTH]")
        print("")
        print("Examples:")
        print("  python -m app.jobs.ingest_seguro_defeso 2024 10")
        print("")
        print("Data source: Portal da Transparência - Seguro Defeso")
        print("URL: https://portaldatransparencia.gov.br/download-de-dados/seguro-defeso")
        print("")
        print("Note: Seguro Defeso is paid during fishing closed seasons (defeso)")
        print("which vary by species and region. Data may be sparse in some months.")
    else:
        run_ingestion()
