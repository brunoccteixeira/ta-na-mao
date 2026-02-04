"""
Servico de pesquisa de campo digital.

Templates de questionarios, coleta offline-first
e analise de respostas com IA.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# Templates de questionarios
# =============================================================================

TEMPLATE_SATISFACAO = {
    "id": "satisfacao_v1",
    "titulo": "O que voce achou do Ta na Mao?",
    "descricao": "Pesquisa rapida para melhorar o app (100% anonima)",
    "perguntas": [
        {
            "id": "q1",
            "texto": "Voce conseguiu o que precisava?",
            "tipo": "escolha_unica",
            "opcoes": ["Sim, tudo certo", "Mais ou menos", "Nao consegui"],
        },
        {
            "id": "q2",
            "texto": "Foi facil de usar?",
            "tipo": "escala",
            "opcoes": ["Muito dificil", "Dificil", "Normal", "Facil", "Muito facil"],
        },
        {
            "id": "q3",
            "texto": "Voce indicaria para alguem?",
            "tipo": "escala",
            "opcoes": ["Com certeza nao", "Acho que nao", "Talvez", "Acho que sim", "Com certeza sim"],
        },
        {
            "id": "q4",
            "texto": "O que podemos melhorar?",
            "tipo": "texto_livre",
            "obrigatoria": False,
        },
    ],
}

TEMPLATE_NECESSIDADES = {
    "id": "necessidades_v1",
    "titulo": "Queremos te conhecer melhor",
    "descricao": "Nos ajude a entender o que voce mais precisa",
    "perguntas": [
        {
            "id": "q1",
            "texto": "Qual sua maior dificuldade para acessar beneficios?",
            "tipo": "escolha_unica",
            "opcoes": [
                "Nao sei quais tenho direito",
                "Nao tenho documentos",
                "O CRAS eh longe da minha casa",
                "Nao consigo entender o que pedem",
                "Outro",
            ],
        },
        {
            "id": "q2",
            "texto": "Como voce fica sabendo de novos beneficios?",
            "tipo": "multipla_escolha",
            "opcoes": [
                "WhatsApp/redes sociais",
                "TV/radio",
                "Vizinhos/amigos",
                "CRAS/assistente social",
                "Internet",
            ],
        },
        {
            "id": "q3",
            "texto": "Qual aparelho voce usa?",
            "tipo": "escolha_unica",
            "opcoes": [
                "Celular com internet",
                "Celular sem internet",
                "Computador",
                "Nao tenho aparelho proprio",
            ],
        },
    ],
}

TEMPLATE_ATENDIMENTO_CRAS = {
    "id": "atendimento_cras_v1",
    "titulo": "Como foi seu atendimento no CRAS?",
    "descricao": "Sua opiniao ajuda a melhorar o atendimento",
    "perguntas": [
        {
            "id": "q1",
            "texto": "Quanto tempo voce esperou para ser atendido?",
            "tipo": "escolha_unica",
            "opcoes": ["Menos de 30 min", "30 min a 1 hora", "1 a 2 horas", "Mais de 2 horas"],
        },
        {
            "id": "q2",
            "texto": "O atendente explicou tudo de forma clara?",
            "tipo": "escala",
            "opcoes": ["Nada claro", "Pouco claro", "Normal", "Claro", "Muito claro"],
        },
        {
            "id": "q3",
            "texto": "Seu problema foi resolvido?",
            "tipo": "escolha_unica",
            "opcoes": ["Sim, totalmente", "Sim, parcialmente", "Nao foi resolvido", "Preciso voltar"],
        },
        {
            "id": "q4",
            "texto": "Quer deixar algum comentario?",
            "tipo": "texto_livre",
            "obrigatoria": False,
        },
    ],
}

TEMPLATES = {
    "satisfacao": TEMPLATE_SATISFACAO,
    "necessidades": TEMPLATE_NECESSIDADES,
    "atendimento_cras": TEMPLATE_ATENDIMENTO_CRAS,
}

# Armazenamento em memoria (em producao: banco de dados)
_respostas_coletadas: List[Dict[str, Any]] = []


def listar_questionarios() -> Dict[str, Any]:
    """Lista questionarios disponiveis.

    Returns:
        dict com questionarios e suas descricoes
    """
    return {
        "questionarios": [
            {
                "id": t["id"],
                "titulo": t["titulo"],
                "descricao": t["descricao"],
                "total_perguntas": len(t["perguntas"]),
            }
            for t in TEMPLATES.values()
        ],
        "total": len(TEMPLATES),
    }


def obter_questionario(questionario_id: str) -> Dict[str, Any]:
    """Retorna um questionario completo para preenchimento.

    Args:
        questionario_id: ID do template (satisfacao, necessidades, atendimento_cras)

    Returns:
        dict com perguntas do questionario
    """
    template = TEMPLATES.get(questionario_id)
    if not template:
        return {
            "erro": f"Questionario '{questionario_id}' nao encontrado.",
            "disponiveis": list(TEMPLATES.keys()),
        }

    return template


def registrar_resposta(
    questionario_id: str,
    respostas: Dict[str, Any],
    canal: str = "app",
    municipio_ibge: Optional[str] = None,
) -> Dict[str, Any]:
    """Registra resposta de questionario (100% anonima).

    IMPORTANTE: Nao coleta CPF, nome, telefone ou endereco.

    Args:
        questionario_id: ID do questionario
        respostas: Dict com respostas (chave: id da pergunta, valor: resposta)
        canal: Canal de coleta: app, web, whatsapp, presencial
        municipio_ibge: Municipio (opcional, para agregacao)

    Returns:
        dict confirmando registro
    """
    template = TEMPLATES.get(questionario_id)
    if not template:
        return {"erro": f"Questionario '{questionario_id}' nao encontrado."}

    registro = {
        "questionario_id": questionario_id,
        "respostas": respostas,
        "canal": canal,
        "municipio_ibge": municipio_ibge,
        "registrado_em": datetime.now().isoformat(),
    }

    _respostas_coletadas.append(registro)

    return {
        "sucesso": True,
        "mensagem": "Obrigado por responder! Sua opiniao ajuda a melhorar o Ta na Mao.",
        "anonimo": True,
    }


def gerar_relatorio_pesquisa(
    questionario_id: str,
) -> Dict[str, Any]:
    """Gera relatorio agregado das respostas (minimo 10 respostas).

    Args:
        questionario_id: ID do questionario

    Returns:
        dict com resumo estatistico das respostas
    """
    respostas = [
        r for r in _respostas_coletadas
        if r["questionario_id"] == questionario_id
    ]

    if len(respostas) < 10:
        return {
            "questionario_id": questionario_id,
            "total_respostas": len(respostas),
            "relatorio_disponivel": False,
            "mensagem": f"Precisa de pelo menos 10 respostas (tem {len(respostas)}). Anonimato garantido.",
        }

    template = TEMPLATES.get(questionario_id, {})

    # Agregar respostas por pergunta
    agregado = {}
    for pergunta in template.get("perguntas", []):
        pid = pergunta["id"]
        valores = [r["respostas"].get(pid) for r in respostas if pid in r.get("respostas", {})]

        if pergunta["tipo"] in ("escolha_unica", "escala"):
            contagem = {}
            for v in valores:
                contagem[v] = contagem.get(v, 0) + 1
            agregado[pid] = {
                "pergunta": pergunta["texto"],
                "tipo": pergunta["tipo"],
                "total_respostas": len(valores),
                "distribuicao": contagem,
            }
        elif pergunta["tipo"] == "texto_livre":
            agregado[pid] = {
                "pergunta": pergunta["texto"],
                "tipo": "texto_livre",
                "total_respostas": len(valores),
                "amostra": valores[:5],  # Primeiras 5 respostas
            }

    # Calcular NPS se aplicavel
    nps = None
    if questionario_id == "satisfacao":
        nps = _calcular_nps(respostas)

    return {
        "questionario_id": questionario_id,
        "total_respostas": len(respostas),
        "relatorio_disponivel": True,
        "resultados": agregado,
        "nps": nps,
        "canais": _contar_canais(respostas),
    }


def _calcular_nps(respostas: List[Dict]) -> Dict[str, Any]:
    """Calcula Net Promoter Score."""
    notas = []
    for r in respostas:
        resposta_q3 = r.get("respostas", {}).get("q3")
        mapa = {
            "Com certeza nao": 0,
            "Acho que nao": 3,
            "Talvez": 5,
            "Acho que sim": 8,
            "Com certeza sim": 10,
        }
        if resposta_q3 in mapa:
            notas.append(mapa[resposta_q3])

    if not notas:
        return None

    promotores = sum(1 for n in notas if n >= 9) / len(notas) * 100
    detratores = sum(1 for n in notas if n <= 6) / len(notas) * 100
    nps = promotores - detratores

    return {
        "score": round(nps, 1),
        "promotores_pct": round(promotores, 1),
        "detratores_pct": round(detratores, 1),
        "total_avaliadores": len(notas),
        "classificacao": "Excelente" if nps > 50 else "Bom" if nps > 0 else "Precisa melhorar",
    }


def _contar_canais(respostas: List[Dict]) -> Dict[str, int]:
    """Conta respostas por canal."""
    canais = {}
    for r in respostas:
        canal = r.get("canal", "desconhecido")
        canais[canal] = canais.get(canal, 0) + 1
    return canais
