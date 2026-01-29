"""
Regras de elegibilidade para o Bolsa Família.

Critérios (2024/2025):
- Renda familiar per capita de até R$ 218,00 (linha de pobreza)
- Estar cadastrado no CadÚnico
- Cumprir condicionalidades (frequência escolar, vacinação)

Valores:
- Benefício Primeira Infância: R$ 150 (crianças 0-7 anos)
- Benefício Composição Familiar: R$ 50 (por pessoa 7-18 anos)
- Benefício Complementar: completar até R$ 600 mínimo
- Adicional de R$ 50-150 por gestante/nutriz
"""

from . import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
    LIMITE_POBREZA,
    LIMITE_EXTREMA_POBREZA,
)


def verificar_elegibilidade(perfil: CitizenProfile) -> EligibilityResult:
    """
    Verifica elegibilidade para o Bolsa Família.

    Args:
        perfil: Dados do cidadão

    Returns:
        EligibilityResult com status e detalhes
    """
    # Se já recebe, retornar status
    if perfil.recebe_bolsa_familia:
        return EligibilityResult(
            programa="BOLSA_FAMILIA",
            programa_nome="Bolsa Família",
            status=EligibilityStatus.JA_RECEBE,
            motivo=f"Você já recebe Bolsa Família (R$ {perfil.valor_bolsa_familia:.2f}/mês)",
            valor_estimado=perfil.valor_bolsa_familia,
            observacoes="Mantenha seu CadÚnico atualizado para continuar recebendo.",
        )

    # Calcular renda per capita
    renda_per_capita = perfil.renda_per_capita

    # Verificar elegibilidade por renda
    if renda_per_capita <= LIMITE_POBREZA:
        # Estimar valor do benefício
        valor_estimado = _estimar_valor_beneficio(perfil)

        # Determinar faixa
        if renda_per_capita <= LIMITE_EXTREMA_POBREZA:
            faixa = "extrema pobreza"
        else:
            faixa = "pobreza"

        # Verificar se já está no CadÚnico
        if perfil.cadastrado_cadunico:
            return EligibilityResult(
                programa="BOLSA_FAMILIA",
                programa_nome="Bolsa Família",
                status=EligibilityStatus.ELEGIVEL,
                motivo=f"Você pode ter direito ao Bolsa Família! Sua renda per capita de R$ {renda_per_capita:.2f} está dentro do limite de R$ {LIMITE_POBREZA:.2f} (faixa de {faixa}).",
                valor_estimado=valor_estimado,
                proximos_passos=[
                    "Vá ao CRAS mais próximo",
                    "Solicite inclusão no Bolsa Família",
                    "Aguarde análise (até 45 dias)",
                ],
                documentos_necessarios=[
                    "CPF de todos da família",
                    "RG ou certidão de nascimento",
                    "Comprovante de residência",
                    "Comprovante de renda (se tiver)",
                    "Carteira de trabalho (se tiver)",
                ],
                onde_solicitar="CRAS (Centro de Referência de Assistência Social)",
            )
        else:
            return EligibilityResult(
                programa="BOLSA_FAMILIA",
                programa_nome="Bolsa Família",
                status=EligibilityStatus.ELEGIVEL,
                motivo="Você pode ter direito ao Bolsa Família! Sua renda está dentro do limite. Primeiro você precisa fazer o CadÚnico.",
                valor_estimado=valor_estimado,
                proximos_passos=[
                    "Primeiro: Fazer cadastro no CadÚnico",
                    "Depois: Solicitar Bolsa Família",
                    "Vá ao CRAS com seus documentos",
                ],
                documentos_necessarios=[
                    "CPF de todos da família",
                    "RG ou certidão de nascimento",
                    "Comprovante de residência",
                    "Comprovante de renda (se tiver)",
                ],
                onde_solicitar="CRAS (Centro de Referência de Assistência Social)",
                observacoes="O CadÚnico é obrigatório para receber o Bolsa Família.",
            )
    else:
        return EligibilityResult(
            programa="BOLSA_FAMILIA",
            programa_nome="Bolsa Família",
            status=EligibilityStatus.INELEGIVEL,
            motivo=f"Sua renda per capita de R$ {renda_per_capita:.2f} está acima do limite de R$ {LIMITE_POBREZA:.2f} para o Bolsa Família.",
            observacoes="Se sua situação mudar, você pode solicitar novamente.",
        )


def _estimar_valor_beneficio(perfil: CitizenProfile) -> float:
    """
    Estima valor aproximado do benefício.

    Regras simplificadas:
    - Mínimo garantido: R$ 600
    - + R$ 150 por criança 0-7 anos
    - + R$ 50 por pessoa 7-18 anos
    - + R$ 50-150 por gestante
    """
    valor_base = 600.0  # Mínimo garantido

    # Adicional por filhos (estimativa)
    if perfil.tem_filhos_menores and perfil.quantidade_filhos > 0:
        # Assumir média: metade 0-7, metade 7-18
        criancas_pequenas = perfil.quantidade_filhos // 2 or 1
        criancas_maiores = perfil.quantidade_filhos - criancas_pequenas

        valor_base += criancas_pequenas * 150  # Primeira Infância
        valor_base += criancas_maiores * 50     # Composição Familiar

    # Adicional por gestante
    if perfil.tem_gestante:
        valor_base += 50

    return valor_base
