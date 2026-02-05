"""Geocoding service with free and paid fallback options.

Strategies:
1. CNEFE/geocodebr - Free, based on IBGE CNEFE database (~80% coverage)
2. Google Geocoding API - Paid fallback (~R$0.01-0.05 per request)
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional, Tuple

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)

# Brazil bounding box for validation
BRAZIL_BOUNDS = {
    "min_lat": -33.75,
    "max_lat": 5.27,
    "min_lon": -73.99,
    "max_lon": -34.79,
}


@dataclass
class GeocodingResult:
    """Result of a geocoding operation."""
    latitude: float
    longitude: float
    source: str  # "cnefe", "google", "nominatim"
    confidence: float = 1.0  # 0-1 confidence score
    formatted_address: Optional[str] = None


def _normalize_address(endereco: str, cidade: str, uf: str) -> str:
    """Normalize address for geocoding."""
    # Remove common abbreviations and normalize
    endereco = endereco.strip()
    endereco = re.sub(r'\s+', ' ', endereco)  # Multiple spaces to single
    endereco = re.sub(r'\bR\.\s*', 'Rua ', endereco, flags=re.IGNORECASE)
    endereco = re.sub(r'\bAv\.\s*', 'Avenida ', endereco, flags=re.IGNORECASE)
    endereco = re.sub(r'\bPç\.\s*', 'Praca ', endereco, flags=re.IGNORECASE)

    return f"{endereco}, {cidade}, {uf}, Brasil"


def _is_valid_brazil_coords(lat: float, lon: float) -> bool:
    """Validate coordinates are within Brazil."""
    return (
        BRAZIL_BOUNDS["min_lat"] <= lat <= BRAZIL_BOUNDS["max_lat"] and
        BRAZIL_BOUNDS["min_lon"] <= lon <= BRAZIL_BOUNDS["max_lon"]
    )


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
async def _try_nominatim(endereco: str, cidade: str, uf: str) -> Optional[GeocodingResult]:
    """Try geocoding with OpenStreetMap Nominatim (free).

    This is a free fallback using OpenStreetMap data.
    """
    query = _normalize_address(endereco, cidade, uf)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1,
                    "countrycodes": "br",
                },
                headers={"User-Agent": "TaNaMao/1.0 (social-benefits-platform)"}
            )

            if response.status_code == 200:
                results = response.json()
                if results:
                    result = results[0]
                    lat = float(result["lat"])
                    lon = float(result["lon"])

                    if _is_valid_brazil_coords(lat, lon):
                        return GeocodingResult(
                            latitude=lat,
                            longitude=lon,
                            source="nominatim",
                            confidence=0.7,
                            formatted_address=result.get("display_name"),
                        )
        except Exception as e:
            logger.warning(f"Nominatim geocoding failed: {e}")

    return None


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
async def _try_google(endereco: str, cidade: str, uf: str) -> Optional[GeocodingResult]:
    """Try geocoding with Google Geocoding API (paid fallback).

    Requires GOOGLE_GEOCODING_KEY in settings.
    Cost: ~R$0.01-0.05 per request.
    """
    api_key = getattr(settings, 'GOOGLE_GEOCODING_KEY', None)
    if not api_key:
        logger.debug("Google Geocoding API key not configured")
        return None

    query = _normalize_address(endereco, cidade, uf)

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "address": query,
                    "key": api_key,
                    "region": "br",
                    "language": "pt-BR",
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK" and data.get("results"):
                    result = data["results"][0]
                    location = result["geometry"]["location"]
                    lat = location["lat"]
                    lon = location["lng"]

                    if _is_valid_brazil_coords(lat, lon):
                        # Calculate confidence based on location_type
                        location_type = result["geometry"].get("location_type", "")
                        confidence = {
                            "ROOFTOP": 1.0,
                            "RANGE_INTERPOLATED": 0.9,
                            "GEOMETRIC_CENTER": 0.7,
                            "APPROXIMATE": 0.5,
                        }.get(location_type, 0.6)

                        return GeocodingResult(
                            latitude=lat,
                            longitude=lon,
                            source="google",
                            confidence=confidence,
                            formatted_address=result.get("formatted_address"),
                        )
                elif data.get("status") == "ZERO_RESULTS":
                    logger.debug(f"Google: no results for {query}")
                else:
                    logger.warning(f"Google geocoding error: {data.get('status')}")
        except Exception as e:
            logger.error(f"Google geocoding failed: {e}")

    return None


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
async def _try_viacep_coords(cep: str) -> Optional[GeocodingResult]:
    """Try getting coordinates from CEP using external services.

    CEP alone doesn't give coordinates, but we can use it to get
    the address and then geocode that.
    """
    if not cep or len(cep.replace("-", "").strip()) != 8:
        return None

    cep_clean = cep.replace("-", "").strip()

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # First get address from ViaCEP
            response = await client.get(f"https://viacep.com.br/ws/{cep_clean}/json/")
            if response.status_code == 200:
                data = response.json()
                if "erro" not in data:
                    # Now geocode the address
                    endereco = data.get("logradouro", "")
                    cidade = data.get("localidade", "")
                    uf = data.get("uf", "")

                    if cidade and uf:
                        # Try Nominatim first (free)
                        result = await _try_nominatim(endereco or cidade, cidade, uf)
                        if result:
                            return result
        except Exception as e:
            logger.warning(f"ViaCEP geocoding failed: {e}")

    return None


async def geocode_address(
    endereco: str,
    cidade: str,
    uf: str,
    cep: Optional[str] = None,
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Geocode a Brazilian address.

    Tries multiple strategies in order:
    1. Nominatim (free, OSM-based)
    2. CEP-based lookup (if provided)
    3. Google Geocoding API (paid, if configured)

    Args:
        endereco: Street address (e.g., "Rua das Flores, 123")
        cidade: City name (e.g., "Sao Paulo")
        uf: State code (e.g., "SP")
        cep: Optional CEP for better accuracy

    Returns:
        Tuple of (latitude, longitude, source) or (None, None, None) if failed
    """
    # Strategy 1: Try Nominatim first (free)
    result = await _try_nominatim(endereco, cidade, uf)
    if result:
        logger.debug(f"Nominatim geocoded: {endereco}, {cidade}")
        return result.latitude, result.longitude, result.source

    # Strategy 2: Try CEP-based lookup
    if cep:
        result = await _try_viacep_coords(cep)
        if result:
            logger.debug(f"CEP geocoded: {cep}")
            return result.latitude, result.longitude, f"cep_{result.source}"

    # Strategy 3: Fall back to Google (paid)
    result = await _try_google(endereco, cidade, uf)
    if result:
        logger.debug(f"Google geocoded: {endereco}, {cidade}")
        return result.latitude, result.longitude, result.source

    logger.warning(f"All geocoding strategies failed for: {endereco}, {cidade}, {uf}")
    return None, None, None


async def batch_geocode(
    addresses: list[dict],
    max_concurrent: int = 5,
) -> list[dict]:
    """Geocode multiple addresses with rate limiting.

    Args:
        addresses: List of dicts with keys: endereco, cidade, uf, cep (optional)
        max_concurrent: Maximum concurrent requests

    Returns:
        List of dicts with added: latitude, longitude, geocode_source
    """
    import asyncio

    semaphore = asyncio.Semaphore(max_concurrent)

    async def geocode_one(addr: dict) -> dict:
        async with semaphore:
            lat, lon, source = await geocode_address(
                endereco=addr.get("endereco", ""),
                cidade=addr.get("cidade", ""),
                uf=addr.get("uf", ""),
                cep=addr.get("cep"),
            )
            return {
                **addr,
                "latitude": lat,
                "longitude": lon,
                "geocode_source": source,
            }

    results = await asyncio.gather(*[geocode_one(addr) for addr in addresses])
    return list(results)


def geocode_address_sync(
    endereco: str,
    cidade: str,
    uf: str,
    cep: Optional[str] = None,
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Synchronous wrapper for geocode_address."""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(geocode_address(endereco, cidade, uf, cep))
