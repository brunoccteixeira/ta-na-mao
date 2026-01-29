"""
Regras de elegibilidade para o Programa Dignidade Menstrual.

Critérios:
- Ser mulher em idade fértil (12 a 51 anos aproximadamente)
- Estar cadastrada no CadÚnico
- Renda per capita de até meio salário mínimo

Benefício: Absorventes higiênicos gratuitos
Local de retirada: Farmácias credenciadas ao Farmácia Popular e UBS
"""

from . import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
    LIMITE_BAIXA_RENDA,
)


IDADE_MINIMA = 12
IDADE_MAXIMA = 51


def verificar_elegibilidade(perfil: CitizenProfile) -> EligibilityResult:
    """
    Verifica elegibilidade para o Programa Dignidade Menstrual.

    Args:
        perfil: Dados do cidadão

    Returns:
        EligibilityResult com status e detalhes
    """
    # Verificar idade (se disponível)
    idade = perfil.idade
    if idade is not None:
        if idade < IDADE_MINIMA or idade > IDADE_MAXIMA:
            return EligibilityResult(
                programa="DIGNIDADE_MENSTRUAL",
                programa_nome="Dignidade Menstrual",
                status=EligibilityStatus.INELEGIVEL,
                motivo=f"O programa é destinado a mulheres de {IDADE_MINIMA} a {IDADE_MAXIMA} anos.",
            )

    # Verificar CadÚnico
    if not perfil.cadastrado_cadunico and not perfil.recebe_bolsa_familia:
        # Verificar se teria direito se fizesse CadÚnico
        if perfil.renda_per_capita <= LIMITE_BAIXA_RENDA:
            return EligibilityResult(
                programa="DIGNIDADE_MENSTRUAL",
                programa_nome="Dignidade Menstrual",
                status=EligibilityStatus.ELEGIVEL,
                motivo="Você pode ter direito a absorventes gratuitos, mas precisa estar no CadÚnico.",
                proximos_passos=[
                    "Faça o CadÚnico no CRAS",
                    "Depois, vá a uma farmácia credenciada ou UBS",
                    "Apresente seu CPF para retirar os absorventes",
                ],
                documentos_necessarios=[
                    "CPF",
                    "RG",
                    "Comprovante de residência",
                ],
                onde_solicitar="CRAS (para CadÚnico) e depois farmácia ou UBS",
            )
        else:
            return EligibilityResult(
                programa="DIGNIDADE_MENSTRUAL",
                programa_nome="Dignidade Menstrual",
                status=EligibilityStatus.INELEGIVEL,
                motivo=f"Sua renda per capita de R$ {perfil.renda_per_capita:.2f} está acima do limite de R$ {LIMITE_BAIXA_RENDA:.2f}.",
            )

    # Verificar renda
    if perfil.renda_per_capita > LIMITE_BAIXA_RENDA:
        return EligibilityResult(
            programa="DIGNIDADE_MENSTRUAL",
            programa_nome="Dignidade Menstrual",
            status=EligibilityStatus.INELEGIVEL,
            motivo=f"Sua renda per capita de R$ {perfil.renda_per_capita:.2f} está acima do limite.",
        )

    # Elegível
    return EligibilityResult(
        programa="DIGNIDADE_MENSTRUAL",
        programa_nome="Dignidade Menstrual",
        status=EligibilityStatus.ELEGIVEL,
        motivo="Você tem direito a absorventes gratuitos pelo programa Dignidade Menstrual!",
        proximos_passos=[
            "Vá a uma farmácia credenciada ao Farmácia Popular",
            "Ou vá a uma UBS (Unidade Básica de Saúde)",
            "Apresente seu CPF",
            "Retire seus absorventes gratuitamente",
        ],
        documentos_necessarios=[
            "CPF",
        ],
        onde_solicitar="Farmácias credenciadas (Drogasil, Pague Menos, etc.) ou UBS",
        observacoes="A retirada é mensal. Você pode pegar absorventes todo mês.",
    )
