"""
Sub-agentes especializados para o Tá na Mão.

Cada sub-agente gerencia um fluxo de conversa específico,
mantendo estado e coordenando múltiplas tools.
"""

from .farmacia_agent import FarmaciaSubAgent
from .beneficio_agent import BeneficioSubAgent
from .documentacao_agent import DocumentacaoSubAgent

__all__ = ["FarmaciaSubAgent", "BeneficioSubAgent", "DocumentacaoSubAgent"]
