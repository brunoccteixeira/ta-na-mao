"""
Serviço de busca de lugares usando Google Places API.

Usado para encontrar farmácias, CRAS e outros estabelecimentos
próximos baseado em coordenadas GPS.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Google Places API endpoints
PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


@dataclass
class PlaceResult:
    """Resultado de busca de lugar."""
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    distance_meters: Optional[float] = None
    rating: Optional[float] = None
    total_ratings: Optional[int] = None
    phone: Optional[str] = None
    opening_hours: Optional[List[str]] = None
    is_open_now: Optional[bool] = None
    types: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "place_id": self.place_id,
            "nome": self.name,
            "endereco": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "distancia_metros": self.distance_meters,
            "avaliacao": self.rating,
            "total_avaliacoes": self.total_ratings,
            "telefone": self.phone,
            "horario_funcionamento": self.opening_hours,
            "aberto_agora": self.is_open_now,
            "tipos": self.types or [],
        }


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula distância entre dois pontos usando fórmula de Haversine.
    Retorna distância em metros.
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000  # Raio da Terra em metros

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


async def buscar_lugares_proximos(
    latitude: float,
    longitude: float,
    tipo: str = "pharmacy",
    raio_metros: int = 5000,
    limite: int = 5,
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    Busca lugares próximos usando Google Places API.

    Args:
        latitude: Latitude do ponto central
        longitude: Longitude do ponto central
        tipo: Tipo de lugar (pharmacy, hospital, etc)
        raio_metros: Raio de busca em metros (máx 50000)
        limite: Número máximo de resultados
        keyword: Palavra-chave adicional para filtrar

    Returns:
        Dict com lista de lugares e metadados
    """
    api_key = settings.GOOGLE_API_KEY

    if not api_key:
        logger.warning("GOOGLE_API_KEY não configurada, usando dados locais")
        return {
            "sucesso": False,
            "erro": "API_KEY_NOT_CONFIGURED",
            "lugares": [],
            "total": 0
        }

    # Parâmetros da requisição
    params = {
        "location": f"{latitude},{longitude}",
        "radius": min(raio_metros, 50000),  # Máximo 50km
        "type": tipo,
        "key": api_key,
        "language": "pt-BR"
    }

    if keyword:
        params["keyword"] = keyword

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(PLACES_NEARBY_URL, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "OK":
            status = data.get("status", "UNKNOWN")
            error_message = data.get("error_message", "")
            logger.warning(f"Google Places API retornou status: {status} - {error_message}")

            if status == "ZERO_RESULTS":
                return {
                    "sucesso": True,
                    "lugares": [],
                    "total": 0,
                    "mensagem": f"Nenhum {tipo} encontrado na região"
                }

            return {
                "sucesso": False,
                "erro": status,
                "erro_detalhe": error_message,
                "lugares": [],
                "total": 0
            }

        # Processar resultados
        lugares = []
        for place in data.get("results", [])[:limite]:
            location = place.get("geometry", {}).get("location", {})
            place_lat = location.get("lat", 0)
            place_lng = location.get("lng", 0)

            # Calcular distância
            distancia = _calculate_distance(latitude, longitude, place_lat, place_lng)

            lugar = PlaceResult(
                place_id=place.get("place_id", ""),
                name=place.get("name", ""),
                address=place.get("vicinity", ""),
                latitude=place_lat,
                longitude=place_lng,
                distance_meters=round(distancia),
                rating=place.get("rating"),
                total_ratings=place.get("user_ratings_total"),
                is_open_now=place.get("opening_hours", {}).get("open_now"),
                types=place.get("types", [])
            )
            lugares.append(lugar)

        # Ordenar por distância
        lugares.sort(key=lambda x: x.distance_meters or float('inf'))

        return {
            "sucesso": True,
            "lugares": [l.to_dict() for l in lugares],
            "total": len(lugares),
            "coordenadas_busca": {"latitude": latitude, "longitude": longitude},
            "raio_metros": raio_metros
        }

    except httpx.TimeoutException:
        logger.error("Timeout ao chamar Google Places API")
        return {
            "sucesso": False,
            "erro": "TIMEOUT",
            "lugares": [],
            "total": 0
        }
    except httpx.HTTPError as e:
        logger.error(f"Erro HTTP ao chamar Google Places API: {e}")
        return {
            "sucesso": False,
            "erro": "HTTP_ERROR",
            "erro_detalhe": str(e),
            "lugares": [],
            "total": 0
        }
    except Exception as e:
        logger.error(f"Erro ao chamar Google Places API: {e}")
        return {
            "sucesso": False,
            "erro": "UNKNOWN_ERROR",
            "erro_detalhe": str(e),
            "lugares": [],
            "total": 0
        }


async def obter_detalhes_lugar(place_id: str) -> Dict[str, Any]:
    """
    Obtém detalhes de um lugar específico (telefone, horários, etc).

    Args:
        place_id: ID do lugar no Google Places

    Returns:
        Dict com detalhes do lugar
    """
    api_key = settings.GOOGLE_API_KEY

    if not api_key:
        return {"sucesso": False, "erro": "API_KEY_NOT_CONFIGURED"}

    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,opening_hours,website,url",
        "key": api_key,
        "language": "pt-BR"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(PLACES_DETAILS_URL, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "OK":
            return {
                "sucesso": False,
                "erro": data.get("status"),
                "erro_detalhe": data.get("error_message", "")
            }

        result = data.get("result", {})

        return {
            "sucesso": True,
            "nome": result.get("name"),
            "endereco": result.get("formatted_address"),
            "telefone": result.get("formatted_phone_number"),
            "horarios": result.get("opening_hours", {}).get("weekday_text", []),
            "aberto_agora": result.get("opening_hours", {}).get("open_now"),
            "website": result.get("website"),
            "google_maps_url": result.get("url")
        }

    except Exception as e:
        logger.error(f"Erro ao obter detalhes do lugar: {e}")
        return {
            "sucesso": False,
            "erro": "UNKNOWN_ERROR",
            "erro_detalhe": str(e)
        }


async def buscar_farmacias_proximas(
    latitude: float,
    longitude: float,
    raio_metros: int = 3000,
    limite: int = 5
) -> Dict[str, Any]:
    """
    Busca farmácias próximas.

    Wrapper específico para farmácias que usa keyword "farmacia popular"
    para priorizar farmácias credenciadas.

    Args:
        latitude: Latitude do ponto central
        longitude: Longitude do ponto central
        raio_metros: Raio de busca em metros
        limite: Número máximo de resultados

    Returns:
        Dict com lista de farmácias
    """
    # Primeiro busca farmácias em geral
    resultado = await buscar_lugares_proximos(
        latitude=latitude,
        longitude=longitude,
        tipo="pharmacy",
        raio_metros=raio_metros,
        limite=limite * 2,  # Busca mais para ter margem
        keyword="farmácia"
    )

    if not resultado.get("sucesso"):
        return resultado

    # Formatar resultados
    farmacias = []
    for lugar in resultado.get("lugares", [])[:limite]:
        farmacia = {
            "nome": lugar["nome"],
            "endereco": lugar["endereco"],
            "latitude": lugar["latitude"],
            "longitude": lugar["longitude"],
            "distancia": _formatar_distancia(lugar.get("distancia_metros", 0)),
            "distancia_metros": lugar.get("distancia_metros", 0),
            "avaliacao": lugar.get("avaliacao"),
            "aberto_agora": lugar.get("aberto_agora"),
            "place_id": lugar.get("place_id"),
            "links": {
                "maps": f"https://www.google.com/maps/place/?q=place_id:{lugar.get('place_id')}",
                "direcoes": f"https://www.google.com/maps/dir/?api=1&destination={lugar['latitude']},{lugar['longitude']}"
            }
        }
        farmacias.append(farmacia)

    return {
        "sucesso": True,
        "farmacias": farmacias,
        "total": len(farmacias),
        "coordenadas_busca": resultado.get("coordenadas_busca"),
        "raio_metros": raio_metros
    }


async def buscar_cras_proximos(
    latitude: float,
    longitude: float,
    raio_metros: int = 10000,
    limite: int = 3
) -> Dict[str, Any]:
    """
    Busca CRAS (Centro de Referência de Assistência Social) próximos.

    Args:
        latitude: Latitude do ponto central
        longitude: Longitude do ponto central
        raio_metros: Raio de busca em metros
        limite: Número máximo de resultados

    Returns:
        Dict com lista de CRAS
    """
    # CRAS não tem tipo específico no Google Places, usa keyword
    resultado = await buscar_lugares_proximos(
        latitude=latitude,
        longitude=longitude,
        tipo="local_government_office",
        raio_metros=raio_metros,
        limite=limite * 3,
        keyword="CRAS assistência social"
    )

    if not resultado.get("sucesso"):
        # Tenta busca alternativa
        resultado = await buscar_lugares_proximos(
            latitude=latitude,
            longitude=longitude,
            tipo="point_of_interest",
            raio_metros=raio_metros,
            limite=limite * 3,
            keyword="CRAS"
        )

    if not resultado.get("sucesso"):
        return resultado

    # Filtrar apenas resultados que parecem ser CRAS
    cras_list = []
    for lugar in resultado.get("lugares", []):
        nome_lower = lugar["nome"].lower()
        if "cras" in nome_lower or "assistência social" in nome_lower or "centro de referência" in nome_lower:
            cras = {
                "nome": lugar["nome"],
                "endereco": lugar["endereco"],
                "latitude": lugar["latitude"],
                "longitude": lugar["longitude"],
                "distancia": _formatar_distancia(lugar.get("distancia_metros", 0)),
                "distancia_metros": lugar.get("distancia_metros", 0),
                "aberto_agora": lugar.get("aberto_agora"),
                "place_id": lugar.get("place_id"),
                "links": {
                    "maps": f"https://www.google.com/maps/place/?q=place_id:{lugar.get('place_id')}",
                    "direcoes": f"https://www.google.com/maps/dir/?api=1&destination={lugar['latitude']},{lugar['longitude']}"
                }
            }
            cras_list.append(cras)

            if len(cras_list) >= limite:
                break

    return {
        "sucesso": True,
        "cras": cras_list,
        "total": len(cras_list),
        "coordenadas_busca": resultado.get("coordenadas_busca"),
        "raio_metros": raio_metros
    }


def _formatar_distancia(metros: float) -> str:
    """Formata distância para exibição."""
    if metros < 1000:
        return f"{int(metros)}m"
    return f"{metros/1000:.1f}km"
