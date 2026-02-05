"""CRAS data ingestion from MDS/SAGI API.

Downloads and processes CRAS (Centro de Referencia de Assistencia Social)
data from the official MDS/SAGI Equipamentos API.

Data source: http://aplicacoes.mds.gov.br/sagi/servicos/equipamentos
API provides ~8,923 CRAS records with geocoding included.

Pipeline:
1. Fetch CRAS data from SAGI Equipamentos API (JSON format)
2. Map API fields to CrasLocation schema
3. Upsert to cras_locations table (no geocoding needed - API provides coordinates)
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from app.database import SessionLocal
from app.models import Municipality
from app.models.cras_location import CrasLocation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API oficial MDS/SAGI - Equipamentos SUAS
# Retorna ~8,923 CRAS com geocodificação inclusa
# IMPORTANTE: Usar HTTPS - HTTP retorna "Connection reset by peer"
SAGI_EQUIPAMENTOS_URL = "https://aplicacoes.mds.gov.br/sagi/servicos/equipamentos"

# Bounding box do Brasil para validação de coordenadas
BRASIL_LAT_MIN = -33.75  # RS sul
BRASIL_LAT_MAX = 5.27    # RR norte
BRASIL_LON_MIN = -73.99  # AC oeste
BRASIL_LON_MAX = -32.39  # Fernando de Noronha leste


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
async def fetch_sagi_cras_data(batch_size: int = 5000) -> list[dict[str, Any]] | None:
    """Fetch CRAS data from the official MDS/SAGI Equipamentos API.

    The API provides ~8,923 CRAS records with geocoding already included.
    Uses Solr-style query parameters.

    Args:
        batch_size: Number of records per request (API limit is ~10000)

    Returns:
        List of CRAS records or None if fetch fails
    """
    logger.info("Fetching CRAS data from SAGI Equipamentos API...")

    all_records: list[dict[str, Any]] = []
    start = 0

    try:
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            while True:
                params = {
                    "q": "*:*",
                    "fq": "tipo_equipamento:CRAS",
                    "wt": "json",
                    "rows": batch_size,
                    "start": start,
                }

                response = await client.get(SAGI_EQUIPAMENTOS_URL, params=params)

                if response.status_code != 200:
                    logger.error(f"SAGI API returned status {response.status_code}")
                    break

                data = response.json()
                response_data = data.get("response", {})
                docs = response_data.get("docs", [])
                total = response_data.get("numFound", 0)

                if not docs:
                    break

                # Map API fields to our schema
                for doc in docs:
                    record = _map_sagi_to_cras(doc)
                    if record:
                        all_records.append(record)

                logger.info(f"Fetched batch {start}-{start + len(docs)} of {total}")

                start += len(docs)
                if start >= total:
                    break

                # Small delay between batches to be polite
                await asyncio.sleep(0.5)

            if all_records:
                logger.info(f"Total CRAS fetched from SAGI: {len(all_records)}")
                return all_records

    except httpx.TimeoutException:
        logger.warning("SAGI API timeout")
    except httpx.RequestError as e:
        logger.warning(f"SAGI API request error: {e}")
    except json.JSONDecodeError as e:
        logger.warning(f"SAGI API JSON parse error: {e}")
    except Exception as e:
        logger.warning(f"SAGI API fetch failed: {e}")

    return None


def _map_sagi_to_cras(doc: dict[str, Any]) -> dict[str, Any] | None:
    """Map SAGI API document to CrasLocation schema.

    API fields:
        - id_equipamento: unique ID
        - ibge: IBGE code (7 digits)
        - nome: CRAS name
        - endereco: street address
        - numero: street number
        - bairro: neighborhood
        - cep: postal code
        - cidade: city name
        - uf: state code
        - telefone: phone number
        - georef_location: "lat,lon" string
        - data_atualizacao: last update date
    """
    ibge = doc.get("ibge")
    nome = doc.get("nome")

    if not ibge or not nome:
        return None

    # Parse georef_location (format: "lat,lon")
    lat, lon = None, None
    georef = doc.get("georef_location")
    if georef and isinstance(georef, str) and "," in georef:
        try:
            parts = georef.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())

            # Validate coordinates are within Brazil
            if not _is_valid_brazil_coordinate(lat, lon):
                logger.debug(f"Invalid coordinates for {nome}: {lat}, {lon}")
                lat, lon = None, None
        except (ValueError, IndexError):
            pass

    # Build full address
    endereco = doc.get("endereco", "")
    numero = doc.get("numero")
    if numero:
        endereco = f"{endereco}, {numero}".strip(", ")

    return {
        "id_equipamento": doc.get("id_equipamento"),
        "ibge_code": str(ibge),
        "nome": nome,
        "endereco": endereco or None,
        "bairro": doc.get("bairro"),
        "cep": _normalize_cep(doc.get("cep")),
        "cidade": doc.get("cidade"),
        "uf": doc.get("uf"),
        "telefone": doc.get("telefone"),
        "latitude": lat,
        "longitude": lon,
        "geocode_source": "sagi" if lat else None,
        "data_atualizacao": doc.get("data_atualizacao"),
    }


def _is_valid_brazil_coordinate(lat: float | None, lon: float | None) -> bool:
    """Validate that coordinates are within Brazil's bounding box."""
    if lat is None or lon is None:
        return False
    return (
        BRASIL_LAT_MIN <= lat <= BRASIL_LAT_MAX
        and BRASIL_LON_MIN <= lon <= BRASIL_LON_MAX
    )


def _normalize_ibge_code(code: str | None) -> str | None:
    """Normalize IBGE code to 7 digits."""
    if not code:
        return None

    code = re.sub(r"\D", "", str(code))

    if len(code) == 6:
        return code + "0"
    elif len(code) == 7:
        return code

    return None


def _normalize_cep(cep: str | None) -> str | None:
    """Normalize CEP to 8 digits without formatting."""
    if not cep:
        return None

    cep = re.sub(r"\D", "", str(cep))
    return cep if len(cep) == 8 else None


def save_cras_to_db(
    db: Session,
    cras_records: list[dict[str, Any]],
    source: str = "sagi",
) -> dict[str, int]:
    """Save CRAS records to database using upsert logic.

    Args:
        db: Database session
        cras_records: List of CRAS records (already geocoded from SAGI)
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


async def ingest_cras_data(dry_run: bool = False) -> dict[str, Any]:
    """Main function to ingest CRAS data.

    Pipeline:
    1. Fetch from SAGI API (includes geocoding)
    2. Fallback to local JSON if API fails
    3. Upsert to database

    Args:
        dry_run: If True, fetch and process data but don't save to DB

    Returns:
        Dict with ingestion statistics
    """
    logger.info("Starting CRAS data ingestion")
    start_time = datetime.now()

    result: dict[str, Any] = {
        "started_at": start_time.isoformat(),
        "source": "sagi",
        "records_fetched": 0,
        "records_geocoded": 0,
        "records_saved": 0,
        "errors": [],
    }

    # Step 1: Fetch data from SAGI API (already geocoded)
    cras_records = await fetch_sagi_cras_data()

    if not cras_records:
        # Fallback to local JSON file
        logger.info("SAGI API failed, trying local fallback...")
        cras_records = _load_fallback_data()
        if cras_records:
            result["source"] = "fallback_json"

    if not cras_records:
        result["errors"].append("Failed to fetch CRAS data from any source")
        result["finished_at"] = datetime.now().isoformat()
        return result

    result["records_fetched"] = len(cras_records)
    # SAGI data already includes geocoding
    result["records_geocoded"] = sum(1 for r in cras_records if r.get("latitude"))

    logger.info(
        f"Fetched {len(cras_records)} CRAS records, "
        f"{result['records_geocoded']} with coordinates"
    )

    if dry_run:
        logger.info("Dry run - skipping database save")
        result["dry_run"] = True
        result["finished_at"] = datetime.now().isoformat()
        return result

    # Step 2: Save to database
    db = SessionLocal()
    try:
        save_stats = save_cras_to_db(db, cras_records, source=result["source"])
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


def _load_fallback_data() -> list[dict[str, Any]] | None:
    """Load CRAS data from local fallback file if available.

    The fallback file contains sample CRAS data covering all Brazilian regions.
    """
    fallback_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "data", "cras_exemplo.json"
    )

    try:
        with open(fallback_path, encoding="utf-8") as f:
            data = json.load(f)
            cras_list = data.get("cras", [])
            if cras_list:
                # Map fallback format to standard schema
                mapped = []
                for item in cras_list:
                    coords = item.get("coordenadas", {})
                    mapped.append({
                        "ibge_code": item.get("ibge_code"),
                        "nome": item.get("nome"),
                        "endereco": item.get("endereco"),
                        "bairro": item.get("bairro"),
                        "cep": item.get("cep"),
                        "cidade": item.get("cidade"),
                        "uf": item.get("uf"),
                        "telefone": item.get("telefone"),
                        "latitude": coords.get("lat"),
                        "longitude": coords.get("lng"),
                        "geocode_source": "fallback",
                    })
                logger.info(f"Loaded {len(mapped)} CRAS from fallback file")
                return mapped
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
