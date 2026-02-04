"""
Tools de navegacao da Rede SUAS.

Classifica necessidades do cidadao e encaminha para o
equipamento correto: CRAS, CREAS, Centro POP, CAPS.
"""

import logging
import re
from typing import Optional, List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# Equipamentos SUAS
# =============================================================================

class TipoEquipamento(str, Enum):
    CRAS = "CRAS"
    CREAS = "CREAS"
    CENTRO_POP = "CENTRO_POP"
    CAPS = "CAPS"
    CONSELHO_TUTELAR = "CONSELHO_TUTELAR"
    ABRIGO = "ABRIGO"


# Servicos por equipamento
EQUIPAMENTOS_SUAS = {
    TipoEquipamento.CRAS: {
        "nome": "CRAS - Centro de Referencia de Assistencia Social",
        "tipo_protecao": "Protecao Social Basica",
        "descricao": "Atende familias em situacao de vulnerabilidade. Porta de entrada para beneficios.",
        "servicos": [
            "CadUnico (Cadastro Unico)",
            "Bolsa Familia",
            "BPC / LOAS",
            "Tarifa Social de Energia",
            "PAIF (acompanhamento familiar)",
            "SCFV (convivencia e fortalecimento de vinculos)",
            "Orientacao sobre direitos",
            "Encaminhamento para outros servicos",
        ],
        "publico": "Familias em vulnerabilidade social, baixa renda, desempregados",
        "quando_procurar": [
            "Quer se cadastrar no CadUnico",
            "Quer pedir Bolsa Familia ou BPC",
            "Precisa de orientacao sobre beneficios",
            "Precisa de documentos",
            "Situacao de vulnerabilidade (nao urgente)",
        ],
    },
    TipoEquipamento.CREAS: {
        "nome": "CREAS - Centro de Referencia Especializado de Assistencia Social",
        "tipo_protecao": "Protecao Social Especial - Media Complexidade",
        "descricao": "Atende pessoas com direitos violados: violencia, abuso, abandono.",
        "servicos": [
            "PAEFI (atendimento a familias com direitos violados)",
            "Medidas socioeducativas",
            "Abordagem social",
            "Atendimento a violencia domestica",
            "Atendimento a idosos violentados",
            "Atendimento a criancas e adolescentes",
        ],
        "publico": "Vitimas de violencia, abuso, negligencia, exploracao",
        "quando_procurar": [
            "Sofre violencia domestica",
            "Crianca ou adolescente em risco",
            "Idoso sofrendo maus-tratos",
            "Pessoa com deficiencia sendo negligenciada",
            "Trabalho infantil",
            "Exploracão sexual",
        ],
    },
    TipoEquipamento.CENTRO_POP: {
        "nome": "Centro POP - Centro de Referencia para Populacao de Rua",
        "tipo_protecao": "Protecao Social Especial - Alta Complexidade",
        "descricao": "Atende pessoas em situacao de rua com servicos basicos e encaminhamentos.",
        "servicos": [
            "Higiene pessoal (banho, roupas)",
            "Alimentacao",
            "Documentos (encaminhamento)",
            "Atendimento de saude basico",
            "Encaminhamento para abrigo",
            "Guarda de pertences",
            "Endereco de referencia",
        ],
        "publico": "Pessoas em situacao de rua",
        "quando_procurar": [
            "Esta morando na rua",
            "Precisa de abrigo",
            "Precisa de alimentacao e higiene",
            "Precisa de endereco para documentos",
        ],
    },
    TipoEquipamento.CAPS: {
        "nome": "CAPS - Centro de Atencao Psicossocial",
        "tipo_protecao": "Saude Mental (via SUS)",
        "descricao": "Atende pessoas com sofrimento mental: depressao, ansiedade, dependencia quimica.",
        "servicos": [
            "Atendimento psicologico",
            "Atendimento psiquiatrico",
            "Terapia em grupo",
            "Oficinas terapeuticas",
            "Acolhimento em crise",
            "Tratamento de dependencia quimica (CAPS AD)",
        ],
        "publico": "Pessoas com transtornos mentais, sofrimento psiquico, dependencia quimica",
        "quando_procurar": [
            "Depressao, ansiedade severa",
            "Pensamentos suicidas",
            "Dependencia de alcool ou drogas",
            "Crise psiquica",
            "Transtornos mentais graves",
        ],
    },
    TipoEquipamento.CONSELHO_TUTELAR: {
        "nome": "Conselho Tutelar",
        "tipo_protecao": "Defesa de Direitos da Crianca e Adolescente",
        "descricao": "Protege direitos de criancas e adolescentes (0-17 anos).",
        "servicos": [
            "Denuncia de violencia contra crianca",
            "Denuncia de negligencia",
            "Denuncia de trabalho infantil",
            "Medidas de protecao",
            "Encaminhamento para abrigo infantil",
        ],
        "publico": "Criancas e adolescentes em situacao de risco",
        "quando_procurar": [
            "Crianca sendo maltratada",
            "Crianca abandonada",
            "Trabalho infantil",
            "Crianca fora da escola",
            "Adolescente em situacao de rua",
        ],
    },
}


# =============================================================================
# Classificacao de necessidade
# =============================================================================

# Keywords por tipo de equipamento
_KEYWORDS_ENCAMINHAMENTO = {
    TipoEquipamento.CREAS: {
        "primary": [
            "violencia", "violência", "apanhando", "abuso",
            "maus tratos", "maus-tratos", "agredida", "agredido",
            "ameaca", "ameaça", "bate", "espanca",
        ],
        "secondary": [
            "medo", "socorro", "perigo", "exploração",
            "negligencia", "abandono", "idoso maltratado",
        ],
    },
    TipoEquipamento.CENTRO_POP: {
        "primary": [
            "morando na rua", "situacao de rua", "situação de rua",
            "sem casa", "desabrigado", "abrigo",
            "morador de rua", "na rua",
        ],
        "secondary": [
            "sem teto", "expulso de casa", "despejado",
        ],
    },
    TipoEquipamento.CAPS: {
        "primary": [
            "depressao", "depressão", "ansiedade",
            "quero morrer", "suicidio", "suicídio",
            "drogas", "alcool", "álcool", "vicio", "vício",
            "dependencia quimica", "dependência química",
        ],
        "secondary": [
            "nao aguento mais", "não aguento mais",
            "muito triste", "sem esperanca",
            "bebendo muito", "usando drogas",
        ],
    },
    TipoEquipamento.CONSELHO_TUTELAR: {
        "primary": [
            "crianca", "criança", "adolescente",
            "trabalho infantil", "menor abandonado",
            "crianca na rua", "criança na rua",
        ],
        "secondary": [
            "filho abandonado", "menor", "menino de rua",
        ],
    },
}


def classificar_necessidade_suas(
    mensagem: str,
    tem_criancas: bool = False,
    idoso: bool = False,
    situacao_rua: bool = False,
) -> dict:
    """Classifica necessidade do cidadao e indica equipamento SUAS correto.

    Analisa a mensagem e contexto para encaminhar ao servico adequado:
    - CRAS: beneficios, cadastro, orientacao (basico)
    - CREAS: violencia, direitos violados (especial)
    - Centro POP: populacao de rua
    - CAPS: saude mental, dependencia quimica
    - Conselho Tutelar: criancas e adolescentes em risco

    Args:
        mensagem: Mensagem do cidadao descrevendo necessidade
        tem_criancas: Se ha criancas envolvidas
        idoso: Se envolve idoso
        situacao_rua: Se esta em situacao de rua

    Returns:
        dict com equipamento recomendado, urgencia e servicos
    """
    logger.info("Classificando necessidade SUAS")

    mensagem_lower = mensagem.lower()
    scores = {}

    # Pontuar cada equipamento
    for tipo, keywords in _KEYWORDS_ENCAMINHAMENTO.items():
        score = 0
        matches = []

        for kw in keywords.get("primary", []):
            if kw in mensagem_lower:
                score += 2
                matches.append(kw)
        for kw in keywords.get("secondary", []):
            if kw in mensagem_lower:
                score += 1
                matches.append(kw)

        if score > 0:
            scores[tipo] = {"score": score, "matches": matches}

    # Ajustar por contexto
    if situacao_rua and TipoEquipamento.CENTRO_POP not in scores:
        scores[TipoEquipamento.CENTRO_POP] = {"score": 3, "matches": ["contexto: situacao de rua"]}

    if tem_criancas:
        if TipoEquipamento.CREAS in scores:
            scores[TipoEquipamento.CONSELHO_TUTELAR] = scores.get(
                TipoEquipamento.CONSELHO_TUTELAR,
                {"score": 0, "matches": []}
            )
            scores[TipoEquipamento.CONSELHO_TUTELAR]["score"] += 2
            scores[TipoEquipamento.CONSELHO_TUTELAR]["matches"].append("contexto: criancas envolvidas")

    # Se nenhum especializado, encaminha para CRAS (porta de entrada)
    if not scores:
        equipamento = TipoEquipamento.CRAS
        urgente = False
    else:
        equipamento = max(scores, key=lambda t: scores[t]["score"])
        urgente = equipamento in (TipoEquipamento.CREAS, TipoEquipamento.CONSELHO_TUTELAR)

    info = EQUIPAMENTOS_SUAS[equipamento]

    return {
        "equipamento": equipamento.value,
        "nome": info["nome"],
        "tipo_protecao": info["tipo_protecao"],
        "descricao": info["descricao"],
        "servicos": info["servicos"],
        "urgente": urgente,
        "quando_procurar": info["quando_procurar"],
        "keywords_detectadas": scores.get(equipamento, {}).get("matches", []),
        "outros_possiveis": [
            {"equipamento": t.value, "score": s["score"]}
            for t, s in sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
            if t != equipamento
        ][:2],
        "telefones_uteis": _telefones_uteis(equipamento, urgente),
    }


def _telefones_uteis(tipo: TipoEquipamento, urgente: bool) -> List[Dict[str, str]]:
    """Retorna telefones uteis para o encaminhamento."""
    telefones = []

    if urgente:
        telefones.append({"nome": "Emergencia", "numero": "190", "descricao": "Policia Militar"})

    mapa = {
        TipoEquipamento.CREAS: [
            {"nome": "Disque 100", "numero": "100", "descricao": "Denuncias de violacoes de direitos"},
            {"nome": "Ligue 180", "numero": "180", "descricao": "Central de Atendimento a Mulher"},
        ],
        TipoEquipamento.CAPS: [
            {"nome": "CVV", "numero": "188", "descricao": "Centro de Valorizacao da Vida (24h)"},
            {"nome": "SAMU", "numero": "192", "descricao": "Emergencia medica"},
        ],
        TipoEquipamento.CONSELHO_TUTELAR: [
            {"nome": "Disque 100", "numero": "100", "descricao": "Denuncias - criancas e adolescentes"},
        ],
        TipoEquipamento.CENTRO_POP: [
            {"nome": "SAMU", "numero": "192", "descricao": "Emergencia medica"},
        ],
    }

    telefones.extend(mapa.get(tipo, []))

    # Sempre incluir Disque Social
    telefones.append({"nome": "Disque Social", "numero": "121", "descricao": "Informacoes sobre beneficios"})

    return telefones


# =============================================================================
# Tool: listar_equipamentos_suas
# =============================================================================

def listar_equipamentos_suas(tipo: Optional[str] = None) -> dict:
    """Lista equipamentos da Rede SUAS com servicos oferecidos.

    Args:
        tipo: Tipo especifico: CRAS, CREAS, CENTRO_POP, CAPS, CONSELHO_TUTELAR.
             Se nao informado, lista todos.

    Returns:
        dict com informacoes dos equipamentos
    """
    if tipo:
        try:
            tipo_enum = TipoEquipamento(tipo.upper())
        except ValueError:
            return {
                "erro": f"Tipo '{tipo}' nao reconhecido.",
                "tipos_disponiveis": [t.value for t in TipoEquipamento],
            }

        info = EQUIPAMENTOS_SUAS.get(tipo_enum)
        if info:
            return {
                "equipamento": tipo_enum.value,
                **info,
            }

    # Listar todos
    return {
        "equipamentos": [
            {
                "tipo": t.value,
                "nome": info["nome"],
                "descricao": info["descricao"],
                "tipo_protecao": info["tipo_protecao"],
            }
            for t, info in EQUIPAMENTOS_SUAS.items()
        ],
        "mensagem": "Me conta o que voce precisa que eu indico o servico certo pra voce.",
    }
