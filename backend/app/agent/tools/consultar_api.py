"""Tool para consulta de benefícios via API Tá na Mão."""

import httpx
from typing import Optional


# Mapeamento de programas para nomes amigáveis
PROGRAMAS_NOMES = {
    "BOLSA_FAMILIA": "Bolsa Família",
    "BPC": "BPC/LOAS (Benefício de Prestação Continuada)",
    "FARMACIA_POPULAR": "Farmácia Popular",
    "TSEE": "Tarifa Social de Energia Elétrica",
    "DIGNIDADE_MENSTRUAL": "Dignidade Menstrual (Absorventes Grátis)",
}


async def consultar_beneficios_municipio(ibge_code: str, api_base_url: str = "http://localhost:8000") -> dict:
    """Consulta benefícios disponíveis em um município.

    Args:
        ibge_code: Código IBGE do município (7 dígitos)
        api_base_url: URL base da API Tá na Mão

    Returns:
        dict: Lista de programas com estatísticas
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Consulta dados do município
            response = await client.get(f"{api_base_url}/api/v1/municipalities/{ibge_code}/programs")
            response.raise_for_status()
            data = response.json()

        if not data.get("programs"):
            return {
                "encontrado": False,
                "ibge_code": ibge_code,
                "mensagem": "Município não encontrado ou sem dados de programas."
            }

        programas = []
        for prog in data.get("programs", []):
            nome = PROGRAMAS_NOMES.get(prog.get("program"), prog.get("program"))
            programas.append({
                "programa": nome,
                "codigo": prog.get("program"),
                "beneficiarios": prog.get("total_beneficiaries", 0),
                "familias": prog.get("total_families", 0),
                "cobertura": f"{prog.get('coverage_rate', 0) * 100:.1f}%",
                "valor_total": prog.get("total_value_brl"),
            })

        return {
            "encontrado": True,
            "municipio": data.get("municipality", {}).get("name"),
            "uf": data.get("municipality", {}).get("state"),
            "ibge_code": ibge_code,
            "programas": programas,
            "total_programas": len(programas),
            "mensagem": f"Encontrados {len(programas)} programas sociais no município."
        }

    except httpx.HTTPError as e:
        return {
            "encontrado": False,
            "ibge_code": ibge_code,
            "mensagem": f"Erro ao consultar API: {str(e)}"
        }


async def listar_programas_disponiveis(api_base_url: str = "http://localhost:8000") -> dict:
    """Lista todos os programas sociais disponíveis no sistema.

    Args:
        api_base_url: URL base da API Tá na Mão

    Returns:
        dict: Lista de programas com totais nacionais
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{api_base_url}/api/v1/programs/")
            response.raise_for_status()
            data = response.json()

        programas = []
        for prog in data:
            nome = PROGRAMAS_NOMES.get(prog.get("name"), prog.get("name"))
            programas.append({
                "programa": nome,
                "codigo": prog.get("name"),
                "descricao": prog.get("description"),
                "total_nacional_beneficiarios": prog.get("total_beneficiaries"),
                "total_nacional_familias": prog.get("total_families"),
            })

        return {
            "programas": programas,
            "total": len(programas),
            "mensagem": f"Sistema Tá na Mão possui {len(programas)} programas sociais cadastrados."
        }

    except httpx.HTTPError as e:
        return {
            "programas": [],
            "total": 0,
            "mensagem": f"Erro ao consultar programas: {str(e)}"
        }


def consultar_beneficios(
    ibge_code: Optional[str] = None,
    listar_todos: bool = False,
    api_base_url: str = "http://localhost:8000"
) -> dict:
    """Consulta benefícios sociais disponíveis.

    Esta é a função principal usada pelo agente para consultar benefícios.

    Args:
        ibge_code: Código IBGE do município (7 dígitos). Se fornecido, busca programas deste município.
        listar_todos: Se True, lista todos os programas disponíveis no sistema.
        api_base_url: URL base da API Tá na Mão.

    Returns:
        dict: Dados dos benefícios encontrados ou mensagem de erro.

    Examples:
        # Listar programas de São Paulo
        >>> consultar_beneficios(ibge_code="3550308")

        # Listar todos os programas do sistema
        >>> consultar_beneficios(listar_todos=True)
    """
    import asyncio

    if listar_todos:
        try:
            asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, listar_programas_disponiveis(api_base_url))
                return future.result()
        except RuntimeError:
            return asyncio.run(listar_programas_disponiveis(api_base_url))

    if ibge_code:
        try:
            asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, consultar_beneficios_municipio(ibge_code, api_base_url))
                return future.result()
        except RuntimeError:
            return asyncio.run(consultar_beneficios_municipio(ibge_code, api_base_url))

    return {
        "encontrado": False,
        "mensagem": "Forneça o código IBGE do município ou use listar_todos=True para ver todos os programas."
    }
