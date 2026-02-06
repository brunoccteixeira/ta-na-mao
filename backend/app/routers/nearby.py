"""Endpoints para buscar serviços próximos ao cidadão.

Expõe funcionalidades de busca de farmácias e CRAS por coordenadas GPS.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.agent.tools.buscar_farmacia import (
    buscar_farmacia,
    buscar_farmacia_por_coordenadas
)
from app.agent.tools.buscar_cras import (
    buscar_cras,
    buscar_cras_por_coordenadas
)

router = APIRouter(prefix="/nearby", tags=["nearby"])


class ServiceLocation(BaseModel):
    """Modelo de local de serviço."""
    nome: str
    endereco: str
    distancia: Optional[str] = None
    distancia_metros: Optional[int] = None
    telefone: Optional[str] = None
    horario: Optional[str] = None
    aberto_agora: Optional[bool] = None
    delivery: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    links: dict = {}


class NearbyResponse(BaseModel):
    """Resposta padrão para busca de serviços próximos."""
    sucesso: bool
    encontrados: int
    locais: list[ServiceLocation]
    mensagem: Optional[str] = None
    redes_nacionais: Optional[list[str]] = None


@router.get("/farmacias", response_model=NearbyResponse)
async def buscar_farmacias_proximas(
    latitude: Optional[float] = Query(None, description="Latitude do usuário"),
    longitude: Optional[float] = Query(None, description="Longitude do usuário"),
    cep: Optional[str] = Query(None, description="CEP do usuário (alternativa às coordenadas)"),
    programa: Optional[str] = Query("FARMACIA_POPULAR", description="Programa: FARMACIA_POPULAR ou DIGNIDADE_MENSTRUAL"),
    raio_metros: int = Query(3000, description="Raio de busca em metros"),
    limite: int = Query(5, description="Número máximo de farmácias")
):
    """
    Busca farmácias credenciadas próximas ao cidadão.

    Pode usar coordenadas GPS (latitude/longitude) ou CEP.

    Retorna lista de farmácias com links para:
    - Google Maps (navegação)
    - Waze (navegação)
    - WhatsApp (contato)

    IMPORTANTE: Para Farmácia Popular e Dignidade Menstrual,
    o cidadão NÃO precisa ir ao CRAS. Vai direto na farmácia.
    """
    try:
        # Preferir coordenadas GPS se disponíveis
        if latitude is not None and longitude is not None:
            resultado = await buscar_farmacia_por_coordenadas(
                latitude=latitude,
                longitude=longitude,
                raio_metros=raio_metros,
                limite=limite
            )

            if resultado.get("erro"):
                # Fallback para busca por CEP se GPS falhar
                if cep:
                    resultado = buscar_farmacia(cep=cep, programa=programa, limite=limite)
                else:
                    return NearbyResponse(
                        sucesso=False,
                        encontrados=0,
                        locais=[],
                        mensagem=resultado.get("erro_mensagem", "Erro ao buscar farmácias"),
                        redes_nacionais=resultado.get("redes_nacionais", [])
                    )
        elif cep:
            # Buscar por CEP
            resultado = buscar_farmacia(cep=cep, programa=programa, limite=limite)
        else:
            raise HTTPException(
                status_code=400,
                detail="Informe latitude/longitude ou CEP para buscar farmácias"
            )

        # Converter para formato padrão
        farmacias = resultado.get("farmacias", [])
        locais = [
            ServiceLocation(
                nome=f.get("nome", ""),
                endereco=f.get("endereco", ""),
                distancia=f.get("distancia"),
                distancia_metros=f.get("distancia_metros"),
                telefone=f.get("telefone"),
                horario=f.get("horario"),
                aberto_agora=f.get("aberto_agora"),
                delivery=f.get("delivery"),
                links=f.get("links", {})
            )
            for f in farmacias
        ]

        return NearbyResponse(
            sucesso=True,
            encontrados=len(locais),
            locais=locais,
            mensagem=None if locais else "Não encontramos farmácias próximas. Tente em uma rede credenciada como Drogasil, Drogaria São Paulo ou Pague Menos.",
            redes_nacionais=resultado.get("redes_nacionais", [])
        )

    except Exception as e:
        return NearbyResponse(
            sucesso=False,
            encontrados=0,
            locais=[],
            mensagem=f"Erro ao buscar farmácias: {str(e)}",
            redes_nacionais=["Drogasil", "Drogaria São Paulo", "Pague Menos", "Droga Raia"]
        )


@router.get("/cras", response_model=NearbyResponse)
async def buscar_cras_proximos(
    latitude: Optional[float] = Query(None, description="Latitude do usuário"),
    longitude: Optional[float] = Query(None, description="Longitude do usuário"),
    cep: Optional[str] = Query(None, description="CEP do usuário (alternativa às coordenadas)"),
    raio_metros: int = Query(10000, description="Raio de busca em metros"),
    limite: int = Query(3, description="Número máximo de CRAS")
):
    """
    Busca CRAS (postos de assistência social) próximos ao cidadão.

    Pode usar coordenadas GPS (latitude/longitude) ou CEP.

    O CRAS é o local para:
    - Fazer ou atualizar CadÚnico
    - Solicitar Bolsa Família
    - Iniciar pedido de BPC/LOAS
    - Solicitar Tarifa Social de Energia
    """
    try:
        # Preferir coordenadas GPS se disponíveis
        if latitude is not None and longitude is not None:
            resultado = await buscar_cras_por_coordenadas(
                latitude=latitude,
                longitude=longitude,
                raio_metros=raio_metros,
                limite=limite
            )

            if resultado.get("erro"):
                # Fallback para busca por CEP se GPS falhar
                if cep:
                    resultado = buscar_cras(cep=cep, limite=limite)
                else:
                    return NearbyResponse(
                        sucesso=False,
                        encontrados=0,
                        locais=[],
                        mensagem="Não encontramos CRAS próximos. Ligue para o Disque Social: 121 (gratuito)"
                    )
        elif cep:
            # Buscar por CEP
            resultado = buscar_cras(cep=cep, limite=limite)
        else:
            raise HTTPException(
                status_code=400,
                detail="Informe latitude/longitude ou CEP para buscar CRAS"
            )

        # Converter para formato padrão
        cras_list = resultado.get("cras", [])
        locais = [
            ServiceLocation(
                nome=c.get("nome", ""),
                endereco=c.get("endereco", ""),
                distancia=c.get("distancia"),
                distancia_metros=c.get("distancia_metros"),
                telefone=c.get("telefone"),
                horario=c.get("horario"),
                aberto_agora=c.get("aberto_agora"),
                latitude=c.get("latitude"),
                longitude=c.get("longitude"),
                links=c.get("links", {})
            )
            for c in cras_list
        ]

        return NearbyResponse(
            sucesso=True,
            encontrados=len(locais),
            locais=locais,
            mensagem=None if locais else "Não encontramos CRAS próximos. Ligue para o Disque Social: 121 (gratuito)"
        )

    except Exception:
        return NearbyResponse(
            sucesso=False,
            encontrados=0,
            locais=[],
            mensagem="Erro ao buscar CRAS. Ligue para o Disque Social: 121 (gratuito)"
        )
