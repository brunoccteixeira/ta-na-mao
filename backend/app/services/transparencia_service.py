"""
Servico de integracao com Portal da Transparencia.

API publica e gratuita para consultar:
- Bolsa Familia / Auxilio Brasil
- BPC (Beneficio de Prestacao Continuada)
- Auxilio Gas
- Seguro Defeso

Documentacao: https://api.portaldatransparencia.gov.br/swagger-ui.html

Rate limits:
- 06h-24h: 90 req/min
- 00h-06h: 300 req/min

SEGURANCA: CPF nunca eh logado diretamente. Usa hash para logs.
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Constantes
# =============================================================================

TRANSPARENCIA_BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

_HTTP_TIMEOUT = 15.0

# Endpoints disponiveis
ENDPOINTS = {
    "bolsa_familia": "/bolsa-familia-disponivel-por-cpf-ou-nis",
    "bpc": "/bpc-por-cpf-ou-nis",
    "auxilio_emergencial": "/auxilio-emergencial-por-cpf-ou-nis",
    "seguro_defeso": "/seguro-defeso-por-cpf-ou-nis",
}


# =============================================================================
# Helpers
# =============================================================================

def _hash_cpf(cpf: str) -> str:
    """Gera hash do CPF para logs seguros."""
    return hashlib.sha256(cpf.encode()).hexdigest()[:12]


def _limpar_cpf(cpf: str) -> str:
    """Remove formatacao do CPF."""
    return "".join(c for c in cpf if c.isdigit())


def _get_api_key() -> str:
    """Retorna API key do Portal da Transparencia."""
    try:
        from app.config import settings
        return getattr(settings, "TRANSPARENCIA_API_KEY", "")
    except Exception:
        return ""


def is_transparencia_configured() -> bool:
    """Verifica se o Portal da Transparencia esta configurado."""
    return bool(_get_api_key())


def _is_horario_noturno() -> bool:
    """Verifica se estamos no horario de maior rate limit (00h-06h)."""
    hora = datetime.now().hour
    return hora < 6


# =============================================================================
# Cliente HTTP
# =============================================================================

async def _fazer_requisicao(
    endpoint: str,
    cpf: str,
    pagina: int = 1,
) -> Optional[dict[str, Any]]:
    """Faz requisicao ao Portal da Transparencia.

    Args:
        endpoint: Endpoint da API (ex: /bolsa-familia-disponivel-por-cpf-ou-nis)
        cpf: CPF para consulta (sera limpo automaticamente)
        pagina: Numero da pagina para paginacao

    Returns:
        dict com resposta da API ou None se falhou
    """
    api_key = _get_api_key()
    cpf_limpo = _limpar_cpf(cpf)
    cpf_hash = _hash_cpf(cpf_limpo)

    if not api_key:
        logger.warning("Portal da Transparencia nao configurado (TRANSPARENCIA_API_KEY vazio)")
        return None

    url = f"{TRANSPARENCIA_BASE_URL}{endpoint}"
    headers = {
        "Accept": "application/json",
        "chave-api-dados": api_key,
    }
    params = {
        "cpfNisBeneficiario": cpf_limpo,
        "pagina": pagina,
    }

    try:
        logger.info(f"Transparencia API: endpoint={endpoint}, cpf_hash={cpf_hash}")

        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            response = await client.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Transparencia API: sucesso para cpf_hash={cpf_hash}, registros={len(data) if isinstance(data, list) else 1}")
            return {"success": True, "data": data}

        if response.status_code == 429:
            logger.warning(f"Transparencia API: rate limit excedido")
            return {"success": False, "error": "rate_limit", "message": "Limite de requisicoes excedido. Tente novamente em alguns minutos."}

        if response.status_code == 404:
            logger.info(f"Transparencia API: CPF nao encontrado cpf_hash={cpf_hash}")
            return {"success": True, "data": []}  # CPF nao eh beneficiario

        logger.warning(f"Transparencia API: status={response.status_code} endpoint={endpoint}")
        return {"success": False, "error": "api_error", "message": f"Erro na API: status {response.status_code}"}

    except httpx.TimeoutException:
        logger.error(f"Transparencia API: timeout para cpf_hash={cpf_hash}")
        return {"success": False, "error": "timeout", "message": "Tempo de resposta excedido. Tente novamente."}
    except Exception as e:
        logger.error(f"Transparencia API: erro {e}")
        return {"success": False, "error": "connection_error", "message": "Erro de conexao com o Portal da Transparencia."}


# =============================================================================
# Consultas de Beneficios
# =============================================================================

async def consultar_bolsa_familia(cpf: str) -> dict[str, Any]:
    """Consulta se CPF eh beneficiario do Bolsa Familia / Auxilio Brasil.

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com:
            - beneficiario: bool
            - parcelas: lista de parcelas (se beneficiario)
            - valor_total: soma dos valores
            - ultima_parcela: dados da parcela mais recente
    """
    resultado = await _fazer_requisicao(ENDPOINTS["bolsa_familia"], cpf)

    if not resultado or not resultado.get("success"):
        return {
            "beneficiario": False,
            "erro": resultado.get("message") if resultado else "Erro na consulta",
            "programa": "Bolsa Familia / Auxilio Brasil",
        }

    data = resultado.get("data", [])

    if not data:
        return {
            "beneficiario": False,
            "programa": "Bolsa Familia / Auxilio Brasil",
            "mensagem": "CPF nao consta como beneficiario no Portal da Transparencia.",
        }

    # Processar parcelas
    parcelas = []
    for item in data:
        parcela = {
            "mes_ano": item.get("dataReferencia", ""),
            "valor": float(item.get("valor", 0)),
            "municipio": item.get("municipio", {}).get("nomeIBGE", ""),
            "uf": item.get("uf", {}).get("sigla", ""),
        }
        parcelas.append(parcela)

    # Ordenar por data mais recente
    parcelas.sort(key=lambda x: x["mes_ano"], reverse=True)

    valor_total = sum(p["valor"] for p in parcelas)

    return {
        "beneficiario": True,
        "programa": "Bolsa Familia / Auxilio Brasil",
        "parcelas": parcelas[:12],  # Ultimas 12 parcelas
        "valor_total": valor_total,
        "quantidade_parcelas": len(parcelas),
        "ultima_parcela": parcelas[0] if parcelas else None,
    }


async def consultar_bpc(cpf: str) -> dict[str, Any]:
    """Consulta se CPF eh beneficiario do BPC (idoso ou PCD).

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com dados do BPC
    """
    resultado = await _fazer_requisicao(ENDPOINTS["bpc"], cpf)

    if not resultado or not resultado.get("success"):
        return {
            "beneficiario": False,
            "erro": resultado.get("message") if resultado else "Erro na consulta",
            "programa": "BPC - Beneficio de Prestacao Continuada",
        }

    data = resultado.get("data", [])

    if not data:
        return {
            "beneficiario": False,
            "programa": "BPC - Beneficio de Prestacao Continuada",
            "mensagem": "CPF nao consta como beneficiario do BPC.",
        }

    # Processar dados
    parcelas = []
    for item in data:
        parcela = {
            "mes_ano": item.get("dataReferencia", ""),
            "valor": float(item.get("valor", 0)),
            "tipo": item.get("tipoBeneficio", ""),
            "municipio": item.get("municipio", {}).get("nomeIBGE", ""),
            "uf": item.get("uf", {}).get("sigla", ""),
        }
        parcelas.append(parcela)

    parcelas.sort(key=lambda x: x["mes_ano"], reverse=True)

    return {
        "beneficiario": True,
        "programa": "BPC - Beneficio de Prestacao Continuada",
        "tipo": parcelas[0].get("tipo", "") if parcelas else "",
        "parcelas": parcelas[:12],
        "valor_mensal": parcelas[0]["valor"] if parcelas else 0,
        "ultima_parcela": parcelas[0] if parcelas else None,
    }


async def consultar_auxilio_gas(cpf: str) -> dict[str, Any]:
    """Consulta se CPF eh beneficiario do Auxilio Gas.

    Nota: Usa o mesmo endpoint do auxilio emergencial que inclui
    diversos programas sociais.

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com dados do Auxilio Gas
    """
    resultado = await _fazer_requisicao(ENDPOINTS["auxilio_emergencial"], cpf)

    if not resultado or not resultado.get("success"):
        return {
            "beneficiario": False,
            "erro": resultado.get("message") if resultado else "Erro na consulta",
            "programa": "Auxilio Gas",
        }

    data = resultado.get("data", [])

    # Filtrar apenas Auxilio Gas
    auxilio_gas = [item for item in data if "gas" in item.get("programa", "").lower()]

    if not auxilio_gas:
        return {
            "beneficiario": False,
            "programa": "Auxilio Gas",
            "mensagem": "CPF nao consta como beneficiario do Auxilio Gas.",
        }

    parcelas = []
    for item in auxilio_gas:
        parcela = {
            "mes_ano": item.get("dataReferencia", ""),
            "valor": float(item.get("valor", 0)),
            "municipio": item.get("municipio", {}).get("nomeIBGE", ""),
            "uf": item.get("uf", {}).get("sigla", ""),
        }
        parcelas.append(parcela)

    parcelas.sort(key=lambda x: x["mes_ano"], reverse=True)

    return {
        "beneficiario": True,
        "programa": "Auxilio Gas",
        "parcelas": parcelas[:6],
        "valor_total": sum(p["valor"] for p in parcelas),
        "ultima_parcela": parcelas[0] if parcelas else None,
    }


async def consultar_seguro_defeso(cpf: str) -> dict[str, Any]:
    """Consulta se CPF eh beneficiario do Seguro Defeso (pescadores).

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com dados do Seguro Defeso
    """
    resultado = await _fazer_requisicao(ENDPOINTS["seguro_defeso"], cpf)

    if not resultado or not resultado.get("success"):
        return {
            "beneficiario": False,
            "erro": resultado.get("message") if resultado else "Erro na consulta",
            "programa": "Seguro Defeso",
        }

    data = resultado.get("data", [])

    if not data:
        return {
            "beneficiario": False,
            "programa": "Seguro Defeso",
            "mensagem": "CPF nao consta como beneficiario do Seguro Defeso.",
        }

    parcelas = []
    for item in data:
        parcela = {
            "mes_ano": item.get("dataReferencia", ""),
            "valor": float(item.get("valor", 0)),
            "municipio": item.get("municipio", {}).get("nomeIBGE", ""),
            "uf": item.get("uf", {}).get("sigla", ""),
        }
        parcelas.append(parcela)

    parcelas.sort(key=lambda x: x["mes_ano"], reverse=True)

    return {
        "beneficiario": True,
        "programa": "Seguro Defeso",
        "parcelas": parcelas[:12],
        "valor_total": sum(p["valor"] for p in parcelas),
        "ultima_parcela": parcelas[0] if parcelas else None,
    }


# =============================================================================
# Consulta Consolidada
# =============================================================================

async def consultar_todos_beneficios(cpf: str) -> dict[str, Any]:
    """Consulta todos os beneficios de um CPF em paralelo.

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com resumo de todos os beneficios:
            - beneficios_ativos: lista de programas ativos
            - detalhes: dict com detalhes de cada programa
            - total_mensal: valor total recebido por mes
    """
    cpf_limpo = _limpar_cpf(cpf)
    cpf_hash = _hash_cpf(cpf_limpo)

    logger.info(f"Consultando todos beneficios para cpf_hash={cpf_hash}")

    # Executar todas as consultas em paralelo
    resultados = await asyncio.gather(
        consultar_bolsa_familia(cpf),
        consultar_bpc(cpf),
        consultar_auxilio_gas(cpf),
        consultar_seguro_defeso(cpf),
        return_exceptions=True,
    )

    beneficios_ativos = []
    detalhes = {}
    total_mensal = 0.0

    programas = ["bolsa_familia", "bpc", "auxilio_gas", "seguro_defeso"]

    for i, resultado in enumerate(resultados):
        programa = programas[i]

        if isinstance(resultado, Exception):
            logger.error(f"Erro ao consultar {programa}: {resultado}")
            detalhes[programa] = {"erro": str(resultado)}
            continue

        detalhes[programa] = resultado

        if resultado.get("beneficiario"):
            beneficios_ativos.append({
                "programa": resultado.get("programa"),
                "valor_mensal": resultado.get("valor_mensal") or (
                    resultado.get("ultima_parcela", {}).get("valor", 0)
                ),
            })
            # Somar valor mensal
            if "valor_mensal" in resultado:
                total_mensal += resultado["valor_mensal"]
            elif resultado.get("ultima_parcela"):
                total_mensal += resultado["ultima_parcela"].get("valor", 0)

    return {
        "cpf_consultado": True,
        "beneficiario_algum_programa": len(beneficios_ativos) > 0,
        "quantidade_beneficios": len(beneficios_ativos),
        "beneficios_ativos": beneficios_ativos,
        "total_mensal_estimado": total_mensal,
        "detalhes": detalhes,
        "fonte": "Portal da Transparencia",
        "aviso": "Dados publicos. Para informacoes oficiais, consulte o CRAS ou Caixa Economica.",
    }


# =============================================================================
# Mock para Desenvolvimento
# =============================================================================

def _mock_consultar_beneficios(cpf: str) -> dict[str, Any]:
    """Mock para desenvolvimento quando API nao esta configurada."""
    cpf_limpo = _limpar_cpf(cpf)

    # CPFs de teste
    mocks = {
        "52998224725": {
            "cpf_consultado": True,
            "beneficiario_algum_programa": True,
            "quantidade_beneficios": 2,
            "beneficios_ativos": [
                {"programa": "Bolsa Familia / Auxilio Brasil", "valor_mensal": 600.0},
                {"programa": "Auxilio Gas", "valor_mensal": 104.0},
            ],
            "total_mensal_estimado": 704.0,
            "detalhes": {
                "bolsa_familia": {
                    "beneficiario": True,
                    "programa": "Bolsa Familia / Auxilio Brasil",
                    "valor_mensal": 600.0,
                },
                "auxilio_gas": {
                    "beneficiario": True,
                    "programa": "Auxilio Gas",
                    "valor_mensal": 104.0,
                },
            },
            "fonte": "Mock (TRANSPARENCIA_API_KEY nao configurado)",
        },
        "11144477735": {
            "cpf_consultado": True,
            "beneficiario_algum_programa": True,
            "quantidade_beneficios": 1,
            "beneficios_ativos": [
                {"programa": "BPC - Beneficio de Prestacao Continuada", "valor_mensal": 1412.0},
            ],
            "total_mensal_estimado": 1412.0,
            "detalhes": {
                "bpc": {
                    "beneficiario": True,
                    "programa": "BPC - Beneficio de Prestacao Continuada",
                    "tipo": "BPC Idoso",
                    "valor_mensal": 1412.0,
                },
            },
            "fonte": "Mock (TRANSPARENCIA_API_KEY nao configurado)",
        },
    }

    if cpf_limpo in mocks:
        return mocks[cpf_limpo]

    return {
        "cpf_consultado": True,
        "beneficiario_algum_programa": False,
        "quantidade_beneficios": 0,
        "beneficios_ativos": [],
        "total_mensal_estimado": 0,
        "detalhes": {},
        "fonte": "Mock (TRANSPARENCIA_API_KEY nao configurado)",
        "mensagem": "CPF nao encontrado no mock. Configure TRANSPARENCIA_API_KEY para consulta real.",
    }


async def consultar_beneficios_ou_mock(cpf: str) -> dict[str, Any]:
    """Consulta beneficios usando API real ou mock.

    Usa mock quando TRANSPARENCIA_API_KEY nao esta configurado.

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com dados dos beneficios
    """
    if not is_transparencia_configured():
        logger.info("Usando mock do Portal da Transparencia (API nao configurada)")
        return _mock_consultar_beneficios(cpf)

    return await consultar_todos_beneficios(cpf)
