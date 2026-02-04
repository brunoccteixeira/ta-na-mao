"""
Servico de indicadores sociais.

Consome APIs do IBGE, IPEA e SAGI/MDS para fornecer
indicadores sociais por territorio.
"""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


# =============================================================================
# Indicadores IBGE (SIDRA)
# =============================================================================

INDICADORES_IBGE = {
    "populacao": {"tabela": 4714, "descricao": "Populacao estimada"},
    "renda_per_capita": {"tabela": 6579, "descricao": "Rendimento medio mensal per capita"},
    "taxa_analfabetismo": {"tabela": 3540, "descricao": "Taxa de analfabetismo (15+ anos)"},
    "saneamento": {"tabela": 6445, "descricao": "Acesso a esgoto e agua tratada"},
    "piramide_etaria": {"tabela": 9514, "descricao": "Distribuicao por faixa etaria"},
    "tipo_domicilio": {"tabela": 6373, "descricao": "Tipo de domicilio (proprio, alugado, etc)"},
}

INDICADORES_IPEA = {
    "IDHM": {"nome": "IDH Municipal", "descricao": "Indice de Desenvolvimento Humano Municipal"},
    "GINI": {"nome": "Indice de Gini", "descricao": "Desigualdade de renda (0=igual, 1=desigual)"},
    "IVS": {"nome": "Indice de Vulnerabilidade Social", "descricao": "Vulnerabilidade em 3 dimensoes"},
    "TXPOB": {"nome": "Taxa de Pobreza", "descricao": "Percentual da populacao abaixo da linha de pobreza"},
}


# =============================================================================
# Dados mock por municipio
# =============================================================================

_DADOS_MUNICIPIOS = {
    "3550308": {
        "nome": "Sao Paulo", "uf": "SP",
        "populacao": 12396372, "renda_per_capita": 2043.0,
        "taxa_analfabetismo": 2.1, "idhm": 0.805, "gini": 0.6153,
        "ivs": 0.252, "taxa_pobreza": 8.4, "saneamento_pct": 92.0,
        "cadunico_familias": 1200000, "bolsa_familia_cobertura_pct": 72.0,
    },
    "3304557": {
        "nome": "Rio de Janeiro", "uf": "RJ",
        "populacao": 6775561, "renda_per_capita": 1816.0,
        "taxa_analfabetismo": 2.5, "idhm": 0.799, "gini": 0.6391,
        "ivs": 0.289, "taxa_pobreza": 12.1, "saneamento_pct": 85.0,
        "cadunico_familias": 850000, "bolsa_familia_cobertura_pct": 68.0,
    },
    "2927408": {
        "nome": "Salvador", "uf": "BA",
        "populacao": 2900319, "renda_per_capita": 1112.0,
        "taxa_analfabetismo": 4.8, "idhm": 0.759, "gini": 0.6310,
        "ivs": 0.357, "taxa_pobreza": 22.5, "saneamento_pct": 72.0,
        "cadunico_familias": 520000, "bolsa_familia_cobertura_pct": 85.0,
    },
    "5300108": {
        "nome": "Brasilia", "uf": "DF",
        "populacao": 3094325, "renda_per_capita": 2918.0,
        "taxa_analfabetismo": 2.0, "idhm": 0.824, "gini": 0.6318,
        "ivs": 0.225, "taxa_pobreza": 6.2, "saneamento_pct": 95.0,
        "cadunico_familias": 280000, "bolsa_familia_cobertura_pct": 60.0,
    },
    "1302603": {
        "nome": "Manaus", "uf": "AM",
        "populacao": 2255903, "renda_per_capita": 845.0,
        "taxa_analfabetismo": 5.3, "idhm": 0.737, "gini": 0.5880,
        "ivs": 0.395, "taxa_pobreza": 28.7, "saneamento_pct": 48.0,
        "cadunico_familias": 380000, "bolsa_familia_cobertura_pct": 90.0,
    },
}

# Medias nacionais para comparacao
_MEDIAS_NACIONAIS = {
    "renda_per_capita": 1380.0,
    "taxa_analfabetismo": 5.6,
    "idhm": 0.765,
    "gini": 0.524,
    "taxa_pobreza": 18.6,
    "saneamento_pct": 78.0,
    "bolsa_familia_cobertura_pct": 76.0,
}


def consultar_indicadores(
    municipio_ibge: Optional[str] = None,
    indicador: Optional[str] = None,
) -> Dict[str, Any]:
    """Consulta indicadores sociais de um municipio.

    Args:
        municipio_ibge: Codigo IBGE do municipio (7 digitos)
        indicador: Indicador especifico (populacao, idhm, gini, etc)

    Returns:
        dict com indicadores e interpretacoes em linguagem simples
    """
    logger.info(f"Consultando indicadores: municipio={municipio_ibge}, indicador={indicador}")

    if not municipio_ibge:
        return {
            "indicadores_disponiveis": {
                "ibge": INDICADORES_IBGE,
                "ipea": INDICADORES_IPEA,
            },
            "mensagem": "Informe o codigo IBGE do municipio para consultar indicadores.",
        }

    dados = _DADOS_MUNICIPIOS.get(municipio_ibge)
    if not dados:
        return {
            "erro": f"Municipio {municipio_ibge} nao encontrado.",
            "dica": "Use buscar_cep para obter o codigo IBGE do municipio.",
        }

    if indicador:
        return _detalhar_indicador(dados, indicador)

    # Painel completo
    return _gerar_painel(dados, municipio_ibge)


def comparar_municipios(lista_ibge: List[str]) -> Dict[str, Any]:
    """Compara indicadores entre municipios.

    Args:
        lista_ibge: Lista de codigos IBGE (2-5 municipios)

    Returns:
        dict com comparativo entre municipios
    """
    if len(lista_ibge) < 2:
        return {"erro": "Informe pelo menos 2 municipios para comparar."}

    comparativo = []
    for ibge in lista_ibge[:5]:
        dados = _DADOS_MUNICIPIOS.get(ibge)
        if dados:
            comparativo.append({
                "municipio": dados["nome"],
                "uf": dados["uf"],
                "ibge": ibge,
                "populacao": dados["populacao"],
                "idhm": dados["idhm"],
                "gini": dados["gini"],
                "taxa_pobreza": dados["taxa_pobreza"],
                "renda_per_capita": dados["renda_per_capita"],
            })

    return {
        "comparativo": comparativo,
        "total": len(comparativo),
        "media_nacional": {
            "idhm": _MEDIAS_NACIONAIS["idhm"],
            "gini": _MEDIAS_NACIONAIS["gini"],
            "taxa_pobreza": _MEDIAS_NACIONAIS["taxa_pobreza"],
        },
    }


def _gerar_painel(dados: Dict, ibge: str) -> Dict[str, Any]:
    """Gera painel completo de indicadores."""
    return {
        "municipio": dados["nome"],
        "uf": dados["uf"],
        "ibge": ibge,
        "indicadores": {
            "populacao": dados["populacao"],
            "renda_per_capita": dados["renda_per_capita"],
            "taxa_analfabetismo": dados["taxa_analfabetismo"],
            "idhm": dados["idhm"],
            "gini": dados["gini"],
            "ivs": dados["ivs"],
            "taxa_pobreza": dados["taxa_pobreza"],
            "saneamento_pct": dados["saneamento_pct"],
        },
        "protecao_social": {
            "cadunico_familias": dados["cadunico_familias"],
            "bolsa_familia_cobertura_pct": dados["bolsa_familia_cobertura_pct"],
        },
        "interpretacoes": {
            "idhm": _interpretar_idh(dados["idhm"]),
            "gini": _interpretar_gini(dados["gini"]),
            "taxa_pobreza": _interpretar_pobreza(dados["taxa_pobreza"]),
        },
        "comparacao_nacional": {
            "renda_vs_media": "acima" if dados["renda_per_capita"] > _MEDIAS_NACIONAIS["renda_per_capita"] else "abaixo",
            "idhm_vs_media": "acima" if dados["idhm"] > _MEDIAS_NACIONAIS["idhm"] else "abaixo",
            "pobreza_vs_media": "acima" if dados["taxa_pobreza"] > _MEDIAS_NACIONAIS["taxa_pobreza"] else "abaixo",
        },
    }


def _detalhar_indicador(dados: Dict, indicador: str) -> Dict[str, Any]:
    """Detalha um indicador especifico."""
    mapa = {
        "populacao": ("populacao", "pessoas"),
        "renda": ("renda_per_capita", "R$/mes"),
        "renda_per_capita": ("renda_per_capita", "R$/mes"),
        "analfabetismo": ("taxa_analfabetismo", "%"),
        "idhm": ("idhm", "indice 0-1"),
        "idh": ("idhm", "indice 0-1"),
        "gini": ("gini", "indice 0-1"),
        "pobreza": ("taxa_pobreza", "%"),
        "saneamento": ("saneamento_pct", "%"),
    }

    chave_info = mapa.get(indicador.lower())
    if not chave_info:
        return {"erro": f"Indicador '{indicador}' nao reconhecido.", "disponiveis": list(mapa.keys())}

    chave, unidade = chave_info
    valor = dados.get(chave)
    media = _MEDIAS_NACIONAIS.get(chave)

    resultado = {
        "municipio": dados["nome"],
        "indicador": indicador,
        "valor": valor,
        "unidade": unidade,
    }

    if media is not None:
        resultado["media_nacional"] = media
        resultado["comparacao"] = "acima da media" if valor > media else "abaixo da media"

    return resultado


def _interpretar_idh(valor: float) -> str:
    if valor >= 0.8:
        return "Muito alto - entre os melhores do pais"
    if valor >= 0.7:
        return "Alto - acima da media nacional"
    if valor >= 0.6:
        return "Medio - precisa melhorar em educacao e renda"
    return "Baixo - situacao preocupante, investimentos urgentes necessarios"


def _interpretar_gini(valor: float) -> str:
    if valor <= 0.4:
        return "Desigualdade baixa"
    if valor <= 0.5:
        return "Desigualdade moderada"
    if valor <= 0.6:
        return "Desigualdade alta - diferenca grande entre ricos e pobres"
    return "Desigualdade muito alta - urgente redistribuir renda"


def _interpretar_pobreza(valor: float) -> str:
    if valor <= 5:
        return "Taxa baixa de pobreza"
    if valor <= 15:
        return "Taxa moderada - acoes de inclusao necessarias"
    if valor <= 30:
        return "Taxa alta - muitas familias precisando de ajuda"
    return "Taxa muito alta - situacao critica"
