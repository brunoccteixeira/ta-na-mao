"""
Tool para recomendar conta bancária adequada ao cidadão.
Prioriza CAIXA para benefícios federais (Bolsa Família, BPC, etc.)
"""

from typing import Optional
from app.agent.tools.base import ToolResult, UIHint


# Dados estáticos dos parceiros bancários
# Em produção, vem do banco de dados via partner_service
PARCEIROS_BANCARIOS = {
    "caixa": {
        "nome": "Caixa Tem",
        "slug": "caixa",
        "descricao": "App da Caixa para receber beneficios sociais",
        "vantagens": [
            "Conta 100% gratis",
            "Pix ilimitado",
            "Bolsa Familia direto no app",
            "BPC e auxilios pagos pela Caixa",
            "Saques em loterias e caixas eletronicos",
            "Cartao de debito virtual",
        ],
        "como_abrir": (
            "Baixe o app Caixa Tem na Play Store ou App Store. "
            "Voce precisa apenas do CPF e um celular com camera. "
            "A conta e aberta na hora, sem ir ao banco."
        ),
        "url": "https://www.caixa.gov.br/caixa-tem/Paginas/default.aspx",
        # Programas para os quais a CAIXA é o banco oficial
        "programas_oficiais": [
            "BOLSA_FAMILIA", "BPC", "BPC_IDOSO", "BPC_PCD",
            "AUXILIO_GAS", "SEGURO_DESEMPREGO", "ABONO_SALARIAL",
            "PIS_PASEP", "FGTS", "MCMV",
        ],
    },
    "nubank": {
        "nome": "Nubank",
        "slug": "nubank",
        "descricao": "Conta digital sem taxas",
        "vantagens": [
            "Conta gratis",
            "Cartao sem anuidade",
            "Pix ilimitado",
            "Rendimento automatico",
        ],
        "como_abrir": (
            "Baixe o app Nubank e abra sua conta em minutos. "
            "Precisa de CPF e um documento com foto."
        ),
        "url": "https://nubank.com.br",
        "programas_oficiais": [],
    },
}


def recomendar_conta_bancaria(
    uf: str = "",
    beneficios_elegiveis: Optional[list[str]] = None,
) -> dict:
    """
    Recomenda a conta bancária mais adequada para o cidadão
    com base nos benefícios que ele pode receber.

    Args:
        uf: Estado do cidadão (UF)
        beneficios_elegiveis: Lista de códigos dos benefícios elegíveis

    Returns:
        dict com recomendação de parceiro bancário
    """
    beneficios = beneficios_elegiveis or []

    # Verifica se algum benefício é pago pela CAIXA
    caixa = PARCEIROS_BANCARIOS["caixa"]
    tem_beneficio_caixa = any(
        b in caixa["programas_oficiais"] for b in beneficios
    )

    # CAIXA é prioridade para quem tem benefícios federais
    if tem_beneficio_caixa or not beneficios:
        parceiro = caixa
        motivo = (
            "A Caixa Economica Federal e o banco que paga os beneficios sociais do governo. "
            "Com o app Caixa Tem, voce recebe Bolsa Familia, BPC, auxilios e FGTS "
            "direto no celular, sem ir ao banco."
        )
    else:
        parceiro = PARCEIROS_BANCARIOS["nubank"]
        motivo = (
            "Para receber seus beneficios, voce precisa de uma conta bancaria. "
            "O Nubank oferece conta gratis e cartao sem anuidade."
        )

    # Identifica quais benefícios serão pagos nesse banco
    beneficios_no_banco = [
        b for b in beneficios if b in parceiro.get("programas_oficiais", [])
    ]

    result = ToolResult.ok(
        data={
            "parceiro": {
                "nome": parceiro["nome"],
                "slug": parceiro["slug"],
                "descricao": parceiro["descricao"],
                "vantagens": parceiro["vantagens"],
                "como_abrir": parceiro["como_abrir"],
                "url": parceiro["url"],
            },
            "motivo": motivo,
            "beneficios_no_banco": beneficios_no_banco,
            "mensagem_cidadao": (
                f"{motivo}\n\n"
                f"Como abrir sua conta:\n{parceiro['como_abrir']}\n\n"
                f"Vantagens do {parceiro['nome']}:\n"
                + "\n".join(f"- {v}" for v in parceiro["vantagens"])
            ),
        },
        ui_hint=UIHint.PARTNER_CARD,
    )

    return result.model_dump()
