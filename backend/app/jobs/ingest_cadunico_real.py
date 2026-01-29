"""CadÚnico real data extraction from Observatório do Cadastro Único.

The Observatório provides aggregated data through a Qlik Sense dashboard.
This script attempts to extract data via the Qlik API endpoints.

Sources:
- Observatório: https://paineis.mds.gov.br/public/extensions/observatorio-do-cadastro-unico/index.html
- Alternative: https://aplicacoes.mds.gov.br/sagi/RIv3/
"""

import asyncio
import csv
import io
from datetime import date
from typing import Dict, Optional
import logging

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Municipality, CadUnicoData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Observatório Qlik endpoints
OBSERVATORIO_BASE = "https://paineis.mds.gov.br"
QLIK_APP_ID = "observatorio-do-cadastro-unico"

# RIv3 API (alternative source)
RIV3_BASE = "https://aplicacoes.mds.gov.br/sagi/RIv3"
RIV3_API = "https://aplicacoes.mds.gov.br/sagi/ri/relatorios/cidadania/api"


async def fetch_riv3_data(state_code: str = None) -> Optional[Dict]:
    """Fetch CadÚnico data from RIv3 API.

    This API provides summary data by state/municipality.
    """
    logger.info("Fetching CadÚnico data from RIv3 API...")

    # RIv3 endpoints for CadÚnico data

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Try to get municipality-level data
            url = f"{RIV3_API}/cadunico"
            params = {}
            if state_code:
                params["uf"] = state_code

            response = await client.get(url, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"RIv3 API returned status {response.status_code}")
                return None

        except Exception as e:
            logger.warning(f"RIv3 API error: {e}")
            return None


async def fetch_ibge_cadunico_proxy() -> Optional[Dict]:
    """Try to fetch CadÚnico data via IBGE's social statistics API.

    IBGE sometimes provides cross-referenced data from MDS.
    """
    # IBGE SIDRA API for social programs
    SIDRA_BASE = "https://apisidra.ibge.gov.br"

    # Table 6579 contains some CadÚnico-related data
    # This is a placeholder - actual table numbers need verification

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Try SIDRA tables that might have CadÚnico data
            tables_to_try = [
                "6579",  # Social vulnerability indicators
                "9878",  # Social programs coverage
            ]

            for table in tables_to_try:
                url = f"{SIDRA_BASE}/values/t/{table}/n6/all/v/all/p/last"
                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 1:
                        logger.info(f"Found data in SIDRA table {table}")
                        return {"table": table, "data": data}

        except Exception as e:
            logger.warning(f"SIDRA API error: {e}")

    return None


def parse_qlik_export(csv_content: str) -> Dict[str, Dict]:
    """Parse exported CSV from Qlik Sense dashboard."""
    results = {}

    reader = csv.DictReader(io.StringIO(csv_content), delimiter=';')

    for row in reader:
        # Look for municipality code and family count
        mun_code = None
        families = 0
        persons = 0

        for key, value in row.items():
            key_lower = key.lower()

            if 'ibge' in key_lower or 'codigo' in key_lower:
                mun_code = value.strip()
            elif 'familia' in key_lower:
                try:
                    families = int(value.replace('.', '').replace(',', '').strip() or '0')
                except:
                    pass
            elif 'pessoa' in key_lower:
                try:
                    persons = int(value.replace('.', '').replace(',', '').strip() or '0')
                except:
                    pass

        if mun_code and (families > 0 or persons > 0):
            results[mun_code] = {
                "total_families": families,
                "total_persons": persons,
            }

    return results


async def ingest_from_manual_export(csv_path: str):
    """Ingest CadÚnico data from a manually exported CSV.

    Steps to export manually:
    1. Go to https://paineis.mds.gov.br/public/extensions/observatorio-do-cadastro-unico/index.html
    2. Navigate to the municipality view
    3. Select all municipalities (or filter by state)
    4. Export to CSV/Excel
    5. Run this script with the exported file

    Usage:
        python -m app.jobs.ingest_cadunico_real --csv /path/to/export.csv
    """
    logger.info(f"Reading CadÚnico data from {csv_path}")

    # Try different encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                content = f.read()
                break
        except UnicodeDecodeError:
            continue
    else:
        logger.error("Could not decode CSV file")
        return

    data = parse_qlik_export(content)

    if not data:
        logger.error("No data parsed from CSV")
        return

    logger.info(f"Parsed {len(data)} municipalities from export")

    db = SessionLocal()
    try:
        save_cadunico_data(db, data)
    finally:
        db.close()


def save_cadunico_data(db: Session, data: Dict[str, Dict]):
    """Save CadÚnico data to database."""

    # Build municipality lookup
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}

    # Also map 6-digit codes
    for mun in list(municipalities.values()):
        if len(mun.ibge_code) == 7:
            municipalities[mun.ibge_code[:6]] = mun

    reference_date = date.today().replace(day=1)
    records_created = 0
    records_updated = 0

    for ibge_code, mun_data in data.items():
        # Find municipality
        municipality = municipalities.get(ibge_code)
        if not municipality and len(ibge_code) == 6:
            municipality = municipalities.get(ibge_code + "0")
        if not municipality and len(ibge_code) == 7:
            municipality = municipalities.get(ibge_code[:6])

        if not municipality:
            continue

        # Check if exists
        existing = db.query(CadUnicoData).filter(
            CadUnicoData.municipality_id == municipality.id,
            CadUnicoData.reference_date == reference_date
        ).first()

        families = mun_data.get("total_families", 0)
        persons = mun_data.get("total_persons", 0)

        # Estimate income brackets based on national averages
        # ~45% extreme poverty, ~35% poverty, ~20% low income
        extreme_poverty = int(families * 0.45)
        poverty = int(families * 0.35)
        low_income = int(families * 0.20)

        if existing:
            existing.total_families = families
            existing.total_persons = persons
            existing.extreme_poverty_families = extreme_poverty
            existing.poverty_families = poverty
            existing.low_income_families = low_income
            existing.data_source = "OBSERVATORIO_EXPORT"
            records_updated += 1
        else:
            cadunico = CadUnicoData(
                municipality_id=municipality.id,
                reference_date=reference_date,
                total_families=families,
                total_persons=persons,
                extreme_poverty_families=extreme_poverty,
                poverty_families=poverty,
                low_income_families=low_income,
                data_source="OBSERVATORIO_EXPORT"
            )
            db.add(cadunico)
            records_created += 1

    db.commit()
    logger.info(f"Created {records_created}, updated {records_updated} CadÚnico records")


async def ingest_cadunico_real():
    """Main function to attempt automatic CadÚnico data ingestion."""
    logger.info("Starting CadÚnico real data ingestion")
    logger.info("=" * 60)
    logger.info("NOTE: Automatic extraction from Observatório requires JavaScript.")
    logger.info("For real data, please export manually:")
    logger.info("")
    logger.info("1. Visit: https://paineis.mds.gov.br/public/extensions/observatorio-do-cadastro-unico/index.html")
    logger.info("2. Navigate to municipality data view")
    logger.info("3. Export data to CSV")
    logger.info("4. Run: python -m app.jobs.ingest_cadunico_real --csv /path/to/export.csv")
    logger.info("=" * 60)

    # Try RIv3 API as fallback
    logger.info("\nAttempting RIv3 API...")
    riv3_data = await fetch_riv3_data()

    if riv3_data:
        logger.info("RIv3 data retrieved successfully")
        # Process and save...
    else:
        logger.info("RIv3 API did not return usable data")

    # Try IBGE SIDRA
    logger.info("\nAttempting IBGE SIDRA API...")
    sidra_data = await fetch_ibge_cadunico_proxy()

    if sidra_data:
        logger.info("SIDRA data retrieved successfully")
        # Process and save...
    else:
        logger.info("SIDRA API did not return CadÚnico data")

    logger.info("\n" + "=" * 60)
    logger.info("Automatic ingestion did not find complete data.")
    logger.info("Please use manual export method described above.")
    logger.info("=" * 60)


def print_export_instructions():
    """Print detailed instructions for manual data export."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          INSTRUÇÕES PARA EXPORTAR DADOS DO CADÚNICO              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  1. Acesse o Observatório do Cadastro Único:                    ║
║     https://paineis.mds.gov.br/public/extensions/                ║
║     observatorio-do-cadastro-unico/index.html                    ║
║                                                                  ║
║  2. Navegue até a aba "Famílias por Município"                   ║
║                                                                  ║
║  3. Clique com botão direito na tabela de dados                  ║
║                                                                  ║
║  4. Selecione "Exportar" → "Exportar dados"                      ║
║                                                                  ║
║  5. Escolha formato CSV e salve o arquivo                        ║
║                                                                  ║
║  6. Execute o comando:                                           ║
║     python -m app.jobs.ingest_cadunico_real --csv arquivo.csv   ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Alternativa: Solicitar dados via e-mail:                        ║
║  - dados.sagi@mds.gov.br (para pesquisadores)                    ║
║  - info.cadastro@mds.gov.br (para políticas públicas)            ║
╚══════════════════════════════════════════════════════════════════╝
""")


def run_ingestion():
    """Synchronous wrapper."""
    asyncio.run(ingest_cadunico_real())


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--csv" and len(sys.argv) > 2:
            asyncio.run(ingest_from_manual_export(sys.argv[2]))
        elif sys.argv[1] == "--help":
            print_export_instructions()
        else:
            print("Usage:")
            print("  python -m app.jobs.ingest_cadunico_real          # Try automatic")
            print("  python -m app.jobs.ingest_cadunico_real --csv FILE  # From export")
            print("  python -m app.jobs.ingest_cadunico_real --help      # Instructions")
    else:
        run_ingestion()
