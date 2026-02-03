"""
Tools de monitoramento de legislacao para o agente.

Wrapper do servico monitor_legislacao.py exposto como tool
para o agente Gemini consultar mudancas legislativas.
"""

import logging
from typing import Optional

from app.services.monitor_legislacao import (
    consultar_mudancas_legislativas as _consultar_mudancas,
)

logger = logging.getLogger(__name__)


def consultar_mudancas_legislativas(
    programa: Optional[str] = None,
) -> dict:
    """Consulta mudancas recentes na legislacao que afetam beneficios sociais.

    Monitora o Diario Oficial da Uniao (DOU) e a Camara dos Deputados
    em busca de novas leis, decretos e medidas provisorias que possam
    mudar regras de beneficios como Bolsa Familia, BPC, CadUnico, etc.

    Args:
        programa: Filtrar por programa especifico (opcional):
            BOLSA_FAMILIA, BPC, CADUNICO, FARMACIA_POPULAR, TSEE,
            SEGURO_DESEMPREGO, PIS_PASEP, FGTS

    Returns:
        dict com mudancas encontradas em linguagem simples
    """
    logger.info(f"Consultando mudancas legislativas: programa={programa}")

    resultado = _consultar_mudancas(programa=programa)

    # Simplificar para o agente
    mudancas_simples = []
    for m in resultado.get("mudancas", []):
        mudancas_simples.append({
            "resumo": m.get("resumo_simples", m.get("ementa", "")),
            "severidade": m.get("severidade", "baixa"),
            "fonte": m.get("fonte", ""),
            "data": m.get("data", ""),
            "beneficios_afetados": m.get("beneficios_afetados", []),
        })

    return {
        "total_mudancas": resultado.get("total_mudancas", 0),
        "mudancas": mudancas_simples,
        "fontes_consultadas": resultado.get("fontes_consultadas", []),
        "mensagem": resultado.get("mensagem", ""),
        "dica": resultado.get("dica", ""),
    }
