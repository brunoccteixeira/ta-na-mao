"""
Tools para o modo Acompanhante Digital.

Interface simplificada para agentes comunitarios (ACS),
assistentes sociais (CRAS) e familiares ajudarem cidadaos
com baixa literacia digital a navegar a plataforma.

Funcionalidades:
- Perfis de acompanhante (ACS, assistente social, familiar)
- Checklist pre-visita CRAS personalizado
- Registro anonimizado de atendimento
- Orientacao passo-a-passo guiado
"""

import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class PerfilAcompanhante(str, Enum):
    ACS = "acs"                # Agente Comunitario de Saude
    ASSISTENTE_SOCIAL = "assistente_social"  # Assistente Social (CRAS)
    FAMILIAR = "familiar"      # Familiar / vizinho


class ResultadoAtendimento(str, Enum):
    BENEFICIO_ENCONTRADO = "beneficio_encontrado"
    ENCAMINHADO_CRAS = "encaminhado_cras"
    CHECKLIST_GERADO = "checklist_gerado"
    CONSULTA_REALIZADA = "consulta_realizada"
    SEM_RESULTADO = "sem_resultado"


# =============================================================================
# Perfis de acompanhante
# =============================================================================

_PERFIS = {
    PerfilAcompanhante.ACS: {
        "titulo": "Agente Comunitario de Saude (ACS)",
        "contexto": "Visitas domiciliares, cadastramento de familias, identificacao de vulnerabilidades",
        "permissoes": [
            "Consultar beneficios disponiveis",
            "Preencher formularios",
            "Gerar checklist de documentos",
            "Buscar CRAS e farmacias",
        ],
        "restricoes": [
            "Sem acesso a dados financeiros detalhados",
            "Sem alteracao de cadastro",
        ],
        "instrucoes_acompanhante": (
            "Como ACS, voce pode ajudar a familia a:\n"
            "1. Descobrir quais beneficios tem direito\n"
            "2. Preparar documentos para o CRAS\n"
            "3. Encontrar farmacias credenciadas\n"
            "4. Preencher formularios juntos"
        ),
    },
    PerfilAcompanhante.ASSISTENTE_SOCIAL: {
        "titulo": "Assistente Social (CRAS)",
        "contexto": "Atendimento presencial no CRAS, pre-triagem, encaminhamento",
        "permissoes": [
            "Consulta completa de beneficios",
            "Pre-atendimento",
            "Gerar cartas de encaminhamento",
            "Checklist personalizado",
        ],
        "restricoes": [
            "Cadastro usa sistema proprio do CadUnico",
        ],
        "instrucoes_acompanhante": (
            "Como assistente social, voce pode:\n"
            "1. Fazer pre-triagem do cidadao\n"
            "2. Consultar beneficios por CPF\n"
            "3. Gerar checklist personalizado\n"
            "4. Preparar encaminhamento para outros servicos"
        ),
    },
    PerfilAcompanhante.FAMILIAR: {
        "titulo": "Familiar ou Vizinho",
        "contexto": "Ajuda informal para pessoa com baixa literacia digital",
        "permissoes": [
            "Navegacao guiada",
            "Leitura de resultados",
            "Buscar informacoes gerais",
        ],
        "restricoes": [
            "CPF completo nao eh exibido",
            "Sem acesso a dados sensiveis",
        ],
        "instrucoes_acompanhante": (
            "Voce esta ajudando alguem a usar o Ta na Mao.\n"
            "Dicas:\n"
            "1. Leia em voz alta os resultados\n"
            "2. Explique com suas palavras\n"
            "3. Anote as informacoes importantes\n"
            "4. Se precisar de CPF, peca para a pessoa digitar"
        ),
    },
}


# =============================================================================
# Tool: iniciar_modo_acompanhante
# =============================================================================

def iniciar_modo_acompanhante(
    perfil: str,
    nome_acompanhante: Optional[str] = None,
    municipio: Optional[str] = None,
) -> dict:
    """Inicia o modo acompanhante digital.

    Configura o perfil e retorna instrucoes para o acompanhante
    e conteudo para o cidadao.

    Args:
        perfil: Tipo de acompanhante: acs, assistente_social, familiar
        nome_acompanhante: Nome do acompanhante (opcional, para personalizacao)
        municipio: Municipio do atendimento (para metricas)

    Returns:
        dict com instrucoes, permissoes e passo-a-passo
    """
    logger.info(f"Iniciando modo acompanhante: perfil={perfil}")

    try:
        perfil_enum = PerfilAcompanhante(perfil.lower())
    except ValueError:
        return {
            "erro": f"Perfil '{perfil}' nao reconhecido.",
            "perfis_disponiveis": [p.value for p in PerfilAcompanhante],
        }

    info = _PERFIS[perfil_enum]

    return {
        "modo_ativo": True,
        "perfil": perfil_enum.value,
        "titulo": info["titulo"],
        "instrucoes_acompanhante": info["instrucoes_acompanhante"],
        "permissoes": info["permissoes"],
        "restricoes": info["restricoes"],
        "conteudo_cidadao": (
            "Uma pessoa esta te ajudando a usar o Ta na Mao.\n\n"
            "Voce pode pedir:\n"
            "- Ver seus beneficios\n"
            "- Saber quais documentos precisa\n"
            "- Encontrar o CRAS ou farmacia perto de voce\n\n"
            "E so falar o que precisa!"
        ),
        "passos_sugeridos": _gerar_passos_sugeridos(perfil_enum),
        "municipio": municipio,
    }


def _gerar_passos_sugeridos(perfil: PerfilAcompanhante) -> List[Dict[str, str]]:
    """Gera passos sugeridos para o acompanhante."""
    passos_comuns = [
        {
            "numero": "1",
            "titulo": "Perguntar o que precisa",
            "instrucao_acompanhante": "Pergunte ao cidadao: 'Voce sabe qual ajuda do governo precisa?'",
            "conteudo_cidadao": "Que tipo de ajuda voce precisa hoje?",
        },
        {
            "numero": "2",
            "titulo": "Consultar beneficios",
            "instrucao_acompanhante": "Se o cidadao tem CPF, peca para digitar. Vamos consultar os beneficios.",
            "conteudo_cidadao": "Digite seu CPF para eu ver quais ajudas voce pode receber.",
        },
        {
            "numero": "3",
            "titulo": "Gerar checklist",
            "instrucao_acompanhante": "Vamos gerar a lista de documentos. Confira com o cidadao se tem todos.",
            "conteudo_cidadao": "Vou preparar a lista de documentos que voce precisa levar.",
        },
        {
            "numero": "4",
            "titulo": "Buscar local de atendimento",
            "instrucao_acompanhante": "Busque o CRAS ou farmacia mais perto. Anote o endereco e telefone.",
            "conteudo_cidadao": "Vou mostrar onde voce deve ir, com endereco e telefone.",
        },
    ]

    if perfil == PerfilAcompanhante.ACS:
        passos_comuns.append({
            "numero": "5",
            "titulo": "Registrar visita",
            "instrucao_acompanhante": "Registre o atendimento no seu caderno de visitas e no sistema.",
            "conteudo_cidadao": "Pronto! O agente de saude vai anotar tudo pra voce nao esquecer.",
        })

    return passos_comuns


# =============================================================================
# Tool: gerar_checklist_pre_visita
# =============================================================================

def gerar_checklist_pre_visita(
    programa: str,
    nome_cidadao: Optional[str] = None,
    composicao_familiar: int = 1,
    tem_filhos: bool = False,
    idoso: bool = False,
    gestante: bool = False,
    deficiencia: bool = False,
) -> dict:
    """Gera checklist personalizado para pre-visita ao CRAS.

    Diferente do checklist basico, este inclui:
    - Dicas para o cidadao (leve originais E copias)
    - Horario recomendado (chegar cedo)
    - Estimativa de tempo
    - Formato imprimivel

    Args:
        programa: Programa desejado (CADUNICO, BOLSA_FAMILIA, BPC, TSEE)
        nome_cidadao: Nome do cidadao (para personalizar)
        composicao_familiar: Numero de pessoas na familia
        tem_filhos: Se tem filhos menores de 18
        idoso: Se tem 65+ anos
        gestante: Se esta gravida
        deficiencia: Se tem deficiencia

    Returns:
        dict com checklist completo e dicas
    """
    logger.info(f"Gerando checklist pre-visita: programa={programa}")

    programa = programa.upper()

    # Documentos base por programa
    docs_base = {
        "CADUNICO": [
            "RG ou certidao de nascimento de TODOS da familia",
            "CPF de TODOS da familia",
            "Comprovante de endereco recente (conta de luz ou agua)",
            "Carteira de trabalho (mesmo sem registro)",
            "Comprovante de renda (se trabalha)",
        ],
        "BOLSA_FAMILIA": [
            "Todos os documentos do CadUnico (acima)",
            "Certidao de nascimento dos filhos",
            "Cartao de vacinacao dos filhos",
            "Comprovante de matricula escolar dos filhos",
        ],
        "BPC": [
            "RG e CPF do requerente",
            "Comprovante de endereco",
            "Laudo medico (para deficiencia)",
            "Comprovante de renda de TODOS da familia",
            "CadUnico atualizado (fazer primeiro se nao tem)",
        ],
        "TSEE": [
            "CPF do titular da conta de luz",
            "Conta de luz recente",
            "Comprovante de inscricao no CadUnico",
            "NIS (Numero de Identificacao Social)",
        ],
    }

    documentos = docs_base.get(programa, docs_base["CADUNICO"])

    # Adicionar documentos extras conforme situacao
    extras = []
    if tem_filhos:
        extras.append("Certidao de nascimento de cada filho")
        extras.append("Cartao de vacinacao atualizado")
        extras.append("Declaracao escolar dos filhos (6-17 anos)")
    if gestante:
        extras.append("Cartao de pre-natal")
        extras.append("Exame que comprova a gravidez")
    if deficiencia:
        extras.append("Laudo medico com CID (codigo da doenca)")
        extras.append("Laudos de exames complementares")
    if idoso and programa == "BPC":
        extras.append("Certidao de nascimento ou casamento")

    # Dicas de preparacao
    dicas = [
        "Leve documentos ORIGINAIS e COPIAS de tudo",
        "Chegue cedo (de preferencia antes das 8h)",
        "Leve um lanche e agua (pode demorar)",
        "Se tiver celular, leve carregado (pode precisar do app Gov.br)",
    ]

    if composicao_familiar > 1:
        dicas.append(f"Leve documentos de TODAS as {composicao_familiar} pessoas da familia")
    if programa == "BPC":
        dicas.append("O laudo medico eh OBRIGATORIO - sem ele nao consegue protocolar")

    # Estimativa de tempo
    tempo_estimado = "1 a 2 horas"
    if programa == "BPC":
        tempo_estimado = "2 a 3 horas (tem pericia)"
    elif programa == "CADUNICO" and composicao_familiar > 3:
        tempo_estimado = "1 a 3 horas (familia grande, mais dados para preencher)"

    saudacao = f"Ola{', ' + nome_cidadao if nome_cidadao else ''}!"

    return {
        "programa": programa,
        "saudacao": saudacao,
        "documentos_obrigatorios": documentos,
        "documentos_extras": extras,
        "total_documentos": len(documentos) + len(extras),
        "dicas_preparacao": dicas,
        "tempo_estimado": tempo_estimado,
        "horario_recomendado": "Chegue antes das 8h da manha",
        "o_que_acontece_no_cras": _descrever_fluxo_cras(programa),
        "formato_imprimivel": _formatar_para_impressao(
            programa, documentos, extras, dicas, nome_cidadao
        ),
    }


def _descrever_fluxo_cras(programa: str) -> List[str]:
    """Descreve o que acontece no CRAS passo a passo."""
    fluxos = {
        "CADUNICO": [
            "1. Voce chega e pega uma senha na recepcao",
            "2. Espera ser chamado (pode demorar, leve um lanche)",
            "3. O atendente vai pedir seus documentos",
            "4. Ele vai perguntar sobre todos da familia (nome, idade, renda)",
            "5. Voce assina o formulario",
            "6. Recebe o numero do NIS na hora",
        ],
        "BOLSA_FAMILIA": [
            "1. Primeiro precisa ter o CadUnico atualizado",
            "2. Se nao tem, faz o CadUnico no mesmo dia",
            "3. O sistema avalia automaticamente se voce tem direito",
            "4. Se aprovado, o cartao chega em 30-45 dias",
            "5. O pagamento cai todo mes no app Caixa Tem",
        ],
        "BPC": [
            "1. Precisa ter CadUnico atualizado",
            "2. Leve o laudo medico (para deficiencia)",
            "3. O assistente social faz uma avaliacao",
            "4. Voce sera agendado para pericia medica no INSS",
            "5. Resultado sai em 30-90 dias",
            "6. Se aprovado, recebe 1 salario minimo por mes",
        ],
        "TSEE": [
            "1. Se ja tem CadUnico, nao precisa ir ao CRAS",
            "2. Va a distribuidora de energia com NIS e conta de luz",
            "3. Desconto eh aplicado na proxima conta",
            "4. Se nao tem CadUnico, faca primeiro no CRAS",
        ],
    }
    return fluxos.get(programa, fluxos["CADUNICO"])


def _formatar_para_impressao(
    programa: str,
    documentos: list,
    extras: list,
    dicas: list,
    nome: Optional[str],
) -> str:
    """Formata checklist para impressao (texto puro)."""
    linhas = []
    linhas.append("=" * 50)
    linhas.append("CHECKLIST - TA NA MAO")
    linhas.append(f"Programa: {programa}")
    if nome:
        linhas.append(f"Cidadao: {nome}")
    linhas.append(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    linhas.append("=" * 50)
    linhas.append("")
    linhas.append("DOCUMENTOS OBRIGATORIOS:")
    for i, doc in enumerate(documentos, 1):
        linhas.append(f"  [ ] {i}. {doc}")
    if extras:
        linhas.append("")
        linhas.append("DOCUMENTOS EXTRAS (para sua situacao):")
        for i, doc in enumerate(extras, 1):
            linhas.append(f"  [ ] {i}. {doc}")
    linhas.append("")
    linhas.append("DICAS:")
    for dica in dicas:
        linhas.append(f"  * {dica}")
    linhas.append("")
    linhas.append("=" * 50)

    return "\n".join(linhas)


# =============================================================================
# Tool: registrar_atendimento
# =============================================================================

def registrar_atendimento(
    perfil_acompanhante: str,
    acoes_realizadas: List[str],
    resultado: str,
    municipio: Optional[str] = None,
    cpf_cidadao: Optional[str] = None,
) -> dict:
    """Registra atendimento de forma anonimizada.

    IMPORTANTE: CPF nunca eh armazenado - apenas hash.
    Dados sao agregados por municipio para metricas de impacto.

    Args:
        perfil_acompanhante: acs, assistente_social, familiar
        acoes_realizadas: Lista de acoes: consulta, checklist, encaminhamento, etc
        resultado: Resultado do atendimento (ver ResultadoAtendimento)
        municipio: Municipio do atendimento
        cpf_cidadao: CPF do cidadao (sera hasheado, NUNCA armazenado)

    Returns:
        dict com confirmacao do registro
    """
    # Hash do CPF (NUNCA armazenar texto plano)
    cpf_hash = ""
    if cpf_cidadao:
        cpf_limpo = cpf_cidadao.replace(".", "").replace("-", "")
        cpf_hash = hashlib.sha256(cpf_limpo.encode()).hexdigest()[:16]

    registro = {
        "timestamp": datetime.now().isoformat(),
        "perfil_acompanhante": perfil_acompanhante,
        "acoes_realizadas": acoes_realizadas,
        "resultado": resultado,
        "municipio": municipio or "nao_informado",
        "cpf_hash": cpf_hash,
    }

    logger.info(
        f"Atendimento registrado: perfil={perfil_acompanhante}, "
        f"acoes={len(acoes_realizadas)}, resultado={resultado}, "
        f"municipio={municipio}"
    )

    # Em producao, salvar no banco de dados
    # Por enquanto, apenas loga

    return {
        "registrado": True,
        "id_atendimento": hashlib.md5(
            f"{registro['timestamp']}{cpf_hash}".encode()
        ).hexdigest()[:12],
        "mensagem": "Atendimento registrado com sucesso!",
        "resumo": {
            "perfil": perfil_acompanhante,
            "total_acoes": len(acoes_realizadas),
            "resultado": resultado,
            "municipio": municipio,
        },
    }


# =============================================================================
# Tool: obter_orientacao_passo_a_passo
# =============================================================================

def obter_orientacao_passo_a_passo(
    objetivo: str,
    passo_atual: int = 1,
    perfil_acompanhante: Optional[str] = None,
) -> dict:
    """Retorna orientacao passo-a-passo para um objetivo.

    Cada passo inclui:
    - Instrucao para o acompanhante (se houver)
    - Conteudo para o cidadao (linguagem simples, fonte grande)
    - Acao sugerida

    Args:
        objetivo: O que o cidadao quer fazer:
            CONSULTAR_BENEFICIOS, FAZER_CADUNICO, PEDIR_REMEDIO,
            ATUALIZAR_CADUNICO, PEDIR_BPC
        passo_atual: Numero do passo atual (1-indexed)
        perfil_acompanhante: Perfil do acompanhante (para instrucoes)

    Returns:
        dict com o passo atual, total de passos e conteudo
    """
    logger.info(f"Orientacao passo-a-passo: objetivo={objetivo}, passo={passo_atual}")

    objetivo = objetivo.upper().replace(" ", "_")

    passos = _PASSOS_POR_OBJETIVO.get(objetivo)
    if not passos:
        return {
            "erro": f"Objetivo '{objetivo}' nao reconhecido.",
            "objetivos_disponiveis": list(_PASSOS_POR_OBJETIVO.keys()),
        }

    total_passos = len(passos)
    if passo_atual < 1 or passo_atual > total_passos:
        return {
            "erro": f"Passo {passo_atual} invalido. Total de passos: {total_passos}.",
        }

    passo = passos[passo_atual - 1]

    return {
        "objetivo": objetivo,
        "passo_atual": passo_atual,
        "total_passos": total_passos,
        "progresso": f"{passo_atual}/{total_passos}",
        "titulo": passo["titulo"],
        "instrucao_acompanhante": passo.get("instrucao_acompanhante", ""),
        "conteudo_cidadao": passo["conteudo_cidadao"],
        "acao_sugerida": passo.get("acao", ""),
        "proximo_passo": passo_atual < total_passos,
        "dica": passo.get("dica", ""),
    }


# =============================================================================
# Passos por objetivo
# =============================================================================

_PASSOS_POR_OBJETIVO = {
    "CONSULTAR_BENEFICIOS": [
        {
            "titulo": "Informar o CPF",
            "instrucao_acompanhante": "Peca para o cidadao digitar o CPF dele. Se nao souber, veja no RG ou cartao do SUS.",
            "conteudo_cidadao": "Digite seu CPF (os 11 numeros) para eu ver seus beneficios.",
            "acao": "Digitar CPF",
            "dica": "O CPF tem 11 numeros. Esta no RG, cartao do SUS ou carteira de trabalho.",
        },
        {
            "titulo": "Ver resultados",
            "instrucao_acompanhante": "Leia os resultados em voz alta para o cidadao. Explique cada beneficio de forma simples.",
            "conteudo_cidadao": "Aqui estao os beneficios que voce recebe. Vou ler pra voce.",
            "acao": "Consultar beneficios",
        },
        {
            "titulo": "Verificar novos beneficios",
            "instrucao_acompanhante": "Pergunte se o cidadao quer saber se tem direito a outros beneficios.",
            "conteudo_cidadao": "Quer saber se voce tem direito a mais alguma ajuda do governo?",
            "acao": "Verificar elegibilidade",
        },
    ],
    "FAZER_CADUNICO": [
        {
            "titulo": "Juntar documentos",
            "instrucao_acompanhante": "Gere o checklist de documentos e confira com o cidadao quais ja tem.",
            "conteudo_cidadao": "Primeiro, vamos ver quais documentos voce precisa levar ao CRAS.",
            "acao": "Gerar checklist",
        },
        {
            "titulo": "Encontrar o CRAS",
            "instrucao_acompanhante": "Busque o CRAS mais proximo. Anote endereco e telefone para o cidadao.",
            "conteudo_cidadao": "Vou mostrar onde fica o CRAS perto da sua casa, com endereco e telefone.",
            "acao": "Buscar CRAS",
            "dica": "Pergunte o CEP ou endereco do cidadao.",
        },
        {
            "titulo": "Preparar para a visita",
            "instrucao_acompanhante": "Confira se o cidadao entendeu tudo: documentos, endereco, horario. Imprima o checklist se possivel.",
            "conteudo_cidadao": "Pronto! Leve todos os documentos da lista ao CRAS. Chegue cedo de manha.",
            "acao": "Imprimir checklist",
        },
    ],
    "PEDIR_REMEDIO": [
        {
            "titulo": "Preparar receita",
            "instrucao_acompanhante": "Pergunte se o cidadao tem a receita medica. Pode ser foto ou digitar o nome dos remedios.",
            "conteudo_cidadao": "Voce tem a receita do medico? Pode tirar uma foto ou falar o nome dos remedios.",
            "acao": "Enviar receita",
        },
        {
            "titulo": "Encontrar farmacia",
            "instrucao_acompanhante": "Busque farmacias credenciadas no Farmacia Popular perto do cidadao.",
            "conteudo_cidadao": "Vou mostrar as farmacias perto de voce onde os remedios sao de graca.",
            "acao": "Buscar farmacia",
        },
        {
            "titulo": "Orientar ida a farmacia",
            "instrucao_acompanhante": "Explique que eh so ir na farmacia com CPF e receita. NAO precisa ir ao CRAS.",
            "conteudo_cidadao": "E so ir na farmacia com seu CPF e a receita do medico. Os remedios sao de graca!",
            "acao": "Concluir",
            "dica": "A receita medica tem validade. Confira se nao esta vencida.",
        },
    ],
    "ATUALIZAR_CADUNICO": [
        {
            "titulo": "Verificar situacao atual",
            "instrucao_acompanhante": "Peca o CPF do cidadao para verificar quando foi a ultima atualizacao.",
            "conteudo_cidadao": "Vou verificar se seu CadUnico esta em dia. Me fala seu CPF.",
            "acao": "Verificar CadUnico",
        },
        {
            "titulo": "Juntar documentos atualizados",
            "instrucao_acompanhante": "Se o cadastro precisa ser atualizado, gere o checklist e confira os documentos.",
            "conteudo_cidadao": "Precisa atualizar! Vou preparar a lista de documentos que voce precisa levar.",
            "acao": "Gerar checklist",
        },
        {
            "titulo": "Ir ao CRAS",
            "instrucao_acompanhante": "Busque o CRAS e explique a importancia de atualizar (pode perder beneficios se nao atualizar).",
            "conteudo_cidadao": "Leve os documentos ao CRAS para atualizar. Se nao atualizar, pode perder o beneficio!",
            "acao": "Buscar CRAS",
        },
    ],
    "PEDIR_BPC": [
        {
            "titulo": "Verificar requisitos",
            "instrucao_acompanhante": "Pergunte: tem 65+ anos OU deficiencia? Renda familiar eh baixa? Tem CadUnico?",
            "conteudo_cidadao": "O BPC paga 1 salario minimo por mes para idosos (65+) e pessoas com deficiencia.",
            "acao": "Verificar elegibilidade",
        },
        {
            "titulo": "Atualizar CadUnico",
            "instrucao_acompanhante": "O CadUnico PRECISA estar atualizado para pedir BPC. Se nao tem, faca primeiro.",
            "conteudo_cidadao": "Para pedir o BPC, seu CadUnico precisa estar em dia. Vamos verificar.",
            "acao": "Verificar CadUnico",
        },
        {
            "titulo": "Juntar documentos",
            "instrucao_acompanhante": "Gere checklist do BPC. Laudo medico eh OBRIGATORIO para deficiencia.",
            "conteudo_cidadao": "Vou preparar a lista de documentos. Se for por deficiencia, precisa de laudo medico.",
            "acao": "Gerar checklist",
        },
        {
            "titulo": "Dar entrada no CRAS",
            "instrucao_acompanhante": "Explique que apos o CRAS, tera pericia no INSS. Resultado em 30-90 dias.",
            "conteudo_cidadao": "Leve tudo ao CRAS. Depois voce sera chamado para uma avaliacao no INSS.",
            "acao": "Buscar CRAS",
        },
    ],
}
