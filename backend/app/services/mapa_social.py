"""
Servico de mapeamento social territorial.

Gera dados para visualizacao geoespacial de indicadores,
equipamentos SUAS e desertos de assistencia social.
"""

import logging
from typing import Optional, Dict, Any, List

from .indicadores_sociais import _DADOS_MUNICIPIOS

logger = logging.getLogger(__name__)


# =============================================================================
# Camadas do mapa
# =============================================================================

CAMADAS_MAPA = {
    "indicadores": [
        {"id": "idh_m", "nome": "IDH Municipal", "fonte": "IPEA", "tipo": "choropleth"},
        {"id": "taxa_pobreza", "nome": "Taxa de Pobreza", "fonte": "IBGE", "tipo": "choropleth"},
        {"id": "cobertura_bf", "nome": "Cobertura Bolsa Familia", "fonte": "MDS", "tipo": "choropleth"},
        {"id": "cobertura_cadunico", "nome": "Cobertura CadUnico", "fonte": "MDS", "tipo": "choropleth"},
        {"id": "gini", "nome": "Desigualdade (Gini)", "fonte": "IPEA", "tipo": "choropleth"},
        {"id": "saneamento", "nome": "Acesso a Saneamento", "fonte": "IBGE", "tipo": "choropleth"},
    ],
    "equipamentos": [
        {"id": "cras", "nome": "CRAS", "tipo": "pontos"},
        {"id": "creas", "nome": "CREAS", "tipo": "pontos"},
        {"id": "caps", "nome": "CAPS", "tipo": "pontos"},
        {"id": "centro_pop", "nome": "Centro POP", "tipo": "pontos"},
        {"id": "farmacia_popular", "nome": "Farmacia Popular", "tipo": "pontos"},
        {"id": "ubs", "nome": "UBS", "tipo": "pontos"},
    ],
    "analise": [
        {"id": "deserto_social", "nome": "Desertos de Assistencia", "tipo": "heatmap"},
        {"id": "vulnerabilidade", "nome": "Score de Vulnerabilidade", "tipo": "heatmap"},
    ],
}

# Classificacao de desertos sociais
CLASSIFICACAO_DESERTO = {
    "SEM_COBERTURA": {"descricao": "Sem CRAS no municipio", "cor": "#d73027", "severidade": 4},
    "CRITICO": {"descricao": "Mais de 5000 familias por CRAS", "cor": "#f46d43", "severidade": 3},
    "INSUFICIENTE": {"descricao": "Mais de 3500 familias por CRAS", "cor": "#fdae61", "severidade": 2},
    "ADEQUADO": {"descricao": "Ate 2500 familias por CRAS", "cor": "#1a9850", "severidade": 1},
}


def listar_camadas() -> Dict[str, Any]:
    """Lista camadas disponiveis para o mapa social.

    Returns:
        dict com camadas organizadas por tipo
    """
    return {
        "camadas": CAMADAS_MAPA,
        "total": sum(len(v) for v in CAMADAS_MAPA.values()),
        "mensagem": "Escolha uma camada para visualizar no mapa.",
    }


def consultar_mapa_social(
    camada: str,
    uf: Optional[str] = None,
    municipio_ibge: Optional[str] = None,
) -> Dict[str, Any]:
    """Consulta dados de uma camada do mapa social.

    Args:
        camada: ID da camada (idh_m, taxa_pobreza, cras, deserto_social, etc)
        uf: Filtrar por estado
        municipio_ibge: Filtrar por municipio

    Returns:
        dict com dados geoespaciais da camada
    """
    logger.info(f"Consultando mapa social: camada={camada}, uf={uf}")

    # Camadas de indicadores
    indicador_map = {
        "idh_m": "idhm",
        "taxa_pobreza": "taxa_pobreza",
        "cobertura_bf": "bolsa_familia_cobertura_pct",
        "gini": "gini",
        "saneamento": "saneamento_pct",
    }

    if camada in indicador_map:
        return _gerar_choropleth(camada, indicador_map[camada], uf)

    if camada == "deserto_social":
        return identificar_desertos(uf)

    if camada in ("cras", "creas", "caps", "centro_pop", "farmacia_popular", "ubs"):
        return _gerar_pontos_equipamento(camada, uf, municipio_ibge)

    return {
        "erro": f"Camada '{camada}' nao reconhecida.",
        "camadas_disponiveis": CAMADAS_MAPA,
    }


def identificar_desertos(uf: Optional[str] = None) -> Dict[str, Any]:
    """Identifica desertos de assistencia social.

    Deserto social: municipio com ratio familias/CRAS acima do recomendado.

    Args:
        uf: Filtrar por estado

    Returns:
        dict com classificacao de desertos por municipio
    """
    desertos = []

    for ibge, dados in _DADOS_MUNICIPIOS.items():
        if uf and dados["uf"] != uf:
            continue

        familias = dados["cadunico_familias"]
        # Estimar CRAS existentes (mock: 1 para cada 3000 familias)
        cras_estimados = max(1, familias // 3000)
        ratio = familias / cras_estimados

        if ratio > 5000:
            classificacao = "CRITICO"
        elif ratio > 3500:
            classificacao = "INSUFICIENTE"
        elif ratio > 2500:
            classificacao = "INSUFICIENTE"
        else:
            classificacao = "ADEQUADO"

        desertos.append({
            "municipio_ibge": ibge,
            "municipio": dados["nome"],
            "uf": dados["uf"],
            "familias_cadunico": familias,
            "cras_estimados": cras_estimados,
            "ratio_familias_cras": round(ratio),
            "classificacao": classificacao,
            "cor": CLASSIFICACAO_DESERTO[classificacao]["cor"],
        })

    # Ordenar por severidade (pior primeiro)
    severidade = {k: v["severidade"] for k, v in CLASSIFICACAO_DESERTO.items()}
    desertos.sort(key=lambda d: severidade.get(d["classificacao"], 0), reverse=True)

    criticos = sum(1 for d in desertos if d["classificacao"] in ("CRITICO", "SEM_COBERTURA"))

    return {
        "total_municipios": len(desertos),
        "criticos": criticos,
        "desertos": desertos,
        "classificacoes": CLASSIFICACAO_DESERTO,
        "mensagem": (
            f"{criticos} municipio(s) em situacao critica de cobertura SUAS."
            if criticos > 0
            else "Todos os municipios com cobertura adequada!"
        ),
    }


def _gerar_choropleth(camada: str, campo: str, uf: Optional[str]) -> Dict[str, Any]:
    """Gera dados para mapa choropleth."""
    dados = []
    for ibge, mun in _DADOS_MUNICIPIOS.items():
        if uf and mun["uf"] != uf:
            continue
        dados.append({
            "municipio_ibge": ibge,
            "municipio": mun["nome"],
            "uf": mun["uf"],
            "valor": mun.get(campo, 0),
        })

    return {
        "camada": camada,
        "tipo": "choropleth",
        "dados": dados,
        "total": len(dados),
    }


def _gerar_pontos_equipamento(
    tipo: str,
    uf: Optional[str],
    municipio_ibge: Optional[str],
) -> Dict[str, Any]:
    """Gera pontos de equipamentos para o mapa (dados mock)."""
    # Em producao: consulta banco com coordenadas reais
    pontos = []
    for ibge, mun in _DADOS_MUNICIPIOS.items():
        if uf and mun["uf"] != uf:
            continue
        if municipio_ibge and ibge != municipio_ibge:
            continue

        # Mock: gerar pontos estimados
        qtd = max(1, mun["cadunico_familias"] // 3000) if tipo == "cras" else max(1, mun["populacao"] // 200000)
        for i in range(qtd):
            pontos.append({
                "tipo": tipo.upper(),
                "municipio_ibge": ibge,
                "municipio": mun["nome"],
                "uf": mun["uf"],
                "id": f"{tipo}_{ibge}_{i+1}",
            })

    return {
        "camada": tipo,
        "tipo": "pontos",
        "pontos": pontos,
        "total": len(pontos),
    }
