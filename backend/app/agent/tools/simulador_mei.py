"""
Tools do MEI Simplificado.

Simulador de impacto nos beneficios ao se tornar MEI,
guia passo-a-passo de formalizacao e alertas de obrigacoes.
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Constantes 2025
_SALARIO_MINIMO = 1518.00
_DAS_MENSAL = 75.60  # Valor aproximado do DAS-MEI 2025
_LIMITE_FATURAMENTO_ANUAL = 81000.00
_LIMITE_FATURAMENTO_MENSAL = _LIMITE_FATURAMENTO_ANUAL / 12

# Faixas de renda para beneficios
_BOLSA_FAMILIA_EXTREMA_POBREZA = 105.00  # per capita
_BOLSA_FAMILIA_POBREZA = 218.00  # per capita
_BOLSA_FAMILIA_PROTECAO = 660.00  # per capita (regra de protecao 24 meses)
_BPC_LIMITE = _SALARIO_MINIMO / 4  # 1/4 do salario minimo per capita


def simular_impacto_mei(
    faturamento_estimado: float,
    despesas_estimadas: float = 0,
    membros_familia: int = 1,
    renda_familiar_atual: float = 0,
    beneficios_atuais: Optional[List[str]] = None,
) -> dict:
    """Simula impacto de se tornar MEI nos beneficios sociais.

    Responde a pergunta central: "Se eu virar MEI, vou perder meu beneficio?"

    Args:
        faturamento_estimado: Faturamento mensal estimado como MEI (R$)
        despesas_estimadas: Despesas mensais do negocio (R$)
        membros_familia: Numero de pessoas na familia
        renda_familiar_atual: Renda familiar total ATUAL (sem MEI) (R$)
        beneficios_atuais: Lista de beneficios que recebe:
            BOLSA_FAMILIA, BPC, TSEE, FARMACIA_POPULAR

    Returns:
        dict com analise de impacto em cada beneficio e comparativo financeiro
    """
    logger.info(
        f"Simulando impacto MEI: faturamento={faturamento_estimado}, "
        f"membros={membros_familia}"
    )

    if beneficios_atuais is None:
        beneficios_atuais = []

    # Calcular lucro liquido (o que conta como renda)
    lucro_mensal = faturamento_estimado - despesas_estimadas
    # Na pratica, o governo usa um percentual do faturamento como presuncao de lucro
    # MEI servicos: 32% do faturamento. MEI comercio: 8%. Usamos simplificado.
    lucro_presumido = faturamento_estimado * 0.32  # Presuncao de lucro para servicos

    # Renda per capita com e sem MEI
    renda_pc_atual = renda_familiar_atual / max(membros_familia, 1)
    renda_pc_com_mei = (renda_familiar_atual + lucro_mensal) / max(membros_familia, 1)

    # Analisar impacto em cada beneficio
    impactos = []

    # Bolsa Familia
    if "BOLSA_FAMILIA" in beneficios_atuais or not beneficios_atuais:
        impacto_bf = _analisar_bolsa_familia(renda_pc_atual, renda_pc_com_mei, lucro_mensal)
        impactos.append(impacto_bf)

    # BPC
    if "BPC" in beneficios_atuais:
        impacto_bpc = _analisar_bpc(renda_pc_com_mei)
        impactos.append(impacto_bpc)

    # Tarifa Social
    if "TSEE" in beneficios_atuais or not beneficios_atuais:
        impacto_tsee = _analisar_tsee(renda_pc_com_mei)
        impactos.append(impacto_tsee)

    # Farmacia Popular
    if "FARMACIA_POPULAR" in beneficios_atuais or not beneficios_atuais:
        impactos.append({
            "beneficio": "Farmacia Popular",
            "status": "MANTEM",
            "explicacao": "Farmacia Popular nao depende de renda. Qualquer pessoa pode usar.",
        })

    # Comparativo financeiro
    custo_mei = _DAS_MENSAL
    ganho_liquido = lucro_mensal - custo_mei

    comparativo = {
        "renda_atual": renda_familiar_atual,
        "renda_com_mei": renda_familiar_atual + lucro_mensal,
        "lucro_estimado_mensal": round(lucro_mensal, 2),
        "custo_mei_mensal": custo_mei,
        "ganho_liquido_mensal": round(ganho_liquido, 2),
        "ganho_liquido_anual": round(ganho_liquido * 12, 2),
        "renda_per_capita_atual": round(renda_pc_atual, 2),
        "renda_per_capita_com_mei": round(renda_pc_com_mei, 2),
    }

    # Beneficios de ser MEI
    beneficios_mei = [
        "CNPJ - pode emitir nota fiscal",
        "Aposentadoria por idade (apos 15 anos de contribuicao)",
        "Auxilio-doenca (apos 12 meses de contribuicao)",
        "Salario-maternidade (apos 10 meses de contribuicao)",
        f"Custo baixo: so R$ {custo_mei:.2f}/mes",
        "Acesso a credito com juros menores",
        "Pode abrir conta de empresa",
    ]

    # Veredicto: vale a pena?
    vale_a_pena = ganho_liquido > 0
    algum_perde = any(i["status"] == "PODE_PERDER" for i in impactos)

    if vale_a_pena and not algum_perde:
        veredicto = "RECOMENDADO"
        mensagem = (
            f"Vale a pena! Voce ganha R$ {ganho_liquido:.2f}/mes a mais "
            "e nao perde nenhum beneficio."
        )
    elif vale_a_pena and algum_perde:
        veredicto = "AVALIAR"
        mensagem = (
            f"Voce ganha R$ {ganho_liquido:.2f}/mes a mais, "
            "mas pode afetar algum beneficio. Avalie com cuidado."
        )
    else:
        veredicto = "NAO_RECOMENDADO"
        mensagem = (
            "Neste momento, o custo do MEI eh maior que o ganho. "
            "Tente aumentar o faturamento antes de se formalizar."
        )

    return {
        "impactos": impactos,
        "comparativo": comparativo,
        "beneficios_mei": beneficios_mei,
        "veredicto": veredicto,
        "mensagem": mensagem,
        "vale_a_pena": vale_a_pena,
        "obrigacoes_mei": _listar_obrigacoes(),
    }


def _analisar_bolsa_familia(renda_pc_atual: float, renda_pc_com_mei: float, lucro_mei: float) -> dict:
    """Analisa impacto no Bolsa Familia."""
    if renda_pc_com_mei <= _BOLSA_FAMILIA_POBREZA:
        return {
            "beneficio": "Bolsa Familia",
            "status": "MANTEM",
            "explicacao": (
                f"Sua renda per capita com MEI seria R$ {renda_pc_com_mei:.2f}, "
                f"abaixo do limite de R$ {_BOLSA_FAMILIA_POBREZA:.2f}. "
                "Voce continua recebendo normalmente."
            ),
        }
    elif renda_pc_com_mei <= _BOLSA_FAMILIA_PROTECAO:
        return {
            "beneficio": "Bolsa Familia",
            "status": "PROTEGIDO",
            "explicacao": (
                f"Sua renda per capita com MEI seria R$ {renda_pc_com_mei:.2f}. "
                "Voce entra na REGRA DE PROTECAO: continua recebendo por ate 24 meses, "
                "mesmo com renda acima do limite. Tempo para se estabilizar."
            ),
        }
    else:
        return {
            "beneficio": "Bolsa Familia",
            "status": "PODE_PERDER",
            "explicacao": (
                f"Sua renda per capita com MEI seria R$ {renda_pc_com_mei:.2f}, "
                f"acima do limite de protecao de R$ {_BOLSA_FAMILIA_PROTECAO:.2f}. "
                "Voce pode perder o Bolsa Familia. Avalie se o ganho compensa."
            ),
        }


def _analisar_bpc(renda_pc_com_mei: float) -> dict:
    """Analisa impacto no BPC."""
    if renda_pc_com_mei <= _BPC_LIMITE:
        return {
            "beneficio": "BPC",
            "status": "MANTEM",
            "explicacao": (
                f"Renda per capita de R$ {renda_pc_com_mei:.2f} esta abaixo "
                f"do limite de R$ {_BPC_LIMITE:.2f} (1/4 do salario minimo). "
                "Voce continua recebendo."
            ),
        }
    else:
        return {
            "beneficio": "BPC",
            "status": "PODE_PERDER",
            "explicacao": (
                f"Renda per capita de R$ {renda_pc_com_mei:.2f} ultrapassa "
                f"o limite de R$ {_BPC_LIMITE:.2f}. O BPC pode ser cortado. "
                "IMPORTANTE: Converse com o assistente social do CRAS antes."
            ),
        }


def _analisar_tsee(renda_pc_com_mei: float) -> dict:
    """Analisa impacto na Tarifa Social de Energia."""
    limite_tsee = _SALARIO_MINIMO / 2  # Meio salario minimo per capita
    if renda_pc_com_mei <= limite_tsee:
        return {
            "beneficio": "Tarifa Social de Energia",
            "status": "MANTEM",
            "explicacao": "Renda dentro do limite. Voce continua com desconto na luz.",
        }
    else:
        return {
            "beneficio": "Tarifa Social de Energia",
            "status": "PODE_PERDER",
            "explicacao": (
                f"Renda per capita de R$ {renda_pc_com_mei:.2f} pode ultrapassar "
                "o limite da Tarifa Social. Voce pode perder o desconto na conta de luz."
            ),
        }


def _listar_obrigacoes() -> list:
    """Lista obrigacoes do MEI."""
    return [
        {
            "nome": "DAS mensal",
            "descricao": f"Pagar o boleto de R$ {_DAS_MENSAL:.2f} ate o dia 20 de cada mes",
            "consequencia_atraso": "Multa + juros. Acumular 3 meses pode cancelar o CNPJ.",
        },
        {
            "nome": "DASN-SIMEI anual",
            "descricao": "Declaracao anual de faturamento ate 31 de maio",
            "consequencia_atraso": "Multa de R$ 50. Nao consegue emitir DAS.",
        },
        {
            "nome": "Limite de faturamento",
            "descricao": f"Maximo R$ {_LIMITE_FATURAMENTO_ANUAL:,.0f} por ano",
            "consequencia_atraso": "Se ultrapassar, vira Microempresa e paga mais imposto.",
        },
        {
            "nome": "Maximo 1 funcionario",
            "descricao": "MEI pode ter no maximo 1 empregado registrado",
            "consequencia_atraso": "Nao pode contratar mais sem mudar de categoria.",
        },
    ]


# =============================================================================
# Tool: guia_formalizacao_mei
# =============================================================================

def guia_formalizacao_mei() -> dict:
    """Retorna guia passo-a-passo para se formalizar como MEI.

    Returns:
        dict com passos, requisitos, custos e links
    """
    return {
        "titulo": "Como virar MEI em 5 passos",
        "requisitos": [
            "Faturar ate R$ 81.000 por ano",
            "Nao ser socio de outra empresa",
            "Ter atividade permitida (a maioria eh permitida)",
            "Ter no maximo 1 funcionario",
        ],
        "passos": [
            {
                "numero": 1,
                "titulo": "Acesse o Portal do Empreendedor",
                "descricao": "Entre em gov.br/mei com sua conta Gov.br",
                "dica": "Se nao tem conta Gov.br, crie uma primeiro.",
            },
            {
                "numero": 2,
                "titulo": "Preencha seus dados",
                "descricao": "CPF, data de nascimento, telefone, endereco e tipo de atividade",
                "dica": "Escolha a atividade que mais se parece com o que voce faz.",
            },
            {
                "numero": 3,
                "titulo": "Receba seu CNPJ",
                "descricao": "Na hora! O CNPJ sai na tela para voce anotar.",
                "dica": "Salve ou tire foto do numero do CNPJ.",
            },
            {
                "numero": 4,
                "titulo": "Emita seu CCMEI",
                "descricao": "Certificado de Condicao de Microempreendedor - seu 'alvara'",
                "dica": "Esse documento substitui o alvara de funcionamento na maioria das cidades.",
            },
            {
                "numero": 5,
                "titulo": "Pague o primeiro DAS",
                "descricao": f"Boleto de R$ {_DAS_MENSAL:.2f} - acesse no app MEI ou Portal do Empreendedor",
                "dica": "Coloque lembrete no celular para pagar todo mes ate dia 20.",
            },
        ],
        "custo_total": f"R$ {_DAS_MENSAL:.2f}/mes (so isso! Nao tem taxa de abertura.)",
        "tempo": "Leva menos de 30 minutos",
        "onde_pedir_ajuda": [
            "SEBRAE: ligue 0800-570-0800 (gratuito)",
            "Sala do Empreendedor da sua prefeitura",
            "CRAS (pode orientar sobre impacto nos beneficios)",
        ],
    }
