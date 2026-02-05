"""CRAS data ingestion from Censo SUAS.

Downloads and processes CRAS (Centro de Referencia de Assistencia Social)
data from the Censo SUAS (Sistema Unico de Assistencia Social).

Data source: https://aplicacoes.mds.gov.br/sagi/censosuas

Pipeline:
1. Download Censo SUAS data (Excel/CSV)
2. Parse addresses and contact information
3. Geocode addresses using free services (Nominatim) with Google fallback
4. Upsert to cras_locations table
"""

import asyncio
import csv
import io
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from app.database import SessionLocal
from app.models import Municipality
from app.models.cras_location import CrasLocation
from app.services.geocoding_service import geocode_address

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Censo SUAS data URLs
# The MDS publishes Censo SUAS data in various formats
# Check: https://aplicacoes.mds.gov.br/sagi/censosuas
CENSO_SUAS_BASE_URL = "https://aplicacoes.mds.gov.br/sagi"

# Mapa Social - Alternative source with CRAS locations
MAPA_SOCIAL_URL = "https://aplicacoes.mds.gov.br/sagi/miv/miv.php"

# Fallback: IBGE service listing (may have CRAS)
IBGE_SERVICODADOS_URL = "https://servicodados.ibge.gov.br"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
async def fetch_censo_suas_data(ano: int = 2023) -> Optional[List[Dict[str, Any]]]:
    """Fetch CRAS data from Censo SUAS.

    The Censo SUAS publishes data about social assistance units including CRAS.
    Data is typically available in Excel format.

    Args:
        ano: Reference year (default: most recent available)

    Returns:
        List of CRAS records or None if fetch fails
    """
    logger.info(f"Fetching Censo SUAS data for year {ano}...")

    # NOTE: The actual URL varies by year and MDS infrastructure changes
    # This is a placeholder that should be updated based on current MDS portal
    # Typical format: censosuas/{ano}/EquipamentosCRAS.csv

    # Try the Mapa Social API which provides CRAS locations
    try:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            # Check if there's a direct CSV/JSON endpoint
            # MDS often provides data downloads on specific pages
            response = await client.get(
                f"{CENSO_SUAS_BASE_URL}/censosuas/censo{ano}",
                params={"formato": "json"}
            )

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"Fetched {len(data)} CRAS records from Censo SUAS")
                    return data

    except Exception as e:
        logger.warning(f"Direct Censo SUAS fetch failed: {e}")

    # Fallback: Try to download from dados.gov.br
    try:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            # dados.gov.br often mirrors MDS data
            response = await client.get(
                "https://dados.gov.br/dados/conjuntos-dados/censo-suas",
                headers={"Accept": "application/json"}
            )

            if response.status_code == 200:
                # Parse the catalog to find CRAS data
                data = response.json()
                resources = data.get("resources", [])
                for resource in resources:
                    if "cras" in resource.get("name", "").lower():
                        csv_url = resource.get("url")
                        if csv_url:
                            csv_response = await client.get(csv_url)
                            if csv_response.status_code == 200:
                                return _parse_cras_csv(csv_response.text)

    except Exception as e:
        logger.warning(f"dados.gov.br fetch failed: {e}")

    logger.warning("Could not fetch Censo SUAS data from any source")
    return None


def _parse_cras_csv(csv_content: str) -> List[Dict[str, Any]]:
    """Parse CRAS CSV data into structured records."""
    records = []

    # Try to detect delimiter
    delimiter = ";" if ";" in csv_content[:1000] else ","

    reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)

    for row in reader:
        # Map common column names to our schema
        record = {
            "nome": _get_field(row, ["nome", "nome_cras", "nm_cras", "equipamento"]),
            "ibge_code": _get_field(row, ["ibge", "cod_ibge", "co_ibge", "municipio_ibge"]),
            "endereco": _get_field(row, ["endereco", "logradouro", "ds_endereco"]),
            "bairro": _get_field(row, ["bairro", "ds_bairro"]),
            "cep": _get_field(row, ["cep", "co_cep"]),
            "telefone": _get_field(row, ["telefone", "nu_telefone", "fone"]),
            "email": _get_field(row, ["email", "ds_email"]),
            "cidade": _get_field(row, ["municipio", "nome_municipio", "cidade"]),
            "uf": _get_field(row, ["uf", "sigla_uf", "estado"]),
        }

        # Only add if we have minimum required fields
        if record["nome"] and (record["ibge_code"] or (record["cidade"] and record["uf"])):
            records.append(record)

    logger.info(f"Parsed {len(records)} CRAS records from CSV")
    return records


def _get_field(row: dict, possible_keys: List[str]) -> Optional[str]:
    """Get field value trying multiple possible column names."""
    for key in possible_keys:
        # Try exact match (case-insensitive)
        for actual_key in row.keys():
            if actual_key.lower() == key.lower():
                value = row[actual_key]
                if value and str(value).strip():
                    return str(value).strip()
    return None


def _normalize_ibge_code(code: Optional[str]) -> Optional[str]:
    """Normalize IBGE code to 7 digits."""
    if not code:
        return None

    code = re.sub(r"\D", "", str(code))

    if len(code) == 6:
        return code + "0"
    elif len(code) == 7:
        return code

    return None


def _normalize_cep(cep: Optional[str]) -> Optional[str]:
    """Normalize CEP to 8 digits without formatting."""
    if not cep:
        return None

    cep = re.sub(r"\D", "", str(cep))
    return cep if len(cep) == 8 else None


async def geocode_cras_batch(
    cras_records: List[Dict[str, Any]],
    batch_size: int = 10,
    delay_seconds: float = 1.0,
) -> List[Dict[str, Any]]:
    """Geocode CRAS records in batches with rate limiting.

    Args:
        cras_records: List of CRAS records to geocode
        batch_size: Number of concurrent geocoding requests
        delay_seconds: Delay between batches to respect rate limits

    Returns:
        List of CRAS records with added latitude/longitude/geocode_source
    """
    results = []
    total = len(cras_records)

    for i in range(0, total, batch_size):
        batch = cras_records[i:i + batch_size]

        tasks = []
        for record in batch:
            tasks.append(geocode_single_cras(record))

        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)

        geocoded = sum(1 for r in batch_results if r.get("latitude"))
        logger.info(f"Geocoded batch {i//batch_size + 1}: {geocoded}/{len(batch)} success")

        if i + batch_size < total:
            await asyncio.sleep(delay_seconds)

    total_geocoded = sum(1 for r in results if r.get("latitude"))
    logger.info(f"Total geocoded: {total_geocoded}/{total} ({100*total_geocoded/total:.1f}%)")

    return results


async def geocode_single_cras(record: Dict[str, Any]) -> Dict[str, Any]:
    """Geocode a single CRAS record."""
    endereco = record.get("endereco", "")
    cidade = record.get("cidade", "")
    uf = record.get("uf", "")
    cep = record.get("cep")

    if not (endereco or cidade):
        return record

    lat, lon, source = await geocode_address(
        endereco=endereco,
        cidade=cidade,
        uf=uf,
        cep=cep,
    )

    return {
        **record,
        "latitude": lat,
        "longitude": lon,
        "geocode_source": source,
    }


def save_cras_to_db(
    db: Session,
    cras_records: List[Dict[str, Any]],
    source: str = "censo_suas",
) -> Dict[str, int]:
    """Save CRAS records to database using upsert logic.

    Args:
        db: Database session
        cras_records: List of CRAS records with geocoding data
        source: Data source identifier

    Returns:
        Dict with counts: created, updated, skipped
    """
    # Build municipality lookup by IBGE code
    municipalities = {m.ibge_code: m for m in db.query(Municipality).all()}

    stats = {"created": 0, "updated": 0, "skipped": 0}

    for record in cras_records:
        ibge_code = _normalize_ibge_code(record.get("ibge_code"))

        if not ibge_code:
            stats["skipped"] += 1
            continue

        if ibge_code not in municipalities:
            # Try 6-digit variation
            ibge_6 = ibge_code[:6] if len(ibge_code) == 7 else None
            if ibge_6 and any(m.startswith(ibge_6) for m in municipalities.keys()):
                # Find the matching 7-digit code
                ibge_code = next(m for m in municipalities.keys() if m.startswith(ibge_6))
            else:
                stats["skipped"] += 1
                continue

        nome = record.get("nome", "").strip()
        if not nome:
            stats["skipped"] += 1
            continue

        # Check if CRAS already exists (by name and ibge_code)
        existing = db.query(CrasLocation).filter(
            CrasLocation.ibge_code == ibge_code,
            CrasLocation.nome == nome,
        ).first()

        cras_data = {
            "ibge_code": ibge_code,
            "nome": nome,
            "endereco": record.get("endereco"),
            "bairro": record.get("bairro"),
            "cep": _normalize_cep(record.get("cep")),
            "telefone": record.get("telefone"),
            "email": record.get("email"),
            "latitude": record.get("latitude"),
            "longitude": record.get("longitude"),
            "servicos": ["CadUnico", "BolsaFamilia", "BPC", "TarifaSocial"],  # Default services
            "horario_funcionamento": "Seg-Sex 8h-17h",  # Default hours
            "source": source,
            "geocode_source": record.get("geocode_source"),
        }

        if existing:
            # Update existing record
            for key, value in cras_data.items():
                if value is not None:
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            stats["updated"] += 1
        else:
            # Create new record
            new_cras = CrasLocation(**cras_data)
            db.add(new_cras)
            stats["created"] += 1

    db.commit()
    logger.info(f"Database save complete: {stats}")
    return stats


async def ingest_cras_data(dry_run: bool = False) -> Dict[str, Any]:
    """Main function to ingest CRAS data.

    Args:
        dry_run: If True, fetch and process data but don't save to DB

    Returns:
        Dict with ingestion statistics
    """
    logger.info("Starting CRAS data ingestion")
    start_time = datetime.now()

    result = {
        "started_at": start_time.isoformat(),
        "source": "censo_suas",
        "records_fetched": 0,
        "records_geocoded": 0,
        "records_saved": 0,
        "errors": [],
    }

    # Step 1: Fetch data
    cras_records = await fetch_censo_suas_data()

    if not cras_records:
        # Try loading from local fallback file
        cras_records = _load_fallback_data()

    if not cras_records:
        result["errors"].append("Failed to fetch CRAS data from any source")
        result["finished_at"] = datetime.now().isoformat()
        return result

    result["records_fetched"] = len(cras_records)
    logger.info(f"Fetched {len(cras_records)} CRAS records")

    # Step 2: Geocode addresses
    geocoded_records = await geocode_cras_batch(cras_records)
    result["records_geocoded"] = sum(1 for r in geocoded_records if r.get("latitude"))

    if dry_run:
        logger.info("Dry run - skipping database save")
        result["dry_run"] = True
        result["finished_at"] = datetime.now().isoformat()
        return result

    # Step 3: Save to database
    db = SessionLocal()
    try:
        save_stats = save_cras_to_db(db, geocoded_records)
        result["records_saved"] = save_stats["created"] + save_stats["updated"]
        result["created"] = save_stats["created"]
        result["updated"] = save_stats["updated"]
        result["skipped"] = save_stats["skipped"]
    except Exception as e:
        logger.error(f"Database save error: {e}")
        result["errors"].append(str(e))
    finally:
        db.close()

    result["finished_at"] = datetime.now().isoformat()
    elapsed = datetime.now() - start_time
    result["elapsed_seconds"] = elapsed.total_seconds()

    logger.info(
        f"CRAS ingestion complete: {result['records_fetched']} fetched, "
        f"{result['records_geocoded']} geocoded, {result.get('records_saved', 0)} saved "
        f"in {elapsed.total_seconds():.1f}s"
    )

    return result


def _load_fallback_data() -> Optional[List[Dict[str, Any]]]:
    """Load CRAS data from local fallback file if available."""
    import json
    import os

    fallback_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "data", "cras_exemplo.json"
    )

    try:
        with open(fallback_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            cras_list = data.get("cras", [])
            if cras_list:
                logger.info(f"Loaded {len(cras_list)} CRAS from fallback file")
                return cras_list
    except FileNotFoundError:
        logger.debug("No fallback CRAS file found")
    except Exception as e:
        logger.warning(f"Error loading fallback CRAS data: {e}")

    return None


def run_ingestion(dry_run: bool = False):
    """Synchronous wrapper for running the ingestion."""
    return asyncio.run(ingest_cras_data(dry_run=dry_run))


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv
    result = run_ingestion(dry_run=dry_run)

    print("\n=== CRAS Ingestion Results ===")
    print(f"Records fetched: {result['records_fetched']}")
    print(f"Records geocoded: {result['records_geocoded']}")
    print(f"Records saved: {result.get('records_saved', 'N/A (dry run)')}")
    if result.get("errors"):
        print(f"Errors: {result['errors']}")
