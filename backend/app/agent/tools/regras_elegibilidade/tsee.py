"""
Regras de elegibilidade para a Tarifa Social de Energia Elétrica (TSEE).

Critérios:
- Cadastrado no CadÚnico com renda per capita até 1/2 salário mínimo
- OU beneficiário do BPC
- OU família com membro que use equipamento vital (ex: respirador)

Descontos:
- Até 30 kWh/mês: 65% de desconto
- 31 a 100 kWh/mês: 40% de desconto
- 101 a 220 kWh/mês: 10% de desconto
- Acima de 220 kWh/mês: sem desconto

Indígenas e quilombolas: desconto para qualquer consumo.
"""

from . import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
    LIMITE_BAIXA_RENDA,
)


def verificar_elegibilidade(perfil: CitizenProfile) -> EligibilityResult:
    """
    Verifica elegibilidade para a Tarifa Social de Energia Elétrica.

    Args:
        perfil: Dados do cidadão

    Returns:
        EligibilityResult com status e detalhes
    """
    # Verificar critérios de elegibilidade
    elegivel, motivo_elegibilidade = _verificar_criterios(perfil)

    if elegivel:
        return EligibilityResult(
            programa="TSEE",
            programa_nome="Tarifa Social de Energia Elétrica",
            status=EligibilityStatus.ELEGIVEL,
            motivo=f"Você pode ter direito ao desconto na conta de luz! {motivo_elegibilidade}",
            valor_estimado=None,  # Varia conforme consumo
            proximos_passos=[
                "Verifique se sua conta de luz já tem o desconto",
                "Se não tiver, entre em contato com sua distribuidora de energia",
                "Solicite a inclusão na Tarifa Social",
                "Apresente seus documentos",
            ],
            documentos_necessarios=[
                "CPF",
                "RG",
                "Conta de luz recente",
                "Comprovante de CadÚnico (NIS)",
            ],
            onde_solicitar="Distribuidora de energia (CPFL, Enel, Light, Cemig, etc.)",
            observacoes=_obter_observacoes_desconto(),
        )
    else:
        # Verificar se pode se tornar elegível fazendo CadÚnico
        if perfil.renda_per_capita <= LIMITE_BAIXA_RENDA and not perfil.cadastrado_cadunico:
            return EligibilityResult(
                programa="TSEE",
                programa_nome="Tarifa Social de Energia Elétrica",
                status=EligibilityStatus.ELEGIVEL,
                motivo="Você pode ter direito ao desconto na conta de luz, mas precisa fazer o CadÚnico primeiro.",
                proximos_passos=[
                    "Faça o CadÚnico no CRAS",
                    "Depois, solicite a Tarifa Social na distribuidora",
                ],
                documentos_necessarios=[
                    "CPF",
                    "RG",
                    "Comprovante de residência",
                    "Comprovante de renda",
                ],
                onde_solicitar="CRAS (para CadÚnico) e depois distribuidora de energia",
                observacoes="O CadÚnico é obrigatório para ter direito à Tarifa Social.",
            )
        else:
            return EligibilityResult(
                programa="TSEE",
                programa_nome="Tarifa Social de Energia Elétrica",
                status=EligibilityStatus.INELEGIVEL,
                motivo=f"Sua renda per capita de R$ {perfil.renda_per_capita:.2f} está acima do limite de R$ {LIMITE_BAIXA_RENDA:.2f} para a Tarifa Social.",
                observacoes="Se sua situação mudar, você pode solicitar novamente.",
            )


def _verificar_criterios(perfil: CitizenProfile) -> tuple[bool, str]:
    """
    Verifica se atende aos critérios de elegibilidade.

    Returns:
        (elegível, motivo)
    """
    # BPC é critério automático
    if perfil.recebe_bpc:
        return True, "Você é beneficiário do BPC."

    # CadÚnico com baixa renda
    if perfil.cadastrado_cadunico:
        if perfil.renda_per_capita <= LIMITE_BAIXA_RENDA:
            return True, "Você está no CadÚnico com renda dentro do limite."

    # Bolsa Família implica CadÚnico
    if perfil.recebe_bolsa_familia:
        return True, "Você é beneficiário do Bolsa Família."

    return False, ""


def _obter_observacoes_desconto() -> str:
    """Retorna texto explicativo sobre os descontos."""
    return """Descontos conforme consumo:
- Até 30 kWh/mês: 65% de desconto
- 31 a 100 kWh/mês: 40% de desconto
- 101 a 220 kWh/mês: 10% de desconto
- Acima de 220 kWh/mês: sem desconto adicional

Famílias indígenas e quilombolas têm desconto para qualquer consumo."""
