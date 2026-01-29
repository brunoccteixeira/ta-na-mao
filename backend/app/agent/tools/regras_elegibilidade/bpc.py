"""
Regras de elegibilidade para o BPC/LOAS.

BPC = Benefício de Prestação Continuada
LOAS = Lei Orgânica da Assistência Social

Critérios:
- Idoso (65+ anos) OU pessoa com deficiência
- Renda familiar per capita de até 1/4 do salário mínimo
- Não receber outro benefício da Previdência Social
- Estar inscrito no CadÚnico

Valor: 1 salário mínimo (R$ 1.412 em 2024)
"""

from . import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
    SALARIO_MINIMO,
)


# Limite de renda: 1/4 do salário mínimo per capita
LIMITE_RENDA_BPC = SALARIO_MINIMO / 4  # R$ 353,00


def verificar_elegibilidade(perfil: CitizenProfile) -> EligibilityResult:
    """
    Verifica elegibilidade para o BPC/LOAS.

    Args:
        perfil: Dados do cidadão

    Returns:
        EligibilityResult com status e detalhes
    """
    # Se já recebe BPC
    if perfil.recebe_bpc:
        return EligibilityResult(
            programa="BPC",
            programa_nome="BPC/LOAS",
            status=EligibilityStatus.JA_RECEBE,
            motivo=f"Você já recebe BPC/LOAS (R$ {perfil.valor_bpc:.2f}/mês)",
            valor_estimado=perfil.valor_bpc,
            observacoes="Mantenha seu CadÚnico atualizado. A revisão do BPC acontece a cada 2 anos.",
        )

    # Verificar se é idoso ou PCD
    e_idoso = _verificar_idoso(perfil)
    e_pcd = perfil.tem_pcd

    if not e_idoso and not e_pcd:
        return EligibilityResult(
            programa="BPC",
            programa_nome="BPC/LOAS",
            status=EligibilityStatus.INELEGIVEL,
            motivo="O BPC é destinado a idosos (65+ anos) ou pessoas com deficiência.",
            observacoes="Se você tem alguma deficiência que impede de trabalhar, consulte um médico para obter laudo.",
        )

    # Verificar renda
    renda_per_capita = perfil.renda_per_capita

    if renda_per_capita > LIMITE_RENDA_BPC:
        return EligibilityResult(
            programa="BPC",
            programa_nome="BPC/LOAS",
            status=EligibilityStatus.INELEGIVEL,
            motivo=f"Sua renda per capita de R$ {renda_per_capita:.2f} está acima do limite de R$ {LIMITE_RENDA_BPC:.2f} (1/4 do salário mínimo).",
            observacoes="Se sua renda mudar, você pode solicitar novamente.",
        )

    # Elegível - determinar tipo
    tipo_bpc = "BPC Idoso" if e_idoso else "BPC para Pessoa com Deficiência"

    if e_idoso:
        return EligibilityResult(
            programa="BPC",
            programa_nome=tipo_bpc,
            status=EligibilityStatus.ELEGIVEL,
            motivo=f"Você pode ter direito ao {tipo_bpc}! Idade de 65+ anos e renda per capita de R$ {renda_per_capita:.2f} (abaixo de R$ {LIMITE_RENDA_BPC:.2f}).",
            valor_estimado=SALARIO_MINIMO,
            proximos_passos=[
                "Fazer ou atualizar CadÚnico no CRAS",
                "Agendar atendimento no INSS (Meu INSS ou 135)",
                "Comparecer na data agendada com documentos",
                "Aguardar análise (até 45 dias)",
            ],
            documentos_necessarios=[
                "CPF",
                "RG ou certidão de nascimento",
                "Comprovante de residência",
                "Comprovante de renda familiar",
                "Número do CadÚnico (NIS)",
            ],
            onde_solicitar="INSS (agendar pelo Meu INSS ou ligue 135)",
        )
    else:  # PCD
        return EligibilityResult(
            programa="BPC",
            programa_nome=tipo_bpc,
            status=EligibilityStatus.ELEGIVEL,
            motivo=f"Você pode ter direito ao {tipo_bpc}! Renda per capita de R$ {renda_per_capita:.2f} está abaixo do limite.",
            valor_estimado=SALARIO_MINIMO,
            proximos_passos=[
                "Fazer ou atualizar CadÚnico no CRAS",
                "Obter laudo médico atualizado",
                "Agendar perícia no INSS (Meu INSS ou 135)",
                "Comparecer na perícia com documentos",
                "Aguardar resultado (até 45 dias)",
            ],
            documentos_necessarios=[
                "CPF",
                "RG ou certidão de nascimento",
                "Comprovante de residência",
                "Comprovante de renda familiar",
                "Número do CadÚnico (NIS)",
                "Laudos médicos (atestando deficiência)",
                "Exames e relatórios médicos",
            ],
            onde_solicitar="INSS (agendar pelo Meu INSS ou ligue 135)",
            observacoes="A perícia médica do INSS vai avaliar se a deficiência impede de trabalhar. Leve todos os laudos e exames que tiver.",
        )


def _verificar_idoso(perfil: CitizenProfile) -> bool:
    """Verifica se o cidadão tem 65+ anos."""
    # Primeiro, verificar flag explícita
    if perfil.tem_idoso_65_mais:
        return True

    # Depois, calcular pela data de nascimento
    idade = perfil.idade
    if idade is not None and idade >= 65:
        return True

    return False
