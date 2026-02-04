"""
Servico de protecao de dados do cidadao (LGPD).

Consentimento granular, portabilidade de dados,
direito ao esquecimento e auditoria de acessos.
"""

import hashlib
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# Classificacao de dados (Art. 5)
# =============================================================================

CLASSIFICACAO_DADOS = {
    "DADOS_PESSOAIS": {
        "artigo": "Art. 5, I",
        "campos": ["cpf", "nome", "data_nascimento", "endereco", "telefone", "nis", "composicao_familiar"],
    },
    "DADOS_SENSIVEIS": {
        "artigo": "Art. 5, II",
        "campos": ["saude", "deficiencia", "violencia", "orientacao_sexual", "raca_etnia"],
    },
    "DADOS_MENORES": {
        "artigo": "Art. 14",
        "campos": ["criancas_adolescentes"],
        "nota": "Requer consentimento do responsavel",
    },
    "DADOS_FINANCEIROS": {
        "artigo": "Art. 5, I",
        "campos": ["renda", "beneficios", "dinheiro_esquecido", "historico_pagamentos"],
    },
}


# =============================================================================
# Finalidades de tratamento (Art. 7)
# =============================================================================

FINALIDADES = {
    "consulta_beneficio": {
        "descricao": "Consultar seus beneficios sociais",
        "dados_necessarios": ["cpf"],
        "dados_opcionais": ["nome", "endereco"],
        "base_legal": "consentimento",
        "retencao": "durante_sessao",
    },
    "elegibilidade": {
        "descricao": "Verificar quais beneficios voce tem direito",
        "dados_necessarios": ["cpf", "renda", "composicao_familiar"],
        "dados_opcionais": ["endereco", "trabalho"],
        "base_legal": "consentimento",
        "retencao": "24_horas",
    },
    "farmacia": {
        "descricao": "Pedir medicamentos na Farmacia Popular",
        "dados_necessarios": ["cpf", "receita_medica"],
        "dados_opcionais": ["localizacao"],
        "base_legal": "consentimento",
        "dados_sensiveis": True,
        "retencao": "30_dias",
    },
    "encaminhamento_cras": {
        "descricao": "Gerar carta de encaminhamento para o CRAS",
        "dados_necessarios": ["cpf", "nome", "endereco"],
        "base_legal": "consentimento",
        "retencao": "90_dias",
    },
    "pesquisa": {
        "descricao": "Responder pesquisa para melhorar o app (anonimo)",
        "dados_necessarios": [],
        "dados_opcionais": ["municipio"],
        "base_legal": "consentimento",
        "retencao": "indefinida_anonimizada",
    },
}


# =============================================================================
# Plano de resposta a incidentes
# =============================================================================

PLANO_RESPOSTA_INCIDENTE = {
    "etapas": [
        {"passo": 1, "acao": "Identificar escopo do vazamento", "responsavel": "Equipe tecnica", "prazo": "2 horas"},
        {"passo": 2, "acao": "Conter o vazamento (revogar tokens, bloquear acesso)", "responsavel": "Equipe tecnica", "prazo": "4 horas"},
        {"passo": 3, "acao": "Notificar ANPD (Autoridade Nacional de Protecao de Dados)", "responsavel": "DPO", "prazo": "72 horas (obrigatorio)"},
        {"passo": 4, "acao": "Notificar titulares afetados", "responsavel": "DPO + Comunicacao", "prazo": "72 horas"},
        {"passo": 5, "acao": "Documentar incidente e medidas tomadas", "responsavel": "DPO", "prazo": "30 dias"},
    ],
    "contatos": {
        "anpd": "https://www.gov.br/anpd/pt-br",
    },
}


# Armazenamento em memoria (em producao: banco de dados)
_consentimentos: List[Dict[str, Any]] = []
_log_auditoria: List[Dict[str, Any]] = []


# =============================================================================
# Funcoes de hash (seguranca)
# =============================================================================

def hash_cpf(cpf: str) -> str:
    """Gera hash seguro do CPF. NUNCA armazena CPF em texto."""
    cpf_limpo = cpf.replace(".", "").replace("-", "").strip()
    return hashlib.sha256(cpf_limpo.encode()).hexdigest()


def hash_ip(ip: str) -> str:
    """Gera hash do IP para auditoria sem rastreamento."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


# =============================================================================
# Consentimento granular
# =============================================================================

def registrar_consentimento(
    cpf: str,
    finalidade: str,
    canal: str = "app",
) -> Dict[str, Any]:
    """Registra consentimento do cidadao para uma finalidade.

    Args:
        cpf: CPF do cidadao (sera hasheado)
        finalidade: Finalidade do tratamento (consulta_beneficio, farmacia, etc)
        canal: Canal: app, whatsapp, web

    Returns:
        dict confirmando consentimento
    """
    if finalidade not in FINALIDADES:
        return {
            "erro": f"Finalidade '{finalidade}' nao reconhecida.",
            "finalidades_disponiveis": list(FINALIDADES.keys()),
        }

    cpf_hash = hash_cpf(cpf)
    info = FINALIDADES[finalidade]

    registro = {
        "cpf_hash": cpf_hash,
        "finalidade": finalidade,
        "dados_autorizados": info["dados_necessarios"] + info.get("dados_opcionais", []),
        "data_consentimento": datetime.now().isoformat(),
        "canal": canal,
        "revogado": False,
    }

    _consentimentos.append(registro)

    return {
        "consentimento_registrado": True,
        "finalidade": finalidade,
        "descricao": info["descricao"],
        "dados_utilizados": info["dados_necessarios"],
        "retencao": info["retencao"],
        "mensagem_cidadao": _mensagem_consentimento(finalidade),
    }


def verificar_consentimento(cpf: str, finalidade: str) -> bool:
    """Verifica se cidadao consentiu para esta finalidade.

    Args:
        cpf: CPF do cidadao
        finalidade: Finalidade a verificar

    Returns:
        True se ha consentimento valido
    """
    cpf_hash = hash_cpf(cpf)
    for c in _consentimentos:
        if (c["cpf_hash"] == cpf_hash
                and c["finalidade"] == finalidade
                and not c["revogado"]):
            return True
    return False


def revogar_consentimento(cpf: str, finalidade: Optional[str] = None) -> Dict[str, Any]:
    """Revoga consentimento do cidadao.

    Args:
        cpf: CPF do cidadao
        finalidade: Finalidade especifica (ou None para revogar todos)

    Returns:
        dict com confirmacao
    """
    cpf_hash = hash_cpf(cpf)
    revogados = 0

    for c in _consentimentos:
        if c["cpf_hash"] == cpf_hash and not c["revogado"]:
            if finalidade is None or c["finalidade"] == finalidade:
                c["revogado"] = True
                c["data_revogacao"] = datetime.now().isoformat()
                revogados += 1

    return {
        "revogados": revogados,
        "mensagem": (
            f"{revogados} consentimento(s) revogado(s)."
            if revogados > 0
            else "Nenhum consentimento encontrado para revogar."
        ),
    }


# =============================================================================
# Portabilidade de dados (Art. 18, V)
# =============================================================================

def exportar_dados(cpf: str) -> Dict[str, Any]:
    """Exporta todos os dados do cidadao (portabilidade LGPD).

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com todos os dados em formato legivel
    """
    cpf_hash = hash_cpf(cpf)
    cpf_parcial = f"***{cpf[3:9]}**" if len(cpf) >= 11 else "***"

    consentimentos = [
        {
            "finalidade": c["finalidade"],
            "data": c["data_consentimento"],
            "canal": c["canal"],
            "revogado": c["revogado"],
        }
        for c in _consentimentos
        if c["cpf_hash"] == cpf_hash
    ]

    acessos = [
        a for a in _log_auditoria
        if a.get("cpf_hash") == cpf_hash
    ]

    return {
        "titular": {
            "cpf_parcial": cpf_parcial,
            "data_export": datetime.now().isoformat(),
        },
        "consentimentos": consentimentos,
        "acessos_registrados": len(acessos),
        "formatos_disponiveis": ["json", "pdf"],
        "mensagem": "Estes sao todos os dados que temos sobre voce.",
    }


# =============================================================================
# Direito ao esquecimento (Art. 18, VI)
# =============================================================================

def excluir_dados(cpf: str, confirmar: bool = False) -> Dict[str, Any]:
    """Exclui todos os dados do cidadao.

    Args:
        cpf: CPF do cidadao
        confirmar: Se True, executa a exclusao

    Returns:
        dict com confirmacao ou aviso
    """
    if not confirmar:
        return {
            "aviso": (
                "Isso vai apagar TODOS os seus dados do Ta na Mao. "
                "Voce NAO vai perder seus beneficios - eles continuam normais. "
                "So apagamos o que esta aqui no app."
            ),
            "confirmar": "Envie novamente com confirmar=True para excluir.",
        }

    cpf_hash = hash_cpf(cpf)

    # Remover consentimentos
    global _consentimentos
    antes = len(_consentimentos)
    _consentimentos = [c for c in _consentimentos if c["cpf_hash"] != cpf_hash]
    removidos = antes - len(_consentimentos)

    # Registrar exclusao (sem dados pessoais)
    _log_auditoria.append({
        "tipo": "exclusao_dados",
        "cpf_hash": cpf_hash,
        "timestamp": datetime.now().isoformat(),
        "registros_removidos": removidos,
    })

    return {
        "sucesso": True,
        "registros_removidos": removidos,
        "mensagem": (
            "Seus dados foram apagados do Ta na Mao. "
            "Isso NAO afeta seus beneficios - eles continuam normais. "
            "Se quiser usar de novo no futuro, eh so entrar normalmente."
        ),
    }


# =============================================================================
# Auditoria de acessos
# =============================================================================

def registrar_acesso(
    endpoint: str,
    metodo: str,
    ip: Optional[str] = None,
    status_code: int = 200,
) -> None:
    """Registra acesso a dados pessoais na trilha de auditoria.

    NAO registra payload ou dados pessoais, apenas o fato do acesso.
    """
    _log_auditoria.append({
        "tipo": "acesso",
        "endpoint": endpoint,
        "metodo": metodo,
        "ip_hash": hash_ip(ip) if ip else None,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat(),
    })


# =============================================================================
# Tool wrapper para o agente
# =============================================================================

def consultar_politica_privacidade() -> Dict[str, Any]:
    """Retorna politica de privacidade em linguagem simples.

    Returns:
        dict com explicacao dos direitos do cidadao
    """
    return {
        "titulo": "Seus dados estao seguros",
        "o_que_fazemos": [
            "Consultamos seus beneficios usando seu CPF",
            "NUNCA guardamos seu CPF depois da consulta",
            "NUNCA compartilhamos seus dados com ninguem",
            "NUNCA vendemos seus dados",
        ],
        "seus_direitos": [
            "Ver todos os dados que temos sobre voce",
            "Apagar seus dados a qualquer momento",
            "Revogar permissao de uso",
            "Receber seus dados em formato digital",
        ],
        "como_exercer": {
            "ver_dados": "Pergunte: 'quais dados voces tem sobre mim?'",
            "apagar_dados": "Pergunte: 'apaguem meus dados'",
            "revogar": "Pergunte: 'revogar minha permissao'",
        },
        "base_legal": "LGPD - Lei Geral de Protecao de Dados (Lei 13.709/2018)",
        "contato_dpo": "dpo@tanamao.com.br",
    }


def _mensagem_consentimento(finalidade: str) -> str:
    """Gera mensagem de consentimento em linguagem simples."""
    mensagens = {
        "consulta_beneficio": (
            "Para consultar seus beneficios, vou usar seu CPF. "
            "Nao guardo seus dados depois e nao compartilho com ninguem."
        ),
        "elegibilidade": (
            "Para verificar seus direitos, vou usar CPF, renda e familia. "
            "Apago tudo em 24 horas."
        ),
        "farmacia": (
            "Para pedir remedios, preciso de CPF e receita. "
            "Guardo por 30 dias e depois apago."
        ),
        "encaminhamento_cras": (
            "Para gerar sua carta, preciso de nome, CPF e endereco. "
            "Guardo por 90 dias."
        ),
        "pesquisa": (
            "A pesquisa eh 100% anonima. Nao pego nome nem CPF."
        ),
    }
    return mensagens.get(finalidade, "Seus dados serao tratados conforme a LGPD.")
