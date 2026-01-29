"""Tool para busca de endereço por CEP via MCP Brasil API ou ViaCEP."""

import re
import logging
import httpx

from app.agent.mcp import mcp_manager, BrasilAPIMCP

logger = logging.getLogger(__name__)


async def _buscar_cep_mcp(cep_limpo: str) -> dict | None:
    """Tenta buscar CEP via MCP Brasil API.

    Args:
        cep_limpo: CEP com 8 dígitos (sem formatação)

    Returns:
        dict com dados do endereço ou None se falhar
    """
    try:
        wrapper = mcp_manager.get_wrapper("brasil-api")
        if not wrapper or not isinstance(wrapper, BrasilAPIMCP):
            logger.debug("brasil-api MCP not available")
            return None

        resultado = await wrapper.buscar_cep(cep_limpo)
        if not resultado:
            return None

        # Converte EnderecoResult para formato esperado
        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"

        return {
            "encontrado": True,
            "cep": cep_formatado,
            "logradouro": resultado.logradouro,
            "complemento": resultado.complemento,
            "bairro": resultado.bairro,
            "cidade": resultado.cidade,
            "uf": resultado.estado,
            "ibge": resultado.ibge,
            "endereco_completo": f"{resultado.logradouro}, {resultado.bairro} - {resultado.cidade}/{resultado.estado}",
            "mensagem": "Endereço encontrado!",
            "fonte": "brasil-api-mcp"
        }

    except Exception as e:
        logger.warning(f"MCP buscar_cep failed: {e}")
        return None


async def _buscar_cep_viacep(cep_limpo: str) -> dict:
    """Fallback para ViaCEP quando MCP não disponível.

    Args:
        cep_limpo: CEP com 8 dígitos (sem formatação)

    Returns:
        dict com dados do endereço ou mensagem de erro
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            response.raise_for_status()
            data = response.json()

        # ViaCEP retorna {"erro": true} quando CEP não existe
        if data.get("erro"):
            return {
                "encontrado": False,
                "cep": cep_limpo,
                "mensagem": "CEP não encontrado. Verifique se está correto."
            }

        # Formata CEP com traço
        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"

        return {
            "encontrado": True,
            "cep": cep_formatado,
            "logradouro": data.get("logradouro", ""),
            "complemento": data.get("complemento", ""),
            "bairro": data.get("bairro", ""),
            "cidade": data.get("localidade", ""),
            "uf": data.get("uf", ""),
            "ibge": data.get("ibge", ""),
            "endereco_completo": f"{data.get('logradouro', '')}, {data.get('bairro', '')} - {data.get('localidade', '')}/{data.get('uf', '')}",
            "mensagem": "Endereço encontrado!",
            "fonte": "viacep"
        }

    except httpx.TimeoutException:
        return {
            "encontrado": False,
            "cep": cep_limpo,
            "mensagem": "Tempo esgotado ao consultar o CEP. Tente novamente."
        }
    except httpx.HTTPError as e:
        return {
            "encontrado": False,
            "cep": cep_limpo,
            "mensagem": f"Erro ao consultar CEP: {str(e)}"
        }


async def buscar_cep(cep: str) -> dict:
    """Busca endereço completo pelo CEP.

    Usa MCP Brasil API como fonte primária, com fallback para ViaCEP.

    Args:
        cep: CEP com 8 dígitos (pode conter traço)

    Returns:
        dict: Dados do endereço ou mensagem de erro
    """
    # Remove caracteres não numéricos
    cep_limpo = re.sub(r'\D', '', cep)

    # Valida formato
    if len(cep_limpo) != 8:
        return {
            "encontrado": False,
            "mensagem": f"CEP deve ter 8 dígitos. Você informou {len(cep_limpo)} dígitos."
        }

    # Tenta MCP primeiro
    resultado = await _buscar_cep_mcp(cep_limpo)
    if resultado:
        logger.debug(f"CEP {cep_limpo} found via MCP")
        return resultado

    # Fallback para ViaCEP
    logger.debug(f"Falling back to ViaCEP for {cep_limpo}")
    return await _buscar_cep_viacep(cep_limpo)


def buscar_cep_sync(cep: str) -> dict:
    """Versão síncrona para uso com Google ADK.

    Args:
        cep: CEP com 8 dígitos (pode conter traço)

    Returns:
        dict: Dados do endereço ou mensagem de erro
    """
    import asyncio

    # Se já existe um loop rodando, usa run_in_executor
    try:
        asyncio.get_running_loop()
        # Estamos dentro de um loop async - não podemos usar asyncio.run
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, buscar_cep(cep))
            return future.result()
    except RuntimeError:
        # Não há loop rodando - podemos usar asyncio.run
        return asyncio.run(buscar_cep(cep))
