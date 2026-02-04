"""
Tools para comparar servicos populares: planos de celular,
contas bancarias e tarifas de energia.

Foco em opcoes economicas para o publico de baixa renda.
"""

from typing import Optional
from app.agent.tools.base import ToolResult, UIHint


# --- Planos de celular populares (pre-pago e controle) ---
PLANOS_CELULAR = [
    {
        "operadora": "Claro",
        "nome": "Claro Controle 8GB",
        "tipo": "Controle",
        "preco": "R$ 29,99/mes",
        "dados": "8GB",
        "apps_ilimitados": ["WhatsApp", "Instagram"],
        "ligacoes": "Ilimitadas",
        "vantagens": ["Roaming nacional incluso"],
    },
    {
        "operadora": "Vivo",
        "nome": "Vivo Controle 7GB",
        "tipo": "Controle",
        "preco": "R$ 29,99/mes",
        "dados": "7GB",
        "apps_ilimitados": ["WhatsApp"],
        "ligacoes": "Ilimitadas",
        "vantagens": ["Desconto na fatura com debito automatico"],
    },
    {
        "operadora": "TIM",
        "nome": "TIM Controle Smart 9GB",
        "tipo": "Controle",
        "preco": "R$ 29,99/mes",
        "dados": "9GB",
        "apps_ilimitados": ["WhatsApp", "Messenger"],
        "ligacoes": "Ilimitadas",
        "vantagens": ["Mais dados por menos", "Roaming incluso"],
    },
    {
        "operadora": "Claro",
        "nome": "Claro Pre 7 dias",
        "tipo": "Pre-pago",
        "preco": "R$ 7,99/semana",
        "dados": "2GB por semana",
        "apps_ilimitados": ["WhatsApp"],
        "ligacoes": "100 minutos",
        "vantagens": ["Sem compromisso mensal", "Paga so quando usa"],
    },
    {
        "operadora": "TIM",
        "nome": "TIM Pre TOP 7 dias",
        "tipo": "Pre-pago",
        "preco": "R$ 9,99/semana",
        "dados": "3GB por semana",
        "apps_ilimitados": ["WhatsApp", "Messenger", "Instagram"],
        "ligacoes": "Ilimitadas",
        "vantagens": ["Melhor custo-beneficio pre-pago"],
    },
]

# --- Contas bancarias gratuitas ---
CONTAS_BANCARIAS = [
    {
        "banco": "Caixa Tem",
        "tipo": "Conta poupanca digital",
        "taxa_mensal": "Gratis",
        "pix": "Ilimitado e gratis",
        "cartao": "Virtual (debito)",
        "saques": "Gratis em caixas da CAIXA e loterias",
        "vantagens": [
            "Recebe Bolsa Familia e BPC automaticamente",
            "Saques em loterias",
            "Pagamento de boletos e contas",
        ],
        "ideal_para": "Quem recebe beneficio do governo",
        "destaque": True,
    },
    {
        "banco": "Nubank",
        "tipo": "Conta corrente digital",
        "taxa_mensal": "Gratis",
        "pix": "Ilimitado e gratis",
        "cartao": "Debito e credito (sem anuidade)",
        "saques": "Gratis em Banco24Horas (limitado)",
        "vantagens": [
            "Dinheiro rende automaticamente (100% CDI)",
            "Cartao de credito sem anuidade",
            "App facil de usar",
        ],
        "ideal_para": "Uso no dia a dia com cartao",
        "destaque": False,
    },
    {
        "banco": "PicPay",
        "tipo": "Conta de pagamento",
        "taxa_mensal": "Gratis",
        "pix": "Ilimitado e gratis",
        "cartao": "Virtual e fisico (gratis)",
        "saques": "Gratis (limitado)",
        "vantagens": [
            "Cashback em compras",
            "Pode pagar boletos com cartao de credito",
            "Rendimento automatico",
        ],
        "ideal_para": "Quem quer cashback nas compras",
        "destaque": False,
    },
    {
        "banco": "Inter",
        "tipo": "Conta corrente digital",
        "taxa_mensal": "Gratis",
        "pix": "Ilimitado e gratis",
        "cartao": "Debito e credito (sem anuidade)",
        "saques": "Gratis em Banco24Horas (limitado)",
        "vantagens": [
            "Cashback no marketplace",
            "Investimentos a partir de R$ 1",
            "Seguro de vida gratis",
        ],
        "ideal_para": "Quem quer conta completa gratis",
        "destaque": False,
    },
]


def comparar_planos_celular(
    uso: str = "",
) -> dict:
    """
    Compara planos de celular pre-pago e controle
    com foco em opcoes economicas.

    Args:
        uso: Tipo de uso (ex: "so whatsapp", "redes sociais", "internet")

    Returns:
        dict com comparacao de planos e recomendacao
    """
    uso_lower = uso.lower().strip() if uso else ""

    # Recomendacao baseada no uso
    if "whatsapp" in uso_lower and ("so" in uso_lower or "apenas" in uso_lower):
        recomendados = [p for p in PLANOS_CELULAR if p["tipo"] == "Pre-pago"]
        dica = (
            "Se voce usa so WhatsApp, um plano pre-pago semanal e mais economico. "
            "Voce paga so quando precisa e ainda tem WhatsApp ilimitado."
        )
    elif any(x in uso_lower for x in ["instagram", "redes", "video", "youtube"]):
        recomendados = [p for p in PLANOS_CELULAR if int(p["dados"].split("GB")[0].strip()) >= 7]
        dica = (
            "Para redes sociais e videos, voce precisa de mais dados. "
            "Um plano controle com 7GB ou mais e a melhor opcao."
        )
    else:
        recomendados = PLANOS_CELULAR
        dica = (
            "Para uso geral, um plano controle e mais economico que recarga avulsa. "
            "Todos os planos abaixo incluem WhatsApp ilimitado."
        )

    planos = recomendados[:5]

    mensagem = (
        f"Comparei os planos mais baratos das operadoras. {dica}\n\n"
        "Dica importante: NUNCA compre chip ou credito de vendedor ambulante. "
        "Compre sempre em loja oficial da operadora ou pelo app."
    )

    result = ToolResult.ok(
        data={
            "planos": planos,
            "total": len(planos),
            "uso_informado": uso or "geral",
            "dica": dica,
            "mensagem_cidadao": mensagem,
        },
        ui_hint=UIHint.INFO,
    )
    return result.model_dump()


def comparar_contas_bancarias() -> dict:
    """
    Compara contas bancarias digitais gratuitas,
    priorizando Caixa Tem para beneficiarios.

    Returns:
        dict com comparacao de contas bancarias
    """
    mensagem = (
        "Todas essas contas sao 100% gratis e voce abre pelo celular.\n\n"
        "Se voce recebe beneficio do governo (Bolsa Familia, BPC, FGTS), "
        "a Caixa Tem e obrigatoria — e por la que o dinheiro chega.\n\n"
        "Voce pode ter mais de uma conta! Muita gente usa Caixa Tem "
        "para os beneficios e Nubank ou PicPay para o dia a dia."
    )

    result = ToolResult.ok(
        data={
            "contas": CONTAS_BANCARIAS,
            "total": len(CONTAS_BANCARIAS),
            "recomendacao_beneficiarios": "Caixa Tem",
            "mensagem_cidadao": mensagem,
        },
        ui_hint=UIHint.INFO,
    )
    return result.model_dump()


def verificar_tarifa_energia(
    uf: str = "",
    consumo_kwh: float = 0,
) -> dict:
    """
    Verifica se o cidadao pode ter desconto na conta de luz
    (TSEE - Tarifa Social de Energia Eletrica) e calcula economia.

    Args:
        uf: Estado do cidadao
        consumo_kwh: Consumo mensal em kWh

    Returns:
        dict com informacoes sobre TSEE e dicas de economia
    """
    # Faixas de desconto da TSEE (Lei 12.212/2010)
    faixas_desconto = [
        {"ate_kwh": 30, "desconto": 65},
        {"ate_kwh": 100, "desconto": 40},
        {"ate_kwh": 220, "desconto": 10},
    ]

    # Calcula desconto estimado
    desconto_percentual = 0
    for faixa in faixas_desconto:
        if consumo_kwh <= faixa["ate_kwh"]:
            desconto_percentual = faixa["desconto"]
            break

    if desconto_percentual == 0 and consumo_kwh > 220:
        desconto_percentual = 10  # mínimo para TSEE

    # Tarifa media nacional
    tarifa_media = 0.85  # R$/kWh (media nacional)
    valor_sem_desconto = consumo_kwh * tarifa_media
    valor_com_desconto = valor_sem_desconto * (1 - desconto_percentual / 100)
    economia_mensal = valor_sem_desconto - valor_com_desconto

    dicas_economia = [
        "Desligue aparelhos da tomada quando nao estiver usando",
        "Use lampadas LED (gastam 80% menos que as comuns)",
        "Passe roupa de uma vez so (ligar o ferro varias vezes gasta mais)",
        "Banho rapido: chuveiro eletrico e o vilao da conta de luz",
        "Geladeira: nao coloque comida quente e nao abra a porta desnecessariamente",
    ]

    mensagem = (
        f"Com consumo de {consumo_kwh:.0f} kWh/mes"
        + (f" em {uf}" if uf else "")
        + ":\n\n"
    )

    if desconto_percentual > 0:
        mensagem += (
            f"Voce pode ter {desconto_percentual}% de desconto com a Tarifa Social!\n"
            f"Economia estimada: R$ {economia_mensal:.2f}/mes "
            f"(R$ {economia_mensal * 12:.2f}/ano)\n\n"
            f"Para ter o desconto, voce precisa:\n"
            f"1. Estar inscrito no CadUnico com renda de ate meio salario minimo por pessoa\n"
            f"2. Ligar para a sua distribuidora de energia e pedir a Tarifa Social\n"
            f"3. Informar o NIS (numero do CadUnico)"
        )
    else:
        mensagem += (
            "Seu consumo esta acima da faixa principal de desconto, "
            "mas voce ainda pode ter 10% de desconto com a Tarifa Social "
            "se estiver no CadUnico."
        )

    result = ToolResult.ok(
        data={
            "consumo_kwh": consumo_kwh,
            "uf": uf,
            "desconto_percentual": desconto_percentual,
            "valor_estimado_sem_desconto": round(valor_sem_desconto, 2),
            "valor_estimado_com_desconto": round(valor_com_desconto, 2),
            "economia_mensal": round(economia_mensal, 2),
            "economia_anual": round(economia_mensal * 12, 2),
            "faixas_desconto": faixas_desconto,
            "dicas_economia": dicas_economia,
            "como_solicitar": (
                "Ligue para a distribuidora de energia da sua regiao "
                "e peca a Tarifa Social. Tenha em maos o NIS (CadUnico) "
                "e o numero da conta de luz."
            ),
            "mensagem_cidadao": mensagem,
        },
        ui_hint=UIHint.INFO,
    )
    return result.model_dump()
