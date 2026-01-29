"""
Tool para Pré-Atendimento CRAS.

Prepara TUDO digitalmente antes do atendimento presencial:
- Coleta dados do cidadão
- Gera checklist de documentos necessários
- Indica CRAS mais próximo
- Reduz tempo de atendimento de 2h para 30min
"""

from datetime import datetime
from typing import Optional, Dict, Any, List

from app.agent.tools.base import ToolResult, UIHint


# =============================================================================
# Documentos necessários por situação
# =============================================================================

DOCUMENTOS_BASE = [
    {
        "nome": "RG ou CNH",
        "nome_simples": "Documento com foto (RG ou carteira de motorista)",
        "obrigatorio": True,
        "dica": "Pode ser RG, CNH ou Carteira de Trabalho",
        "todos_familia": True
    },
    {
        "nome": "CPF",
        "nome_simples": "CPF de todos da família",
        "obrigatorio": True,
        "dica": "Pode consultar no site da Receita Federal se não tiver o cartão",
        "todos_familia": True
    },
    {
        "nome": "Comprovante de Residência",
        "nome_simples": "Conta de luz, água ou telefone com seu endereço",
        "obrigatorio": True,
        "dica": "Pode ser dos últimos 3 meses. Se não tiver no seu nome, leve declaração do dono",
        "todos_familia": False
    },
    {
        "nome": "Certidão de Nascimento ou Casamento",
        "nome_simples": "Certidão de nascimento de cada pessoa da família",
        "obrigatorio": True,
        "dica": "Para menores de idade, é obrigatório",
        "todos_familia": True
    }
]

DOCUMENTOS_RENDA = [
    {
        "nome": "Carteira de Trabalho",
        "nome_simples": "Carteira de trabalho (física ou digital)",
        "obrigatorio": False,
        "situacao": "trabalha_formal",
        "dica": "Pode ser a digital (app CTPS Digital)"
    },
    {
        "nome": "Comprovante de Renda",
        "nome_simples": "Contracheque ou declaração de renda",
        "obrigatorio": False,
        "situacao": "trabalha_formal",
        "dica": "Últimos 3 meses. Se autônomo, faça uma declaração simples"
    },
    {
        "nome": "Declaração de Autônomo",
        "nome_simples": "Declaração escrita à mão de quanto você ganha",
        "obrigatorio": False,
        "situacao": "autonomo",
        "dica": "Escreva quanto ganha por mês em média"
    },
    {
        "nome": "Declaração de Desemprego",
        "nome_simples": "Declaração de que não está trabalhando",
        "obrigatorio": False,
        "situacao": "desempregado",
        "dica": "Pode ser feita à mão, dizendo que está desempregado"
    }
]

DOCUMENTOS_ESPECIAIS = [
    {
        "nome": "Laudo Médico",
        "nome_simples": "Papel do médico dizendo qual é a deficiência ou doença",
        "obrigatorio": True,
        "situacao": "deficiencia",
        "dica": "Precisa ter CID (código da doença) e carimbo do médico"
    },
    {
        "nome": "Comprovante de Matrícula Escolar",
        "nome_simples": "Declaração da escola de cada filho",
        "obrigatorio": True,
        "situacao": "tem_filhos",
        "dica": "Pegue na secretaria da escola"
    },
    {
        "nome": "Cartão de Vacina",
        "nome_simples": "Caderneta de vacina das crianças",
        "obrigatorio": True,
        "situacao": "tem_filhos_pequenos",
        "dica": "Crianças até 7 anos precisam estar com vacinas em dia"
    },
    {
        "nome": "Comprovante de Gestação",
        "nome_simples": "Cartão do pré-natal ou exame de gravidez",
        "obrigatorio": True,
        "situacao": "gestante",
        "dica": "Pegue no posto de saúde"
    }
]


def preparar_pre_atendimento_cras(
    programa: str,
    nome: Optional[str] = None,
    cpf: Optional[str] = None,
    composicao_familiar: Optional[int] = None,
    tem_filhos: bool = False,
    tem_filhos_pequenos: bool = False,
    idoso: bool = False,
    gestante: bool = False,
    deficiencia: bool = False,
    trabalha_formal: bool = False,
    autonomo: bool = False,
    desempregado: bool = True
) -> ToolResult:
    """
    Prepara pré-atendimento para ida ao CRAS.

    Gera checklist personalizada de documentos baseada na situação do cidadão.

    Args:
        programa: Programa desejado (CADUNICO, BOLSA_FAMILIA, BPC, etc)
        nome: Nome do cidadão
        cpf: CPF do cidadão
        composicao_familiar: Número de pessoas na família
        tem_filhos: Se tem filhos menores de 18 anos
        tem_filhos_pequenos: Se tem filhos até 7 anos
        idoso: Se tem 65 anos ou mais
        gestante: Se está grávida
        deficiencia: Se tem deficiência
        trabalha_formal: Se trabalha com carteira assinada
        autonomo: Se trabalha por conta própria
        desempregado: Se está desempregado

    Returns:
        ToolResult com checklist e orientações
    """
    # Monta situação do cidadão
    situacao = {
        "tem_filhos": tem_filhos,
        "tem_filhos_pequenos": tem_filhos_pequenos,
        "idoso": idoso,
        "gestante": gestante,
        "deficiencia": deficiencia,
        "trabalha_formal": trabalha_formal,
        "autonomo": autonomo,
        "desempregado": desempregado
    }

    # Gera checklist personalizada
    checklist = _gerar_checklist_documentos(programa, situacao, composicao_familiar)

    # Informações do programa
    info_programa = _get_info_programa(programa)

    # Tempo estimado de atendimento
    tempo_estimado = _calcular_tempo_estimado(len(checklist), composicao_familiar or 1)

    # Dicas para o atendimento
    dicas = _gerar_dicas_atendimento(programa, situacao)

    # Gera resumo em linguagem simples
    resumo = _gerar_resumo_pre_atendimento(
        programa=programa,
        nome=nome,
        checklist=checklist,
        tempo_estimado=tempo_estimado
    )

    return ToolResult.ok(
        data={
            "programa": programa,
            "programa_nome": info_programa["nome"],
            "nome_cidadao": nome,
            "situacao": situacao,
            "checklist": checklist,
            "total_documentos": len(checklist),
            "documentos_obrigatorios": len([d for d in checklist if d["obrigatorio"]]),
            "tempo_estimado_minutos": tempo_estimado,
            "tempo_estimado_texto": f"{tempo_estimado} minutos" if tempo_estimado < 60 else f"{tempo_estimado // 60}h{tempo_estimado % 60:02d}",
            "dicas": dicas,
            "proximos_passos": info_programa.get("proximos_passos", []),
            "resumo_simples": resumo,
            "pode_gerar_pdf": True
        },
        ui_hint=UIHint.CHECKLIST,
        context_updates={
            "pre_atendimento_preparado": True,
            "programa_desejado": programa
        }
    )


def gerar_formulario_pre_cras(
    nome: str,
    cpf: str,
    data_nascimento: str,
    telefone: str,
    endereco: str,
    composicao_familiar: List[Dict[str, str]],
    renda_familiar: float,
    situacao_moradia: str = "PROPRIA",
    programa: str = "CADUNICO"
) -> ToolResult:
    """
    Gera formulário pré-preenchido para levar ao CRAS.

    Este formulário agiliza o atendimento pois o cidadão já chega
    com todos os dados preenchidos.

    Args:
        nome: Nome completo do responsável familiar
        cpf: CPF do responsável
        data_nascimento: Data de nascimento (DD/MM/AAAA)
        telefone: Telefone para contato
        endereco: Endereço completo
        composicao_familiar: Lista de membros da família
        renda_familiar: Renda total da família
        situacao_moradia: PROPRIA, ALUGADA, CEDIDA, OCUPACAO
        programa: Programa desejado

    Returns:
        ToolResult com formulário preenchido
    """
    # Calcula renda per capita
    num_pessoas = len(composicao_familiar) + 1  # +1 para o responsável
    renda_per_capita = renda_familiar / num_pessoas if num_pessoas > 0 else 0

    # Determina faixa de renda
    salario_minimo = 1412  # 2024
    if renda_per_capita <= salario_minimo * 0.25:
        faixa_renda = "EXTREMA_POBREZA"
        faixa_texto = "Extrema pobreza (até 1/4 salário mínimo por pessoa)"
    elif renda_per_capita <= salario_minimo * 0.5:
        faixa_renda = "POBREZA"
        faixa_texto = "Pobreza (até 1/2 salário mínimo por pessoa)"
    elif renda_per_capita <= salario_minimo:
        faixa_renda = "BAIXA_RENDA"
        faixa_texto = "Baixa renda (até 1 salário mínimo por pessoa)"
    else:
        faixa_renda = "ACIMA_LIMITE"
        faixa_texto = "Acima do limite de renda"

    # Monta formulário
    formulario = {
        "data_preenchimento": datetime.now().strftime("%d/%m/%Y"),
        "responsavel_familiar": {
            "nome": nome,
            "cpf": cpf,
            "data_nascimento": data_nascimento,
            "telefone": telefone
        },
        "endereco": endereco,
        "situacao_moradia": situacao_moradia,
        "composicao_familiar": composicao_familiar,
        "total_pessoas": num_pessoas,
        "renda_familiar_total": renda_familiar,
        "renda_familiar_formatada": f"R$ {renda_familiar:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "renda_per_capita": renda_per_capita,
        "renda_per_capita_formatada": f"R$ {renda_per_capita:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "faixa_renda": faixa_renda,
        "faixa_renda_texto": faixa_texto,
        "programa_solicitado": programa
    }

    # Verifica elegibilidade preliminar
    elegibilidade = _verificar_elegibilidade_preliminar(faixa_renda, programa)

    return ToolResult.ok(
        data={
            "formulario": formulario,
            "elegibilidade_preliminar": elegibilidade,
            "mensagem_simples": _gerar_mensagem_formulario(formulario, elegibilidade),
            "pode_gerar_pdf": True,
            "instrucoes": [
                "Imprima este formulário ou mostre no celular",
                "Leve todos os documentos da checklist",
                "Chegue cedo ao CRAS (filas são menores pela manhã)",
                "Peça um protocolo de atendimento"
            ]
        },
        ui_hint=UIHint.CHECKLIST
    )


def _gerar_checklist_documentos(
    programa: str,
    situacao: Dict[str, bool],
    composicao_familiar: Optional[int]
) -> List[Dict[str, Any]]:
    """Gera checklist personalizada de documentos."""
    checklist = []

    # Adiciona documentos base
    for doc in DOCUMENTOS_BASE:
        item = doc.copy()
        item["status"] = "pendente"
        if item.get("todos_familia") and composicao_familiar:
            item["quantidade"] = composicao_familiar
            item["nome_simples"] = f"{item['nome_simples']} (de todos os {composicao_familiar} da família)"
        checklist.append(item)

    # Adiciona documentos de renda baseado na situação
    for doc in DOCUMENTOS_RENDA:
        situacao_doc = doc.get("situacao")
        if situacao_doc and situacao.get(situacao_doc):
            item = doc.copy()
            item["status"] = "pendente"
            checklist.append(item)

    # Adiciona documentos especiais baseado na situação
    for doc in DOCUMENTOS_ESPECIAIS:
        situacao_doc = doc.get("situacao")
        if situacao_doc and situacao.get(situacao_doc):
            item = doc.copy()
            item["status"] = "pendente"
            checklist.append(item)

    # Documentos específicos por programa
    if programa == "BPC":
        # BPC precisa de laudo médico obrigatório para PCD
        if situacao.get("deficiencia"):
            # Já foi adicionado nos especiais
            pass
        checklist.append({
            "nome": "Comprovante de Renda de Todos",
            "nome_simples": "Comprovante de quanto cada pessoa da família ganha",
            "obrigatorio": True,
            "status": "pendente",
            "dica": "BPC exige renda familiar de até 1/4 do salário mínimo por pessoa"
        })

    return checklist


def _get_info_programa(programa: str) -> Dict[str, Any]:
    """Retorna informações sobre o programa."""
    programas = {
        "CADUNICO": {
            "nome": "CadÚnico (Cadastro Único)",
            "descricao": "Cadastro do governo para acessar programas sociais",
            "proximos_passos": [
                "Ir ao CRAS com documentos",
                "Fazer entrevista",
                "Aguardar processamento (até 15 dias úteis)"
            ]
        },
        "BOLSA_FAMILIA": {
            "nome": "Bolsa Família",
            "descricao": "Dinheiro todo mês para famílias em situação de pobreza",
            "proximos_passos": [
                "Ter CadÚnico atualizado",
                "Aguardar avaliação do governo federal",
                "Se aprovado, sacar com cartão ou Caixa Tem"
            ]
        },
        "BPC": {
            "nome": "BPC/LOAS",
            "descricao": "1 salário mínimo para idosos 65+ ou pessoas com deficiência",
            "proximos_passos": [
                "Ter CadÚnico atualizado",
                "Agendar perícia no INSS (para PCD)",
                "Aguardar análise (pode demorar alguns meses)"
            ]
        },
        "TSEE": {
            "nome": "Tarifa Social de Energia",
            "descricao": "Desconto de até 65% na conta de luz",
            "proximos_passos": [
                "Ter CadÚnico atualizado",
                "Solicitar na empresa de energia (conta de luz)",
                "Desconto começa na próxima conta"
            ]
        }
    }
    return programas.get(programa, {
        "nome": programa,
        "descricao": "Programa social",
        "proximos_passos": ["Consultar CRAS para mais informações"]
    })


def _calcular_tempo_estimado(num_documentos: int, composicao_familiar: int) -> int:
    """Calcula tempo estimado de atendimento em minutos."""
    # Base: 20 minutos
    tempo = 20
    # +5 minutos por documento adicional após os 4 básicos
    tempo += max(0, (num_documentos - 4) * 5)
    # +10 minutos por pessoa na família após a primeira
    tempo += max(0, (composicao_familiar - 1) * 10)
    return min(tempo, 120)  # Máximo 2 horas


def _gerar_dicas_atendimento(programa: str, situacao: Dict[str, bool]) -> List[str]:
    """Gera dicas para o atendimento."""
    dicas = [
        "Chegue cedo - as filas são menores pela manhã",
        "Leve todos os documentos ORIGINAIS e cópias",
        "Leve uma garrafa de água e um lanche",
        "Se possível, vá em dia de semana (evite segunda-feira)"
    ]

    if situacao.get("tem_filhos_pequenos"):
        dicas.append("Se puder, deixe as crianças pequenas com alguém")

    if situacao.get("idoso"):
        dicas.append("Idosos têm atendimento prioritário - informe na recepção")

    if situacao.get("deficiencia"):
        dicas.append("Pessoas com deficiência têm atendimento prioritário")

    if situacao.get("gestante"):
        dicas.append("Gestantes têm atendimento prioritário")

    return dicas


def _verificar_elegibilidade_preliminar(faixa_renda: str, programa: str) -> Dict[str, Any]:
    """Verifica elegibilidade preliminar baseada na renda."""
    if programa == "BOLSA_FAMILIA":
        if faixa_renda in ["EXTREMA_POBREZA", "POBREZA"]:
            return {
                "provavelmente_elegivel": True,
                "mensagem": "Sua família provavelmente tem direito ao Bolsa Família!"
            }
        else:
            return {
                "provavelmente_elegivel": False,
                "mensagem": "Sua renda pode estar acima do limite, mas vale tentar no CRAS."
            }

    elif programa == "BPC":
        if faixa_renda == "EXTREMA_POBREZA":
            return {
                "provavelmente_elegivel": True,
                "mensagem": "Sua renda está dentro do limite do BPC (até 1/4 salário mínimo por pessoa)."
            }
        else:
            return {
                "provavelmente_elegivel": False,
                "mensagem": "O BPC exige renda muito baixa. Converse com o CRAS para avaliar."
            }

    return {
        "provavelmente_elegivel": None,
        "mensagem": "Será avaliado no CRAS."
    }


def _gerar_resumo_pre_atendimento(
    programa: str,
    nome: Optional[str],
    checklist: List[Dict],
    tempo_estimado: int
) -> str:
    """Gera resumo em linguagem simples."""
    info = _get_info_programa(programa)

    partes = []
    if nome:
        partes.append(f"Olá, {nome}!")
    partes.append(f"\nPreparo para o atendimento no CRAS ({info['nome']}):")
    partes.append("")

    partes.append("DOCUMENTOS QUE VOCÊ VAI PRECISAR:")
    for i, doc in enumerate(checklist, 1):
        obrig = " (obrigatório)" if doc["obrigatorio"] else ""
        partes.append(f"{i}. {doc['nome_simples']}{obrig}")

    partes.append("")
    partes.append(f"Tempo estimado de atendimento: {tempo_estimado} minutos")
    partes.append("")
    partes.append("DICA: Chegue cedo e leve todos os documentos!")

    return "\n".join(partes)


def _gerar_mensagem_formulario(formulario: Dict, elegibilidade: Dict) -> str:
    """Gera mensagem sobre o formulário preenchido."""
    partes = [
        f"Formulário preparado para {formulario['responsavel_familiar']['nome']}!",
        "",
        f"Família com {formulario['total_pessoas']} pessoas",
        f"Renda por pessoa: {formulario['renda_per_capita_formatada']}",
        f"Faixa: {formulario['faixa_renda_texto']}",
        "",
        elegibilidade.get("mensagem", ""),
        "",
        "Leve este formulário ao CRAS junto com os documentos!"
    ]
    return "\n".join(partes)
