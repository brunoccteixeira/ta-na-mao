"""
Tool para escalonar casos complexos para assessores humanos (Anjo Social).

Quando a IA detecta situacao complexa (idoso 65+, PCD, 3+ beneficios,
emergencia), ela pode escalonar para um assessor social humano.
"""

from typing import Optional
from uuid import uuid4

from app.agent.tools.base import ToolResult, UIHint


# Critérios automáticos de escalonamento
CRITERIOS_ESCALONAMENTO = {
    "idoso_65": "Pessoa idosa (65+) com dificuldade de acesso",
    "pcd": "Pessoa com deficiência que precisa de BPC/LOAS",
    "multiplos_beneficios": "Situação complexa com 3 ou mais benefícios simultâneos",
    "emergencia": "Situação de vulnerabilidade extrema ou emergência social",
    "documentacao_complexa": "Dificuldade com documentação ou burocracia",
    "recurso_negado": "Benefício negado que precisa de recurso/revisão",
}


def escalonar_anjo_social(
    motivo: str,
    beneficios: Optional[list[str]] = None,
    prioridade: str = "medium",
    session_id: str = "",
    uf: str = "",
    contexto_cidadao: Optional[dict] = None,
) -> dict:
    """
    Escalona o caso para um assessor social humano (Anjo Social).

    Esta tool cria um caso no sistema de assessoria para que um
    profissional humano acompanhe o cidadão.

    Args:
        motivo: Motivo do escalonamento (por que a IA está escalando)
        beneficios: Lista de códigos dos benefícios em questão
        prioridade: low, medium, high, emergency
        session_id: ID anônimo da sessão do cidadão
        uf: Estado do cidadão
        contexto_cidadao: Contexto anônimo adicional (sem PII)

    Returns:
        dict com confirmação do escalonamento e info do assessor
    """
    beneficios_lista = beneficios or []
    contexto = contexto_cidadao or {}
    if uf:
        contexto["uf"] = uf

    # Determina prioridade automática se não especificada
    if prioridade == "medium":
        if any(b in ["BPC", "BPC_PCD", "BPC_IDOSO"] for b in beneficios_lista):
            prioridade = "high"
        if len(beneficios_lista) >= 3:
            prioridade = "high"

    # Em produção, aqui chamaria o advisor_service para criar o caso
    # e atribuir um assessor real. Por enquanto, retorna resposta simulada.
    case_id = str(uuid4())[:8]

    # Simula assessor atribuído baseado nos benefícios
    assessor_info = _simular_assessor(beneficios_lista, uf)

    mensagem_cidadao = (
        f"Entendi que sua situacao precisa de um acompanhamento especial. "
        f"Vou conectar voce com {assessor_info['nome']}, "
        f"{assessor_info['cargo']} {assessor_info['organizacao']}.\n\n"
        f"O que vai acontecer agora:\n"
        f"1. {assessor_info['nome']} vai receber seu caso (numero {case_id})\n"
        f"2. Em ate 3 dias uteis, vai entrar em contato por WhatsApp\n"
        f"3. Vai te ajudar com toda a parte de documentos e agendamento\n\n"
        f"Voce NAO precisa fazer nada agora. Pode continuar tirando duvidas comigo "
        f"enquanto aguarda o contato."
    )

    result = ToolResult.ok(
        data={
            "escalonamento": {
                "case_id": case_id,
                "status": "assigned",
                "prioridade": prioridade,
                "motivo": motivo,
                "beneficios": beneficios_lista,
            },
            "assessor": assessor_info,
            "mensagem_cidadao": mensagem_cidadao,
            "prazo_contato": "3 dias uteis",
        },
        ui_hint=UIHint.INFO,
        context_updates={
            "caso_assessoria": case_id,
            "assessor_atribuido": assessor_info["nome"],
        },
    )

    return result.model_dump()


def _simular_assessor(beneficios: list[str], uf: str) -> dict:
    """Simula atribuição de assessor baseado no perfil.

    Em produção, usa advisor_service.find_best_advisor().
    """
    # Assessores simulados por especialidade
    assessores = [
        {
            "nome": "Maria Silva",
            "cargo": "Assistente Social",
            "organizacao": "do CRAS Centro",
            "especialidades": ["BPC", "BPC_PCD", "BPC_IDOSO", "BOLSA_FAMILIA"],
        },
        {
            "nome": "João Santos",
            "cargo": "Voluntário",
            "organizacao": "da Rede de Proteção Social",
            "especialidades": ["SEGURO_DESEMPREGO", "FGTS", "PIS_PASEP", "ABONO_SALARIAL"],
        },
        {
            "nome": "Ana Oliveira",
            "cargo": "Assistente Social",
            "organizacao": "do CREAS",
            "especialidades": ["AUXILIO_GAS", "TSEE", "MCMV", "FARMACIA_POPULAR"],
        },
    ]

    # Encontra assessor com maior match de especialidade
    best = assessores[0]
    best_score = 0

    for assessor in assessores:
        score = sum(1 for b in beneficios if b in assessor["especialidades"])
        if score > best_score:
            best_score = score
            best = assessor

    return {
        "nome": best["nome"],
        "cargo": best["cargo"],
        "organizacao": best["organizacao"],
    }
