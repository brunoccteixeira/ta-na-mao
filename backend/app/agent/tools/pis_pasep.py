"""
Tools para PIS/PASEP - Abono Salarial 2026.

Inclui:
- Verificador de elegibilidade interativo
- Calendário personalizado por mês de nascimento
- Calculadora de valor do abono
- Guia passo a passo para saque

Abono PIS/PASEP 2026:
- Valor máximo: R$ 1.621 (salário mínimo 2026)
- Pagamento: Fevereiro a Agosto de 2026
- Prazo para sacar: Até 29 de dezembro de 2026
"""

from typing import Optional, Dict, Any
from datetime import date
from app.agent.tools.base import ToolResult, UIHint


# =============================================================================
# Constantes do Abono 2026
# =============================================================================

SALARIO_MINIMO_2026 = 1621  # Valor estimado para 2026
ANO_BASE = 2024  # Ano-base para o abono 2026
PRAZO_FINAL = "29 de dezembro de 2026"

# Calendário oficial de pagamento do PIS/PASEP 2026
# Baseado no mês de nascimento (PIS) ou final da inscrição (PASEP)
CALENDARIO_PIS_2026 = {
    1: {"mes_pagamento": "Fevereiro", "data": "15/02/2026", "inicio": "15/02/2026"},
    2: {"mes_pagamento": "Março", "data": "15/03/2026", "inicio": "15/03/2026"},
    3: {"mes_pagamento": "Abril", "data": "15/04/2026", "inicio": "15/04/2026"},
    4: {"mes_pagamento": "Abril", "data": "15/04/2026", "inicio": "15/04/2026"},
    5: {"mes_pagamento": "Maio", "data": "15/05/2026", "inicio": "15/05/2026"},
    6: {"mes_pagamento": "Maio", "data": "15/05/2026", "inicio": "15/05/2026"},
    7: {"mes_pagamento": "Junho", "data": "15/06/2026", "inicio": "15/06/2026"},
    8: {"mes_pagamento": "Junho", "data": "15/06/2026", "inicio": "15/06/2026"},
    9: {"mes_pagamento": "Julho", "data": "15/07/2026", "inicio": "15/07/2026"},
    10: {"mes_pagamento": "Julho", "data": "15/07/2026", "inicio": "15/07/2026"},
    11: {"mes_pagamento": "Agosto", "data": "15/08/2026", "inicio": "15/08/2026"},
    12: {"mes_pagamento": "Agosto", "data": "15/08/2026", "inicio": "15/08/2026"},
}

MESES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

# Limite de renda para ter direito ao abono
LIMITE_RENDA_MENSAL = 2766  # 2 salários mínimos de 2024


# =============================================================================
# Verificador de Elegibilidade
# =============================================================================

def verificar_elegibilidade_abono(
    trabalhou_2024: Optional[bool] = None,
    meses_trabalhados: Optional[int] = None,
    salario_mensal: Optional[float] = None,
    cadastrado_ha_5_anos: Optional[bool] = None
) -> ToolResult:
    """
    Verifica se cidadão tem direito ao Abono PIS/PASEP 2026.

    Critérios:
    - Estar cadastrado no PIS/PASEP há pelo menos 5 anos (desde 2020)
    - Ter trabalhado com carteira assinada por pelo menos 30 dias em 2024
    - Ter recebido em média até 2 salários mínimos por mês em 2024

    Args:
        trabalhou_2024: Se trabalhou com carteira em 2024
        meses_trabalhados: Quantos meses trabalhou em 2024
        salario_mensal: Salário médio mensal em 2024
        cadastrado_ha_5_anos: Se está cadastrado no PIS há 5+ anos

    Returns:
        ToolResult com status de elegibilidade e próximos passos
    """
    # Verificar se temos todas as informações necessárias
    informacoes_faltando = []

    if trabalhou_2024 is None:
        informacoes_faltando.append("se trabalhou com carteira em 2024")
    if meses_trabalhados is None:
        informacoes_faltando.append("quantos meses trabalhou")
    if salario_mensal is None:
        informacoes_faltando.append("quanto ganhava por mes")

    if informacoes_faltando:
        return ToolResult.ok(
            data={
                "status": "incompleto",
                "perguntas": informacoes_faltando,
                "mensagem": f"Pra verificar se voce tem direito, preciso saber: {', '.join(informacoes_faltando)}"
            },
            ui_hint=UIHint.INFO
        )

    # Verificar cada critério
    problemas = []
    avisos = []

    # Critério 1: Trabalhou em 2024?
    if not trabalhou_2024:
        return ToolResult.ok(
            data={
                "elegivel": False,
                "motivo": "O Abono PIS/PASEP 2026 e pra quem trabalhou com carteira assinada em 2024.",
                "dica": "Se voce trabalhou em 2025, voce pode receber o abono de 2027!"
            },
            ui_hint=UIHint.INFO
        )

    # Critério 2: Pelo menos 30 dias trabalhados
    if meses_trabalhados is not None and meses_trabalhados < 1:
        return ToolResult.ok(
            data={
                "elegivel": False,
                "motivo": "Precisa ter trabalhado pelo menos 30 dias (1 mes) em 2024.",
                "dica": "Se trabalhou menos de 30 dias, infelizmente nao tem direito ao abono deste ano."
            },
            ui_hint=UIHint.INFO
        )

    # Critério 3: Limite de renda
    if salario_mensal is not None and salario_mensal > LIMITE_RENDA_MENSAL:
        return ToolResult.ok(
            data={
                "elegivel": False,
                "motivo": f"O limite de salario e R$ {LIMITE_RENDA_MENSAL:,.2f} por mes (2 salarios minimos de 2024).",
                "seu_salario": f"R$ {salario_mensal:,.2f}",
                "dica": "Se voce mudou de emprego e agora ganha menos, pode ter direito no proximo ano!"
            },
            ui_hint=UIHint.INFO
        )

    # Critério 4: Cadastrado há 5 anos (verificar se possível)
    if cadastrado_ha_5_anos is False:
        avisos.append("Voce precisa estar cadastrado no PIS/PASEP desde 2020 ou antes.")

    # ELEGÍVEL!
    valor_estimado = calcular_valor_abono_interno(meses_trabalhados)

    return ToolResult.ok(
        data={
            "elegivel": True,
            "valor_estimado": f"R$ {valor_estimado:,.2f}",
            "meses_trabalhados": meses_trabalhados,
            "calculo": f"{meses_trabalhados} meses ÷ 12 × R$ {SALARIO_MINIMO_2026}",
            "proximos_passos": [
                "Descubra quando voce recebe (pelo mes do seu aniversario)",
                "O dinheiro cai na conta da Caixa/BB ou no Caixa Tem",
                "Prazo pra sacar: ate 29 de dezembro de 2026"
            ],
            "avisos": avisos,
            "mensagem": f"PARABENS! Voce tem direito ao Abono PIS/PASEP 2026! Valor estimado: R$ {valor_estimado:,.2f}"
        },
        ui_hint=UIHint.BENEFIT_CARD,
        context_updates={"elegivel_abono_2026": True, "valor_abono": valor_estimado}
    )


def calcular_valor_abono_interno(meses_trabalhados: int) -> float:
    """Calcula valor do abono internamente."""
    if meses_trabalhados >= 12:
        return float(SALARIO_MINIMO_2026)
    return round((meses_trabalhados / 12) * SALARIO_MINIMO_2026, 2)


# =============================================================================
# Calculadora de Valor
# =============================================================================

def calcular_valor_abono(meses_trabalhados: int) -> ToolResult:
    """
    Calcula o valor do Abono PIS/PASEP 2026 baseado nos meses trabalhados.

    O valor é proporcional:
    - 12 meses = R$ 1.621 (salário mínimo inteiro)
    - 6 meses = R$ 810,50
    - 1 mês = R$ 135,08

    Args:
        meses_trabalhados: Número de meses trabalhados em 2024 (1-12)

    Returns:
        ToolResult com valor calculado e explicação
    """
    if meses_trabalhados < 1:
        return ToolResult.ok(
            data={
                "erro": True,
                "mensagem": "Voce precisa ter trabalhado pelo menos 1 mes (30 dias) pra ter direito."
            },
            ui_hint=UIHint.WARNING
        )

    if meses_trabalhados > 12:
        meses_trabalhados = 12

    valor = calcular_valor_abono_interno(meses_trabalhados)

    # Criar tabela de referência
    tabela = []
    for m in range(1, 13):
        v = calcular_valor_abono_interno(m)
        tabela.append({"meses": m, "valor": f"R$ {v:,.2f}"})

    return ToolResult.ok(
        data={
            "meses_trabalhados": meses_trabalhados,
            "valor": valor,
            "valor_formatado": f"R$ {valor:,.2f}",
            "salario_minimo_2026": SALARIO_MINIMO_2026,
            "calculo_explicado": f"{meses_trabalhados} meses ÷ 12 × R$ {SALARIO_MINIMO_2026} = R$ {valor:,.2f}",
            "tabela_referencia": tabela,
            "mensagem": f"Trabalhando {meses_trabalhados} mes(es) em 2024, voce recebe aproximadamente R$ {valor:,.2f}!"
        },
        ui_hint=UIHint.INFO
    )


# =============================================================================
# Calendário Personalizado
# =============================================================================

def consultar_calendario_pis(mes_nascimento: int) -> ToolResult:
    """
    Consulta quando o cidadão recebe o Abono PIS baseado no mês de nascimento.

    Calendário PIS 2026 (trabalhadores do setor privado):
    - Janeiro: 15/02/2026
    - Fevereiro: 15/03/2026
    - Março/Abril: 15/04/2026
    - Maio/Junho: 15/05/2026
    - Julho/Agosto: 15/06/2026
    - Setembro/Outubro: 15/07/2026
    - Novembro/Dezembro: 15/08/2026

    Args:
        mes_nascimento: Mês de nascimento (1-12)

    Returns:
        ToolResult com data de pagamento e orientações
    """
    if mes_nascimento < 1 or mes_nascimento > 12:
        return ToolResult.ok(
            data={
                "erro": True,
                "mensagem": "Me fala o numero do mes (1 pra Janeiro, 2 pra Fevereiro, etc.)"
            },
            ui_hint=UIHint.WARNING
        )

    calendario = CALENDARIO_PIS_2026.get(mes_nascimento)
    mes_nome = MESES_PT.get(mes_nascimento)

    return ToolResult.ok(
        data={
            "mes_nascimento": mes_nascimento,
            "mes_nome": mes_nome,
            "data_pagamento": calendario["data"],
            "mes_pagamento": calendario["mes_pagamento"],
            "prazo_final": PRAZO_FINAL,
            "como_receber": [
                "Se voce tem conta na Caixa, cai automatico!",
                "Se nao tem, baixe o app Caixa Tem - e de graca",
                "Ou va a uma agencia da Caixa com RG e CPF"
            ],
            "calendario_completo": CALENDARIO_PIS_2026,
            "mensagem": f"Voce nasceu em {mes_nome}? Seu PIS estara disponivel a partir de {calendario['data']}! O prazo pra sacar vai ate {PRAZO_FINAL}."
        },
        ui_hint=UIHint.INFO,
        context_updates={"mes_nascimento": mes_nascimento, "data_pis": calendario["data"]}
    )


def mostrar_calendario_completo() -> ToolResult:
    """
    Mostra o calendário completo do PIS/PASEP 2026.

    Útil para quem quer ver todas as datas de uma vez.
    """
    calendario_formatado = []

    for mes in range(1, 13):
        info = CALENDARIO_PIS_2026[mes]
        calendario_formatado.append({
            "mes_nascimento": MESES_PT[mes],
            "mes_numero": mes,
            "data_pagamento": info["data"],
            "mes_pagamento": info["mes_pagamento"]
        })

    return ToolResult.ok(
        data={
            "titulo": "Calendario PIS/PASEP 2026",
            "ano_base": ANO_BASE,
            "calendario": calendario_formatado,
            "prazo_final": PRAZO_FINAL,
            "observacoes": [
                "PIS: pelo mes de NASCIMENTO (trabalhadores privados)",
                "PASEP: pelo final da INSCRICAO (servidores publicos)",
                "O dinheiro fica disponivel ate 29 de dezembro de 2026",
                "Depois dessa data, voce PERDE o direito!"
            ],
            "onde_sacar": {
                "pis": "Caixa Economica Federal (conta, Caixa Tem ou agencia)",
                "pasep": "Banco do Brasil"
            }
        },
        ui_hint=UIHint.INFO
    )


# =============================================================================
# Guia Completo de Como Sacar
# =============================================================================

def guia_como_sacar_pis() -> ToolResult:
    """
    Guia passo a passo de como sacar o Abono PIS/PASEP 2026.
    """
    passos = [
        {
            "passo": 1,
            "titulo": "Descubra sua data",
            "descricao": "Veja no calendario quando voce pode sacar (pelo mes do seu aniversario).",
            "dica": "Me fala seu mes de nascimento que eu te digo a data!"
        },
        {
            "passo": 2,
            "titulo": "Escolha como receber",
            "descricao": "Voce tem 3 opcoes:",
            "opcoes": [
                "CONTA CAIXA: Se voce tem conta na Caixa, cai automatico!",
                "CAIXA TEM: Baixe o app Caixa Tem - e de graca e facil",
                "AGENCIA: Va a uma agencia da Caixa com RG e CPF"
            ]
        },
        {
            "passo": 3,
            "titulo": "Aguarde a data",
            "descricao": "O dinheiro fica disponivel a partir da sua data do calendario.",
            "importante": "Voce tem ate 29 de dezembro de 2026 pra sacar!"
        },
        {
            "passo": 4,
            "titulo": "Saque o dinheiro",
            "descricao": "Se caiu no Caixa Tem, voce pode transferir pra outra conta ou sacar em lotérica.",
            "dica": "No Caixa Tem da pra pagar boletos e fazer Pix tambem!"
        }
    ]

    return ToolResult.ok(
        data={
            "titulo": "Como Sacar o PIS/PASEP 2026",
            "passos": passos,
            "total_passos": len(passos),
            "documentos_necessarios": ["RG ou CNH", "CPF"],
            "onde_sacar": {
                "trabalhador_privado": "Caixa Economica Federal",
                "servidor_publico": "Banco do Brasil"
            },
            "prazo": PRAZO_FINAL,
            "alerta": "IMPORTANTE: Depois de 29 de dezembro de 2026, voce PERDE o direito ao abono!"
        },
        ui_hint=UIHint.CHECKLIST
    )


# =============================================================================
# Função Principal de Consulta
# =============================================================================

def consultar_abono_pis_pasep(
    mes_nascimento: Optional[int] = None,
    meses_trabalhados: Optional[int] = None,
    salario_mensal: Optional[float] = None
) -> ToolResult:
    """
    Consulta completa sobre Abono PIS/PASEP 2026.

    Pode:
    - Verificar elegibilidade
    - Calcular valor
    - Mostrar data de pagamento

    Args:
        mes_nascimento: Mês de nascimento (1-12) para ver calendário
        meses_trabalhados: Meses trabalhados em 2024 para calcular valor
        salario_mensal: Salário médio em 2024 para verificar elegibilidade

    Returns:
        ToolResult com todas as informações relevantes
    """
    resultado = {
        "programa": "Abono Salarial PIS/PASEP 2026",
        "ano_base": ANO_BASE,
        "valor_maximo": f"R$ {SALARIO_MINIMO_2026:,.2f}",
        "prazo_final": PRAZO_FINAL
    }

    # Se informou meses trabalhados, calcula valor
    if meses_trabalhados is not None:
        if meses_trabalhados >= 1:
            valor = calcular_valor_abono_interno(meses_trabalhados)
            resultado["valor_estimado"] = f"R$ {valor:,.2f}"
            resultado["meses_trabalhados"] = meses_trabalhados
            resultado["calculo"] = f"{meses_trabalhados}/12 × R$ {SALARIO_MINIMO_2026}"

    # Se informou mês de nascimento, mostra data
    if mes_nascimento is not None and 1 <= mes_nascimento <= 12:
        calendario = CALENDARIO_PIS_2026.get(mes_nascimento)
        resultado["mes_nascimento"] = MESES_PT.get(mes_nascimento)
        resultado["data_pagamento"] = calendario["data"]

    # Se informou salário, verifica elegibilidade
    if salario_mensal is not None:
        if salario_mensal <= LIMITE_RENDA_MENSAL:
            resultado["elegivel_por_renda"] = True
            resultado["status_renda"] = "Dentro do limite de renda"
        else:
            resultado["elegivel_por_renda"] = False
            resultado["status_renda"] = f"Salario acima do limite (R$ {LIMITE_RENDA_MENSAL:,.2f})"

    # Montar mensagem resumida
    partes_mensagem = []

    if "valor_estimado" in resultado:
        partes_mensagem.append(f"Valor: {resultado['valor_estimado']}")

    if "data_pagamento" in resultado:
        partes_mensagem.append(f"Disponivel em: {resultado['data_pagamento']}")

    if "elegivel_por_renda" in resultado:
        if resultado["elegivel_por_renda"]:
            partes_mensagem.append("Renda OK!")
        else:
            partes_mensagem.append("Renda acima do limite")

    resultado["resumo"] = " | ".join(partes_mensagem) if partes_mensagem else "Me fala mais detalhes pra eu calcular!"

    return ToolResult.ok(
        data=resultado,
        ui_hint=UIHint.BENEFIT_CARD
    )
