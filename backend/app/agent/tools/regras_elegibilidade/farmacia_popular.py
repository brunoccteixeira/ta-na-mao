"""
Regras de elegibilidade para o Farmácia Popular.

Programa universal com 3 níveis de acesso:

1. GRATUITO (100% desconto):
   - Medicamentos para hipertensão, diabetes e asma
   - Qualquer brasileiro com receita médica

2. GRATUITO TOTAL (todos os medicamentos):
   - Cadastrado no CadÚnico com renda até 1/2 salário mínimo
   - OU beneficiário do Bolsa Família
   - OU beneficiário do BPC

3. COM DESCONTO (até 90%):
   - Outros medicamentos da lista
   - Qualquer brasileiro com receita
"""

from . import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
    LIMITE_BAIXA_RENDA,
)


# Medicamentos gratuitos para todos (com receita)
MEDICAMENTOS_GRATUITOS_UNIVERSAL = [
    "Hipertensão: Losartana, Atenolol, Propranolol, Captopril, Enalapril, Hidroclorotiazida",
    "Diabetes: Metformina, Glibenclamida, Insulina",
    "Asma: Salbutamol, Brometo de Ipratrópio, Beclometasona",
]

# Categorias de medicamentos com desconto
MEDICAMENTOS_COM_DESCONTO = [
    "Anticoncepcionais",
    "Fraldas geriátricas",
    "Medicamentos para osteoporose",
    "Medicamentos para Parkinson",
    "Medicamentos para rinite",
    "Medicamentos para glaucoma",
]


def verificar_elegibilidade(perfil: CitizenProfile) -> EligibilityResult:
    """
    Verifica elegibilidade para o Farmácia Popular.

    Args:
        perfil: Dados do cidadão

    Returns:
        EligibilityResult com status e detalhes
    """
    # Farmácia Popular é universal - todos têm algum acesso

    # Verificar se tem acesso gratuito total (todos os medicamentos)
    tem_acesso_gratuito_total = _verificar_acesso_gratuito_total(perfil)

    if tem_acesso_gratuito_total:
        motivo_gratuidade = _obter_motivo_gratuidade(perfil)
        return EligibilityResult(
            programa="FARMACIA_POPULAR",
            programa_nome="Farmácia Popular (Gratuito Total)",
            status=EligibilityStatus.ELEGIVEL,
            motivo=f"Você tem direito a medicamentos GRATUITOS no Farmácia Popular! {motivo_gratuidade}",
            valor_estimado=None,  # Não é valor em dinheiro
            proximos_passos=[
                "Obtenha receita médica (SUS ou particular)",
                "Vá a uma farmácia credenciada",
                "Apresente CPF e receita",
                "Retire seus medicamentos gratuitamente",
            ],
            documentos_necessarios=[
                "CPF",
                "Receita médica (válida por 120 dias)",
            ],
            onde_solicitar="Qualquer farmácia credenciada (Drogasil, Pague Menos, Droga Raia, etc.)",
            observacoes="Medicamentos gratuitos: " + "; ".join(MEDICAMENTOS_GRATUITOS_UNIVERSAL),
        )
    else:
        return EligibilityResult(
            programa="FARMACIA_POPULAR",
            programa_nome="Farmácia Popular",
            status=EligibilityStatus.ELEGIVEL,
            motivo="Você pode comprar medicamentos com desconto de até 90% no Farmácia Popular! Medicamentos para hipertensão, diabetes e asma são GRATUITOS para todos.",
            valor_estimado=None,
            proximos_passos=[
                "Obtenha receita médica",
                "Vá a uma farmácia credenciada",
                "Apresente CPF e receita",
            ],
            documentos_necessarios=[
                "CPF",
                "Receita médica (válida por 120 dias)",
            ],
            onde_solicitar="Qualquer farmácia credenciada",
            observacoes="Para ter todos os medicamentos gratuitos, faça o CadÚnico no CRAS. Medicamentos já gratuitos para todos: " + "; ".join(MEDICAMENTOS_GRATUITOS_UNIVERSAL),
        )


def _verificar_acesso_gratuito_total(perfil: CitizenProfile) -> bool:
    """
    Verifica se tem direito a todos os medicamentos gratuitos.

    Critérios:
    - CadÚnico com renda até 1/2 SM per capita, OU
    - Beneficiário do Bolsa Família, OU
    - Beneficiário do BPC
    """
    # Beneficiário de programas sociais
    if perfil.recebe_bolsa_familia or perfil.recebe_bpc:
        return True

    # Cadastrado no CadÚnico com baixa renda
    if perfil.cadastrado_cadunico:
        if perfil.renda_per_capita <= LIMITE_BAIXA_RENDA:
            return True

    return False


def _obter_motivo_gratuidade(perfil: CitizenProfile) -> str:
    """Retorna o motivo pelo qual tem acesso gratuito total."""
    if perfil.recebe_bolsa_familia:
        return "Você é beneficiário do Bolsa Família."
    elif perfil.recebe_bpc:
        return "Você é beneficiário do BPC."
    elif perfil.cadastrado_cadunico:
        return "Você está no CadÚnico com renda dentro do limite."
    return ""
