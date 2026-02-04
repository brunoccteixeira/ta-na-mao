"""
Tools de orcamento participativo.

Conecta cidadaos a processos de orcamento participativo
municipal, estadual e federal.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# =============================================================================
# Consultas participativas (mock data)
# =============================================================================

_CONSULTAS_MOCK = [
    {
        "id": "bp-2026-01",
        "titulo": "Brasil Participativo 2026 - Prioridades Nacionais",
        "descricao": "Vote nas prioridades de investimento do governo federal para 2027.",
        "esfera": "federal",
        "municipio_ibge": None,
        "uf": None,
        "data_inicio": "2026-01-15",
        "data_fim": "2026-03-15",
        "url_votacao": "https://brasilparticipativo.presidencia.gov.br",
        "canal_votacao": ["web", "presencial"],
        "valor_total": 5000000000.0,
        "status": "aberta",
        "fonte": "brasil_participativo",
        "propostas_destaque": [
            "Mais creches e escolas em periodo integral",
            "Saude publica: mais medicos e remedios",
            "Moradia popular e saneamento basico",
        ],
    },
    {
        "id": "sp-op-2026",
        "titulo": "Orcamento Participativo Sao Paulo 2026",
        "descricao": "Escolha onde investir R$ 500 milhoes em obras na cidade.",
        "esfera": "municipal",
        "municipio_ibge": "3550308",
        "uf": "SP",
        "data_inicio": "2026-02-01",
        "data_fim": "2026-04-30",
        "url_votacao": "https://orcamento.prefeitura.sp.gov.br",
        "canal_votacao": ["web", "presencial", "whatsapp"],
        "valor_total": 500000000.0,
        "status": "aberta",
        "fonte": "prefeitura",
        "propostas_destaque": [
            "Reforma de UBS e CRAS",
            "Iluminacao e seguranca em bairros",
            "Transporte publico acessivel",
        ],
    },
    {
        "id": "rj-op-2026",
        "titulo": "Orcamento Participativo Rio de Janeiro",
        "descricao": "Vote nas prioridades para seu bairro.",
        "esfera": "municipal",
        "municipio_ibge": "3304557",
        "uf": "RJ",
        "data_inicio": "2026-01-10",
        "data_fim": "2026-02-28",
        "url_votacao": "https://participativa.rio.rj.gov.br",
        "canal_votacao": ["web", "presencial"],
        "valor_total": 300000000.0,
        "status": "aberta",
        "fonte": "prefeitura",
        "propostas_destaque": [
            "Drenagem e prevencao de enchentes",
            "Pavimentacao de vias em comunidades",
            "Parques e areas de lazer",
        ],
    },
    {
        "id": "ba-op-2025",
        "titulo": "Consulta Popular Bahia 2025",
        "descricao": "Resultado da consulta estadual - obras em andamento.",
        "esfera": "estadual",
        "municipio_ibge": None,
        "uf": "BA",
        "data_inicio": "2025-09-01",
        "data_fim": "2025-11-30",
        "url_votacao": "https://consulta.ba.gov.br",
        "canal_votacao": ["web"],
        "valor_total": 800000000.0,
        "status": "concluida",
        "fonte": "governo_estado",
        "propostas_destaque": [],
    },
]


GUIA_VOTACAO = {
    "web": {
        "passos": [
            "Acesse o site da consulta (link acima)",
            "Faca login com sua conta Gov.br",
            "Escolha sua regiao/bairro",
            "Vote nas propostas que mais importam pra voce",
            "Pronto! Seu voto foi registrado",
        ],
        "requisitos": ["Conta Gov.br (qualquer nivel)", "Acesso a internet"],
    },
    "presencial": {
        "passos": [
            "Va ate um ponto de votacao na sua cidade",
            "Leve CPF e documento com foto",
            "Escolha as propostas no formulario",
            "Entregue o formulario ao atendente",
        ],
        "requisitos": ["CPF", "Documento com foto"],
        "dica": "Procure pontos de votacao em CRAS, escolas e centros comunitarios.",
    },
    "whatsapp": {
        "passos": [
            "Salve o numero oficial da prefeitura",
            "Envie 'VOTAR' para iniciar",
            "Responda as perguntas com numeros (1, 2, 3...)",
            "Confirme seu voto",
        ],
        "requisitos": ["WhatsApp", "CPF"],
    },
}


def buscar_consultas_abertas(
    municipio_ibge: Optional[str] = None,
    uf: Optional[str] = None,
) -> Dict[str, Any]:
    """Busca consultas participativas abertas.

    Args:
        municipio_ibge: Filtrar por municipio (codigo IBGE 7 digitos)
        uf: Filtrar por estado (sigla 2 letras)

    Returns:
        dict com consultas abertas e guia de votacao
    """
    logger.info(f"Buscando consultas: municipio={municipio_ibge}, uf={uf}")

    consultas = []
    for c in _CONSULTAS_MOCK:
        if c["status"] != "aberta":
            continue

        # Federais valem para todos
        if c["esfera"] == "federal":
            consultas.append(c)
            continue

        # Filtrar por municipio ou UF
        if municipio_ibge and c["municipio_ibge"] == municipio_ibge:
            consultas.append(c)
        elif uf and c["uf"] == uf:
            consultas.append(c)
        elif not municipio_ibge and not uf:
            consultas.append(c)

    if not consultas:
        return {
            "total": 0,
            "consultas": [],
            "mensagem": (
                "Nao encontrei consultas abertas para sua regiao agora. "
                "Consultas de orcamento participativo costumam abrir entre janeiro e maio."
            ),
        }

    return {
        "total": len(consultas),
        "consultas": [
            {
                "titulo": c["titulo"],
                "descricao": c["descricao"],
                "esfera": c["esfera"],
                "data_fim": c["data_fim"],
                "url": c["url_votacao"],
                "canais": c["canal_votacao"],
                "valor_total": c["valor_total"],
                "propostas_destaque": c["propostas_destaque"],
            }
            for c in consultas
        ],
        "guia_votacao": GUIA_VOTACAO,
        "mensagem": (
            f"Encontrei {len(consultas)} consulta(s) aberta(s)! "
            "Seu voto ajuda a decidir onde o dinheiro publico eh investido."
        ),
    }


def explicar_proposta(titulo: str, valor: float = 0) -> Dict[str, Any]:
    """Explica uma proposta de orcamento em linguagem simples.

    Args:
        titulo: Titulo ou descricao da proposta
        valor: Valor destinado (R$)

    Returns:
        dict com explicacao em linguagem simples
    """
    valor_formatado = f"R$ {valor:,.0f}".replace(",", ".") if valor > 0 else "valor nao informado"

    return {
        "proposta": titulo,
        "valor": valor_formatado,
        "explicacao": (
            f"Essa proposta destina {valor_formatado} para: {titulo}. "
            "Se voce acha que isso eh importante pro seu bairro, vote nela!"
        ),
        "dica": (
            "Voce tem direito de participar! "
            "Orcamento participativo eh voce ajudando a decidir "
            "onde o dinheiro dos seus impostos vai ser usado."
        ),
    }
