"""
Servico de painel do gestor municipal.

Dashboard analitico para secretarios de assistencia social
com metricas de cobertura, lacunas e planejamento.
"""

import logging
from typing import Optional, Dict, Any, List

from .indicadores_sociais import _DADOS_MUNICIPIOS, _MEDIAS_NACIONAIS

logger = logging.getLogger(__name__)


# CRAS recomendado: 1 para cada 2.500 familias em vulnerabilidade
_CRAS_POR_FAMILIAS = 2500
_CREAS_POR_HABITANTES = 200000


def visao_geral(municipio_ibge: str) -> Dict[str, Any]:
    """Gera visao geral do municipio para o gestor.

    Args:
        municipio_ibge: Codigo IBGE do municipio

    Returns:
        dict com KPIs e indicadores principais
    """
    dados = _DADOS_MUNICIPIOS.get(municipio_ibge)
    if not dados:
        return {"erro": f"Municipio {municipio_ibge} nao encontrado."}

    populacao = dados["populacao"]
    familias_cadunico = dados["cadunico_familias"]
    cobertura_bf = dados["bolsa_familia_cobertura_pct"]

    # Estimar equipamentos SUAS necessarios
    cras_necessarios = max(1, familias_cadunico // _CRAS_POR_FAMILIAS)
    creas_necessarios = max(1, populacao // _CREAS_POR_HABITANTES)

    return {
        "municipio": dados["nome"],
        "uf": dados["uf"],
        "ibge": municipio_ibge,
        "kpis": {
            "populacao": populacao,
            "familias_cadunico": familias_cadunico,
            "cobertura_bolsa_familia_pct": cobertura_bf,
            "idhm": dados["idhm"],
            "taxa_pobreza": dados["taxa_pobreza"],
        },
        "equipamentos_suas": {
            "cras_recomendados": cras_necessarios,
            "creas_recomendados": creas_necessarios,
            "referencia_cras": f"1 CRAS para cada {_CRAS_POR_FAMILIAS} familias CadUnico",
        },
        "alertas": _gerar_alertas_gestor(dados),
    }


def analise_lacunas(municipio_ibge: str) -> Dict[str, Any]:
    """Identifica lacunas de cobertura de beneficios.

    Args:
        municipio_ibge: Codigo IBGE do municipio

    Returns:
        dict com familias nao atendidas e valor nao acessado
    """
    dados = _DADOS_MUNICIPIOS.get(municipio_ibge)
    if not dados:
        return {"erro": f"Municipio {municipio_ibge} nao encontrado."}

    familias = dados["cadunico_familias"]
    cobertura = dados["bolsa_familia_cobertura_pct"] / 100

    familias_bf = int(familias * cobertura)
    familias_sem_bf = familias - familias_bf
    valor_nao_acessado = familias_sem_bf * 600  # Valor medio Bolsa Familia

    lacunas = []

    if cobertura < 0.80:
        lacunas.append({
            "programa": "Bolsa Familia",
            "familias_sem_acesso": familias_sem_bf,
            "valor_nao_acessado_mensal": valor_nao_acessado,
            "acao_sugerida": "Intensificar busca ativa de familias em vulnerabilidade",
        })

    if dados["saneamento_pct"] < 80:
        lacunas.append({
            "programa": "Saneamento Basico",
            "deficit_pct": 100 - dados["saneamento_pct"],
            "acao_sugerida": "Priorizar investimento em agua tratada e esgoto",
        })

    if dados["taxa_analfabetismo"] > _MEDIAS_NACIONAIS["taxa_analfabetismo"]:
        lacunas.append({
            "programa": "Educacao de Jovens e Adultos (EJA)",
            "taxa_analfabetismo": dados["taxa_analfabetismo"],
            "acao_sugerida": "Ampliar oferta de EJA em parceria com escolas",
        })

    return {
        "municipio": dados["nome"],
        "total_lacunas": len(lacunas),
        "lacunas": lacunas,
        "resumo": {
            "familias_cadunico": familias,
            "familias_com_bf": familias_bf,
            "familias_sem_bf": familias_sem_bf,
            "valor_nao_acessado_mensal": valor_nao_acessado,
        },
    }


def benchmark(municipio_ibge: str) -> Dict[str, Any]:
    """Compara municipio com similares e media nacional.

    Args:
        municipio_ibge: Codigo IBGE do municipio

    Returns:
        dict com ranking e comparativo
    """
    dados = _DADOS_MUNICIPIOS.get(municipio_ibge)
    if not dados:
        return {"erro": f"Municipio {municipio_ibge} nao encontrado."}

    # Comparar com todos os municipios disponiveis
    ranking_idhm = sorted(
        _DADOS_MUNICIPIOS.items(),
        key=lambda x: x[1]["idhm"],
        reverse=True,
    )
    posicao = next(
        (i + 1 for i, (ibge, _) in enumerate(ranking_idhm) if ibge == municipio_ibge),
        0,
    )

    return {
        "municipio": dados["nome"],
        "ranking_idhm": {
            "posicao": posicao,
            "total_comparados": len(ranking_idhm),
        },
        "vs_media_nacional": {
            "idhm": {"valor": dados["idhm"], "media": _MEDIAS_NACIONAIS["idhm"], "status": "acima" if dados["idhm"] > _MEDIAS_NACIONAIS["idhm"] else "abaixo"},
            "taxa_pobreza": {"valor": dados["taxa_pobreza"], "media": _MEDIAS_NACIONAIS["taxa_pobreza"], "status": "melhor" if dados["taxa_pobreza"] < _MEDIAS_NACIONAIS["taxa_pobreza"] else "pior"},
            "cobertura_bf": {"valor": dados["bolsa_familia_cobertura_pct"], "media": _MEDIAS_NACIONAIS["bolsa_familia_cobertura_pct"], "status": "acima" if dados["bolsa_familia_cobertura_pct"] > _MEDIAS_NACIONAIS["bolsa_familia_cobertura_pct"] else "abaixo"},
        },
    }


def consultar_dashboard_gestor(
    municipio_ibge: str,
    modulo: Optional[str] = None,
) -> Dict[str, Any]:
    """Tool wrapper para o agente consultar o painel do gestor.

    Args:
        municipio_ibge: Codigo IBGE do municipio
        modulo: Modulo especifico: visao_geral, lacunas, benchmark.
                Se nao informado, retorna visao geral.

    Returns:
        dict com dados do modulo solicitado
    """
    if modulo == "lacunas":
        return analise_lacunas(municipio_ibge)
    if modulo == "benchmark":
        return benchmark(municipio_ibge)
    return visao_geral(municipio_ibge)


def _gerar_alertas_gestor(dados: Dict) -> List[Dict[str, str]]:
    """Gera alertas automaticos para o gestor."""
    alertas = []

    if dados["bolsa_familia_cobertura_pct"] < 70:
        alertas.append({
            "tipo": "cobertura_baixa",
            "mensagem": f"Cobertura do Bolsa Familia esta em {dados['bolsa_familia_cobertura_pct']}% - abaixo dos 70% recomendados.",
            "severidade": "alta",
        })

    if dados["taxa_pobreza"] > 25:
        alertas.append({
            "tipo": "pobreza_alta",
            "mensagem": f"Taxa de pobreza de {dados['taxa_pobreza']}% - acima do critico.",
            "severidade": "alta",
        })

    if dados["saneamento_pct"] < 60:
        alertas.append({
            "tipo": "saneamento_critico",
            "mensagem": f"Apenas {dados['saneamento_pct']}% com acesso a saneamento.",
            "severidade": "alta",
        })

    return alertas
