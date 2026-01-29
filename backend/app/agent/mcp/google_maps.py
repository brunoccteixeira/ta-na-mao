"""
Google Maps MCP Wrapper.

Wrapper para o MCP do Google Maps que fornece acesso a:
- Geocoding (endereco <-> coordenadas)
- Places (busca de locais)
- Distance Matrix (distancias e tempos)
- Directions (rotas)

Referencia: https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

from .base import MCPClient, MCPWrapper

logger = structlog.get_logger(__name__)


class TipoLocal(str, Enum):
    """Tipos de local para busca."""

    FARMACIA = "pharmacy"
    FARMACIA_POPULAR = "pharmacy"  # com keyword
    CRAS = "local_government_office"
    LOTERIA = "lottery"
    BANCO = "bank"
    HOSPITAL = "hospital"
    POSTO_SAUDE = "health"
    SUPERMERCADO = "supermarket"


class ModoTransporte(str, Enum):
    """Modos de transporte para rotas."""

    CARRO = "driving"
    TRANSPORTE_PUBLICO = "transit"
    CAMINHANDO = "walking"
    BICICLETA = "bicycling"


@dataclass
class Coordenadas:
    """Coordenadas geograficas."""

    latitude: float
    longitude: float

    def to_string(self) -> str:
        """Retorna no formato 'lat,lng'."""
        return f"{self.latitude},{self.longitude}"

    def to_dict(self) -> Dict[str, float]:
        """Converte para dicionario."""
        return {"lat": self.latitude, "lng": self.longitude}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Coordenadas":
        """Cria a partir de dicionario."""
        return cls(
            latitude=data.get("lat", 0),
            longitude=data.get("lng", 0),
        )


@dataclass
class EnderecoGeocoding:
    """Resultado de geocoding."""

    endereco_formatado: str
    coordenadas: Coordenadas
    tipos: List[str] = field(default_factory=list)
    place_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "endereco": self.endereco_formatado,
            "coordenadas": self.coordenadas.to_dict(),
            "tipos": self.tipos,
            "place_id": self.place_id,
        }


@dataclass
class HorarioFuncionamento:
    """Horario de funcionamento de um local."""

    aberto_agora: bool
    periodos: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HorarioFuncionamento":
        """Cria a partir de dicionario."""
        return cls(
            aberto_agora=data.get("open_now", False),
            periodos=data.get("weekday_text", []),
        )


@dataclass
class LocalProximo:
    """Local encontrado na busca."""

    nome: str
    endereco: str
    coordenadas: Coordenadas
    place_id: str
    tipos: List[str] = field(default_factory=list)
    avaliacao: Optional[float] = None
    total_avaliacoes: Optional[int] = None
    distancia_metros: Optional[int] = None
    duracao_minutos: Optional[int] = None
    telefone: Optional[str] = None
    website: Optional[str] = None
    horario: Optional[HorarioFuncionamento] = None
    fotos: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "nome": self.nome,
            "endereco": self.endereco,
            "coordenadas": self.coordenadas.to_dict(),
            "place_id": self.place_id,
            "tipos": self.tipos,
            "avaliacao": self.avaliacao,
            "total_avaliacoes": self.total_avaliacoes,
            "distancia_metros": self.distancia_metros,
            "duracao_minutos": self.duracao_minutos,
            "telefone": self.telefone,
            "website": self.website,
            "aberto_agora": self.horario.aberto_agora if self.horario else None,
        }

    def distancia_formatada(self) -> str:
        """Retorna distancia formatada."""
        if not self.distancia_metros:
            return "N/D"
        if self.distancia_metros < 1000:
            return f"{self.distancia_metros}m"
        return f"{self.distancia_metros / 1000:.1f}km"


@dataclass
class PassoRota:
    """Passo individual de uma rota."""

    instrucao: str
    distancia: str
    duracao: str
    modo: str

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "instrucao": self.instrucao,
            "distancia": self.distancia,
            "duracao": self.duracao,
            "modo": self.modo,
        }


@dataclass
class Rota:
    """Rota entre dois pontos."""

    origem: str
    destino: str
    distancia_total: str
    duracao_total: str
    modo: ModoTransporte
    passos: List[PassoRota] = field(default_factory=list)
    polyline: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "origem": self.origem,
            "destino": self.destino,
            "distancia_total": self.distancia_total,
            "duracao_total": self.duracao_total,
            "modo": self.modo.value,
            "passos": [p.to_dict() for p in self.passos],
        }


class GoogleMapsMCP(MCPWrapper):
    """
    Wrapper para Google Maps MCP.

    Fornece metodos para:
    - Buscar farmacias, CRAS, loterias proximas
    - Geocoding de enderecos
    - Calcular distancias e rotas

    Exemplo:
        ```python
        maps = GoogleMapsMCP(client)
        farmacias = await maps.buscar_farmacias_proximas(
            lat=-23.5505, lng=-46.6333, raio=2000
        )
        for f in farmacias[:3]:
            print(f"{f.nome} - {f.distancia_formatada()}")
        ```
    """

    SERVER_NAME = "google-maps"

    @property
    def server_name(self) -> str:
        return self.SERVER_NAME

    async def health_check(self) -> bool:
        """Verifica se o MCP esta funcionando."""
        try:
            # Tenta geocoding de endereco conhecido
            result = await self.geocode("Praca da Se, Sao Paulo, SP")
            return result is not None
        except Exception:
            return False

    # =========================================================================
    # Geocoding
    # =========================================================================

    async def geocode(self, endereco: str) -> Optional[EnderecoGeocoding]:
        """
        Converte endereco em coordenadas.

        Args:
            endereco: Endereco completo ou parcial

        Returns:
            EnderecoGeocoding ou None

        Exemplo:
            >>> result = await maps.geocode("Av Paulista 1000, SP")
            >>> print(result.coordenadas.latitude)
            -23.5614
        """
        result = await self.call("maps_geocode", address=endereco)

        if not result.success or not result.data:
            logger.warning("geocode_failed", address=endereco, error=result.error)
            return None

        data = result.data
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        geometry = data.get("geometry", {})
        location = geometry.get("location", {})

        return EnderecoGeocoding(
            endereco_formatado=data.get("formatted_address", endereco),
            coordenadas=Coordenadas(
                latitude=location.get("lat", 0),
                longitude=location.get("lng", 0),
            ),
            tipos=data.get("types", []),
            place_id=data.get("place_id"),
        )

    async def reverse_geocode(
        self, lat: float, lng: float
    ) -> Optional[EnderecoGeocoding]:
        """
        Converte coordenadas em endereco.

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            EnderecoGeocoding ou None

        Exemplo:
            >>> result = await maps.reverse_geocode(-23.5505, -46.6333)
            >>> print(result.endereco_formatado)
            "Praca da Se, 1 - Se, Sao Paulo - SP"
        """
        result = await self.call("maps_reverse_geocode", latlng=f"{lat},{lng}")

        if not result.success or not result.data:
            return None

        data = result.data
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        return EnderecoGeocoding(
            endereco_formatado=data.get("formatted_address", ""),
            coordenadas=Coordenadas(latitude=lat, longitude=lng),
            tipos=data.get("types", []),
            place_id=data.get("place_id"),
        )

    async def cep_para_coordenadas(
        self, cep: str
    ) -> Optional[Tuple[float, float]]:
        """
        Converte CEP para coordenadas.

        Args:
            cep: CEP (com ou sem formatacao)

        Returns:
            Tupla (lat, lng) ou None
        """
        # Limpa CEP
        cep_limpo = "".join(filter(str.isdigit, cep))
        endereco = f"{cep_limpo}, Brasil"

        result = await self.geocode(endereco)
        if result:
            return (result.coordenadas.latitude, result.coordenadas.longitude)
        return None

    # =========================================================================
    # Busca de Locais (Places)
    # =========================================================================

    async def buscar_locais_proximos(
        self,
        lat: float,
        lng: float,
        tipo: TipoLocal,
        raio_metros: int = 5000,
        keyword: Optional[str] = None,
    ) -> List[LocalProximo]:
        """
        Busca locais proximos por tipo.

        Args:
            lat: Latitude
            lng: Longitude
            tipo: Tipo de local
            raio_metros: Raio de busca em metros
            keyword: Palavra-chave adicional

        Returns:
            Lista de LocalProximo ordenada por distancia
        """
        params = {
            "location": f"{lat},{lng}",
            "radius": raio_metros,
            "type": tipo.value,
        }
        if keyword:
            params["keyword"] = keyword

        result = await self.call("search_nearby", **params)

        if not result.success:
            logger.warning("places_search_failed", error=result.error)
            return []

        locais = []
        results = result.data.get("results", []) if isinstance(result.data, dict) else []

        for place in results:
            geometry = place.get("geometry", {})
            location = geometry.get("location", {})

            local = LocalProximo(
                nome=place.get("name", ""),
                endereco=place.get("vicinity", place.get("formatted_address", "")),
                coordenadas=Coordenadas(
                    latitude=location.get("lat", 0),
                    longitude=location.get("lng", 0),
                ),
                place_id=place.get("place_id", ""),
                tipos=place.get("types", []),
                avaliacao=place.get("rating"),
                total_avaliacoes=place.get("user_ratings_total"),
            )

            # Calcula distancia
            if local.coordenadas.latitude and local.coordenadas.longitude:
                local.distancia_metros = self._calcular_distancia_haversine(
                    lat, lng,
                    local.coordenadas.latitude,
                    local.coordenadas.longitude,
                )

            locais.append(local)

        # Ordena por distancia
        locais.sort(key=lambda x: x.distancia_metros or float("inf"))

        return locais

    async def buscar_farmacias_proximas(
        self,
        lat: float,
        lng: float,
        raio_metros: int = 5000,
        farmacia_popular: bool = False,
    ) -> List[LocalProximo]:
        """
        Busca farmacias proximas.

        Args:
            lat: Latitude
            lng: Longitude
            raio_metros: Raio de busca
            farmacia_popular: Se True, filtra por Farmacia Popular

        Returns:
            Lista de farmacias ordenadas por distancia

        Exemplo:
            >>> farmacias = await maps.buscar_farmacias_proximas(-23.55, -46.63)
            >>> for f in farmacias[:3]:
            ...     print(f"{f.nome}: {f.distancia_formatada()}")
        """
        keyword = "farmacia popular" if farmacia_popular else None
        return await self.buscar_locais_proximos(
            lat, lng, TipoLocal.FARMACIA, raio_metros, keyword
        )

    async def buscar_cras_proximos(
        self,
        lat: float,
        lng: float,
        raio_metros: int = 10000,
    ) -> List[LocalProximo]:
        """
        Busca CRAS proximos.

        Args:
            lat: Latitude
            lng: Longitude
            raio_metros: Raio de busca

        Returns:
            Lista de CRAS ordenados por distancia
        """
        return await self.buscar_locais_proximos(
            lat, lng, TipoLocal.CRAS, raio_metros, "CRAS"
        )

    async def buscar_lotericas_proximas(
        self,
        lat: float,
        lng: float,
        raio_metros: int = 5000,
    ) -> List[LocalProximo]:
        """
        Busca lotericas proximas.

        Args:
            lat: Latitude
            lng: Longitude
            raio_metros: Raio de busca

        Returns:
            Lista de lotericas ordenadas por distancia
        """
        return await self.buscar_locais_proximos(
            lat, lng, TipoLocal.LOTERIA, raio_metros, "lotérica caixa"
        )

    async def buscar_postos_saude_proximos(
        self,
        lat: float,
        lng: float,
        raio_metros: int = 5000,
    ) -> List[LocalProximo]:
        """
        Busca postos de saude/UBS proximos.

        Args:
            lat: Latitude
            lng: Longitude
            raio_metros: Raio de busca

        Returns:
            Lista de postos ordenados por distancia
        """
        return await self.buscar_locais_proximos(
            lat, lng, TipoLocal.POSTO_SAUDE, raio_metros, "UBS posto saude"
        )

    # =========================================================================
    # Detalhes de Local
    # =========================================================================

    async def obter_detalhes_local(self, place_id: str) -> Optional[LocalProximo]:
        """
        Obtem detalhes completos de um local.

        Args:
            place_id: ID do local no Google Places

        Returns:
            LocalProximo com detalhes completos
        """
        result = await self.call(
            "get_place_details",
            place_id=place_id,
            fields="name,formatted_address,geometry,formatted_phone_number,website,opening_hours,rating,user_ratings_total,photos",
        )

        if not result.success or not result.data:
            return None

        data = result.data.get("result", result.data)
        geometry = data.get("geometry", {})
        location = geometry.get("location", {})

        horario = None
        if "opening_hours" in data:
            horario = HorarioFuncionamento.from_dict(data["opening_hours"])

        return LocalProximo(
            nome=data.get("name", ""),
            endereco=data.get("formatted_address", ""),
            coordenadas=Coordenadas(
                latitude=location.get("lat", 0),
                longitude=location.get("lng", 0),
            ),
            place_id=place_id,
            tipos=data.get("types", []),
            avaliacao=data.get("rating"),
            total_avaliacoes=data.get("user_ratings_total"),
            telefone=data.get("formatted_phone_number"),
            website=data.get("website"),
            horario=horario,
        )

    # =========================================================================
    # Distancias e Rotas
    # =========================================================================

    async def calcular_distancia(
        self,
        origem_lat: float,
        origem_lng: float,
        destino_lat: float,
        destino_lng: float,
        modo: ModoTransporte = ModoTransporte.CAMINHANDO,
    ) -> Optional[Tuple[int, int]]:
        """
        Calcula distancia e duracao entre dois pontos.

        Args:
            origem_lat, origem_lng: Coordenadas de origem
            destino_lat, destino_lng: Coordenadas de destino
            modo: Modo de transporte

        Returns:
            Tupla (distancia_metros, duracao_segundos) ou None
        """
        result = await self.call(
            "maps_distance_matrix",
            origins=f"{origem_lat},{origem_lng}",
            destinations=f"{destino_lat},{destino_lng}",
            mode=modo.value,
        )

        if not result.success or not result.data:
            return None

        rows = result.data.get("rows", [])
        if not rows:
            return None

        elements = rows[0].get("elements", [])
        if not elements or elements[0].get("status") != "OK":
            return None

        element = elements[0]
        distancia = element.get("distance", {}).get("value", 0)
        duracao = element.get("duration", {}).get("value", 0)

        return (distancia, duracao)

    async def obter_rota(
        self,
        origem_lat: float,
        origem_lng: float,
        destino_lat: float,
        destino_lng: float,
        modo: ModoTransporte = ModoTransporte.CAMINHANDO,
    ) -> Optional[Rota]:
        """
        Obtem rota detalhada entre dois pontos.

        Args:
            origem_lat, origem_lng: Coordenadas de origem
            destino_lat, destino_lng: Coordenadas de destino
            modo: Modo de transporte

        Returns:
            Rota com passos detalhados

        Exemplo:
            >>> rota = await maps.obter_rota(-23.55, -46.63, -23.56, -46.64)
            >>> print(f"Total: {rota.distancia_total}, {rota.duracao_total}")
        """
        result = await self.call(
            "maps_directions",
            origin=f"{origem_lat},{origem_lng}",
            destination=f"{destino_lat},{destino_lng}",
            mode=modo.value,
            language="pt-BR",
        )

        if not result.success or not result.data:
            return None

        routes = result.data.get("routes", [])
        if not routes:
            return None

        route = routes[0]
        legs = route.get("legs", [])
        if not legs:
            return None

        leg = legs[0]

        passos = []
        for step in leg.get("steps", []):
            # Remove tags HTML das instrucoes
            instrucao = step.get("html_instructions", "")
            instrucao = instrucao.replace("<b>", "").replace("</b>", "")
            instrucao = instrucao.replace("<div>", " - ").replace("</div>", "")

            passos.append(
                PassoRota(
                    instrucao=instrucao,
                    distancia=step.get("distance", {}).get("text", ""),
                    duracao=step.get("duration", {}).get("text", ""),
                    modo=step.get("travel_mode", modo.value).lower(),
                )
            )

        return Rota(
            origem=leg.get("start_address", ""),
            destino=leg.get("end_address", ""),
            distancia_total=leg.get("distance", {}).get("text", ""),
            duracao_total=leg.get("duration", {}).get("text", ""),
            modo=modo,
            passos=passos,
            polyline=route.get("overview_polyline", {}).get("points"),
        )

    # =========================================================================
    # Utilidades
    # =========================================================================

    def _calcular_distancia_haversine(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
    ) -> int:
        """
        Calcula distancia aproximada usando formula de Haversine.

        Args:
            lat1, lng1: Ponto 1
            lat2, lng2: Ponto 2

        Returns:
            Distancia em metros
        """
        import math

        R = 6371000  # Raio da Terra em metros

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return int(R * c)

    def gerar_link_google_maps(
        self,
        destino_lat: float,
        destino_lng: float,
        destino_nome: Optional[str] = None,
    ) -> str:
        """
        Gera link para abrir no Google Maps.

        Args:
            destino_lat: Latitude do destino
            destino_lng: Longitude do destino
            destino_nome: Nome do local (opcional)

        Returns:
            URL do Google Maps
        """
        base = "https://www.google.com/maps/dir/?api=1"
        params = f"&destination={destino_lat},{destino_lng}"

        if destino_nome:
            import urllib.parse
            nome_encoded = urllib.parse.quote(destino_nome)
            params += f"&destination_place_id={nome_encoded}"

        return base + params


# Factory function
def create_google_maps_wrapper(client: MCPClient) -> GoogleMapsMCP:
    """
    Cria wrapper Google Maps.

    Args:
        client: Cliente MCP configurado

    Returns:
        GoogleMapsMCP: Wrapper configurado
    """
    return GoogleMapsMCP(client)
