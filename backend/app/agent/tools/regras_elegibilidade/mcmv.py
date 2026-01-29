"""
Regras de elegibilidade para o Minha Casa Minha Vida (MCMV) - 2026.

Faixas de renda (2026):
- Faixa 1: até R$ 2.850/mês (maior subsídio, até R$ 65 mil)
- Faixa 2: R$ 2.850 a R$ 4.700/mês (subsídio até R$ 55 mil)
- Faixa 3: R$ 4.700 a R$ 8.600/mês (sem subsídio, juros reduzidos)
- Faixa 4: R$ 8.600 a R$ 12.000/mês (imóvel até R$ 500 mil)

Programa Reforma Casa Brasil:
- Faixa 1: renda até R$ 3.200 → juros 1,17% a.m.
- Faixa 2: renda R$ 3.200-9.600 → juros 1,95% a.m.
- Crédito de R$ 5.000 a R$ 30.000

Novidades 2026:
- Imóvel usado permitido (Faixas 3 e 4)
- Beneficiários BPC/Bolsa Família: imóvel 100% gratuito na Faixa 1
- Locação Social (PPP Morar no Centro)
- MCMV Entidades (autogestão)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from . import (
    CitizenProfile,
    EligibilityResult,
    EligibilityStatus,
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


class ModalidadeHabitacao(Enum):
    """Modalidades do programa habitacional."""
    AQUISICAO_NOVO = "aquisicao_novo"
    AQUISICAO_USADO = "aquisicao_usado"
    REFORMA = "reforma"
    LOCACAO_SOCIAL = "locacao_social"
    ENTIDADES = "entidades"


@dataclass
class CriterioElegibilidade:
    """Resultado da verificação de um critério específico."""
    criterio: str
    atendido: bool
    motivo: str
    bloqueante: bool = True


@dataclass
class MCMVResult:
    """Resultado detalhado da verificação MCMV."""
    elegivel: bool
    faixa: Optional[str]
    modalidades_disponiveis: List[ModalidadeHabitacao]
    criterios: List[CriterioElegibilidade]
    valor_maximo_imovel: Optional[float]
    subsidio_estimado: Optional[float]
    taxa_juros: Optional[Tuple[float, float]]
    parcela_estimada: Optional[float]
    grupo_prioritario: Optional[str]
    encaminhamento: str
    alternativas: List[Dict[str, Any]]
    observacoes: str


def verificar_elegibilidade(perfil: CitizenProfile) -> EligibilityResult:
    """
    Verifica elegibilidade para o Minha Casa Minha Vida.

    Critérios verificados:
    1. Renda familiar dentro da faixa
    2. Não ser proprietário de imóvel
    3. Não ter recebido benefício habitacional federal
    4. Não ter financiamento ativo
    5. Idade + prazo <= 80 anos e 6 meses
    6. Residir no município do imóvel (informativo)
    7. Sem restrições de crédito (Faixas 2-4)

    Args:
        perfil: Dados do cidadão

    Returns:
        EligibilityResult com status e detalhes
    """
    resultado = _verificar_elegibilidade_completa(perfil)

    # Converter para EligibilityResult padrão
    if resultado.elegivel:
        return _criar_resultado_elegivel(resultado, perfil)
    else:
        # Verificar se pode ter direito a reforma
        if perfil.tem_casa_propria:
            return _verificar_elegibilidade_reformas(perfil)
        return _criar_resultado_inelegivel(resultado, perfil)


def _verificar_elegibilidade_completa(perfil: CitizenProfile) -> MCMVResult:
    """Verifica todos os critérios de elegibilidade."""
    criterios = []
    modalidades = []
    alternativas = []
    grupo_prioritario = None

    renda_familiar = perfil.renda_familiar_mensal

    # 1. Verificar faixa de renda
    faixa, info_faixa = _determinar_faixa_detalhada(renda_familiar)
    if faixa is None:
        criterios.append(CriterioElegibilidade(
            criterio="renda_familiar",
            atendido=False,
            motivo=f"Renda de R$ {renda_familiar:.2f} está acima do limite de R$ {MCMV_FAIXA_4:.2f}",
            bloqueante=True
        ))
    else:
        criterios.append(CriterioElegibilidade(
            criterio="renda_familiar",
            atendido=True,
            motivo=f"Renda de R$ {renda_familiar:.2f} se enquadra na {faixa}",
            bloqueante=True
        ))

    # 2. Verificar propriedade de imóvel
    if perfil.tem_imovel_registrado is True or perfil.tem_casa_propria:
        criterios.append(CriterioElegibilidade(
            criterio="propriedade_imovel",
            atendido=False,
            motivo="Já possui imóvel registrado em seu nome",
            bloqueante=True
        ))
        # Adicionar reforma como alternativa
        alternativas.append({
            "programa": "MCMV_REFORMAS",
            "nome": "Reforma Casa Brasil",
            "descricao": "Crédito para reformar seu imóvel"
        })
    elif perfil.tem_imovel_registrado is None:
        criterios.append(CriterioElegibilidade(
            criterio="propriedade_imovel",
            atendido=True,
            motivo="Declarou não possuir imóvel (será verificado no SIACI/CADMUT)",
            bloqueante=True
        ))
    else:
        criterios.append(CriterioElegibilidade(
            criterio="propriedade_imovel",
            atendido=True,
            motivo="Não possui imóvel registrado",
            bloqueante=True
        ))

    # 3. Verificar benefício habitacional anterior
    if perfil.teve_beneficio_habitacional_federal is True:
        criterios.append(CriterioElegibilidade(
            criterio="beneficio_anterior",
            atendido=False,
            motivo="Já recebeu benefício habitacional federal anteriormente",
            bloqueante=True
        ))
    elif perfil.teve_beneficio_habitacional_federal is None:
        criterios.append(CriterioElegibilidade(
            criterio="beneficio_anterior",
            atendido=True,
            motivo="Declarou não ter recebido benefício habitacional federal",
            bloqueante=True
        ))
    else:
        criterios.append(CriterioElegibilidade(
            criterio="beneficio_anterior",
            atendido=True,
            motivo="Não recebeu benefício habitacional federal",
            bloqueante=True
        ))

    # 4. Verificar financiamento ativo
    if perfil.tem_financiamento_ativo is True:
        criterios.append(CriterioElegibilidade(
            criterio="financiamento_ativo",
            atendido=False,
            motivo="Possui financiamento habitacional ativo",
            bloqueante=True
        ))
    elif perfil.tem_financiamento_ativo is None:
        criterios.append(CriterioElegibilidade(
            criterio="financiamento_ativo",
            atendido=True,
            motivo="Declarou não ter financiamento ativo (será verificado)",
            bloqueante=True
        ))
    else:
        criterios.append(CriterioElegibilidade(
            criterio="financiamento_ativo",
            atendido=True,
            motivo="Não possui financiamento habitacional ativo",
            bloqueante=True
        ))

    # 5. Verificar idade + prazo
    idade = perfil.idade
    if idade is not None:
        prazo_maximo = 35
        idade_final = idade + prazo_maximo
        limite_idade = 80.5  # 80 anos e 6 meses

        if idade_final > limite_idade:
            prazo_possivel = int(limite_idade - idade)
            if prazo_possivel < 5:
                criterios.append(CriterioElegibilidade(
                    criterio="idade_prazo",
                    atendido=False,
                    motivo=f"Com {idade} anos, o prazo mínimo de 5 anos excederia o limite de idade",
                    bloqueante=True
                ))
            else:
                criterios.append(CriterioElegibilidade(
                    criterio="idade_prazo",
                    atendido=True,
                    motivo=f"Com {idade} anos, prazo máximo seria de {prazo_possivel} anos",
                    bloqueante=False
                ))
        else:
            criterios.append(CriterioElegibilidade(
                criterio="idade_prazo",
                atendido=True,
                motivo=f"Idade de {idade} anos permite prazo de até 35 anos",
                bloqueante=True
            ))
    else:
        criterios.append(CriterioElegibilidade(
            criterio="idade_prazo",
            atendido=True,
            motivo="Idade não informada - será verificada na análise",
            bloqueante=False
        ))

    # 6. Verificar restrição de crédito (apenas Faixas 2-4)
    if faixa and faixa != "Faixa 1":
        if perfil.tem_restricao_credito is True:
            criterios.append(CriterioElegibilidade(
                criterio="restricao_credito",
                atendido=False,
                motivo="Possui restrição de crédito (SPC/Serasa)",
                bloqueante=True
            ))
        elif perfil.tem_restricao_credito is None:
            criterios.append(CriterioElegibilidade(
                criterio="restricao_credito",
                atendido=True,
                motivo="Situação de crédito será verificada na análise",
                bloqueante=False
            ))
        else:
            criterios.append(CriterioElegibilidade(
                criterio="restricao_credito",
                atendido=True,
                motivo="Sem restrição de crédito",
                bloqueante=True
            ))

    # Verificar grupos prioritários
    grupo_prioritario = _identificar_grupo_prioritario(perfil)

    # Determinar modalidades disponíveis
    if faixa:
        modalidades.append(ModalidadeHabitacao.AQUISICAO_NOVO)

        if faixa in ["Faixa 3", "Faixa 4"]:
            modalidades.append(ModalidadeHabitacao.AQUISICAO_USADO)

        if faixa == "Faixa 1":
            modalidades.append(ModalidadeHabitacao.ENTIDADES)
            modalidades.append(ModalidadeHabitacao.LOCACAO_SOCIAL)

    # Calcular valores
    valor_max, subsidio, juros = _calcular_valores(faixa, perfil)
    parcela = _estimar_parcela(valor_max, subsidio, juros, perfil) if valor_max else None

    # Determinar encaminhamento
    encaminhamento = _determinar_encaminhamento(faixa, perfil)

    # Verificar elegibilidade geral
    criterios_bloqueantes = [c for c in criterios if c.bloqueante and not c.atendido]
    elegivel = len(criterios_bloqueantes) == 0 and faixa is not None

    # Construir observações
    observacoes = _construir_observacoes(faixa, perfil, grupo_prioritario)

    return MCMVResult(
        elegivel=elegivel,
        faixa=faixa,
        modalidades_disponiveis=modalidades,
        criterios=criterios,
        valor_maximo_imovel=valor_max,
        subsidio_estimado=subsidio,
        taxa_juros=juros,
        parcela_estimada=parcela,
        grupo_prioritario=grupo_prioritario,
        encaminhamento=encaminhamento,
        alternativas=alternativas,
        observacoes=observacoes
    )


def _determinar_faixa_detalhada(renda_familiar: float) -> Tuple[Optional[str], Optional[Dict]]:
    """Determina a faixa do MCMV com informações detalhadas."""
    if renda_familiar <= MCMV_FAIXA_1:
        return ("Faixa 1", {
            "limite": MCMV_FAIXA_1,
            "subsidio_max": MCMV_SUBSIDIO_FAIXA_1,
            "juros_min": MCMV_JUROS_FAIXA_1_MIN,
            "juros_max": MCMV_JUROS_FAIXA_1_MAX,
            "permite_usado": False,
        })
    elif renda_familiar <= MCMV_FAIXA_2:
        return ("Faixa 2", {
            "limite": MCMV_FAIXA_2,
            "subsidio_max": MCMV_SUBSIDIO_FAIXA_2,
            "juros_min": MCMV_JUROS_FAIXA_2_MIN,
            "juros_max": MCMV_JUROS_FAIXA_2_MAX,
            "permite_usado": False,
        })
    elif renda_familiar <= MCMV_FAIXA_3:
        return ("Faixa 3", {
            "limite": MCMV_FAIXA_3,
            "subsidio_max": 0,
            "juros_min": MCMV_JUROS_FAIXA_3_MIN,
            "juros_max": MCMV_JUROS_FAIXA_3_MAX,
            "permite_usado": True,
        })
    elif renda_familiar <= MCMV_FAIXA_4:
        return ("Faixa 4", {
            "limite": MCMV_FAIXA_4,
            "subsidio_max": 0,
            "juros_min": MCMV_JUROS_FAIXA_4,
            "juros_max": MCMV_JUROS_FAIXA_4,
            "permite_usado": True,
        })
    else:
        return (None, None)


def _identificar_grupo_prioritario(perfil: CitizenProfile) -> Optional[str]:
    """Identifica se o cidadão pertence a algum grupo prioritário."""
    # Ordem de prioridade conforme legislação
    if perfil.situacao_rua:
        return "Pessoa em situação de rua - Atendimento prioritário"

    if perfil.vitima_violencia_domestica:
        return "Vítima de violência doméstica - Atendimento prioritário"

    if perfil.em_area_risco:
        return "Família em área de risco - Atendimento prioritário"

    # Benefício 100% gratuito na Faixa 1
    if perfil.recebe_bpc or perfil.recebe_bolsa_familia:
        renda = perfil.renda_familiar_mensal
        if renda <= MCMV_FAIXA_1:
            return "Beneficiário BPC/Bolsa Família - Pode ter imóvel 100% gratuito"

    if perfil.tem_pcd:
        return "Família com pessoa com deficiência - Prioridade"

    if perfil.tem_idoso_65_mais:
        return "Família com idoso 65+ - Prioridade"

    if perfil.tem_filhos_menores:
        return "Família com crianças - Prioridade"

    return None


def _calcular_valores(
    faixa: Optional[str],
    perfil: CitizenProfile
) -> Tuple[Optional[float], Optional[float], Optional[Tuple[float, float]]]:
    """Calcula valores máximos, subsídio e juros para a faixa."""
    if faixa is None:
        return (None, None, None)

    # Determinar teto do imóvel
    if faixa == "Faixa 4":
        valor_max = MCMV_TETO_FAIXA_4
        subsidio = 0.0
        juros = (MCMV_JUROS_FAIXA_4, MCMV_JUROS_FAIXA_4)
    elif faixa == "Faixa 3":
        valor_max = MCMV_TETO_FAIXA_3
        subsidio = 0.0
        juros = (MCMV_JUROS_FAIXA_3_MIN, MCMV_JUROS_FAIXA_3_MAX)
    else:
        # Faixas 1 e 2 - teto depende da região
        if perfil.regiao_metropolitana and (perfil.populacao_municipio or 0) >= 750000:
            valor_max = MCMV_TETO_RM_GRANDE
        else:
            valor_max = MCMV_TETO_DEMAIS

        if faixa == "Faixa 1":
            subsidio = MCMV_SUBSIDIO_FAIXA_1
            juros = (MCMV_JUROS_FAIXA_1_MIN, MCMV_JUROS_FAIXA_1_MAX)
        else:  # Faixa 2
            subsidio = MCMV_SUBSIDIO_FAIXA_2
            juros = (MCMV_JUROS_FAIXA_2_MIN, MCMV_JUROS_FAIXA_2_MAX)

    return (valor_max, subsidio, juros)


def _estimar_parcela(
    valor_imovel: float,
    subsidio: float,
    juros: Tuple[float, float],
    perfil: CitizenProfile,
    prazo_anos: int = 35
) -> Optional[float]:
    """Estima a parcela mensal do financiamento (Sistema Price)."""
    # Valor a financiar
    entrada = perfil.valor_fgts_disponivel or 0
    valor_financiado = valor_imovel - subsidio - entrada

    if valor_financiado <= 0:
        return 0.0

    # Usar taxa média
    taxa_anual = (juros[0] + juros[1]) / 2
    taxa_mensal = taxa_anual / 100 / 12

    # Ajustar prazo pela idade
    idade = perfil.idade
    if idade is not None:
        prazo_max = min(prazo_anos, int(80.5 - idade))
        prazo_anos = max(5, prazo_max)

    n_meses = prazo_anos * 12

    # Fórmula Price: PMT = PV * [i(1+i)^n] / [(1+i)^n - 1]
    if taxa_mensal > 0:
        fator = (1 + taxa_mensal) ** n_meses
        parcela = valor_financiado * (taxa_mensal * fator) / (fator - 1)
    else:
        parcela = valor_financiado / n_meses

    return round(parcela, 2)


def _determinar_encaminhamento(faixa: Optional[str], perfil: CitizenProfile) -> str:
    """Determina o local correto de encaminhamento."""
    if faixa is None:
        return "Sistema Financeiro de Habitação (SFH) - Bancos"

    if faixa == "Faixa 1":
        if not perfil.cadastrado_cadunico:
            return "CRAS - Fazer CadÚnico primeiro, depois Prefeitura (Secretaria de Habitação)"
        return "Prefeitura - Secretaria de Habitação"

    # Faixas 2, 3 e 4
    return "CAIXA Econômica Federal ou correspondentes bancários"


def _construir_observacoes(
    faixa: Optional[str],
    perfil: CitizenProfile,
    grupo_prioritario: Optional[str]
) -> str:
    """Constrói texto de observações detalhado."""
    obs = []

    if grupo_prioritario:
        obs.append(f"PRIORIDADE: {grupo_prioritario}")

    if faixa == "Faixa 1":
        obs.append("Faixa 1 tem o maior subsídio do governo - pode chegar a 95% do valor")

        if perfil.recebe_bpc or perfil.recebe_bolsa_familia:
            obs.append("Como beneficiário BPC/Bolsa Família, pode ter imóvel 100% gratuito!")

    if faixa in ["Faixa 3", "Faixa 4"]:
        obs.append("Nesta faixa, você pode comprar imóvel novo ou usado")

    if perfil.tem_fgts and perfil.tempo_contribuicao_fgts_meses:
        if perfil.tempo_contribuicao_fgts_meses >= 36:
            obs.append("Com 3+ anos de FGTS, você pode usá-lo como entrada")

    return "\n".join(obs) if obs else ""


def _criar_resultado_elegivel(resultado: MCMVResult, perfil: CitizenProfile) -> EligibilityResult:
    """Cria EligibilityResult para resultado positivo."""

    # Montar próximos passos
    proximos_passos = []

    if resultado.faixa == "Faixa 1":
        if not perfil.cadastrado_cadunico:
            proximos_passos.append("Faça ou atualize seu CadÚnico no CRAS")
        proximos_passos.append("Procure a Prefeitura (Secretaria de Habitação)")
        proximos_passos.append("Inscreva-se no programa habitacional do município")
    else:
        proximos_passos.append("Procure a CAIXA ou correspondente bancário")
        proximos_passos.append("Faça a simulação de financiamento")

    proximos_passos.append("Separe os documentos necessários")
    proximos_passos.append("Escolha um imóvel dentro do programa")

    # Documentos necessários
    docs = [
        "CPF e RG (todos da família)",
        "Comprovante de residência atualizado",
        "Comprovante de renda (3 últimos meses)",
        "Certidão de casamento ou nascimento",
    ]

    if resultado.faixa == "Faixa 1":
        docs.insert(0, "CadÚnico atualizado (NIS)")
    else:
        docs.extend([
            "Carteira de trabalho",
            "Declaração de Imposto de Renda (se tiver)",
            "Extrato de FGTS",
        ])

    # Construir motivo
    beneficios = _descrever_beneficios(resultado)

    return EligibilityResult(
        programa="MCMV",
        programa_nome=f"Minha Casa Minha Vida - {resultado.faixa}",
        status=EligibilityStatus.ELEGIVEL,
        motivo=f"Você pode ter direito ao MCMV {resultado.faixa}! {beneficios}",
        valor_estimado=resultado.subsidio_estimado,
        proximos_passos=proximos_passos,
        documentos_necessarios=docs,
        onde_solicitar=resultado.encaminhamento,
        observacoes=resultado.observacoes,
    )


def _criar_resultado_inelegivel(resultado: MCMVResult, perfil: CitizenProfile) -> EligibilityResult:
    """Cria EligibilityResult para resultado negativo."""

    # Identificar motivos de inelegibilidade
    motivos = []
    for criterio in resultado.criterios:
        if not criterio.atendido and criterio.bloqueante:
            motivos.append(criterio.motivo)

    motivo_principal = motivos[0] if motivos else "Não atende aos requisitos do programa"

    # Sugerir alternativas
    alternativas_texto = []
    for alt in resultado.alternativas:
        alternativas_texto.append(f"- {alt['nome']}: {alt['descricao']}")

    obs = ""
    if alternativas_texto:
        obs = "Alternativas disponíveis:\n" + "\n".join(alternativas_texto)

    if perfil.renda_familiar_mensal > MCMV_FAIXA_4:
        obs += "\nVocê pode buscar financiamento pelo Sistema Financeiro de Habitação (SFH)."

    return EligibilityResult(
        programa="MCMV",
        programa_nome="Minha Casa Minha Vida",
        status=EligibilityStatus.INELEGIVEL,
        motivo=motivo_principal,
        observacoes=obs if obs else None,
    )


def _descrever_beneficios(resultado: MCMVResult) -> str:
    """Descreve os benefícios da faixa de forma simples."""
    partes = []

    if resultado.subsidio_estimado and resultado.subsidio_estimado > 0:
        partes.append(f"Subsídio de até R$ {resultado.subsidio_estimado:,.0f}")

    if resultado.taxa_juros:
        if resultado.taxa_juros[0] == resultado.taxa_juros[1]:
            partes.append(f"juros de {resultado.taxa_juros[0]:.1f}% ao ano")
        else:
            partes.append(f"juros de {resultado.taxa_juros[0]:.1f}% a {resultado.taxa_juros[1]:.1f}% ao ano")

    if resultado.valor_maximo_imovel:
        partes.append(f"imóvel de até R$ {resultado.valor_maximo_imovel:,.0f}")

    if resultado.parcela_estimada:
        partes.append(f"parcela estimada de R$ {resultado.parcela_estimada:,.0f}")

    return " | ".join(partes) if partes else ""


def _verificar_elegibilidade_reformas(perfil: CitizenProfile) -> EligibilityResult:
    """Verifica elegibilidade para o Programa Reforma Casa Brasil."""
    renda_familiar = perfil.renda_familiar_mensal

    if renda_familiar <= REFORMA_LIMITE_FAIXA_1:
        faixa = "Faixa 1"
        juros = REFORMA_JUROS_FAIXA_1
        limite_renda = REFORMA_LIMITE_FAIXA_1
    elif renda_familiar <= REFORMA_LIMITE_FAIXA_2:
        faixa = "Faixa 2"
        juros = REFORMA_JUROS_FAIXA_2
        limite_renda = REFORMA_LIMITE_FAIXA_2
    else:
        return EligibilityResult(
            programa="MCMV_REFORMAS",
            programa_nome="Reforma Casa Brasil",
            status=EligibilityStatus.INELEGIVEL,
            motivo=f"Sua renda de R$ {renda_familiar:.2f} está acima do limite de R$ {REFORMA_LIMITE_FAIXA_2:.2f}.",
            observacoes="Você pode buscar linhas de crédito para reforma em bancos comerciais.",
        )

    return EligibilityResult(
        programa="MCMV_REFORMAS",
        programa_nome=f"Reforma Casa Brasil - {faixa}",
        status=EligibilityStatus.ELEGIVEL,
        motivo=f"Você pode ter direito a crédito de R$ {REFORMA_CREDITO_MIN:,.0f} a R$ {REFORMA_CREDITO_MAX:,.0f} para reformar sua casa!",
        proximos_passos=[
            "Procure a CAIXA ou correspondente bancário",
            "Apresente documentos do imóvel (escritura ou contrato)",
            "Solicite orçamento das reformas desejadas",
            "Aguarde análise de crédito",
        ],
        documentos_necessarios=[
            "CPF e RG",
            "Comprovante de residência",
            "Comprovante de renda (3 últimos meses)",
            "Documento do imóvel (escritura, matrícula ou contrato)",
            "Orçamento detalhado das reformas",
        ],
        onde_solicitar="CAIXA Econômica Federal",
        observacoes=f"""Programa Reforma Casa Brasil - {faixa}:
- Renda até R$ {limite_renda:.0f}
- Juros de {juros:.2f}% ao mês
- Crédito de R$ {REFORMA_CREDITO_MIN:,.0f} a R$ {REFORMA_CREDITO_MAX:,.0f}
- Prazo de 24 a 60 meses
- Liberação: 90% inicial + 10% após comprovação""",
    )


# =============================================================================
# Funções auxiliares para uso externo (simulador, carta, etc.)
# =============================================================================

def obter_info_faixa(renda_familiar: float) -> Optional[Dict[str, Any]]:
    """
    Retorna informações detalhadas da faixa para a renda informada.

    Útil para o simulador e carta de encaminhamento.
    """
    faixa, info = _determinar_faixa_detalhada(renda_familiar)
    if faixa is None:
        return None

    return {
        "faixa": faixa,
        "limite_renda": info["limite"],
        "subsidio_maximo": info["subsidio_max"],
        "juros_minimo": info["juros_min"],
        "juros_maximo": info["juros_max"],
        "permite_usado": info["permite_usado"],
    }


def calcular_subsidio_estimado(
    renda_familiar: float,
    valor_imovel: float,
    regiao_metropolitana: bool = False
) -> float:
    """
    Calcula o subsídio estimado para o financiamento.

    O subsídio real depende de fatores como composição familiar,
    região e disponibilidade de recursos.
    """
    faixa, _ = _determinar_faixa_detalhada(renda_familiar)

    if faixa == "Faixa 1":
        # Subsídio pode chegar a 95% do valor
        subsidio_max = min(MCMV_SUBSIDIO_FAIXA_1, valor_imovel * 0.95)
        # Fator de redução baseado na renda
        fator = 1 - (renda_familiar / MCMV_FAIXA_1) * 0.3
        return round(subsidio_max * fator, 2)

    elif faixa == "Faixa 2":
        # Subsídio decrescente com a renda
        fator = 1 - ((renda_familiar - MCMV_FAIXA_1) / (MCMV_FAIXA_2 - MCMV_FAIXA_1))
        return round(MCMV_SUBSIDIO_FAIXA_2 * max(0.3, fator), 2)

    return 0.0


def listar_modalidades_disponiveis(faixa: str) -> List[Dict[str, str]]:
    """Lista as modalidades disponíveis para uma faixa."""
    modalidades = [
        {
            "codigo": "AQUISICAO_NOVO",
            "nome": "Aquisição de imóvel novo",
            "descricao": "Compra de imóvel novo em empreendimentos do programa"
        }
    ]

    if faixa in ["Faixa 3", "Faixa 4"]:
        modalidades.append({
            "codigo": "AQUISICAO_USADO",
            "nome": "Aquisição de imóvel usado",
            "descricao": "Compra de imóvel usado com financiamento MCMV"
        })

    if faixa == "Faixa 1":
        modalidades.extend([
            {
                "codigo": "ENTIDADES",
                "nome": "MCMV Entidades",
                "descricao": "Construção por autogestão via cooperativas e associações"
            },
            {
                "codigo": "LOCACAO_SOCIAL",
                "nome": "Locação Social",
                "descricao": "Aluguel subsidiado em regiões centrais (PPP)"
            }
        ])

    return modalidades
