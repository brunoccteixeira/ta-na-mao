"""
Servico de relatorios de impacto social e ESG.

Gera metricas anonimizadas de impacto para parceiros,
investidores e municipios.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# Metricas de impacto
# =============================================================================

METRICAS_IMPACTO = {
    "acesso": {
        "cidadaos_atendidos": "Total de cidadaos que usaram a plataforma",
        "consultas_realizadas": "Consultas de beneficios feitas",
        "beneficios_descobertos": "Novos beneficios identificados para cidadaos",
        "encaminhamentos_cras": "Encaminhamentos para CRAS gerados",
        "checklists_gerados": "Checklists de documentos gerados",
    },
    "financeiro": {
        "valor_beneficios_conectados": "Valor total de beneficios conectados (R$)",
        "valor_dinheiro_esquecido": "Valor de dinheiro esquecido recuperado (R$)",
        "economia_transporte": "Economia estimada com pre-atendimento digital (R$)",
    },
    "inclusao": {
        "primeiro_acesso_digital": "Cidadaos usando tecnologia pela primeira vez",
        "atendimentos_whatsapp": "Atendimentos via WhatsApp",
        "atendimentos_acompanhante": "Atendimentos em modo acompanhante",
        "atendimentos_voz": "Atendimentos via comando de voz",
    },
    "eficiencia": {
        "tempo_medio_consulta": "Tempo medio de consulta (minutos)",
        "reducao_fila_cras": "Reducao estimada de fila no CRAS (%)",
        "taxa_sucesso_encaminhamento": "Taxa de sucesso em encaminhamentos (%)",
    },
}

ODS_IMPACTADOS = {
    "ODS_1": {"nome": "Erradicacao da Pobreza", "descricao": "Acesso a beneficios sociais e protecao"},
    "ODS_2": {"nome": "Fome Zero", "descricao": "Conexao com programas de seguranca alimentar"},
    "ODS_10": {"nome": "Reducao das Desigualdades", "descricao": "Inclusao digital e acesso a direitos"},
    "ODS_11": {"nome": "Cidades Sustentaveis", "descricao": "Planejamento social municipal"},
    "ODS_16": {"nome": "Instituicoes Fortes", "descricao": "Transparencia e participacao cidada"},
}

REGRAS_ANONIMIZACAO = {
    "cpf": "NUNCA incluir - dados hasheados",
    "nome": "NUNCA incluir",
    "endereco": "Agregar por municipio",
    "renda": "Agregar por faixa",
    "beneficios": "Contar por programa",
    "minimo_grupo": 10,
}


def gerar_relatorio_impacto(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    municipio_ibge: Optional[str] = None,
) -> Dict[str, Any]:
    """Gera relatorio de impacto social anonimizado.

    Dados sao sempre agregados (minimo 10 pessoas por grupo)
    para garantir anonimato conforme LGPD.

    Args:
        mes: Mes de referencia (1-12). Padrao: mes atual.
        ano: Ano de referencia. Padrao: ano atual.
        municipio_ibge: Filtrar por municipio (opcional).

    Returns:
        dict com metricas de impacto anonimizadas
    """
    now = datetime.now()
    mes = mes or now.month
    ano = ano or now.year
    referencia = f"{ano:04d}-{mes:02d}"

    logger.info(f"Gerando relatorio de impacto: ref={referencia}, municipio={municipio_ibge}")

    # Dados mock - em producao, consulta banco agregado
    escopo = municipio_ibge or "nacional"

    dados = _gerar_dados_mock(escopo, referencia)

    return {
        "referencia": referencia,
        "escopo": escopo,
        "metricas": dados,
        "ods_impactados": ODS_IMPACTADOS,
        "anonimizacao": {
            "metodo": "Agregacao minima de 10 pessoas por grupo",
            "conformidade": "LGPD Art. 12 - dados anonimizados",
        },
        "formatos_disponiveis": ["json", "pdf", "csv"],
    }


def consultar_impacto_social(
    tipo: Optional[str] = None,
) -> Dict[str, Any]:
    """Consulta metricas de impacto social da plataforma.

    Args:
        tipo: Tipo de metrica: acesso, financeiro, inclusao, eficiencia.
              Se nao informado, retorna resumo geral.

    Returns:
        dict com metricas solicitadas
    """
    if tipo and tipo in METRICAS_IMPACTO:
        return {
            "tipo": tipo,
            "metricas": METRICAS_IMPACTO[tipo],
            "dados": _gerar_dados_mock("nacional", "resumo").get(tipo, {}),
        }

    return {
        "tipos_disponiveis": list(METRICAS_IMPACTO.keys()),
        "resumo": _gerar_dados_mock("nacional", "resumo"),
        "ods": ODS_IMPACTADOS,
        "mensagem": "Metricas de impacto da plataforma Ta na Mao.",
    }


def _gerar_dados_mock(escopo: str, referencia: str) -> Dict[str, Any]:
    """Gera dados mock de impacto para dev/test."""
    multiplicador = 1.0 if escopo == "nacional" else 0.05

    return {
        "acesso": {
            "cidadaos_atendidos": int(150000 * multiplicador),
            "consultas_realizadas": int(320000 * multiplicador),
            "beneficios_descobertos": int(45000 * multiplicador),
            "encaminhamentos_cras": int(28000 * multiplicador),
            "checklists_gerados": int(67000 * multiplicador),
        },
        "financeiro": {
            "valor_beneficios_conectados": round(180000000 * multiplicador, 2),
            "valor_dinheiro_esquecido": round(25000000 * multiplicador, 2),
            "economia_transporte": round(3500000 * multiplicador, 2),
        },
        "inclusao": {
            "primeiro_acesso_digital": int(12000 * multiplicador),
            "atendimentos_whatsapp": int(89000 * multiplicador),
            "atendimentos_acompanhante": int(15000 * multiplicador),
            "atendimentos_voz": int(3000 * multiplicador),
        },
        "eficiencia": {
            "tempo_medio_consulta_min": 4.5,
            "reducao_fila_cras_pct": 35.0,
            "taxa_sucesso_encaminhamento_pct": 78.0,
        },
    }
