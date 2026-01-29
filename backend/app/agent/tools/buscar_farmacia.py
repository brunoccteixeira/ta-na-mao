"""Tool para buscar farmacias credenciadas no Farmacia Popular.

Esta tool gera links de ACAO para o cidadao:
- Link para abrir no Google Maps (navegacao)
- Link para abrir no Waze (navegacao)
- Link para WhatsApp click-to-chat (contato direto)
- Indicador se tem delivery disponivel

Suporta busca por:
- Coordenadas GPS (via MCP Google Maps ou Google Places API direto)
- CEP (dados locais)
- Código IBGE (dados locais)
"""

import json
import os
import logging
from typing import Optional, List, Dict, Any
from urllib.parse import quote
import httpx

from app.agent.mcp import mcp_manager, GoogleMapsMCP

logger = logging.getLogger(__name__)

# Carrega base de farmacias
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "data", "farmacias_exemplo.json"
)

_FARMACIAS_CACHE = None


def _carregar_farmacias() -> dict:
    """Carrega a base de farmacias do JSON."""
    global _FARMACIAS_CACHE
    if _FARMACIAS_CACHE is None:
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                _FARMACIAS_CACHE = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Arquivo de farmácias não encontrado: {DATA_PATH}")
            _FARMACIAS_CACHE = {"farmacias": [], "redes_nacionais": []}
    return _FARMACIAS_CACHE


def _obter_ibge_por_cep(cep: str) -> Optional[str]:
    """Obtem codigo IBGE do municipio via ViaCEP."""
    cep_limpo = cep.replace("-", "").replace(".", "").strip()
    if len(cep_limpo) != 8:
        return None

    try:
        response = httpx.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            if "erro" not in data:
                return data.get("ibge")
    except Exception:
        pass
    return None


def _gerar_link_maps(lat: float, lng: float, nome: str) -> str:
    """Gera link para Google Maps com navegacao."""
    # Formato que abre direto no app do Maps com navegacao
    return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}&destination_place_id={quote(nome)}"


def _gerar_link_waze(lat: float, lng: float) -> str:
    """Gera link para Waze com navegacao."""
    return f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"


def _gerar_link_whatsapp(numero: str, mensagem: str = "") -> str:
    """Gera link click-to-chat do WhatsApp."""
    # Remove caracteres nao numericos
    numero_limpo = "".join(filter(str.isdigit, numero))
    if mensagem:
        return f"https://wa.me/{numero_limpo}?text={quote(mensagem)}"
    return f"https://wa.me/{numero_limpo}"


def buscar_farmacia(
    cep: Optional[str] = None,
    ibge_code: Optional[str] = None,
    programa: Optional[str] = None,
    limite: int = 3
) -> dict:
    """Busca farmacias credenciadas com links de ACAO.

    Esta tool encontra farmacias e gera links para o cidadao AGIR:
    - Abrir no Maps/Waze para ir ate la
    - Clicar no WhatsApp para falar com a farmacia
    - Ver se tem delivery disponivel

    IMPORTANTE: O cidadao NAO precisa ir ao CRAS para estes programas.
    Basta ir diretamente a uma farmacia credenciada com CPF e receita medica.

    Args:
        cep: CEP do cidadao (8 digitos). Obtem municipio automaticamente.
        ibge_code: Codigo IBGE do municipio (7 digitos). Alternativa ao CEP.
        programa: Filtrar por programa especifico:
            - "FARMACIA_POPULAR": medicamentos
            - "DIGNIDADE_MENSTRUAL": absorventes
            - None: lista todas as farmacias credenciadas
        limite: Numero maximo de farmacias a retornar (padrao: 3).

    Returns:
        dict: {
            "encontrados": int,
            "municipio": str,
            "farmacias": [
                {
                    "nome": "Drogasil - Vila Mariana",
                    "endereco": "Rua X, 123",
                    "telefone": "(11) 3333-4444",
                    "horario": "Seg-Dom 7h-22h",
                    "delivery": true,
                    "links": {
                        "maps": "https://google.com/maps/...",
                        "waze": "https://waze.com/...",
                        "whatsapp": "https://wa.me/..."
                    }
                }
            ],
            "texto_formatado": "Texto com links clicaveis"
        }
    """
    # Obter codigo IBGE
    codigo_ibge = ibge_code
    if not codigo_ibge and cep:
        codigo_ibge = _obter_ibge_por_cep(cep)

    # Carregar base
    dados = _carregar_farmacias()
    farmacias_list = dados.get("farmacias", [])
    redes_nacionais = dados.get("redes_nacionais", [])

    # Mensagem padrao para WhatsApp
    programa_nome = "Farmacia Popular"
    if programa == "DIGNIDADE_MENSTRUAL":
        programa_nome = "Dignidade Menstrual"
        msg_whatsapp = "Ola! Quero retirar absorventes pelo programa Dignidade Menstrual. Voces participam?"
    else:
        msg_whatsapp = "Ola! Quero retirar medicamentos pelo Farmacia Popular. Voces participam?"

    # Se nao tem IBGE, retorna info sobre redes nacionais
    if not codigo_ibge:
        redes_nomes = [r["nome"] for r in redes_nacionais if r.get("credenciada")]
        return {
            "erro": False,
            "encontrados": 0,
            "redes_nacionais": redes_nomes,
            "farmacias": [],
            "texto_formatado": (
                "Nao consegui identificar seu municipio.\n\n"
                "Mas voce pode ir em qualquer farmacia dessas redes:\n"
                + "\n".join([f"- {r}" for r in redes_nomes]) +
                "\n\nTodas sao credenciadas no Farmacia Popular!"
            )
        }

    # Filtrar por municipio
    farmacias_municipio = [
        f for f in farmacias_list
        if f.get("ibge_code") == codigo_ibge
    ]

    # Filtrar por programa se especificado
    if programa:
        farmacias_municipio = [
            f for f in farmacias_municipio
            if programa in f.get("programas", [])
        ]

    # Identificar cidade
    cidade = farmacias_municipio[0].get("cidade", "") if farmacias_municipio else ""

    # Redes nacionais como alternativa
    redes_nomes = [r["nome"] for r in redes_nacionais if r.get("credenciada")]
    if programa:
        redes_nomes = [
            r["nome"] for r in redes_nacionais
            if r.get("credenciada") and programa in r.get("programas", [])
        ]

    if not farmacias_municipio:
        return {
            "erro": False,
            "encontrados": 0,
            "municipio": cidade or codigo_ibge,
            "redes_nacionais": redes_nomes,
            "farmacias": [],
            "texto_formatado": (
                "Nao encontrei farmacias especificas na nossa base para seu municipio.\n\n"
                "Mas voce pode ir em qualquer farmacia dessas redes credenciadas:\n"
                + "\n".join([f"- {r}" for r in redes_nomes]) +
                f"\n\nTodas participam do {programa_nome}!\n"
                f"Leve: CPF e receita medica (se for medicamento)"
            )
        }

    # Limitar resultados
    farmacias_resultado = farmacias_municipio[:limite]

    # Formatar para exibicao com links de ACAO
    resultado = []
    linhas_texto = [f"Encontrei {len(farmacias_resultado)} farmacias credenciadas:\n"]

    for i, farm in enumerate(farmacias_resultado, 1):
        # Extrair coordenadas
        coord = farm.get("coordenadas", {})
        lat = coord.get("lat", 0)
        lng = coord.get("lng", 0)

        # Gerar links de acao
        links = {}
        if lat and lng:
            links["maps"] = _gerar_link_maps(lat, lng, farm["nome"])
            links["waze"] = _gerar_link_waze(lat, lng)

        # WhatsApp
        whatsapp = farm.get("whatsapp")
        if whatsapp:
            links["whatsapp"] = _gerar_link_whatsapp(whatsapp, msg_whatsapp)

        # Verificar delivery
        tem_delivery = farm.get("delivery", False)

        resultado.append({
            "nome": farm["nome"],
            "rede": farm.get("rede", ""),
            "endereco": farm["endereco"],
            "bairro": farm.get("bairro", ""),
            "cidade": farm.get("cidade", ""),
            "telefone": farm.get("telefone", ""),
            "whatsapp": whatsapp,
            "horario": farm.get("horario", ""),
            "programas": farm.get("programas", []),
            "delivery": tem_delivery,
            "links": links
        })

        # Texto formatado com links
        linhas_texto.append(f"{i}. {farm['nome']}")
        linhas_texto.append(f"   {farm['endereco']}, {farm.get('bairro', '')}")
        linhas_texto.append(f"   Horario: {farm.get('horario', '')}")

        # Acoes
        linhas_texto.append("")
        linhas_texto.append("   COMO CHEGAR:")
        if links.get("maps"):
            linhas_texto.append(f"   [Abrir no Maps]({links['maps']})")
        if links.get("waze"):
            linhas_texto.append(f"   [Abrir no Waze]({links['waze']})")

        linhas_texto.append("")
        linhas_texto.append("   FALAR COM A FARMACIA:")
        linhas_texto.append(f"   Telefone: {farm.get('telefone', 'Nao informado')}")
        if links.get("whatsapp"):
            linhas_texto.append(f"   [Falar no WhatsApp]({links['whatsapp']})")

        if tem_delivery:
            linhas_texto.append("")
            linhas_texto.append("   ENTREGA EM CASA DISPONIVEL!")

        linhas_texto.append("")
        linhas_texto.append("-" * 40)

    # Instrucoes finais
    linhas_texto.append("")
    linhas_texto.append("O QUE LEVAR:")
    if programa == "DIGNIDADE_MENSTRUAL":
        linhas_texto.append("- CPF")
        linhas_texto.append("- Estar no CadUnico com renda ate meio salario minimo")
    else:
        linhas_texto.append("- CPF")
        linhas_texto.append("- Receita medica (validade de 120 dias)")

    linhas_texto.append("")
    linhas_texto.append("NAO PRECISA IR AO CRAS!")
    linhas_texto.append("Va direto na farmacia.")

    return {
        "erro": False,
        "encontrados": len(farmacias_resultado),
        "municipio": cidade,
        "redes_nacionais": redes_nomes,
        "farmacias": resultado,
        "texto_formatado": "\n".join(linhas_texto)
    }


def buscar_farmacia_sync(
    cep: Optional[str] = None,
    ibge_code: Optional[str] = None,
    programa: Optional[str] = None,
    limite: int = 3
) -> dict:
    """Versao sincrona de buscar_farmacia para uso com o agente."""
    return buscar_farmacia(cep=cep, ibge_code=ibge_code, programa=programa, limite=limite)


async def _buscar_farmacia_mcp(
    latitude: float,
    longitude: float,
    raio_metros: int = 3000,
    limite: int = 5,
    farmacia_popular: bool = False
) -> List[Dict[str, Any]] | None:
    """Busca farmácias via MCP Google Maps.

    Args:
        latitude: Latitude do ponto central
        longitude: Longitude do ponto central
        raio_metros: Raio de busca em metros
        limite: Número máximo de resultados
        farmacia_popular: Se True, filtra por Farmacia Popular

    Returns:
        Lista de farmácias ou None se MCP falhar
    """
    try:
        wrapper = mcp_manager.get_wrapper("google-maps")
        if not wrapper or not isinstance(wrapper, GoogleMapsMCP):
            logger.debug("google-maps MCP not available")
            return None

        locais = await wrapper.buscar_farmacias_proximas(
            lat=latitude,
            lng=longitude,
            raio_metros=raio_metros,
            farmacia_popular=farmacia_popular
        )

        if not locais:
            return None

        # Converte LocalProximo para formato esperado
        farmacias = []
        for local in locais[:limite]:
            farmacia = {
                "nome": local.nome,
                "endereco": local.endereco,
                "latitude": local.coordenadas.latitude,
                "longitude": local.coordenadas.longitude,
                "distancia": local.distancia_formatada(),
                "distancia_metros": local.distancia_metros or 0,
                "avaliacao": local.avaliacao,
                "aberto_agora": local.horario.aberto_agora if local.horario else None,
                "place_id": local.place_id,
                "telefone": local.telefone,
                "links": {
                    "maps": f"https://www.google.com/maps/place/?q=place_id:{local.place_id}",
                    "direcoes": wrapper.gerar_link_google_maps(
                        local.coordenadas.latitude,
                        local.coordenadas.longitude,
                        local.nome
                    ),
                    "waze": _gerar_link_waze(local.coordenadas.latitude, local.coordenadas.longitude)
                },
                "fonte": "google-maps-mcp"
            }
            farmacias.append(farmacia)

        return farmacias

    except Exception as e:
        logger.warning(f"MCP buscar_farmacia failed: {e}")
        return None


async def _buscar_farmacia_google_direto(
    latitude: float,
    longitude: float,
    raio_metros: int = 3000,
    limite: int = 5
) -> Dict[str, Any]:
    """Fallback para Google Places API direto quando MCP não disponível."""
    from .google_places import buscar_farmacias_proximas as buscar_google_direto

    try:
        resultado = await buscar_google_direto(
            latitude=latitude,
            longitude=longitude,
            raio_metros=raio_metros,
            limite=limite
        )

        if resultado.get("sucesso") and resultado.get("farmacias"):
            # Adiciona fonte ao resultado
            for farmacia in resultado["farmacias"]:
                farmacia["fonte"] = "google-places-api"

        return resultado

    except Exception as e:
        logger.error(f"Fallback Google Places API failed: {e}")
        return {
            "sucesso": False,
            "erro": str(e),
            "farmacias": []
        }


async def buscar_farmacia_por_coordenadas(
    latitude: float,
    longitude: float,
    raio_metros: int = 3000,
    limite: int = 5
) -> dict:
    """
    Busca farmácias próximas usando coordenadas GPS.

    Usa MCP Google Maps como fonte primária, com fallback para Google Places API.

    Args:
        latitude: Latitude do usuário
        longitude: Longitude do usuário
        raio_metros: Raio de busca em metros (padrão: 3km)
        limite: Número máximo de farmácias a retornar

    Returns:
        dict: {
            "sucesso": bool,
            "encontrados": int,
            "farmacias": [...],
            "texto_formatado": str
        }
    """
    try:
        # Tenta MCP primeiro
        farmacias_mcp = await _buscar_farmacia_mcp(
            latitude=latitude,
            longitude=longitude,
            raio_metros=raio_metros,
            limite=limite
        )

        if farmacias_mcp:
            logger.debug("Farmácias encontradas via MCP")
            farmacias = farmacias_mcp
        else:
            # Fallback para Google Places API direto
            logger.debug("Falling back to Google Places API")
            resultado_fallback = await _buscar_farmacia_google_direto(
                latitude=latitude,
                longitude=longitude,
                raio_metros=raio_metros,
                limite=limite
            )

            if not resultado_fallback.get("sucesso"):
                # Último fallback para dados locais
                logger.warning("Google Places API falhou, usando dados locais")
                return {
                    "erro": False,
                    "encontrados": 0,
                    "farmacias": [],
                    "redes_nacionais": _get_redes_nacionais(),
                    "texto_formatado": _texto_redes_nacionais_fallback()
                }

            farmacias = resultado_fallback.get("farmacias", [])

        if not farmacias:
            return {
                "erro": False,
                "encontrados": 0,
                "farmacias": [],
                "redes_nacionais": _get_redes_nacionais(),
                "texto_formatado": (
                    "Não encontrei farmácias na região.\n\n"
                    "Mas você pode ir em qualquer farmacia dessas redes:\n"
                    + _texto_redes_nacionais()
                )
            }

        # Formatar resultado
        farmacias_formatadas = []
        linhas_texto = [f"Encontrei {len(farmacias)} farmácias perto de você:\n"]

        for i, farm in enumerate(farmacias, 1):
            links = farm.get("links", {})
            if not links.get("maps") and farm.get("place_id"):
                links["maps"] = f"https://www.google.com/maps/place/?q=place_id:{farm['place_id']}"
            if not links.get("direcoes") and farm.get("latitude") and farm.get("longitude"):
                links["direcoes"] = f"https://www.google.com/maps/dir/?api=1&destination={farm['latitude']},{farm['longitude']}"

            # Adicionar link Waze se ainda não tem
            if not links.get("waze") and farm.get("latitude") and farm.get("longitude"):
                links["waze"] = _gerar_link_waze(farm["latitude"], farm["longitude"])

            farmacias_formatadas.append({
                "nome": farm.get("nome", ""),
                "endereco": farm.get("endereco", ""),
                "distancia": farm.get("distancia", ""),
                "distancia_metros": farm.get("distancia_metros", 0),
                "avaliacao": farm.get("avaliacao"),
                "aberto_agora": farm.get("aberto_agora"),
                "telefone": farm.get("telefone"),
                "links": links,
                "fonte": farm.get("fonte", "unknown")
            })

            # Texto formatado
            status_aberto = "Aberto" if farm.get("aberto_agora") else "Horário não confirmado"
            linhas_texto.append(f"{i}. **{farm.get('nome', '')}**")
            linhas_texto.append(f"   {farm.get('endereco', '')}")
            linhas_texto.append(f"   {farm.get('distancia', 'Distância não calculada')}")
            linhas_texto.append(f"   {status_aberto}")

            if farm.get("avaliacao"):
                linhas_texto.append(f"   {farm['avaliacao']}/5")

            linhas_texto.append("")
            linhas_texto.append(f"   [Ver no Maps]({links.get('direcoes', '')})")
            if links.get("waze"):
                linhas_texto.append(f"   [Waze]({links['waze']})")
            linhas_texto.append("")
            linhas_texto.append("-" * 30)

        linhas_texto.append("")
        linhas_texto.append("**O QUE LEVAR:**")
        linhas_texto.append("- CPF")
        linhas_texto.append("- Receita médica (validade 120 dias)")
        linhas_texto.append("")
        linhas_texto.append("NÃO PRECISA IR AO CRAS!")

        return {
            "erro": False,
            "encontrados": len(farmacias_formatadas),
            "farmacias": farmacias_formatadas,
            "coordenadas_busca": {"latitude": latitude, "longitude": longitude},
            "raio_metros": raio_metros,
            "texto_formatado": "\n".join(linhas_texto)
        }

    except Exception as e:
        logger.error(f"Erro ao buscar farmácias por coordenadas: {e}")
        return {
            "erro": True,
            "erro_mensagem": str(e),
            "encontrados": 0,
            "farmacias": [],
            "texto_formatado": "Erro ao buscar farmácias. Tente novamente."
        }


def _get_redes_nacionais() -> list:
    """Retorna lista de redes nacionais credenciadas."""
    dados = _carregar_farmacias()
    return [r["nome"] for r in dados.get("redes_nacionais", []) if r.get("credenciada")]


def _texto_redes_nacionais() -> str:
    """Retorna texto com lista de redes nacionais."""
    redes = _get_redes_nacionais()
    if not redes:
        return "- Drogasil\n- Drogaria São Paulo\n- Pague Menos\n- Droga Raia"
    return "\n".join([f"- {r}" for r in redes])


def _texto_redes_nacionais_fallback() -> str:
    """Texto de fallback quando não consegue buscar por coordenadas."""
    return (
        "Não consegui buscar farmácias próximas no momento.\n\n"
        "Mas você pode ir em qualquer farmácia dessas redes credenciadas:\n"
        + _texto_redes_nacionais() +
        "\n\nTodas participam do Farmácia Popular!\n"
        "Leve: CPF e receita médica"
    )
