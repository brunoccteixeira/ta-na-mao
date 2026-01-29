"""
Regras de elegibilidade para PIS/PASEP (dinheiro esquecido).

Contexto:
- PIS (Programa de Integração Social) - trabalhadores do setor privado
- PASEP (Programa de Formação do Patrimônio do Servidor Público) - servidores públicos
- De 1971 a 1988, parte do salário era depositada nessas contas
- Muitas pessoas nunca sacaram esse dinheiro

Critérios:
- Ter trabalhado com carteira assinada entre 1971 e 1988
- Não ter sacado o saldo anteriormente

Valor: Variável (pode ser de R$ 1 a R$ 30.000+)
Onde sacar: CAIXA (PIS) ou Banco do Brasil (PASEP)
"""

from . import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
)


def verificar_elegibilidade(perfil: CitizenProfile) -> EligibilityResult:
    """
    Verifica elegibilidade para saque de PIS/PASEP.

    Args:
        perfil: Dados do cidadão

    Returns:
        EligibilityResult com status e detalhes
    """
    # Verificar se temos informação sobre trabalho 1971-1988
    if perfil.trabalhou_1971_1988 is None:
        # Não sabemos - retornar inconclusivo com orientação
        return EligibilityResult(
            programa="PIS_PASEP",
            programa_nome="PIS/PASEP (Dinheiro Esquecido)",
            status=EligibilityStatus.INCONCLUSIVO,
            motivo="Não temos informação se você trabalhou entre 1971 e 1988. Consulte diretamente para verificar.",
            proximos_passos=[
                "Acesse o app Caixa Trabalhador (PIS) ou app BB (PASEP)",
                "Ou vá a uma agência da CAIXA ou Banco do Brasil",
                "Consulte se há saldo disponível",
            ],
            documentos_necessarios=[
                "CPF",
                "RG",
                "Carteira de trabalho (se tiver)",
            ],
            onde_solicitar="CAIXA (PIS) ou Banco do Brasil (PASEP)",
            observacoes="""Como saber se você tem direito:
- Se trabalhou com carteira assinada de 1971 a 1988, pode ter saldo
- Servidores públicos no mesmo período têm PASEP no Banco do Brasil
- Mesmo se já sacou parte, pode haver valores remanescentes
- R$ 26 bilhões ainda estão esquecidos nessas contas!""",
        )

    if not perfil.trabalhou_1971_1988:
        return EligibilityResult(
            programa="PIS_PASEP",
            programa_nome="PIS/PASEP (Dinheiro Esquecido)",
            status=EligibilityStatus.INELEGIVEL,
            motivo="O PIS/PASEP é para quem trabalhou com carteira assinada entre 1971 e 1988.",
            observacoes="Se você não trabalhou nesse período, não há saldo de PIS/PASEP.",
        )

    # Trabalhou no período - provavelmente tem direito
    return EligibilityResult(
        programa="PIS_PASEP",
        programa_nome="PIS/PASEP (Dinheiro Esquecido)",
        status=EligibilityStatus.ELEGIVEL,
        motivo="Você trabalhou entre 1971 e 1988 e pode ter dinheiro esquecido no PIS/PASEP!",
        valor_estimado=None,  # Variável
        proximos_passos=[
            "Acesse o app Caixa Trabalhador (se trabalhou no setor privado)",
            "Ou acesse o app Banco do Brasil (se foi servidor público)",
            "Consulte o saldo disponível",
            "Se preferir, vá a uma agência com seus documentos",
        ],
        documentos_necessarios=[
            "CPF",
            "RG",
            "Carteira de trabalho (opcional, mas ajuda)",
        ],
        onde_solicitar="CAIXA (PIS - setor privado) ou Banco do Brasil (PASEP - servidores)",
        observacoes="""Informações importantes:
- O valor varia: pode ser de R$ 1 a mais de R$ 30.000
- O dinheiro é seu, depositado entre 1971-1988
- Não há prazo para sacar
- Herdeiros também podem sacar (com certidão de óbito e inventário)

Existem R$ 26 bilhões esquecidos no PIS/PASEP. Não deixe o seu!""",
    )
