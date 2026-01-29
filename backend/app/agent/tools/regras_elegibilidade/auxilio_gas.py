"""
Regras de elegibilidade para o Auxílio Gás.

Critérios:
- Cadastrado no CadÚnico
- Renda per capita de até meio salário mínimo
- E ser beneficiário do Bolsa Família OU do BPC

Valor: Aproximadamente R$ 104 (varia conforme preço do gás)
Periodicidade: BIMESTRAL (a cada 2 meses)
"""

from . import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
    LIMITE_BAIXA_RENDA,
)


# Valor aproximado do auxílio gás
VALOR_AUXILIO_GAS = 104.00


def verificar_elegibilidade(perfil: CitizenProfile) -> EligibilityResult:
    """
    Verifica elegibilidade para o Auxílio Gás.

    Args:
        perfil: Dados do cidadão

    Returns:
        EligibilityResult com status e detalhes
    """
    # Verificar se está no CadÚnico
    if not perfil.cadastrado_cadunico and not perfil.recebe_bolsa_familia and not perfil.recebe_bpc:
        # Verificar se teria direito se fizesse CadÚnico
        if perfil.renda_per_capita <= LIMITE_BAIXA_RENDA:
            return EligibilityResult(
                programa="AUXILIO_GAS",
                programa_nome="Auxílio Gás",
                status=EligibilityStatus.ELEGIVEL,
                motivo="Você pode ter direito ao Auxílio Gás, mas precisa estar no CadÚnico e receber Bolsa Família ou BPC.",
                valor_estimado=VALOR_AUXILIO_GAS,
                proximos_passos=[
                    "Faça o CadÚnico no CRAS",
                    "Solicite o Bolsa Família",
                    "O Auxílio Gás é pago automaticamente junto com o Bolsa Família",
                ],
                documentos_necessarios=[
                    "CPF de todos da família",
                    "RG ou certidão de nascimento",
                    "Comprovante de residência",
                    "Comprovante de renda",
                ],
                onde_solicitar="CRAS (Centro de Referência de Assistência Social)",
                observacoes="O Auxílio Gás é pago junto com o Bolsa Família a cada 2 meses.",
            )
        else:
            return EligibilityResult(
                programa="AUXILIO_GAS",
                programa_nome="Auxílio Gás",
                status=EligibilityStatus.INELEGIVEL,
                motivo=f"Sua renda per capita de R$ {perfil.renda_per_capita:.2f} está acima do limite de R$ {LIMITE_BAIXA_RENDA:.2f}.",
            )

    # Verificar se recebe Bolsa Família ou BPC
    if not perfil.recebe_bolsa_familia and not perfil.recebe_bpc:
        return EligibilityResult(
            programa="AUXILIO_GAS",
            programa_nome="Auxílio Gás",
            status=EligibilityStatus.ELEGIVEL,
            motivo="Você está no CadÚnico, mas o Auxílio Gás é pago apenas para quem recebe Bolsa Família ou BPC.",
            proximos_passos=[
                "Solicite o Bolsa Família no CRAS",
                "Após aprovação, o Auxílio Gás será pago automaticamente",
            ],
            onde_solicitar="CRAS",
            observacoes="O Auxílio Gás não pode ser solicitado separadamente.",
        )

    # Verificar renda
    if perfil.renda_per_capita > LIMITE_BAIXA_RENDA:
        return EligibilityResult(
            programa="AUXILIO_GAS",
            programa_nome="Auxílio Gás",
            status=EligibilityStatus.INELEGIVEL,
            motivo=f"Sua renda per capita de R$ {perfil.renda_per_capita:.2f} está acima do limite de R$ {LIMITE_BAIXA_RENDA:.2f}.",
        )

    # Elegível
    fonte_beneficio = "Bolsa Família" if perfil.recebe_bolsa_familia else "BPC"
    return EligibilityResult(
        programa="AUXILIO_GAS",
        programa_nome="Auxílio Gás",
        status=EligibilityStatus.ELEGIVEL,
        motivo=f"Você tem direito ao Auxílio Gás! Como beneficiário do {fonte_beneficio}, você deve receber automaticamente.",
        valor_estimado=VALOR_AUXILIO_GAS,
        proximos_passos=[
            "Verifique se já está recebendo o Auxílio Gás",
            "O valor é depositado junto com o Bolsa Família/BPC",
            "Pagamento é bimestral (meses pares)",
        ],
        observacoes=f"Valor aproximado: R$ {VALOR_AUXILIO_GAS:.2f} a cada 2 meses. Pago automaticamente para beneficiários do {fonte_beneficio}.",
    )
