"""
Servico de monitoramento de legislacao.

Monitora mudancas legislativas que afetam beneficios sociais catalogados:
- Diario Oficial da Uniao (DOU)
- Camara dos Deputados API
- Senado Federal API

Analisa impacto com IA e gera alertas em linguagem simples.
"""

import logging
import re
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from enum import Enum

import httpx

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 30.0


# =============================================================================
# Enums e tipos
# =============================================================================

class Severidade(str, Enum):
    ALTA = "alta"       # Mudanca direta em regras de beneficio
    MEDIA = "media"     # Mudanca indireta ou administrativa
    BAIXA = "baixa"     # Informativa, sem impacto direto


class TipoPublicacao(str, Enum):
    LEI = "lei"
    DECRETO = "decreto"
    MEDIDA_PROVISORIA = "medida_provisoria"
    PORTARIA = "portaria"
    RESOLUCAO = "resolucao"
    INSTRUCAO_NORMATIVA = "instrucao_normativa"
    OUTRO = "outro"


# =============================================================================
# Keywords monitoradas
# =============================================================================

KEYWORDS_MONITORADAS = [
    "bolsa familia", "bolsa família",
    "bpc", "loas", "beneficio de prestacao continuada",
    "cadastro unico", "cadastro único", "cadunico", "cadúnico",
    "assistencia social", "assistência social",
    "renda", "transferencia de renda", "transferência de renda",
    "farmacia popular", "farmácia popular",
    "tarifa social", "energia eletrica",
    "seguro defeso", "seguro-defeso",
    "garantia safra", "garantia-safra",
    "salario minimo", "salário mínimo",
    "auxilio gas", "auxílio gás",
    "dignidade menstrual",
    "pis", "pasep", "fgts", "seguro-desemprego",
    "direitos trabalhistas", "clt",
    "aposentadoria", "inss", "previdencia",
]

# Beneficios afetados por keyword
BENEFICIOS_POR_KEYWORD = {
    "bolsa familia": ["BOLSA_FAMILIA"],
    "bolsa família": ["BOLSA_FAMILIA"],
    "bpc": ["BPC"],
    "loas": ["BPC"],
    "cadastro unico": ["CADUNICO", "BOLSA_FAMILIA", "BPC", "TSEE"],
    "cadastro único": ["CADUNICO", "BOLSA_FAMILIA", "BPC", "TSEE"],
    "cadunico": ["CADUNICO"],
    "farmacia popular": ["FARMACIA_POPULAR"],
    "farmácia popular": ["FARMACIA_POPULAR"],
    "tarifa social": ["TSEE"],
    "seguro defeso": ["SEGURO_DEFESO"],
    "garantia safra": ["GARANTIA_SAFRA"],
    "salario minimo": ["BPC", "SEGURO_DESEMPREGO"],
    "salário mínimo": ["BPC", "SEGURO_DESEMPREGO"],
    "auxilio gas": ["AUXILIO_GAS"],
    "dignidade menstrual": ["DIGNIDADE_MENSTRUAL"],
    "pis": ["PIS_PASEP"],
    "pasep": ["PIS_PASEP"],
    "fgts": ["FGTS"],
    "seguro-desemprego": ["SEGURO_DESEMPREGO"],
}


# =============================================================================
# Scraping do DOU
# =============================================================================

def monitorar_dou(data: Optional[str] = None) -> Dict[str, Any]:
    """Monitora o Diario Oficial da Uniao em busca de publicacoes relevantes.

    Args:
        data: Data no formato YYYY-MM-DD. Se nao informada, usa hoje.

    Returns:
        dict com publicacoes encontradas e analise de impacto
    """
    if data is None:
        data = date.today().isoformat()

    logger.info(f"Monitorando DOU para data={data}")

    try:
        # API publica do DOU (IMPRENSA NACIONAL)
        url = f"https://www.in.gov.br/leiturajornal?data={data}&secao=do1"

        with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
            response = client.get(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "TaNaMao-Monitor/1.0",
                },
            )

        if response.status_code != 200:
            logger.warning(f"DOU: status={response.status_code} para data={data}")
            return _fallback_resultado(data, "DOU indisponivel")

        # Tentar parsear JSON (a API pode retornar HTML)
        try:
            publicacoes = response.json()
        except Exception:
            # Se retornou HTML, fazer scraping basico
            return _scrape_dou_html(response.text, data)

        return _processar_publicacoes(publicacoes, data)

    except httpx.TimeoutException:
        logger.warning(f"DOU: timeout para data={data}")
        return _fallback_resultado(data, "Timeout ao acessar DOU")
    except httpx.ConnectError:
        logger.error("DOU: erro de conexao")
        return _fallback_resultado(data, "Erro de conexao com DOU")
    except Exception as e:
        logger.error(f"DOU: erro inesperado: {e}")
        return _fallback_resultado(data, str(e))


def _scrape_dou_html(html: str, data: str) -> Dict[str, Any]:
    """Extrai publicacoes relevantes do HTML do DOU."""
    publicacoes_relevantes = []

    # Buscar por keywords no HTML
    html_lower = html.lower()
    keywords_encontradas = set()

    for keyword in KEYWORDS_MONITORADAS:
        if keyword.lower() in html_lower:
            keywords_encontradas.add(keyword)

    if keywords_encontradas:
        publicacoes_relevantes.append({
            "tipo": "deteccao_keywords",
            "data": data,
            "keywords_encontradas": list(keywords_encontradas),
            "mensagem": (
                f"Encontradas {len(keywords_encontradas)} keywords relevantes no DOU de {data}. "
                "Analise detalhada requer acesso a API completa."
            ),
        })

    return {
        "data": data,
        "fonte": "DOU (scraping HTML)",
        "total_publicacoes_analisadas": 0,
        "publicacoes_relevantes": publicacoes_relevantes,
        "keywords_monitoradas": len(KEYWORDS_MONITORADAS),
        "keywords_encontradas": list(keywords_encontradas),
    }


def _processar_publicacoes(
    publicacoes: Any,
    data: str,
) -> Dict[str, Any]:
    """Processa lista de publicacoes do DOU e filtra relevantes."""
    if not isinstance(publicacoes, list):
        # Tentar extrair lista de diferentes formatos de resposta
        if isinstance(publicacoes, dict):
            publicacoes = publicacoes.get("jsonArray", publicacoes.get("items", []))

    relevantes = []
    for pub in publicacoes:
        titulo = str(pub.get("title", pub.get("titulo", ""))).lower()
        ementa = str(pub.get("abstract", pub.get("ementa", ""))).lower()
        texto = titulo + " " + ementa

        keywords_match = [k for k in KEYWORDS_MONITORADAS if k.lower() in texto]

        if keywords_match:
            # Determinar beneficios afetados
            beneficios = set()
            for kw in keywords_match:
                beneficios.update(BENEFICIOS_POR_KEYWORD.get(kw, []))

            relevantes.append({
                "titulo": pub.get("title", pub.get("titulo", "")),
                "ementa": pub.get("abstract", pub.get("ementa", "")),
                "orgao": pub.get("pubName", pub.get("orgao", "")),
                "secao": pub.get("section", pub.get("secao", "")),
                "tipo": _classificar_tipo(
                    pub.get("title", pub.get("titulo", ""))
                ).value,
                "url": pub.get("url", pub.get("urlTitle", "")),
                "keywords_detectadas": keywords_match,
                "beneficios_afetados": list(beneficios),
                "severidade": _estimar_severidade(keywords_match, titulo).value,
            })

    return {
        "data": data,
        "fonte": "DOU (API)",
        "total_publicacoes_analisadas": len(publicacoes) if isinstance(publicacoes, list) else 0,
        "publicacoes_relevantes": relevantes,
        "total_relevantes": len(relevantes),
        "keywords_monitoradas": len(KEYWORDS_MONITORADAS),
    }


# =============================================================================
# Monitoramento da Camara dos Deputados
# =============================================================================

def monitorar_projetos_lei(
    tema: str = "assistencia social",
    data_inicio: Optional[str] = None,
) -> Dict[str, Any]:
    """Monitora projetos de lei na Camara dos Deputados.

    Args:
        tema: Tema para buscar (ex: "assistencia social", "trabalho")
        data_inicio: Data de inicio no formato YYYY-MM-DD

    Returns:
        dict com projetos de lei relevantes
    """
    logger.info(f"Monitorando projetos de lei: tema={tema}")

    if data_inicio is None:
        # Ultimos 30 dias
        data_inicio = (datetime.now() - __import__("datetime").timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        url = "https://dadosabertos.camara.leg.br/api/v2/proposicoes"
        params = {
            "siglaTipo": "PL,PLP,MPV,PEC",
            "dataInicio": data_inicio,
            "keywords": tema,
            "ordem": "DESC",
            "ordenarPor": "id",
            "itens": 20,
        }

        with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
            response = client.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
            )

        if response.status_code != 200:
            logger.warning(f"Camara API: status={response.status_code}")
            return {
                "fonte": "Camara dos Deputados",
                "tema": tema,
                "projetos": [],
                "erro": f"API indisponivel (status {response.status_code})",
            }

        data = response.json()
        projetos = data.get("dados", [])

        relevantes = []
        for proj in projetos:
            ementa = str(proj.get("ementa", "")).lower()
            keywords_match = [k for k in KEYWORDS_MONITORADAS if k.lower() in ementa]

            relevantes.append({
                "tipo": proj.get("siglaTipo", ""),
                "numero": proj.get("numero", ""),
                "ano": proj.get("ano", ""),
                "ementa": proj.get("ementa", ""),
                "data_apresentacao": proj.get("dataApresentacao", ""),
                "url": proj.get("uri", ""),
                "keywords_detectadas": keywords_match,
                "relevancia": "alta" if keywords_match else "normal",
            })

        return {
            "fonte": "Camara dos Deputados",
            "tema": tema,
            "data_inicio": data_inicio,
            "total_projetos": len(projetos),
            "projetos": relevantes,
        }

    except Exception as e:
        logger.error(f"Camara API: erro {e}")
        return {
            "fonte": "Camara dos Deputados",
            "tema": tema,
            "projetos": [],
            "erro": str(e),
        }


# =============================================================================
# Analise de impacto
# =============================================================================

def analisar_impacto(publicacao: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa impacto de uma publicacao nos beneficios catalogados.

    Gera resumo em linguagem simples (5a serie).

    Args:
        publicacao: dict com dados da publicacao (titulo, ementa, etc)

    Returns:
        dict com analise de impacto formatada
    """
    titulo = publicacao.get("titulo", "")
    ementa = publicacao.get("ementa", "")
    tipo = publicacao.get("tipo", "outro")
    keywords = publicacao.get("keywords_detectadas", [])
    beneficios = publicacao.get("beneficios_afetados", [])

    # Estimar severidade
    severidade = _estimar_severidade(keywords, titulo.lower())

    # Gerar resumo simples
    resumo = _gerar_resumo_simples(titulo, ementa, beneficios)

    # Determinar quem eh afetado
    publico_afetado = _determinar_publico(beneficios)

    return {
        "titulo_original": titulo,
        "tipo": tipo,
        "severidade": severidade.value,
        "beneficios_afetados": beneficios,
        "resumo_simples": resumo,
        "publico_afetado": publico_afetado,
        "acao_recomendada": _recomendar_acao(severidade, beneficios),
        "data_analise": datetime.now().isoformat(),
    }


def _estimar_severidade(keywords: list, titulo: str) -> Severidade:
    """Estima severidade baseada nas keywords e titulo."""
    titulo_lower = titulo.lower()

    # Alta: mudanca direta em regras
    alta_indicadores = [
        "medida provisoria", "medida provisória",
        "decreto", "altera", "revoga",
        "novo valor", "reajuste", "suspensao",
    ]
    if any(ind in titulo_lower for ind in alta_indicadores):
        return Severidade.ALTA

    # Alta: keywords criticas
    keywords_criticas = {"bolsa familia", "bolsa família", "bpc", "salario minimo", "salário mínimo"}
    if keywords_criticas & set(k.lower() for k in keywords):
        return Severidade.ALTA

    # Media: mudancas administrativas
    media_indicadores = ["portaria", "resolucao", "instrucao normativa", "prazo"]
    if any(ind in titulo_lower for ind in media_indicadores):
        return Severidade.MEDIA

    return Severidade.BAIXA


def _classificar_tipo(titulo: str) -> TipoPublicacao:
    """Classifica tipo de publicacao pelo titulo."""
    titulo_lower = titulo.lower()

    mapeamento = [
        ("medida provisoria", TipoPublicacao.MEDIDA_PROVISORIA),
        ("medida provisória", TipoPublicacao.MEDIDA_PROVISORIA),
        ("decreto", TipoPublicacao.DECRETO),
        ("lei no", TipoPublicacao.LEI),
        ("lei nº", TipoPublicacao.LEI),
        ("portaria", TipoPublicacao.PORTARIA),
        ("resolucao", TipoPublicacao.RESOLUCAO),
        ("resolução", TipoPublicacao.RESOLUCAO),
        ("instrucao normativa", TipoPublicacao.INSTRUCAO_NORMATIVA),
        ("instrução normativa", TipoPublicacao.INSTRUCAO_NORMATIVA),
    ]

    for texto, tipo in mapeamento:
        if texto in titulo_lower:
            return tipo

    return TipoPublicacao.OUTRO


def _gerar_resumo_simples(
    titulo: str,
    ementa: str,
    beneficios: list,
) -> str:
    """Gera resumo em linguagem simples."""
    beneficios_nomes = {
        "BOLSA_FAMILIA": "Bolsa Familia",
        "BPC": "BPC (ajuda para idosos e deficientes)",
        "CADUNICO": "Cadastro Unico",
        "TSEE": "desconto na conta de luz",
        "FARMACIA_POPULAR": "Farmacia Popular (remedios de graca)",
        "SEGURO_DEFESO": "Seguro-Defeso (pescadores)",
        "GARANTIA_SAFRA": "Garantia-Safra (agricultores)",
        "AUXILIO_GAS": "auxilio gas",
        "DIGNIDADE_MENSTRUAL": "absorventes de graca",
        "PIS_PASEP": "PIS/PASEP",
        "FGTS": "FGTS",
        "SEGURO_DESEMPREGO": "seguro-desemprego",
    }

    nomes = [beneficios_nomes.get(b, b) for b in beneficios]

    if nomes:
        programas_texto = ", ".join(nomes[:3])
        if len(nomes) > 3:
            programas_texto += f" e mais {len(nomes) - 3}"
        return f"Saiu uma novidade sobre {programas_texto}. Fique de olho para nao perder nenhum direito."
    else:
        return "Saiu uma novidade que pode afetar beneficios sociais. Estamos acompanhando."


def _determinar_publico(beneficios: list) -> str:
    """Determina quem eh afetado."""
    publicos = set()

    mapa = {
        "BOLSA_FAMILIA": "familias de baixa renda",
        "BPC": "idosos e pessoas com deficiencia",
        "CADUNICO": "todos que tem Cadastro Unico",
        "TSEE": "familias com desconto na luz",
        "FARMACIA_POPULAR": "quem pega remedio de graca",
        "SEGURO_DEFESO": "pescadores artesanais",
        "GARANTIA_SAFRA": "agricultores familiares",
        "SEGURO_DESEMPREGO": "trabalhadores demitidos",
        "PIS_PASEP": "trabalhadores com carteira",
        "FGTS": "trabalhadores com FGTS",
    }

    for b in beneficios:
        if b in mapa:
            publicos.add(mapa[b])

    if publicos:
        return ", ".join(publicos)
    return "cidadaos em geral"


def _recomendar_acao(severidade: Severidade, beneficios: list) -> str:
    """Recomenda acao baseada na severidade."""
    if severidade == Severidade.ALTA:
        return (
            "Fique atento! Essa mudanca pode afetar seu beneficio. "
            "Se tiver duvida, procure o CRAS da sua cidade."
        )
    elif severidade == Severidade.MEDIA:
        return (
            "Mantenha seu cadastro atualizado para nao perder nenhum direito."
        )
    else:
        return "Por enquanto, nao precisa fazer nada. Estamos acompanhando."


def _fallback_resultado(data: str, motivo: str) -> Dict[str, Any]:
    """Resultado fallback quando nao consegue acessar fonte."""
    return {
        "data": data,
        "fonte": "DOU (fallback)",
        "total_publicacoes_analisadas": 0,
        "publicacoes_relevantes": [],
        "erro": motivo,
        "mensagem": "Nao foi possivel acessar o DOU neste momento. Tente novamente mais tarde.",
    }


# =============================================================================
# Tool: consultar_mudancas_legislativas
# =============================================================================

def consultar_mudancas_legislativas(
    programa: Optional[str] = None,
    periodo_dias: int = 30,
) -> dict:
    """Consulta mudancas legislativas recentes que afetam beneficios.

    Esta eh a tool exposta para o agente. Combina DOU + Camara.

    Args:
        programa: Filtrar por programa especifico (ex: BOLSA_FAMILIA, BPC)
        periodo_dias: Quantos dias para tras buscar (padrao: 30)

    Returns:
        dict com mudancas encontradas e seus impactos
    """
    logger.info(f"Consultando mudancas legislativas: programa={programa}, periodo={periodo_dias}")

    # Buscar no DOU (data mais recente)
    dou_resultado = monitorar_dou()

    # Buscar na Camara
    camara_resultado = monitorar_projetos_lei()

    # Combinar resultados
    mudancas = []

    # DOU
    for pub in dou_resultado.get("publicacoes_relevantes", []):
        beneficios = pub.get("beneficios_afetados", [])
        if programa and programa not in beneficios:
            continue
        impacto = analisar_impacto(pub)
        mudancas.append({
            "fonte": "DOU",
            "data": dou_resultado.get("data", ""),
            **impacto,
        })

    # Camara
    for proj in camara_resultado.get("projetos", []):
        if proj.get("relevancia") == "alta":
            mudancas.append({
                "fonte": "Camara dos Deputados",
                "tipo": proj.get("tipo", ""),
                "numero": proj.get("numero", ""),
                "ano": proj.get("ano", ""),
                "ementa": proj.get("ementa", ""),
                "data": proj.get("data_apresentacao", ""),
                "severidade": "media",
                "resumo_simples": f"Novo projeto de lei sobre {', '.join(proj.get('keywords_detectadas', ['beneficios sociais']))}.",
            })

    # Ordenar por severidade
    ordem_severidade = {"alta": 0, "media": 1, "baixa": 2}
    mudancas.sort(key=lambda m: ordem_severidade.get(m.get("severidade", "baixa"), 3))

    return {
        "total_mudancas": len(mudancas),
        "mudancas": mudancas[:10],  # Top 10
        "fontes_consultadas": ["DOU", "Camara dos Deputados"],
        "periodo_dias": periodo_dias,
        "programa_filtro": programa,
        "mensagem": (
            f"Encontrei {len(mudancas)} mudancas recentes."
            if mudancas
            else "Nao encontrei mudancas recentes nos programas monitorados."
        ),
        "dica": "Mantenha seu CadUnico atualizado para nao perder nenhum beneficio com as mudancas.",
    }
