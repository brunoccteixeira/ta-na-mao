"""
Servico de auditoria de acessibilidade textual.

Calcula indice de legibilidade (Flesch adaptado para portugues),
detecta jargoes governamentais e sugere linguagem simples.
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Jargoes governamentais -> linguagem simples
# =============================================================================

JARGOES_GOVERNAMENTAIS = {
    "beneficiário": "pessoa que recebe o beneficio",
    "beneficiario": "pessoa que recebe o beneficio",
    "elegível": "que tem direito",
    "elegivel": "que tem direito",
    "deferido": "aprovado",
    "indeferido": "negado / nao aprovado",
    "auferir renda": "ganhar dinheiro",
    "per capita": "por pessoa",
    "composição familiar": "pessoas da familia",
    "composicao familiar": "pessoas da familia",
    "responsável familiar": "pessoa responsavel pela familia",
    "responsavel familiar": "pessoa responsavel pela familia",
    "vulnerabilidade social": "situacao dificil / precisando de ajuda",
    "cadastro único": "CadUnico (cadastro do governo para beneficios)",
    "cadastro unico": "CadUnico (cadastro do governo para beneficios)",
    "unidade de atendimento": "posto / local de atendimento",
    "protocolar": "dar entrada / registrar pedido",
    "emitir parecer": "dar uma resposta",
    "intersetorial": "entre diferentes areas do governo",
    "condicionalidades": "regras que precisa cumprir (como vacinar filhos, ir a escola)",
    "acompanhamento socioassistencial": "acompanhamento do assistente social",
    "rede socioassistencial": "servicos de assistencia social da cidade",
    "equipamento público": "posto de atendimento do governo",
    "equipamento publico": "posto de atendimento do governo",
    "território": "regiao / bairro",
    "contrapartida": "o que voce precisa fazer em troca",
}


# =============================================================================
# Calculo de silabas em portugues
# =============================================================================

def _contar_silabas(palavra: str) -> int:
    """Conta silabas de uma palavra em portugues (heuristica).

    Usa contagem de vogais com ajustes para ditongos e hiatos.
    """
    palavra = palavra.lower().strip()
    if not palavra:
        return 0

    vogais = "aeiouáéíóúâêîôûãõàèìòù"
    n_silabas = 0
    anterior_vogal = False

    for char in palavra:
        eh_vogal = char in vogais
        if eh_vogal and not anterior_vogal:
            n_silabas += 1
        anterior_vogal = eh_vogal

    return max(1, n_silabas)


# =============================================================================
# Indice de legibilidade
# =============================================================================

def calcular_legibilidade(texto: str) -> Dict[str, Any]:
    """Calcula indice de legibilidade Flesch adaptado para portugues.

    Formula: 248.835 - (1.015 x palavras/sentencas) - (84.6 x silabas/palavras)

    Meta: score >= 60 (equivalente a 5a serie).

    Args:
        texto: Texto para analisar

    Returns:
        dict com score, nivel, estatisticas e aprovacao
    """
    if not texto or not texto.strip():
        return {
            "score": 0,
            "nivel": "Sem texto",
            "aprovado": False,
            "erro": "Texto vazio.",
        }

    # Contar sentencas
    sentencas = re.split(r'[.!?]+', texto)
    sentencas = [s.strip() for s in sentencas if s.strip()]
    n_sentencas = max(1, len(sentencas))

    # Contar palavras
    palavras = re.findall(r'\b[a-záéíóúâêîôûãõàèìòùç]+\b', texto.lower())
    n_palavras = max(1, len(palavras))

    # Contar silabas
    n_silabas = sum(_contar_silabas(p) for p in palavras)

    # Calcular Flesch adaptado para portugues
    media_palavras_sentenca = n_palavras / n_sentencas
    media_silabas_palavra = n_silabas / n_palavras

    score = 248.835 - (1.015 * media_palavras_sentenca) - (84.6 * media_silabas_palavra)
    score = max(0, min(100, round(score, 1)))

    # Classificar nivel
    if score >= 75:
        nivel = "Muito facil"
    elif score >= 60:
        nivel = "Facil"
    elif score >= 50:
        nivel = "Adequado"
    elif score >= 30:
        nivel = "Moderado"
    elif score >= 10:
        nivel = "Dificil"
    else:
        nivel = "Muito dificil"

    aprovado = score >= 60

    return {
        "score": score,
        "nivel": nivel,
        "aprovado": aprovado,
        "estatisticas": {
            "palavras": n_palavras,
            "sentencas": n_sentencas,
            "silabas": n_silabas,
            "media_palavras_por_sentenca": round(media_palavras_sentenca, 1),
            "media_silabas_por_palavra": round(media_silabas_palavra, 2),
        },
        "meta": "Score >= 60 (linguagem simples, equivalente a 5a serie)",
        "sugestoes": _sugestoes_legibilidade(score, media_palavras_sentenca, media_silabas_palavra),
    }


def _sugestoes_legibilidade(
    score: float,
    media_palavras: float,
    media_silabas: float,
) -> List[str]:
    """Gera sugestoes para melhorar legibilidade."""
    sugestoes = []

    if media_palavras > 20:
        sugestoes.append(
            f"Frases muito longas (media: {media_palavras:.0f} palavras). "
            "Tente quebrar em frases de ate 15 palavras."
        )

    if media_silabas > 2.5:
        sugestoes.append(
            "Muitas palavras longas. Troque por sinonimos mais curtos quando possivel."
        )

    if score < 60:
        sugestoes.append(
            "Texto esta abaixo do nivel recomendado. "
            "Use frases curtas e palavras simples."
        )

    if not sugestoes:
        sugestoes.append("Texto esta bom! Linguagem adequada para o publico.")

    return sugestoes


# =============================================================================
# Deteccao de jargoes
# =============================================================================

def detectar_jargoes(texto: str) -> Dict[str, Any]:
    """Detecta jargoes governamentais e sugere linguagem simples.

    Args:
        texto: Texto para analisar

    Returns:
        dict com jargoes encontrados e alternativas simples
    """
    texto_lower = texto.lower()
    jargoes_encontrados = []

    for jargao, alternativa in JARGOES_GOVERNAMENTAIS.items():
        if jargao in texto_lower:
            # Encontrar contexto (ate 50 chars ao redor)
            idx = texto_lower.find(jargao)
            inicio = max(0, idx - 30)
            fim = min(len(texto), idx + len(jargao) + 30)
            contexto = texto[inicio:fim].strip()

            jargoes_encontrados.append({
                "jargao": jargao,
                "alternativa": alternativa,
                "contexto": f"...{contexto}...",
            })

    return {
        "total_jargoes": len(jargoes_encontrados),
        "jargoes": jargoes_encontrados,
        "aprovado": len(jargoes_encontrados) == 0,
        "mensagem": (
            "Texto livre de jargoes!"
            if not jargoes_encontrados
            else f"Encontrados {len(jargoes_encontrados)} jargoes. Substitua por linguagem simples."
        ),
    }


# =============================================================================
# Auditoria completa
# =============================================================================

def auditar_texto(texto: str) -> Dict[str, Any]:
    """Faz auditoria completa de acessibilidade textual.

    Combina legibilidade + deteccao de jargoes.

    Args:
        texto: Texto para auditar

    Returns:
        dict com resultados da auditoria completa
    """
    legibilidade = calcular_legibilidade(texto)
    jargoes = detectar_jargoes(texto)

    aprovado_geral = legibilidade["aprovado"] and jargoes["aprovado"]

    return {
        "aprovado": aprovado_geral,
        "legibilidade": legibilidade,
        "jargoes": jargoes,
        "resumo": (
            "Texto acessivel e adequado ao publico!"
            if aprovado_geral
            else "Texto precisa de ajustes para ficar mais acessivel."
        ),
    }
