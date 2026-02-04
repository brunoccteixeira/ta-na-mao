"""
Servico de analise preditiva de vulnerabilidade.

Calcula score de vulnerabilidade em 6 dimensoes e gera
recomendacoes proativas de beneficios nao acessados.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# Enums e tipos
# =============================================================================

class FaixaRisco(str, Enum):
    BAIXO = "BAIXO"          # 0-25
    MODERADO = "MODERADO"    # 26-50
    ALTO = "ALTO"            # 51-75
    CRITICO = "CRITICO"      # 76-100


class TipoMoradia(str, Enum):
    PROPRIA = "propria"
    ALUGADA = "alugada"
    CEDIDA = "cedida"
    OCUPACAO = "ocupacao"
    RUA = "rua"


class Zona(str, Enum):
    URBANA = "urbana"
    RURAL = "rural"


@dataclass
class PerfilFamiliar:
    """Perfil familiar para calculo de vulnerabilidade."""
    renda_per_capita: float = 0
    membros_familia: int = 1
    criancas_0_6: int = 0
    gestantes: int = 0
    idosos_60_mais: int = 0
    pessoas_com_deficiencia: int = 0
    tipo_moradia: str = "propria"
    trabalho_formal: bool = False
    desempregados: int = 0
    beneficios_ativos: List[str] = field(default_factory=list)
    cadunico_atualizado: bool = True
    meses_desde_atualizacao: int = 0
    zona: str = "urbana"


# =============================================================================
# Pesos das dimensoes
# =============================================================================

PESOS = {
    "renda": 0.30,           # 30% - Renda
    "composicao": 0.20,      # 20% - Composicao familiar
    "moradia": 0.15,         # 15% - Moradia
    "trabalho": 0.15,        # 15% - Trabalho
    "protecao_social": 0.10, # 10% - Protecao social
    "territorio": 0.10,      # 10% - Territorio
}


# =============================================================================
# Calculo do score
# =============================================================================

def calcular_score(perfil: PerfilFamiliar) -> Dict[str, Any]:
    """Calcula score de vulnerabilidade social (0-100).

    Quanto MAIOR o score, MAIOR a vulnerabilidade.

    Args:
        perfil: Dados do perfil familiar

    Returns:
        dict com score, faixa, fatores e dimensoes detalhadas
    """
    logger.info(f"Calculando score de vulnerabilidade: membros={perfil.membros_familia}")

    dimensoes = {}
    fatores = []

    # 1. RENDA (0-100 normalizado, peso 30%)
    score_renda, fator_renda = _calcular_renda(perfil.renda_per_capita)
    dimensoes["renda"] = {"score": score_renda, "peso": PESOS["renda"]}
    if fator_renda:
        fatores.append(fator_renda)

    # 2. COMPOSICAO FAMILIAR (0-100 normalizado, peso 20%)
    score_comp, fatores_comp = _calcular_composicao(perfil)
    dimensoes["composicao"] = {"score": score_comp, "peso": PESOS["composicao"]}
    fatores.extend(fatores_comp)

    # 3. MORADIA (0-100 normalizado, peso 15%)
    score_moradia, fator_moradia = _calcular_moradia(perfil.tipo_moradia)
    dimensoes["moradia"] = {"score": score_moradia, "peso": PESOS["moradia"]}
    if fator_moradia:
        fatores.append(fator_moradia)

    # 4. TRABALHO (0-100 normalizado, peso 15%)
    score_trabalho, fator_trabalho = _calcular_trabalho(perfil)
    dimensoes["trabalho"] = {"score": score_trabalho, "peso": PESOS["trabalho"]}
    if fator_trabalho:
        fatores.append(fator_trabalho)

    # 5. PROTECAO SOCIAL (0-100 normalizado, peso 10%)
    score_protecao, fator_protecao = _calcular_protecao(perfil)
    dimensoes["protecao_social"] = {"score": score_protecao, "peso": PESOS["protecao_social"]}
    if fator_protecao:
        fatores.append(fator_protecao)

    # 6. TERRITORIO (0-100 normalizado, peso 10%)
    score_territorio, fator_territorio = _calcular_territorio(perfil.zona)
    dimensoes["territorio"] = {"score": score_territorio, "peso": PESOS["territorio"]}
    if fator_territorio:
        fatores.append(fator_territorio)

    # Score final ponderado
    score_final = sum(
        d["score"] * d["peso"] for d in dimensoes.values()
    )
    score_final = min(100, max(0, round(score_final)))

    # Faixa de risco
    faixa = _determinar_faixa(score_final)

    return {
        "score": score_final,
        "faixa": faixa.value,
        "faixa_descricao": _descrever_faixa(faixa),
        "dimensoes": dimensoes,
        "fatores_principais": fatores[:5],  # Top 5
        "recomendacao_geral": _recomendacao_geral(faixa),
    }


def _calcular_renda(renda_per_capita: float) -> tuple:
    """Calcula score de renda (0-100)."""
    if renda_per_capita <= 0:
        return 100, "Sem renda declarada"
    if renda_per_capita <= 105:
        return 85, "Renda em faixa de extrema pobreza"
    if renda_per_capita <= 218:
        return 65, "Renda em faixa de pobreza"
    if renda_per_capita <= 660:
        return 35, "Renda baixa (ate meio salario minimo)"
    return 10, None


def _calcular_composicao(perfil: PerfilFamiliar) -> tuple:
    """Calcula score de composicao familiar (0-100)."""
    score = 0
    fatores = []

    # Criancas pequenas aumentam vulnerabilidade
    if perfil.criancas_0_6 > 0:
        score += min(40, perfil.criancas_0_6 * 15)
        fatores.append(f"{perfil.criancas_0_6} crianca(s) de 0-6 anos")

    # Gestantes
    if perfil.gestantes > 0:
        score += 20
        fatores.append("Gestante na familia")

    # Idosos
    if perfil.idosos_60_mais > 0:
        score += min(30, perfil.idosos_60_mais * 15)
        fatores.append(f"{perfil.idosos_60_mais} idoso(s) na familia")

    # PCD
    if perfil.pessoas_com_deficiencia > 0:
        score += min(30, perfil.pessoas_com_deficiencia * 20)
        fatores.append(f"{perfil.pessoas_com_deficiencia} pessoa(s) com deficiencia")

    # Familia grande
    if perfil.membros_familia > 5:
        score += 15
        fatores.append(f"Familia grande ({perfil.membros_familia} pessoas)")

    return min(100, score), fatores


def _calcular_moradia(tipo: str) -> tuple:
    """Calcula score de moradia (0-100)."""
    scores = {
        "rua": (100, "Situacao de rua"),
        "ocupacao": (80, "Moradia em area de ocupacao"),
        "cedida": (50, "Moradia cedida/emprestada"),
        "alugada": (30, "Moradia alugada"),
        "propria": (5, None),
    }
    return scores.get(tipo.lower(), (30, None))


def _calcular_trabalho(perfil: PerfilFamiliar) -> tuple:
    """Calcula score de trabalho (0-100)."""
    if perfil.desempregados > 0 and not perfil.trabalho_formal:
        return 90, f"{perfil.desempregados} desempregado(s) sem trabalho formal"
    if not perfil.trabalho_formal:
        return 60, "Nenhum membro com trabalho formal"
    if perfil.desempregados > 0:
        return 40, f"{perfil.desempregados} desempregado(s) mas ha trabalho formal"
    return 10, None


def _calcular_protecao(perfil: PerfilFamiliar) -> tuple:
    """Calcula score de protecao social (0-100)."""
    score = 50  # Base
    fator = None

    # Beneficios ativos reduzem vulnerabilidade
    if perfil.beneficios_ativos:
        score -= len(perfil.beneficios_ativos) * 15
    else:
        score += 20
        fator = "Sem beneficios sociais ativos"

    # CadUnico desatualizado aumenta risco
    if not perfil.cadunico_atualizado:
        score += 30
        fator = "CadUnico desatualizado - risco de perder beneficios"
    elif perfil.meses_desde_atualizacao > 18:
        score += 15
        fator = "CadUnico proximo de vencer (atualizar em breve)"

    return min(100, max(0, score)), fator


def _calcular_territorio(zona: str) -> tuple:
    """Calcula score de territorio (0-100)."""
    if zona.lower() == "rural":
        return 40, "Zona rural (acesso limitado a servicos)"
    return 15, None


def _determinar_faixa(score: int) -> FaixaRisco:
    """Determina faixa de risco pelo score."""
    if score <= 25:
        return FaixaRisco.BAIXO
    if score <= 50:
        return FaixaRisco.MODERADO
    if score <= 75:
        return FaixaRisco.ALTO
    return FaixaRisco.CRITICO


def _descrever_faixa(faixa: FaixaRisco) -> str:
    """Descricao simples da faixa."""
    descricoes = {
        FaixaRisco.BAIXO: "Situacao estavel. Manter acompanhamento.",
        FaixaRisco.MODERADO: "Atencao moderada. Verificar se ha beneficios nao acessados.",
        FaixaRisco.ALTO: "Vulnerabilidade alta. Acao preventiva recomendada.",
        FaixaRisco.CRITICO: "Situacao critica. Encaminhamento urgente ao CRAS/CREAS.",
    }
    return descricoes.get(faixa, "")


def _recomendacao_geral(faixa: FaixaRisco) -> str:
    """Recomendacao geral baseada na faixa."""
    recomendacoes = {
        FaixaRisco.BAIXO: "Continue mantendo seu CadUnico atualizado.",
        FaixaRisco.MODERADO: (
            "Verifique se voce esta recebendo todos os beneficios que tem direito. "
            "Mantenha o CadUnico em dia."
        ),
        FaixaRisco.ALTO: (
            "Recomendamos procurar o CRAS para uma avaliacao completa. "
            "Voce pode ter direito a beneficios que ainda nao acessa."
        ),
        FaixaRisco.CRITICO: (
            "Situacao urgente! Procure o CRAS ou CREAS mais proximo. "
            "Se estiver em perigo, ligue 100 ou 190."
        ),
    }
    return recomendacoes.get(faixa, "")


# =============================================================================
# Recomendacoes proativas
# =============================================================================

def gerar_recomendacoes(
    perfil: PerfilFamiliar,
    score: int,
) -> List[Dict[str, Any]]:
    """Gera recomendacoes proativas de beneficios nao acessados.

    Args:
        perfil: Perfil familiar
        score: Score de vulnerabilidade calculado

    Returns:
        Lista de recomendacoes ordenadas por prioridade
    """
    recomendacoes = []
    beneficios_ativos = set(b.upper() for b in perfil.beneficios_ativos)

    # Bolsa Familia
    if "BOLSA_FAMILIA" not in beneficios_ativos and perfil.renda_per_capita <= 218:
        recomendacoes.append({
            "tipo": "beneficio_nao_acessado",
            "beneficio": "BOLSA_FAMILIA",
            "mensagem": "Sua renda indica que voce pode ter direito ao Bolsa Familia.",
            "prioridade": "alta",
            "proximo_passo": "Procure o CRAS para se cadastrar ou atualizar o CadUnico.",
        })

    # BPC
    if "BPC" not in beneficios_ativos:
        if perfil.idosos_60_mais > 0 and perfil.renda_per_capita <= 379.50:
            recomendacoes.append({
                "tipo": "beneficio_nao_acessado",
                "beneficio": "BPC",
                "mensagem": "Ha idoso na familia que pode ter direito ao BPC (1 salario minimo/mes).",
                "prioridade": "alta",
                "proximo_passo": "Leve documentos ao CRAS para dar entrada no BPC.",
            })
        if perfil.pessoas_com_deficiencia > 0 and perfil.renda_per_capita <= 379.50:
            recomendacoes.append({
                "tipo": "beneficio_nao_acessado",
                "beneficio": "BPC",
                "mensagem": "Ha pessoa com deficiencia que pode ter direito ao BPC.",
                "prioridade": "alta",
                "proximo_passo": "Leve laudo medico e documentos ao CRAS.",
            })

    # Tarifa Social
    if "TSEE" not in beneficios_ativos and perfil.renda_per_capita <= 660:
        recomendacoes.append({
            "tipo": "beneficio_nao_acessado",
            "beneficio": "TSEE",
            "mensagem": "Voce pode ter direito a desconto na conta de luz (Tarifa Social).",
            "prioridade": "media",
            "proximo_passo": "Leve NIS e conta de luz a distribuidora de energia.",
        })

    # CadUnico desatualizado
    if not perfil.cadunico_atualizado:
        recomendacoes.append({
            "tipo": "alerta_cadastro",
            "mensagem": "Seu CadUnico esta desatualizado! Isso pode BLOQUEAR seus beneficios.",
            "prioridade": "alta",
            "proximo_passo": "Va ao CRAS com documentos de toda a familia para atualizar.",
        })
    elif perfil.meses_desde_atualizacao > 18:
        recomendacoes.append({
            "tipo": "alerta_cadastro",
            "mensagem": (
                f"Seu CadUnico vence em breve ({24 - perfil.meses_desde_atualizacao} meses). "
                "Atualize antes para nao correr risco."
            ),
            "prioridade": "media",
            "proximo_passo": "Agende atualizacao no CRAS.",
        })

    # Farmacia Popular
    if "FARMACIA_POPULAR" not in beneficios_ativos:
        recomendacoes.append({
            "tipo": "beneficio_nao_acessado",
            "beneficio": "FARMACIA_POPULAR",
            "mensagem": "Voce pode pegar remedios de graca pelo Farmacia Popular.",
            "prioridade": "baixa",
            "proximo_passo": "Leve CPF e receita medica a uma farmacia credenciada.",
        })

    # Ordenar por prioridade
    ordem = {"alta": 0, "media": 1, "baixa": 2}
    recomendacoes.sort(key=lambda r: ordem.get(r["prioridade"], 3))

    return recomendacoes


# =============================================================================
# Tool wrapper para o agente
# =============================================================================

def analisar_vulnerabilidade(
    renda_per_capita: float = 0,
    membros_familia: int = 1,
    criancas_0_6: int = 0,
    gestantes: int = 0,
    idosos_60_mais: int = 0,
    pessoas_com_deficiencia: int = 0,
    tipo_moradia: str = "propria",
    trabalho_formal: bool = False,
    desempregados: int = 0,
    beneficios_ativos: Optional[List[str]] = None,
    cadunico_atualizado: bool = True,
    meses_desde_atualizacao: int = 0,
    zona: str = "urbana",
) -> dict:
    """Analisa vulnerabilidade social e gera recomendacoes.

    Calcula score em 6 dimensoes e sugere beneficios nao acessados.

    Returns:
        dict com score, faixa de risco, fatores e recomendacoes
    """
    perfil = PerfilFamiliar(
        renda_per_capita=renda_per_capita,
        membros_familia=membros_familia,
        criancas_0_6=criancas_0_6,
        gestantes=gestantes,
        idosos_60_mais=idosos_60_mais,
        pessoas_com_deficiencia=pessoas_com_deficiencia,
        tipo_moradia=tipo_moradia,
        trabalho_formal=trabalho_formal,
        desempregados=desempregados,
        beneficios_ativos=beneficios_ativos or [],
        cadunico_atualizado=cadunico_atualizado,
        meses_desde_atualizacao=meses_desde_atualizacao,
        zona=zona,
    )

    resultado_score = calcular_score(perfil)
    recomendacoes = gerar_recomendacoes(perfil, resultado_score["score"])

    return {
        **resultado_score,
        "recomendacoes": recomendacoes,
        "total_recomendacoes": len(recomendacoes),
    }
