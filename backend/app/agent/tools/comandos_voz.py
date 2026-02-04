"""
Tools de acessibilidade por voz.

Mapeamento de comandos de voz para acoes do sistema.
Backend routing layer - frontend usa Web Speech API.
"""

import re
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


# =============================================================================
# Comandos de voz mapeados para intencoes
# =============================================================================

COMANDOS_VOZ = [
    {
        "padroes": [
            r"quero\s+(?:pedir|pegar)\s+rem[eé]dio",
            r"farm[aá]cia\s+popular",
            r"rem[eé]dio\s+(?:de\s+)?gra[cç]a",
        ],
        "intencao": "FARMACIA_POPULAR",
        "resposta": "Vou te ajudar a pegar remedio de graca! Me fala seu CEP.",
        "tool": "buscar_farmacia",
    },
    {
        "padroes": [
            r"bolsa\s+fam[ií]lia",
            r"quero\s+(?:o\s+)?bolsa",
            r"cadastrar\s+(?:no\s+)?bolsa",
        ],
        "intencao": "BOLSA_FAMILIA",
        "resposta": "Vou te ajudar com o Bolsa Familia! Me fala seu CPF.",
        "tool": "gerar_checklist",
    },
    {
        "padroes": [
            r"bpc",
            r"beneficio\s+(?:para?\s+)?(?:idoso|deficiente)",
            r"loas",
        ],
        "intencao": "BPC",
        "resposta": "Vou te ajudar com o BPC! Me fala seu CPF.",
        "tool": "gerar_checklist",
    },
    {
        "padroes": [
            r"(?:meus?\s+)?(?:benef[ií]cios?|dados?)",
            r"(?:o\s+que\s+)?eu\s+recebo",
            r"(?:quanto\s+)?recebo",
        ],
        "intencao": "CONSULTAR_BENEFICIOS",
        "resposta": "Vou consultar seus beneficios! Me fala seu CPF.",
        "tool": "consultar_beneficio",
    },
    {
        "padroes": [
            r"cras",
            r"(?:onde\s+)?(?:fica|eh)\s+(?:o\s+)?(?:cras|posto)",
            r"assistencia\s+social",
        ],
        "intencao": "BUSCAR_CRAS",
        "resposta": "Vou encontrar o CRAS perto de voce! Me fala seu CEP.",
        "tool": "buscar_cras",
    },
    {
        "padroes": [
            r"dinheiro\s+esquecido",
            r"pis\s*[\/-]?\s*pasep",
            r"fgts",
            r"valores?\s+a\s+receber",
        ],
        "intencao": "DINHEIRO_ESQUECIDO",
        "resposta": "Vou te ajudar a verificar se tem dinheiro esquecido!",
        "tool": "consultar_dinheiro_esquecido",
    },
    {
        "padroes": [
            r"ajuda",
            r"(?:o\s+que\s+)?(?:voce|vc)\s+faz",
            r"menu",
            r"opcoes",
        ],
        "intencao": "AJUDA",
        "resposta": (
            "Posso te ajudar com: "
            "Bolsa Familia, BPC, Farmacia Popular, "
            "dinheiro esquecido, e muito mais! "
            "Me fala o que voce precisa."
        ),
        "tool": None,
    },
]

# Compilar padroes
for cmd in COMANDOS_VOZ:
    cmd["_compiled"] = [re.compile(p, re.IGNORECASE) for p in cmd["padroes"]]


def mapear_comando_voz(transcricao: str) -> Dict[str, Any]:
    """Mapeia transcricao de voz para intencao do sistema.

    Recebe o texto transcrito pelo Web Speech API e identifica
    qual acao o cidadao quer realizar.

    Args:
        transcricao: Texto transcrito do audio do cidadao

    Returns:
        dict com intencao, resposta sugerida e tool a chamar
    """
    logger.info(f"Mapeando comando de voz: {transcricao[:50]}...")

    transcricao_limpa = transcricao.strip().lower()

    for cmd in COMANDOS_VOZ:
        for pattern in cmd["_compiled"]:
            if pattern.search(transcricao_limpa):
                return {
                    "reconhecido": True,
                    "intencao": cmd["intencao"],
                    "resposta_sugerida": cmd["resposta"],
                    "tool_recomendada": cmd["tool"],
                    "transcricao_original": transcricao,
                }

    return {
        "reconhecido": False,
        "intencao": "GERAL",
        "resposta_sugerida": (
            "Entendi! Vou tentar te ajudar. "
            "Pode repetir de outro jeito?"
        ),
        "tool_recomendada": None,
        "transcricao_original": transcricao,
    }


def listar_comandos_voz() -> Dict[str, Any]:
    """Lista comandos de voz disponiveis.

    Returns:
        dict com lista de comandos e exemplos
    """
    return {
        "comandos": [
            {
                "intencao": cmd["intencao"],
                "exemplos": cmd["padroes"][:2],
                "resposta": cmd["resposta"],
            }
            for cmd in COMANDOS_VOZ
        ],
        "total": len(COMANDOS_VOZ),
        "dica": "Fale o que voce precisa. Exemplo: 'Quero remedio de graca'",
    }


def configurar_voz() -> Dict[str, Any]:
    """Retorna configuracoes de voz recomendadas.

    Returns:
        dict com configuracoes para frontend (Web Speech API)
    """
    return {
        "speech_to_text": {
            "lang": "pt-BR",
            "continuous": False,
            "interimResults": True,
            "maxAlternatives": 3,
        },
        "text_to_speech": {
            "lang": "pt-BR",
            "rate": 0.85,  # Mais lento para melhor compreensao
            "pitch": 1.0,
            "volume": 1.0,
        },
        "dicas_acessibilidade": [
            "Fale devagar e com clareza",
            "Espere o sinal sonoro antes de falar",
            "Se nao entendi, tente de outro jeito",
            "Voce pode falar ou digitar",
        ],
    }
