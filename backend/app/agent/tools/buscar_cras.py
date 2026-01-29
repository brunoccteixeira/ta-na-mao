"""Tool para buscar CRAS mais proximos do cidadao.

Suporta busca por:
- Coordenadas GPS (Google Places API)
- CEP (dados locais)
- Código IBGE (dados locais)
"""

import json
import os
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# Carrega base de CRAS
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "data", "cras_exemplo.json"
)

_CRAS_CACHE = None


def _carregar_cras() -> dict:
    """Carrega a base de CRAS do JSON."""
    global _CRAS_CACHE
    if _CRAS_CACHE is None:
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                _CRAS_CACHE = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Arquivo de CRAS não encontrado: {DATA_PATH}")
            _CRAS_CACHE = {"cras": []}
    return _CRAS_CACHE


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


def buscar_cras(
    cep: Optional[str] = None,
    ibge_code: Optional[str] = None,
    limite: int = 3
) -> dict:
    """Busca CRAS mais proximos do cidadao.

    Esta tool encontra os Centros de Referencia de Assistencia Social (CRAS)
    mais proximos do endereco do cidadao. O CRAS eh o local para:
    - Fazer ou atualizar CadUnico
    - Solicitar Bolsa Familia
    - Encaminhar pedido de BPC/LOAS
    - Solicitar Tarifa Social de Energia

    Args:
        cep: CEP do cidadao (8 digitos). Obtem municipio automaticamente.
        ibge_code: Codigo IBGE do municipio (7 digitos). Alternativa ao CEP.
        limite: Numero maximo de CRAS a retornar (padrao: 3).

    Returns:
        dict: {
            "encontrados": int,
            "municipio": str,
            "cras": [
                {
                    "nome": "CRAS Vila Mariana",
                    "endereco": "Rua X, 123",
                    "bairro": "Vila Mariana",
                    "cidade": "Sao Paulo",
                    "telefone": "(11) 3333-4444",
                    "horario": "Seg-Sex 8h-17h",
                    "servicos": ["CadUnico", "Bolsa Familia", ...]
                }
            ],
            "texto_formatado": "Texto pronto para enviar ao cidadao"
        }

    Examples:
        >>> buscar_cras(cep="04010-100")  # Vila Mariana, SP
        >>> buscar_cras(ibge_code="3550308")  # Sao Paulo
    """
    # Obter codigo IBGE
    codigo_ibge = ibge_code
    if not codigo_ibge and cep:
        codigo_ibge = _obter_ibge_por_cep(cep)

    if not codigo_ibge:
        return {
            "erro": True,
            "mensagem": "Nao foi possivel identificar o municipio. Informe o CEP ou codigo IBGE.",
            "encontrados": 0,
            "cras": []
        }

    # Carregar base de CRAS
    dados = _carregar_cras()
    cras_list = dados.get("cras", [])

    # Filtrar por municipio
    cras_municipio = [
        c for c in cras_list
        if c.get("ibge_code") == codigo_ibge
    ]

    if not cras_municipio:
        # Retorna mensagem informativa se nao tiver na base
        return {
            "erro": False,
            "encontrados": 0,
            "municipio": codigo_ibge,
            "cras": [],
            "mensagem": "Nao encontramos CRAS cadastrados para este municipio na nossa base de exemplo.",
            "dica": "Ligue para o Disque Social 121 para encontrar o CRAS mais proximo.",
            "texto_formatado": (
                "Ainda nao temos os CRAS do seu municipio na nossa base.\n\n"
                "Para encontrar o CRAS mais proximo:\n"
                "- Ligue para o Disque Social: 121 (gratuito)\n"
                "- Ou acesse: https://aplicacoes.mds.gov.br/sagi/miv/miv.php"
            )
        }

    # Limitar resultados
    cras_resultado = cras_municipio[:limite]

    # Identificar cidade
    cidade = cras_resultado[0].get("cidade", "") if cras_resultado else ""

    # Formatar para exibicao
    resultado = []
    linhas_texto = [f"Encontrei {len(cras_resultado)} CRAS perto de voce:\n"]

    for i, cras in enumerate(cras_resultado, 1):
        resultado.append({
            "nome": cras["nome"],
            "endereco": cras["endereco"],
            "bairro": cras.get("bairro", ""),
            "cidade": cras.get("cidade", ""),
            "telefone": cras.get("telefone", ""),
            "horario": cras.get("horario", ""),
            "servicos": cras.get("servicos", [])
        })

        linhas_texto.append(f"{i}. {cras['nome']}")
        linhas_texto.append(f"   Endereco: {cras['endereco']}, {cras.get('bairro', '')}")
        linhas_texto.append(f"   Telefone: {cras.get('telefone', 'Nao informado')}")
        linhas_texto.append(f"   Horario: {cras.get('horario', 'Seg-Sex 8h-17h')}")
        linhas_texto.append("")

    linhas_texto.append("Leve os documentos e va ao CRAS mais proximo de voce!")

    return {
        "erro": False,
        "encontrados": len(cras_resultado),
        "municipio": cidade,
        "cras": resultado,
        "texto_formatado": "\n".join(linhas_texto)
    }


def buscar_cras_sync(
    cep: Optional[str] = None,
    ibge_code: Optional[str] = None,
    limite: int = 3
) -> dict:
    """Versao sincrona de buscar_cras para uso com o agente."""
    return buscar_cras(cep=cep, ibge_code=ibge_code, limite=limite)


async def buscar_cras_por_coordenadas(
    latitude: float,
    longitude: float,
    raio_metros: int = 10000,
    limite: int = 3
) -> dict:
    """
    Busca CRAS próximos usando coordenadas GPS (Google Places API).

    Args:
        latitude: Latitude do usuário
        longitude: Longitude do usuário
        raio_metros: Raio de busca em metros (padrão: 10km)
        limite: Número máximo de CRAS a retornar

    Returns:
        dict: {
            "sucesso": bool,
            "encontrados": int,
            "cras": [...],
            "texto_formatado": str
        }
    """
    from .google_places import buscar_cras_proximos

    try:
        resultado = await buscar_cras_proximos(
            latitude=latitude,
            longitude=longitude,
            raio_metros=raio_metros,
            limite=limite
        )

        if not resultado.get("sucesso") or not resultado.get("cras"):
            # Fallback para informações genéricas
            logger.info("Google Places API não encontrou CRAS, fornecendo alternativas")
            return {
                "erro": False,
                "encontrados": 0,
                "cras": [],
                "texto_formatado": _texto_fallback_cras()
            }

        cras_list = resultado.get("cras", [])

        # Formatar resultado
        cras_formatados = []
        linhas_texto = [f"Encontrei {len(cras_list)} CRAS perto de você:\n"]

        for i, cras in enumerate(cras_list, 1):
            links = cras.get("links", {})

            cras_formatados.append({
                "nome": cras["nome"],
                "endereco": cras["endereco"],
                "distancia": cras.get("distancia", ""),
                "distancia_metros": cras.get("distancia_metros", 0),
                "aberto_agora": cras.get("aberto_agora"),
                "links": links
            })

            # Texto formatado
            status_aberto = "🟢 Aberto" if cras.get("aberto_agora") else "⭕ Horário não confirmado"
            linhas_texto.append(f"{i}. **{cras['nome']}**")
            linhas_texto.append(f"   📍 {cras['endereco']}")
            linhas_texto.append(f"   📏 {cras.get('distancia', 'Distância não calculada')}")
            linhas_texto.append(f"   {status_aberto}")
            linhas_texto.append("")
            linhas_texto.append(f"   [📍 Como chegar]({links.get('direcoes', '')})")
            linhas_texto.append("")
            linhas_texto.append("-" * 30)

        linhas_texto.append("")
        linhas_texto.append("**SERVIÇOS DO CRAS:**")
        linhas_texto.append("- Cadastro Único (CadÚnico)")
        linhas_texto.append("- Bolsa Família")
        linhas_texto.append("- BPC/LOAS")
        linhas_texto.append("- Tarifa Social de Energia")
        linhas_texto.append("")
        linhas_texto.append("**DOCUMENTOS:**")
        linhas_texto.append("- CPF de todos da família")
        linhas_texto.append("- Documento com foto")
        linhas_texto.append("- Comprovante de residência")

        return {
            "erro": False,
            "encontrados": len(cras_formatados),
            "cras": cras_formatados,
            "coordenadas_busca": resultado.get("coordenadas_busca"),
            "raio_metros": raio_metros,
            "texto_formatado": "\n".join(linhas_texto)
        }

    except Exception as e:
        logger.error(f"Erro ao buscar CRAS por coordenadas: {e}")
        return {
            "erro": True,
            "erro_mensagem": str(e),
            "encontrados": 0,
            "cras": [],
            "texto_formatado": _texto_fallback_cras()
        }


def _texto_fallback_cras() -> str:
    """Texto de fallback quando não encontra CRAS por coordenadas."""
    return (
        "Não encontrei CRAS próximos na busca automática.\n\n"
        "**Para encontrar o CRAS mais perto de você:**\n\n"
        "📞 **Disque Social: 121** (gratuito)\n"
        "Funciona de segunda a sexta, das 8h às 18h\n\n"
        "🌐 **Busca online:**\n"
        "https://aplicacoes.mds.gov.br/sagi/miv/miv.php\n\n"
        "**O que fazer no CRAS:**\n"
        "- Fazer ou atualizar CadÚnico\n"
        "- Solicitar Bolsa Família\n"
        "- Iniciar pedido de BPC/LOAS\n"
        "- Solicitar Tarifa Social de Energia"
    )
