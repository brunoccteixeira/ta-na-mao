"""
Tools para FGTS - Consulta, Saque-Aniversário e Simuladores.

Inclui:
- Explicação do Saque-Aniversário vs Saque-Rescisão
- Simulador de impacto para ajudar na decisão
- Calendário de saques
- Guia passo a passo

IMPORTANTE: Ajudar o cidadão a entender os TRADE-OFFS antes de decidir!
Muita gente adere ao Saque-Aniversário sem entender que perde o saque total na demissão.
"""

from typing import Optional, Dict, Any, List
from datetime import date
from app.agent.tools.base import ToolResult, UIHint


# =============================================================================
# Tabela de Alíquotas do Saque-Aniversário
# =============================================================================

# Tabela oficial de alíquotas para o Saque-Aniversário
TABELA_SAQUE_ANIVERSARIO = [
    {"faixa_min": 0, "faixa_max": 500, "aliquota": 0.50, "parcela_adicional": 0},
    {"faixa_min": 500.01, "faixa_max": 1000, "aliquota": 0.40, "parcela_adicional": 50},
    {"faixa_min": 1000.01, "faixa_max": 5000, "aliquota": 0.30, "parcela_adicional": 150},
    {"faixa_min": 5000.01, "faixa_max": 10000, "aliquota": 0.20, "parcela_adicional": 650},
    {"faixa_min": 10000.01, "faixa_max": 15000, "aliquota": 0.15, "parcela_adicional": 1150},
    {"faixa_min": 15000.01, "faixa_max": 20000, "aliquota": 0.10, "parcela_adicional": 1900},
    {"faixa_min": 20000.01, "faixa_max": float('inf'), "aliquota": 0.05, "parcela_adicional": 2900},
]

MULTA_RESCISAO = 0.40  # 40% de multa em demissão sem justa causa

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}


# =============================================================================
# Explicação dos Trade-offs
# =============================================================================

def explicar_saque_aniversario() -> ToolResult:
    """
    Explica o Saque-Aniversário vs Saque Normal em linguagem simples.

    MUITO IMPORTANTE: O cidadão precisa entender que ao aderir,
    ele PERDE o direito de sacar o saldo total se for demitido!
    """
    explicacao = {
        "titulo": "Saque-Aniversario: O Que Voce Precisa Saber",

        "o_que_e": """O Saque-Aniversario eh uma OPCAO que voce pode escolher.
Se voce aderir, pode sacar uma parte do FGTS todo ano no mes do seu aniversario.
MAS ATENCAO: voce perde o direito de sacar TUDO se for demitido!""",

        "opcao_1": {
            "nome": "SAQUE-ANIVERSARIO",
            "vantagens": [
                "Voce saca uma parte todo ano no seu aniversario",
                "Nao precisa esperar ser demitido",
                "Dinheiro disponivel mesmo trabalhando"
            ],
            "desvantagens": [
                "Se for demitido, NAO saca o saldo total",
                "So recebe a multa de 40% na demissao",
                "Se quiser voltar atras, demora 2 anos"
            ],
            "ideal_para": "Quem tem emprego estavel e quer uma renda extra todo ano"
        },

        "opcao_2": {
            "nome": "SAQUE NORMAL (Rescisao)",
            "vantagens": [
                "Se for demitido, saca TUDO + multa de 40%",
                "Valor muito maior de uma vez",
                "Protege voce em caso de demissao"
            ],
            "desvantagens": [
                "So saca quando for demitido (ou outras situacoes especiais)",
                "Dinheiro fica 'parado' enquanto esta empregado"
            ],
            "ideal_para": "Quem tem risco de ser demitido ou quer seguranca"
        },

        "alerta": """PENSE BEM ANTES DE ADERIR!
Se voce for demitido com Saque-Aniversario:
- Voce NAO saca o saldo total
- So recebe a multa de 40%
- Pode perder MUITO dinheiro!

Exemplo: Se tem R$ 20.000 no FGTS
- SEM saque-aniversario: recebe R$ 28.000 (saldo + multa)
- COM saque-aniversario: recebe so R$ 8.000 (multa)
- Diferenca: R$ 20.000 a menos!""",

        "como_aderir": "Pelo app FGTS ou no site fgts.caixa.gov.br",
        "como_voltar_atras": "Tambem pelo app FGTS, mas demora 2 anos pra valer!"
    }

    return ToolResult.ok(
        data=explicacao,
        ui_hint=UIHint.INFO,
        context_updates={"explicou_saque_aniversario": True}
    )


# =============================================================================
# Simulador de Impacto
# =============================================================================

def calcular_saque_aniversario(saldo_fgts: float) -> float:
    """Calcula o valor do saque-aniversário baseado no saldo."""
    for faixa in TABELA_SAQUE_ANIVERSARIO:
        if faixa["faixa_min"] <= saldo_fgts <= faixa["faixa_max"]:
            valor = (saldo_fgts * faixa["aliquota"]) + faixa["parcela_adicional"]
            return round(valor, 2)
    return 0


def simular_impacto_fgts(saldo_fgts: float) -> ToolResult:
    """
    Simula o impacto financeiro do Saque-Aniversário vs Saque Normal.

    Mostra claramente a diferença para ajudar o cidadão a decidir.

    Args:
        saldo_fgts: Saldo atual do FGTS

    Returns:
        Comparação detalhada das duas opções
    """
    if saldo_fgts <= 0:
        return ToolResult.ok(
            data={
                "erro": True,
                "mensagem": "Me fala quanto voce tem no FGTS que eu simulo pra voce!"
            },
            ui_hint=UIHint.WARNING
        )

    # Calcular valores
    valor_saque_aniversario = calcular_saque_aniversario(saldo_fgts)
    multa_40 = round(saldo_fgts * MULTA_RESCISAO, 2)
    total_com_saque_normal = round(saldo_fgts + multa_40, 2)
    total_com_saque_aniversario = multa_40  # Só recebe a multa na demissão
    diferenca = round(total_com_saque_normal - total_com_saque_aniversario, 2)

    # Encontrar a faixa de alíquota
    aliquota_usada = 0
    parcela_adicional = 0
    for faixa in TABELA_SAQUE_ANIVERSARIO:
        if faixa["faixa_min"] <= saldo_fgts <= faixa["faixa_max"]:
            aliquota_usada = faixa["aliquota"]
            parcela_adicional = faixa["parcela_adicional"]
            break

    simulacao = {
        "saldo_fgts": saldo_fgts,
        "saldo_formatado": f"R$ {saldo_fgts:,.2f}",

        "cenario_1_saque_aniversario": {
            "nome": "COM Saque-Aniversario",
            "saque_anual": f"R$ {valor_saque_aniversario:,.2f}",
            "calculo_saque": f"{aliquota_usada*100:.0f}% de R$ {saldo_fgts:,.2f} + R$ {parcela_adicional:,.2f}",
            "se_for_demitido": f"R$ {total_com_saque_aniversario:,.2f} (so a multa de 40%)",
            "total_disponivel_agora": f"R$ {valor_saque_aniversario:,.2f}"
        },

        "cenario_2_saque_normal": {
            "nome": "SEM Saque-Aniversario (normal)",
            "saque_anual": "R$ 0 (so saca quando for demitido)",
            "se_for_demitido": f"R$ {total_com_saque_normal:,.2f} (saldo + multa 40%)",
            "total_disponivel_agora": "R$ 0"
        },

        "comparacao_demissao": {
            "com_saque_aniversario": total_com_saque_aniversario,
            "sem_saque_aniversario": total_com_saque_normal,
            "diferenca": diferenca,
            "diferenca_formatada": f"R$ {diferenca:,.2f}"
        },

        "conclusao": _gerar_conclusao(saldo_fgts, valor_saque_aniversario, diferenca),

        "alerta": f"""ATENCAO!
Se voce for demitido:
- COM saque-aniversario: recebe R$ {total_com_saque_aniversario:,.2f}
- SEM saque-aniversario: recebe R$ {total_com_saque_normal:,.2f}
- DIFERENCA: R$ {diferenca:,.2f} A MENOS com saque-aniversario!"""
    }

    return ToolResult.ok(
        data=simulacao,
        ui_hint=UIHint.INFO,
        context_updates={"simulacao_fgts": simulacao}
    )


def _gerar_conclusao(saldo: float, saque_anual: float, diferenca: float) -> str:
    """Gera conclusão personalizada baseada nos valores."""
    if diferenca > 10000:
        return f"""CUIDADO! Voce pode perder R$ {diferenca:,.2f} se for demitido!
O saque-aniversario de R$ {saque_anual:,.2f} por ano pode nao valer a pena.
So vale se voce tiver CERTEZA que nao vai ser demitido."""

    elif diferenca > 5000:
        return f"""A diferenca eh grande: R$ {diferenca:,.2f}!
Pense bem se vale a pena sacar R$ {saque_anual:,.2f} por ano
e perder esse valor todo se for demitido."""

    else:
        return f"""A diferenca eh de R$ {diferenca:,.2f}.
Se voce precisa do dinheiro agora e tem emprego estavel,
pode fazer sentido. Mas pense bem!"""


# =============================================================================
# Calendário de Saques
# =============================================================================

def consultar_calendario_saque_aniversario(mes_nascimento: int) -> ToolResult:
    """
    Mostra o período de saque do Saque-Aniversário baseado no mês de nascimento.

    O saque fica disponível por 90 dias:
    - Começa no 1º dia do mês de aniversário
    - Termina no último dia do 2º mês seguinte

    Args:
        mes_nascimento: Mês de nascimento (1-12)

    Returns:
        Período de saque e orientações
    """
    if mes_nascimento < 1 or mes_nascimento > 12:
        return ToolResult.ok(
            data={
                "erro": True,
                "mensagem": "Me fala o numero do mes (1 pra Janeiro, 12 pra Dezembro)"
            },
            ui_hint=UIHint.WARNING
        )

    mes_nome = MESES_PT.get(mes_nascimento)

    # Calcular mês final (2 meses depois)
    mes_final = mes_nascimento + 2
    ano_final_adicional = 0
    if mes_final > 12:
        mes_final = mes_final - 12
        ano_final_adicional = 1

    mes_final_nome = MESES_PT.get(mes_final)

    return ToolResult.ok(
        data={
            "mes_nascimento": mes_nascimento,
            "mes_nome": mes_nome,
            "periodo_saque": {
                "inicio": f"1 de {mes_nome}",
                "fim": f"Ultimo dia de {mes_final_nome}",
                "duracao": "90 dias (3 meses)"
            },
            "exemplo_2026": f"Se seu aniversario eh em {mes_nome}, voce pode sacar de 1/{mes_nascimento:02d}/2026 ate o final de {mes_final_nome}/2026",
            "importante": [
                "O dinheiro fica disponivel por 90 dias",
                "Se nao sacar, o valor volta pro FGTS",
                "Voce NAO perde - so volta pra conta",
                "Pode sacar pelo app FGTS ou na Caixa"
            ],
            "como_sacar": [
                "App FGTS: mais facil e rapido",
                "Caixa Tem: se tiver o app",
                "Agencia da Caixa: com RG e CPF"
            ],
            "mensagem": f"Nasceu em {mes_nome}? Seu saque fica disponivel de 1 de {mes_nome} ate o final de {mes_final_nome}. Sao 90 dias pra sacar!"
        },
        ui_hint=UIHint.INFO
    )


def mostrar_tabela_saque_aniversario() -> ToolResult:
    """
    Mostra a tabela completa de alíquotas do Saque-Aniversário.

    Útil para o cidadão entender quanto pode sacar baseado no saldo.
    """
    tabela_formatada = []

    for faixa in TABELA_SAQUE_ANIVERSARIO:
        faixa_max_str = f"R$ {faixa['faixa_max']:,.2f}" if faixa['faixa_max'] != float('inf') else "Acima"

        tabela_formatada.append({
            "faixa": f"R$ {faixa['faixa_min']:,.2f} a {faixa_max_str}",
            "aliquota": f"{faixa['aliquota']*100:.0f}%",
            "parcela_adicional": f"R$ {faixa['parcela_adicional']:,.2f}",
            "exemplo_saque": _calcular_exemplo(faixa)
        })

    return ToolResult.ok(
        data={
            "titulo": "Tabela do Saque-Aniversario",
            "tabela": tabela_formatada,
            "como_calcular": "Valor = (Saldo × Aliquota) + Parcela Adicional",
            "exemplos": [
                {"saldo": "R$ 500", "saque": f"R$ {calcular_saque_aniversario(500):,.2f}"},
                {"saldo": "R$ 2.000", "saque": f"R$ {calcular_saque_aniversario(2000):,.2f}"},
                {"saldo": "R$ 5.000", "saque": f"R$ {calcular_saque_aniversario(5000):,.2f}"},
                {"saldo": "R$ 10.000", "saque": f"R$ {calcular_saque_aniversario(10000):,.2f}"},
                {"saldo": "R$ 20.000", "saque": f"R$ {calcular_saque_aniversario(20000):,.2f}"},
            ]
        },
        ui_hint=UIHint.INFO
    )


def _calcular_exemplo(faixa: Dict) -> str:
    """Calcula exemplo de saque para uma faixa."""
    if faixa["faixa_max"] == float('inf'):
        exemplo_saldo = 30000
    else:
        exemplo_saldo = (faixa["faixa_min"] + faixa["faixa_max"]) / 2

    valor = (exemplo_saldo * faixa["aliquota"]) + faixa["parcela_adicional"]
    return f"Com R$ {exemplo_saldo:,.2f}: saca R$ {valor:,.2f}"


# =============================================================================
# Guia Como Aderir/Cancelar
# =============================================================================

def guia_aderir_saque_aniversario() -> ToolResult:
    """
    Guia passo a passo para aderir ao Saque-Aniversário.
    """
    passos = [
        {
            "passo": 1,
            "titulo": "Pense bem antes!",
            "descricao": "Leia os trade-offs. Se for demitido, voce so recebe a multa de 40%!",
            "importante": True
        },
        {
            "passo": 2,
            "titulo": "Baixe o app FGTS",
            "descricao": "Procure 'FGTS' na loja do celular. E de graca e oficial.",
            "link": "https://www.caixa.gov.br/atendimento/aplicativos/fgts/Paginas/default.aspx"
        },
        {
            "passo": 3,
            "titulo": "Faca login",
            "descricao": "Use seu CPF e senha. Pode usar Gov.br tambem.",
        },
        {
            "passo": 4,
            "titulo": "Va em 'Saque-Aniversario'",
            "descricao": "No menu principal, clique em 'Saque-Aniversario'.",
        },
        {
            "passo": 5,
            "titulo": "Clique em 'Aderir'",
            "descricao": "Leia os termos e confirme se quiser aderir.",
            "alerta": "ATENCAO: A adesao comeca a valer no mes seguinte!"
        },
        {
            "passo": 6,
            "titulo": "Aguarde seu aniversario",
            "descricao": "O saque fica disponivel no mes do seu aniversario por 90 dias.",
        }
    ]

    return ToolResult.ok(
        data={
            "titulo": "Como Aderir ao Saque-Aniversario",
            "passos": passos,
            "total_passos": len(passos),
            "alerta_principal": """IMPORTANTE: Leia isso antes de aderir!

Se voce for demitido apos aderir:
- NAO recebe o saldo total do FGTS
- So recebe a multa de 40%
- Se quiser voltar atras, demora 2 ANOS!

So adira se tiver certeza!""",
            "onde": "App FGTS ou fgts.caixa.gov.br"
        },
        ui_hint=UIHint.CHECKLIST
    )


def guia_cancelar_saque_aniversario() -> ToolResult:
    """
    Guia passo a passo para cancelar o Saque-Aniversário.
    """
    passos = [
        {
            "passo": 1,
            "titulo": "Abra o app FGTS",
            "descricao": "Use o mesmo app que voce usou pra aderir.",
        },
        {
            "passo": 2,
            "titulo": "Faca login",
            "descricao": "Entre com seu CPF e senha.",
        },
        {
            "passo": 3,
            "titulo": "Va em 'Saque-Aniversario'",
            "descricao": "No menu principal, clique em 'Saque-Aniversario'.",
        },
        {
            "passo": 4,
            "titulo": "Clique em 'Cancelar adesao'",
            "descricao": "Confirme que quer voltar pro saque normal.",
        },
        {
            "passo": 5,
            "titulo": "Aguarde 2 ANOS",
            "descricao": "O cancelamento so vale depois de 24 meses!",
            "importante": True,
            "alerta": "Nesse periodo, se voce for demitido, ainda NAO saca o total!"
        }
    ]

    return ToolResult.ok(
        data={
            "titulo": "Como Cancelar o Saque-Aniversario",
            "passos": passos,
            "total_passos": len(passos),
            "alerta_principal": """ATENCAO: O cancelamento demora 2 ANOS pra valer!

Durante esses 2 anos:
- Voce ainda esta no Saque-Aniversario
- Se for demitido, so recebe a multa de 40%
- NAO tem como acelerar esse prazo

Pense bem antes de aderir!""",
            "onde": "App FGTS ou fgts.caixa.gov.br"
        },
        ui_hint=UIHint.CHECKLIST
    )


# =============================================================================
# Consulta Geral de FGTS
# =============================================================================

def consultar_fgts_geral() -> ToolResult:
    """
    Retorna informações gerais sobre FGTS e como consultar.
    """
    return ToolResult.ok(
        data={
            "titulo": "FGTS - O Que Voce Precisa Saber",

            "o_que_e": """O FGTS eh um dinheiro que a empresa deposita pra voce todo mes.
Eh 8% do seu salario. Fica guardado pra quando voce precisar.""",

            "quando_pode_sacar": [
                "Demissao sem justa causa (saldo + 40% de multa)",
                "Comprar casa propria",
                "Aposentadoria",
                "Doenca grave",
                "Saque-Aniversario (se aderir)",
                "FGTS de empregos antigos que nunca sacou"
            ],

            "como_consultar": {
                "app": "Baixe o app FGTS - mostra todo seu saldo",
                "site": "fgts.caixa.gov.br",
                "presencial": "Agencia da Caixa com RG e CPF"
            },

            "dica_importante": """DICA: Voce pode ter FGTS de empregos antigos!
Abra o app e veja TODAS as suas contas.
As contas 'inativas' sao de empregos que voce saiu.""",

            "link_app": "https://www.caixa.gov.br/atendimento/aplicativos/fgts/Paginas/default.aspx"
        },
        ui_hint=UIHint.INFO
    )


# =============================================================================
# Função de Ajuda na Decisão
# =============================================================================

def ajudar_decidir_saque_aniversario(
    saldo_fgts: Optional[float] = None,
    emprego_estavel: Optional[bool] = None,
    precisa_dinheiro_agora: Optional[bool] = None
) -> ToolResult:
    """
    Ajuda o cidadão a decidir se deve ou não aderir ao Saque-Aniversário.

    Faz perguntas e dá uma recomendação baseada nas respostas.

    Args:
        saldo_fgts: Quanto tem no FGTS
        emprego_estavel: Se considera o emprego estável
        precisa_dinheiro_agora: Se precisa urgente do dinheiro

    Returns:
        Recomendação personalizada
    """
    # Verificar se temos todas as informações
    perguntas_faltando = []

    if saldo_fgts is None:
        perguntas_faltando.append("Quanto voce tem no FGTS?")
    if emprego_estavel is None:
        perguntas_faltando.append("Voce acha que seu emprego eh estavel? (sim/nao)")
    if precisa_dinheiro_agora is None:
        perguntas_faltando.append("Voce precisa de dinheiro urgente agora? (sim/nao)")

    if perguntas_faltando:
        return ToolResult.ok(
            data={
                "status": "incompleto",
                "perguntas": perguntas_faltando,
                "mensagem": "Pra te ajudar a decidir, preciso saber:\n- " + "\n- ".join(perguntas_faltando)
            },
            ui_hint=UIHint.INFO
        )

    # Calcular valores
    saque_anual = calcular_saque_aniversario(saldo_fgts)
    multa_40 = round(saldo_fgts * MULTA_RESCISAO, 2)
    total_demissao_normal = round(saldo_fgts + multa_40, 2)
    diferenca = round(saldo_fgts, 2)  # Diferença é o saldo que perde

    # Gerar recomendação
    pontos_contra = 0
    pontos_favor = 0
    motivos = []

    # Análise do emprego
    if emprego_estavel:
        pontos_favor += 2
        motivos.append("Seu emprego eh estavel, menor risco de demissao")
    else:
        pontos_contra += 3
        motivos.append("Emprego instavel = risco de perder R$ {:.2f} na demissao".format(diferenca))

    # Análise da necessidade
    if precisa_dinheiro_agora:
        pontos_favor += 1
        motivos.append("Voce precisa do dinheiro agora")
    else:
        pontos_contra += 1
        motivos.append("Nao tem urgencia, pode esperar")

    # Análise do saldo
    if saldo_fgts > 15000:
        pontos_contra += 2
        motivos.append("Saldo alto = muito a perder se for demitido")
    elif saldo_fgts < 3000:
        pontos_favor += 1
        motivos.append("Saldo baixo, diferenca menor")

    # Decisão
    if pontos_contra > pontos_favor:
        recomendacao = "NAO_RECOMENDADO"
        mensagem = f"""NAO RECOMENDO o Saque-Aniversario pra voce.

MOTIVOS:
{chr(10).join('- ' + m for m in motivos)}

Se voce for demitido, vai perder R$ {diferenca:,.2f}!

O saque de R$ {saque_anual:,.2f} por ano nao compensa esse risco."""
    else:
        recomendacao = "PODE_CONSIDERAR"
        mensagem = f"""Voce PODE considerar o Saque-Aniversario, mas pense bem!

MOTIVOS:
{chr(10).join('- ' + m for m in motivos)}

Voce sacaria R$ {saque_anual:,.2f} por ano.
MAS se for demitido, perde R$ {diferenca:,.2f}!

So adira se tiver CERTEZA que nao vai ser demitido!"""

    return ToolResult.ok(
        data={
            "recomendacao": recomendacao,
            "saldo_fgts": f"R$ {saldo_fgts:,.2f}",
            "saque_anual": f"R$ {saque_anual:,.2f}",
            "perderia_demissao": f"R$ {diferenca:,.2f}",
            "motivos": motivos,
            "mensagem": mensagem
        },
        ui_hint=UIHint.INFO,
        context_updates={"decisao_fgts": recomendacao}
    )
