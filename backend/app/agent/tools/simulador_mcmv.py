"""
Simulador de Financiamento MCMV - Minha Casa Minha Vida.

Permite simular:
- Valor máximo de financiamento por faixa
- Parcelas mensais (Sistema Price e SAC)
- Subsídio estimado
- Uso de FGTS
- Comparação entre modalidades

Valores atualizados para 2026.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from .regras_elegibilidade import (
    MCMV_FAIXA_1,
    MCMV_FAIXA_2,
    MCMV_FAIXA_3,
    MCMV_FAIXA_4,
    MCMV_TETO_RM_GRANDE,
    MCMV_TETO_DEMAIS,
    MCMV_TETO_FAIXA_3,
    MCMV_TETO_FAIXA_4,
    MCMV_SUBSIDIO_FAIXA_1,
    MCMV_SUBSIDIO_FAIXA_2,
    MCMV_JUROS_FAIXA_1_MIN,
    MCMV_JUROS_FAIXA_1_MAX,
    MCMV_JUROS_FAIXA_2_MIN,
    MCMV_JUROS_FAIXA_2_MAX,
    MCMV_JUROS_FAIXA_3_MIN,
    MCMV_JUROS_FAIXA_3_MAX,
    MCMV_JUROS_FAIXA_4,
    REFORMA_LIMITE_FAIXA_1,
    REFORMA_LIMITE_FAIXA_2,
    REFORMA_CREDITO_MIN,
    REFORMA_CREDITO_MAX,
    REFORMA_JUROS_FAIXA_1,
    REFORMA_JUROS_FAIXA_2,
)


class SistemaAmortizacao(Enum):
    """Sistemas de amortização disponíveis."""
    PRICE = "price"  # Parcelas fixas
    SAC = "sac"      # Amortização constante


@dataclass
class SimulacaoResultado:
    """Resultado de uma simulação de financiamento."""
    # Identificação
    faixa: str
    modalidade: str

    # Valores do imóvel
    valor_imovel: float
    valor_entrada: float
    valor_fgts: float
    subsidio: float
    valor_financiado: float

    # Condições do financiamento
    taxa_juros_anual: float
    prazo_meses: int
    sistema: SistemaAmortizacao

    # Parcelas
    parcela_inicial: float
    parcela_final: float  # SAC: última parcela | Price: igual à inicial
    parcela_media: float

    # Custos totais
    custo_total: float
    juros_total: float

    # Análise
    comprometimento_renda: float  # % da renda
    economia_vs_mercado: float    # R$ economizados
    viavel: bool
    observacoes: List[str]


@dataclass
class ComparacaoModalidades:
    """Comparação entre diferentes modalidades."""
    renda_familiar: float
    faixa: str
    modalidades: List[Dict[str, Any]]
    recomendacao: str
    observacoes: List[str]


def simular_financiamento_mcmv(
    renda_familiar: float,
    valor_imovel_desejado: Optional[float] = None,
    valor_entrada_disponivel: float = 0,
    valor_fgts: float = 0,
    prazo_anos: int = 35,
    idade_comprador: Optional[int] = None,
    regiao_metropolitana: bool = False,
    populacao_municipio: int = 0,
    sistema: SistemaAmortizacao = SistemaAmortizacao.PRICE,
) -> SimulacaoResultado:
    """
    Simula financiamento habitacional pelo MCMV.

    Args:
        renda_familiar: Renda bruta mensal da família
        valor_imovel_desejado: Valor do imóvel desejado (None = máximo possível)
        valor_entrada_disponivel: Valor disponível para entrada
        valor_fgts: Saldo de FGTS disponível
        prazo_anos: Prazo desejado em anos (máx 35)
        idade_comprador: Idade do comprador (ajusta prazo máximo)
        regiao_metropolitana: Se está em região metropolitana
        populacao_municipio: População do município
        sistema: Sistema de amortização (PRICE ou SAC)

    Returns:
        SimulacaoResultado com todos os detalhes
    """
    observacoes = []

    # Determinar faixa e limites
    faixa = _determinar_faixa(renda_familiar)
    if faixa is None:
        return _resultado_inelegivel(renda_familiar)

    # Obter parâmetros da faixa
    valor_max, subsidio_max, juros = _obter_parametros_faixa(
        faixa, regiao_metropolitana, populacao_municipio
    )

    # Ajustar prazo pela idade
    prazo_meses = prazo_anos * 12
    if idade_comprador is not None:
        prazo_max_meses = int((80.5 - idade_comprador) * 12)
        if prazo_meses > prazo_max_meses:
            prazo_meses = prazo_max_meses
            prazo_anos = prazo_meses // 12
            observacoes.append(f"Prazo ajustado para {prazo_anos} anos pela idade")

    prazo_meses = max(60, prazo_meses)  # Mínimo 5 anos

    # Determinar valor do imóvel
    if valor_imovel_desejado is not None:
        valor_imovel = min(valor_imovel_desejado, valor_max)
        if valor_imovel_desejado > valor_max:
            observacoes.append(f"Valor do imóvel limitado a R$ {valor_max:,.0f}")
    else:
        valor_imovel = valor_max

    # Calcular subsídio
    subsidio = _calcular_subsidio(
        faixa, renda_familiar, valor_imovel, subsidio_max
    )

    # Calcular valor a financiar
    entrada_total = valor_entrada_disponivel + valor_fgts
    valor_financiado = valor_imovel - subsidio - entrada_total

    if valor_financiado <= 0:
        valor_financiado = 0
        observacoes.append("Entrada + subsídio cobrem o valor total!")

    # Calcular parcelas
    taxa_mensal = juros / 100 / 12

    if sistema == SistemaAmortizacao.PRICE:
        parcela = _calcular_parcela_price(valor_financiado, taxa_mensal, prazo_meses)
        parcela_inicial = parcela
        parcela_final = parcela
        parcela_media = parcela
    else:  # SAC
        parcela_inicial, parcela_final = _calcular_parcelas_sac(
            valor_financiado, taxa_mensal, prazo_meses
        )
        parcela_media = (parcela_inicial + parcela_final) / 2

    # Calcular custos totais
    if sistema == SistemaAmortizacao.PRICE:
        custo_total = parcela * prazo_meses
    else:
        custo_total = (parcela_inicial + parcela_final) / 2 * prazo_meses

    juros_total = custo_total - valor_financiado

    # Análise de viabilidade
    comprometimento = (parcela_inicial / renda_familiar * 100) if renda_familiar > 0 else 0
    viavel = comprometimento <= 30

    if comprometimento > 30:
        observacoes.append(f"Comprometimento de {comprometimento:.1f}% da renda (limite recomendado: 30%)")
    elif comprometimento > 25:
        observacoes.append("Comprometimento próximo do limite recomendado")

    # Economia vs mercado (taxa média de mercado ~12% a.a.)
    taxa_mercado = 12.0
    parcela_mercado = _calcular_parcela_price(
        valor_imovel - entrada_total, taxa_mercado / 100 / 12, prazo_meses
    )
    economia_total = (parcela_mercado - parcela_inicial) * prazo_meses + subsidio
    economia_mensal = parcela_mercado - parcela_inicial

    observacoes.append(f"Economia de R$ {economia_mensal:,.0f}/mês comparado ao mercado")

    return SimulacaoResultado(
        faixa=faixa,
        modalidade="Aquisição",
        valor_imovel=valor_imovel,
        valor_entrada=valor_entrada_disponivel + valor_fgts,
        valor_fgts=valor_fgts,
        subsidio=subsidio,
        valor_financiado=valor_financiado,
        taxa_juros_anual=juros,
        prazo_meses=prazo_meses,
        sistema=sistema,
        parcela_inicial=round(parcela_inicial, 2),
        parcela_final=round(parcela_final, 2),
        parcela_media=round(parcela_media, 2),
        custo_total=round(custo_total, 2),
        juros_total=round(juros_total, 2),
        comprometimento_renda=round(comprometimento, 1),
        economia_vs_mercado=round(economia_total, 2),
        viavel=viavel,
        observacoes=observacoes,
    )


def simular_reforma(
    renda_familiar: float,
    valor_reforma: float,
    prazo_meses: int = 48,
) -> SimulacaoResultado:
    """
    Simula crédito para reforma pelo Programa Reforma Casa Brasil.

    Args:
        renda_familiar: Renda bruta mensal da família
        valor_reforma: Valor total da reforma desejada
        prazo_meses: Prazo em meses (24 a 60)

    Returns:
        SimulacaoResultado com detalhes do financiamento
    """
    observacoes = []

    # Determinar faixa de reforma
    if renda_familiar <= REFORMA_LIMITE_FAIXA_1:
        faixa = "Reforma Faixa 1"
        juros_mensal = REFORMA_JUROS_FAIXA_1
    elif renda_familiar <= REFORMA_LIMITE_FAIXA_2:
        faixa = "Reforma Faixa 2"
        juros_mensal = REFORMA_JUROS_FAIXA_2
    else:
        return SimulacaoResultado(
            faixa="Inelegível",
            modalidade="Reforma",
            valor_imovel=0,
            valor_entrada=0,
            valor_fgts=0,
            subsidio=0,
            valor_financiado=0,
            taxa_juros_anual=0,
            prazo_meses=0,
            sistema=SistemaAmortizacao.PRICE,
            parcela_inicial=0,
            parcela_final=0,
            parcela_media=0,
            custo_total=0,
            juros_total=0,
            comprometimento_renda=0,
            economia_vs_mercado=0,
            viavel=False,
            observacoes=[f"Renda de R$ {renda_familiar:,.0f} acima do limite de R$ {REFORMA_LIMITE_FAIXA_2:,.0f}"],
        )

    # Ajustar valor da reforma aos limites
    valor_credito = max(REFORMA_CREDITO_MIN, min(valor_reforma, REFORMA_CREDITO_MAX))
    if valor_reforma > REFORMA_CREDITO_MAX:
        observacoes.append(f"Crédito limitado a R$ {REFORMA_CREDITO_MAX:,.0f}")

    # Ajustar prazo
    prazo_meses = max(24, min(60, prazo_meses))

    # Calcular parcela (Sistema Price)
    taxa_decimal = juros_mensal / 100
    if taxa_decimal > 0:
        fator = (1 + taxa_decimal) ** prazo_meses
        parcela = valor_credito * (taxa_decimal * fator) / (fator - 1)
    else:
        parcela = valor_credito / prazo_meses

    custo_total = parcela * prazo_meses
    juros_total = custo_total - valor_credito

    comprometimento = (parcela / renda_familiar * 100) if renda_familiar > 0 else 0
    viavel = comprometimento <= 30

    observacoes.append(f"Liberação: 90% inicial (R$ {valor_credito * 0.9:,.0f}) + 10% após comprovação")

    return SimulacaoResultado(
        faixa=faixa,
        modalidade="Reforma Casa Brasil",
        valor_imovel=valor_credito,
        valor_entrada=0,
        valor_fgts=0,
        subsidio=0,
        valor_financiado=valor_credito,
        taxa_juros_anual=juros_mensal * 12,
        prazo_meses=prazo_meses,
        sistema=SistemaAmortizacao.PRICE,
        parcela_inicial=round(parcela, 2),
        parcela_final=round(parcela, 2),
        parcela_media=round(parcela, 2),
        custo_total=round(custo_total, 2),
        juros_total=round(juros_total, 2),
        comprometimento_renda=round(comprometimento, 1),
        economia_vs_mercado=0,
        viavel=viavel,
        observacoes=observacoes,
    )


def comparar_modalidades(
    renda_familiar: float,
    valor_fgts: float = 0,
    tem_casa_propria: bool = False,
    regiao_metropolitana: bool = False,
) -> ComparacaoModalidades:
    """
    Compara diferentes modalidades habitacionais disponíveis.

    Args:
        renda_familiar: Renda bruta mensal da família
        valor_fgts: Saldo de FGTS disponível
        tem_casa_propria: Se já possui casa própria
        regiao_metropolitana: Se está em região metropolitana

    Returns:
        ComparacaoModalidades com análise de cada opção
    """
    modalidades = []
    observacoes = []
    recomendacao = ""

    faixa = _determinar_faixa(renda_familiar)

    # Se já tem casa, só reforma
    if tem_casa_propria:
        if renda_familiar <= REFORMA_LIMITE_FAIXA_2:
            reforma = simular_reforma(renda_familiar, REFORMA_CREDITO_MAX)
            modalidades.append({
                "tipo": "Reforma Casa Brasil",
                "disponivel": True,
                "parcela_estimada": reforma.parcela_inicial,
                "vantagens": ["Crédito para melhorias na sua casa", "Juros subsidiados"],
                "desvantagens": ["Valor limitado a R$ 30 mil"],
            })
            recomendacao = "Reforma Casa Brasil é sua melhor opção"
        else:
            observacoes.append("Renda acima do limite para programa de reformas")
            recomendacao = "Busque linhas de crédito para reforma em bancos"

        return ComparacaoModalidades(
            renda_familiar=renda_familiar,
            faixa=faixa or "Não aplicável",
            modalidades=modalidades,
            recomendacao=recomendacao,
            observacoes=observacoes,
        )

    # Aquisição de imóvel novo
    if faixa:
        sim_novo = simular_financiamento_mcmv(
            renda_familiar=renda_familiar,
            valor_fgts=valor_fgts,
            regiao_metropolitana=regiao_metropolitana,
        )

        vantagens_novo = ["Imóvel novo com garantia", "Padrão construtivo do programa"]
        desvantagens_novo = ["Localização pode ser distante do centro"]

        if sim_novo.subsidio > 0:
            vantagens_novo.insert(0, f"Subsídio de R$ {sim_novo.subsidio:,.0f}")

        modalidades.append({
            "tipo": "Aquisição imóvel novo",
            "disponivel": True,
            "valor_maximo": sim_novo.valor_imovel,
            "subsidio": sim_novo.subsidio,
            "parcela_estimada": sim_novo.parcela_inicial,
            "juros": sim_novo.taxa_juros_anual,
            "vantagens": vantagens_novo,
            "desvantagens": desvantagens_novo,
        })

    # Aquisição de imóvel usado (Faixas 3 e 4)
    if faixa in ["Faixa 3", "Faixa 4"]:
        modalidades.append({
            "tipo": "Aquisição imóvel usado",
            "disponivel": True,
            "valor_maximo": MCMV_TETO_FAIXA_4 if faixa == "Faixa 4" else MCMV_TETO_FAIXA_3,
            "subsidio": 0,
            "parcela_estimada": sim_novo.parcela_inicial,  # Similar
            "juros": sim_novo.taxa_juros_anual,
            "vantagens": [
                "Maior variedade de imóveis",
                "Pode escolher localização melhor",
                "Imóvel pronto para morar"
            ],
            "desvantagens": [
                "Imóvel sem garantia de construtora",
                "Pode precisar de reformas"
            ],
        })

    # MCMV Entidades (Faixa 1)
    if faixa == "Faixa 1":
        modalidades.append({
            "tipo": "MCMV Entidades",
            "disponivel": True,
            "valor_maximo": MCMV_TETO_DEMAIS,
            "subsidio": MCMV_SUBSIDIO_FAIXA_1,
            "parcela_estimada": 0,  # Pode ser 100% subsidiado
            "juros": MCMV_JUROS_FAIXA_1_MIN,
            "vantagens": [
                "Construção por autogestão",
                "Participação da comunidade",
                "Pode ser 100% subsidiado"
            ],
            "desvantagens": [
                "Depende de organização coletiva",
                "Prazo de construção variável"
            ],
        })

        modalidades.append({
            "tipo": "Locação Social",
            "disponivel": True,
            "valor_maximo": 0,
            "subsidio": 0,
            "parcela_estimada": 300,  # Estimativa
            "juros": 0,
            "vantagens": [
                "Aluguel subsidiado",
                "Localização em regiões centrais",
                "Sem necessidade de entrada"
            ],
            "desvantagens": [
                "Imóvel não é seu",
                "Disponibilidade limitada"
            ],
        })

    # Definir recomendação
    if faixa == "Faixa 1":
        recomendacao = "Faixa 1: Procure a Prefeitura para se inscrever no programa habitacional"
    elif faixa in ["Faixa 2"]:
        recomendacao = "Faixa 2: Procure a CAIXA para simular seu financiamento com subsídio"
    elif faixa in ["Faixa 3", "Faixa 4"]:
        recomendacao = f"{faixa}: Você pode escolher entre imóvel novo ou usado na CAIXA"
    else:
        recomendacao = "Busque financiamento pelo Sistema Financeiro de Habitação (SFH)"
        observacoes.append("Renda acima do limite do MCMV")

    return ComparacaoModalidades(
        renda_familiar=renda_familiar,
        faixa=faixa or "Acima do limite MCMV",
        modalidades=modalidades,
        recomendacao=recomendacao,
        observacoes=observacoes,
    )


def calcular_capacidade_pagamento(
    renda_familiar: float,
    percentual_maximo: float = 30.0,
) -> Dict[str, float]:
    """
    Calcula a capacidade de pagamento da família.

    Args:
        renda_familiar: Renda bruta mensal
        percentual_maximo: Percentual máximo de comprometimento

    Returns:
        Dict com parcela máxima e valores estimados
    """
    parcela_maxima = renda_familiar * (percentual_maximo / 100)

    # Estimar valor máximo financiável (35 anos, taxa média 7%)
    taxa_mensal = 7.0 / 100 / 12
    prazo_meses = 35 * 12

    if taxa_mensal > 0:
        fator = (1 + taxa_mensal) ** prazo_meses
        valor_financiavel = parcela_maxima * (fator - 1) / (taxa_mensal * fator)
    else:
        valor_financiavel = parcela_maxima * prazo_meses

    return {
        "renda_familiar": renda_familiar,
        "percentual_comprometimento": percentual_maximo,
        "parcela_maxima": round(parcela_maxima, 2),
        "valor_financiavel_estimado": round(valor_financiavel, 2),
    }


# =============================================================================
# Funções auxiliares internas
# =============================================================================

def _determinar_faixa(renda_familiar: float) -> Optional[str]:
    """Determina a faixa MCMV pela renda."""
    if renda_familiar <= MCMV_FAIXA_1:
        return "Faixa 1"
    elif renda_familiar <= MCMV_FAIXA_2:
        return "Faixa 2"
    elif renda_familiar <= MCMV_FAIXA_3:
        return "Faixa 3"
    elif renda_familiar <= MCMV_FAIXA_4:
        return "Faixa 4"
    return None


def _obter_parametros_faixa(
    faixa: str,
    regiao_metropolitana: bool,
    populacao: int
) -> Tuple[float, float, float]:
    """Retorna (valor_max, subsidio_max, juros_medio) da faixa."""
    if faixa == "Faixa 1":
        teto = MCMV_TETO_RM_GRANDE if (regiao_metropolitana and populacao >= 750000) else MCMV_TETO_DEMAIS
        return (teto, MCMV_SUBSIDIO_FAIXA_1, (MCMV_JUROS_FAIXA_1_MIN + MCMV_JUROS_FAIXA_1_MAX) / 2)

    elif faixa == "Faixa 2":
        teto = MCMV_TETO_RM_GRANDE if (regiao_metropolitana and populacao >= 750000) else MCMV_TETO_DEMAIS
        return (teto, MCMV_SUBSIDIO_FAIXA_2, (MCMV_JUROS_FAIXA_2_MIN + MCMV_JUROS_FAIXA_2_MAX) / 2)

    elif faixa == "Faixa 3":
        return (MCMV_TETO_FAIXA_3, 0, (MCMV_JUROS_FAIXA_3_MIN + MCMV_JUROS_FAIXA_3_MAX) / 2)

    elif faixa == "Faixa 4":
        return (MCMV_TETO_FAIXA_4, 0, MCMV_JUROS_FAIXA_4)

    return (0, 0, 0)


def _calcular_subsidio(
    faixa: str,
    renda_familiar: float,
    valor_imovel: float,
    subsidio_max: float
) -> float:
    """Calcula o subsídio estimado."""
    if faixa == "Faixa 1":
        # Subsídio decrescente com a renda
        fator = 1 - (renda_familiar / MCMV_FAIXA_1) * 0.3
        return round(min(subsidio_max, valor_imovel * 0.95) * fator, 2)

    elif faixa == "Faixa 2":
        fator = 1 - ((renda_familiar - MCMV_FAIXA_1) / (MCMV_FAIXA_2 - MCMV_FAIXA_1))
        return round(subsidio_max * max(0.3, fator), 2)

    return 0


def _calcular_parcela_price(
    valor: float,
    taxa_mensal: float,
    prazo_meses: int
) -> float:
    """Calcula parcela pelo Sistema Price (parcelas fixas)."""
    if valor <= 0:
        return 0

    if taxa_mensal > 0:
        fator = (1 + taxa_mensal) ** prazo_meses
        return valor * (taxa_mensal * fator) / (fator - 1)
    else:
        return valor / prazo_meses


def _calcular_parcelas_sac(
    valor: float,
    taxa_mensal: float,
    prazo_meses: int
) -> Tuple[float, float]:
    """Calcula primeira e última parcela pelo SAC."""
    if valor <= 0:
        return (0, 0)

    amortizacao = valor / prazo_meses

    # Primeira parcela
    juros_inicial = valor * taxa_mensal
    parcela_inicial = amortizacao + juros_inicial

    # Última parcela
    saldo_final = amortizacao
    juros_final = saldo_final * taxa_mensal
    parcela_final = amortizacao + juros_final

    return (parcela_inicial, parcela_final)


def _resultado_inelegivel(renda: float) -> SimulacaoResultado:
    """Retorna resultado para renda acima do limite."""
    return SimulacaoResultado(
        faixa="Inelegível",
        modalidade="N/A",
        valor_imovel=0,
        valor_entrada=0,
        valor_fgts=0,
        subsidio=0,
        valor_financiado=0,
        taxa_juros_anual=0,
        prazo_meses=0,
        sistema=SistemaAmortizacao.PRICE,
        parcela_inicial=0,
        parcela_final=0,
        parcela_media=0,
        custo_total=0,
        juros_total=0,
        comprometimento_renda=0,
        economia_vs_mercado=0,
        viavel=False,
        observacoes=[
            f"Renda de R$ {renda:,.0f} está acima do limite do MCMV (R$ {MCMV_FAIXA_4:,.0f})",
            "Busque financiamento pelo SFH em bancos"
        ],
    )


# =============================================================================
# Funções de formatação para exibição
# =============================================================================

def formatar_simulacao_texto(resultado: SimulacaoResultado) -> str:
    """Formata resultado da simulação em texto simples."""
    if not resultado.viavel or resultado.faixa == "Inelegível":
        return "\n".join(resultado.observacoes)

    linhas = [
        f"Simulação MCMV - {resultado.faixa}",
        "",
        f"Valor do imóvel: R$ {resultado.valor_imovel:,.0f}",
    ]

    if resultado.subsidio > 0:
        linhas.append(f"Subsídio do governo: R$ {resultado.subsidio:,.0f}")

    if resultado.valor_entrada > 0:
        linhas.append(f"Entrada (FGTS + recursos): R$ {resultado.valor_entrada:,.0f}")

    linhas.extend([
        f"Valor financiado: R$ {resultado.valor_financiado:,.0f}",
        "",
        f"Taxa de juros: {resultado.taxa_juros_anual:.1f}% ao ano",
        f"Prazo: {resultado.prazo_meses // 12} anos ({resultado.prazo_meses} meses)",
        "",
        f"Parcela: R$ {resultado.parcela_inicial:,.0f}",
        f"Comprometimento da renda: {resultado.comprometimento_renda:.0f}%",
    ])

    if resultado.economia_vs_mercado > 0:
        linhas.append(f"Economia vs mercado: R$ {resultado.economia_vs_mercado:,.0f}")

    if resultado.observacoes:
        linhas.append("")
        for obs in resultado.observacoes:
            linhas.append(f"* {obs}")

    return "\n".join(linhas)


def formatar_comparacao_texto(comparacao: ComparacaoModalidades) -> str:
    """Formata comparação de modalidades em texto simples."""
    linhas = [
        f"Comparação de Modalidades - {comparacao.faixa}",
        f"Renda familiar: R$ {comparacao.renda_familiar:,.0f}",
        "",
    ]

    for i, mod in enumerate(comparacao.modalidades, 1):
        linhas.append(f"{i}. {mod['tipo']}")
        if mod.get("valor_maximo"):
            linhas.append(f"   Imóvel até R$ {mod['valor_maximo']:,.0f}")
        if mod.get("subsidio", 0) > 0:
            linhas.append(f"   Subsídio: R$ {mod['subsidio']:,.0f}")
        if mod.get("parcela_estimada", 0) > 0:
            linhas.append(f"   Parcela: ~R$ {mod['parcela_estimada']:,.0f}")
        linhas.append("")

    linhas.append(f"Recomendação: {comparacao.recomendacao}")

    return "\n".join(linhas)
