"""
Tools de orientacao sobre direitos trabalhistas.

Implementa consulta de direitos por tipo de trabalho,
calculadora de rescisao trabalhista e calculadora de seguro-desemprego.

Publico-alvo: trabalhadores informais, CLT, domesticos, MEI,
rurais e pescadores artesanais.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Dados: Direitos por tipo de trabalho
# =============================================================================

_DIREITOS_POR_TIPO = {
    "CLT": {
        "titulo": "Trabalhador com Carteira Assinada (CLT)",
        "direitos": [
            {"nome": "13o salario", "descricao": "Salario extra no final do ano, proporcional aos meses trabalhados"},
            {"nome": "Ferias + 1/3", "descricao": "30 dias de ferias por ano com adicional de 1/3 do salario"},
            {"nome": "FGTS (8%)", "descricao": "Empresa deposita 8% do salario todo mes na sua conta FGTS"},
            {"nome": "Seguro-desemprego", "descricao": "3 a 5 parcelas se for demitido sem justa causa"},
            {"nome": "Aviso previo", "descricao": "30 dias + 3 dias por ano trabalhado (maximo 90 dias)"},
            {"nome": "Hora extra", "descricao": "50% a mais no dia de semana, 100% no domingo e feriado"},
            {"nome": "Vale-transporte", "descricao": "Empresa paga transporte, desconta no maximo 6% do salario"},
            {"nome": "Licenca-maternidade", "descricao": "120 dias de licenca com salario integral"},
            {"nome": "Licenca-paternidade", "descricao": "5 dias de licenca (20 dias em empresas cidadas)"},
            {"nome": "Estabilidade gestante", "descricao": "Nao pode ser demitida da confirmacao da gravidez ate 5 meses apos o parto"},
        ],
        "dica": "Guarde seus holerites e contracheques. Em caso de problema, procure o sindicato da sua categoria.",
    },
    "DOMESTICO": {
        "titulo": "Trabalho Domestico",
        "direitos": [
            {"nome": "Carteira assinada obrigatoria", "descricao": "Desde 2015, trabalho domestico deve ter carteira assinada"},
            {"nome": "FGTS obrigatorio", "descricao": "Patrao deposita 8% do salario todo mes + 3,2% de seguro"},
            {"nome": "Salario minimo garantido", "descricao": "Nao pode ganhar menos que o minimo (R$ 1.518 em 2025)"},
            {"nome": "13o salario", "descricao": "Salario extra no final do ano"},
            {"nome": "Ferias + 1/3", "descricao": "30 dias de ferias com adicional"},
            {"nome": "Hora extra", "descricao": "50% a mais apos 8h diarias ou 44h semanais"},
            {"nome": "eSocial", "descricao": "Patrao deve registrar no eSocial todo mes"},
            {"nome": "Seguro-desemprego", "descricao": "3 parcelas de 1 salario minimo se demitida sem justa causa"},
        ],
        "dica": "Se seu patrao nao assina sua carteira, voce pode denunciar na Superintendencia do Trabalho ou procurar a Defensoria Publica.",
    },
    "MEI": {
        "titulo": "Microempreendedor Individual (MEI)",
        "direitos": [
            {"nome": "Aposentadoria", "descricao": "Aposentadoria por idade apos 180 meses de contribuicao (15 anos)"},
            {"nome": "Auxilio-doenca", "descricao": "Beneficio se ficar doente e nao puder trabalhar (apos 12 meses de contribuicao)"},
            {"nome": "Salario-maternidade", "descricao": "Beneficio durante a licenca-maternidade (apos 10 meses de contribuicao)"},
            {"nome": "Auxilio por acidente", "descricao": "Pensao por morte e auxilio-reclusao para dependentes"},
            {"nome": "CNPJ", "descricao": "Pode emitir nota fiscal e abrir conta de empresa"},
        ],
        "obrigacoes": [
            {"nome": "DAS mensal", "descricao": "Pagar o boleto todo mes (cerca de R$ 75 em 2025)"},
            {"nome": "DASN-SIMEI", "descricao": "Declaracao anual ate 31 de maio"},
            {"nome": "Limite de faturamento", "descricao": "Maximo R$ 81.000 por ano"},
        ],
        "dica": "O MEI eh uma otima forma de se formalizar. Com o CNPJ voce acessa credito mais barato e garante aposentadoria.",
    },
    "INFORMAL": {
        "titulo": "Trabalho Informal (Sem Carteira)",
        "direitos": [
            {"nome": "Reconhecimento de vinculo", "descricao": "Pode entrar na Justica para reconhecer vinculo de ate 2 anos atras"},
            {"nome": "Provas aceitas", "descricao": "Mensagens de WhatsApp, fotos, testemunhas, PIX recebidos servem como prova"},
            {"nome": "Defensoria Publica gratuita", "descricao": "Se nao tem dinheiro para advogado, a Defensoria ajuda de graca"},
            {"nome": "Prazo de 2 anos", "descricao": "Voce tem ate 2 ANOS apos sair do trabalho para entrar na Justica"},
        ],
        "alerta": "Se voce trabalha sem carteira, GUARDE provas: prints de conversas, fotos no trabalho, comprovantes de PIX.",
        "dica": "Procure a Defensoria Publica da sua cidade. O atendimento eh gratuito e podem entrar com acao trabalhista por voce.",
    },
    "RURAL": {
        "titulo": "Trabalhador Rural",
        "direitos": [
            {"nome": "Seguro-safra", "descricao": "Protecao em caso de seca ou enchente (R$ 1.200 em 5 parcelas)"},
            {"nome": "Garantia-Safra", "descricao": "Para agricultores do semiarido que perdem a colheita"},
            {"nome": "PRONAF", "descricao": "Credito rural com juros baixos para investir na producao"},
            {"nome": "PAA", "descricao": "Vender producao para o governo a preco justo"},
            {"nome": "PNAE", "descricao": "Vender para a merenda escolar (30% deve vir da agricultura familiar)"},
            {"nome": "Aposentadoria especial", "descricao": "Mulher com 55 anos e homem com 60 anos (5 anos antes do urbano)"},
            {"nome": "SETR", "descricao": "Registro como segurado especial no INSS"},
        ],
        "dica": "Mantenha sua DAP (Declaracao de Aptidao ao PRONAF) ou CAF atualizada. Ela eh a porta de entrada para todos os programas.",
    },
    "PESCADOR": {
        "titulo": "Pescador Artesanal",
        "direitos": [
            {"nome": "Seguro-Defeso", "descricao": "1 salario minimo por mes durante o periodo de piracema (proibicao de pesca)"},
            {"nome": "RGP", "descricao": "Registro Geral da Atividade Pesqueira - documento obrigatorio"},
            {"nome": "Aposentadoria especial", "descricao": "Mesmas regras do trabalhador rural (55F/60M)"},
            {"nome": "PRONAF Pesca", "descricao": "Credito para investir em equipamentos de pesca"},
        ],
        "dica": "Mantenha seu RGP (Registro Geral de Pesca) em dia. Sem ele, voce perde o Seguro-Defeso.",
    },
}

# Mapeamento de situacoes para orientacao
_SITUACOES = {
    "DEMITIDO": {
        "titulo": "Fui demitido",
        "passos": [
            "Calcule sua rescisao (use a calculadora abaixo)",
            "Verifique direito ao seguro-desemprego",
            "Saque o FGTS + multa de 40%",
            "Prazo: empresa tem 10 dias para pagar a rescisao",
        ],
        "alerta": "Se a empresa nao pagar em 10 dias, voce tem direito a multa de 1 salario!",
    },
    "SEM_CARTEIRA": {
        "titulo": "Trabalho sem carteira assinada",
        "passos": [
            "Guarde provas: mensagens, fotos, PIX, testemunhas",
            "Voce tem 2 ANOS apos sair para entrar na Justica",
            "Procure a Defensoria Publica (gratuito!)",
            "Ou o sindicato da sua categoria",
        ],
        "alerta": "NAO espere! O prazo de 2 anos eh contado da data que voce saiu do trabalho.",
    },
    "ASSEDIO": {
        "titulo": "Assedio ou discriminacao no trabalho",
        "passos": [
            "Ligue para o Disque 100 (denuncias - gratuito)",
            "Procure o Ministerio Publico do Trabalho",
            "Procure a Defensoria Publica",
            "Se for violencia: CREAS da sua cidade",
        ],
        "servicos": [
            {"nome": "Disque 100", "telefone": "100", "descricao": "Denuncias de violacoes de direitos"},
            {"nome": "MPT", "telefone": "0800-7286267", "descricao": "Ministerio Publico do Trabalho"},
        ],
    },
    "DIREITOS_NAO_PAGOS": {
        "titulo": "Direitos trabalhistas nao estao sendo pagos",
        "passos": [
            "Identifique quais direitos nao estao sendo pagos (hora extra, 13o, ferias...)",
            "Fale primeiro com o RH da empresa",
            "Se nao resolver, procure o sindicato",
            "Ultima opcao: Justica do Trabalho via Defensoria Publica",
        ],
        "dica": "Anote tudo: horarios reais de trabalho, extras nao pagos, descontos indevidos.",
    },
}


# =============================================================================
# Tool: consultar_direitos_trabalhistas
# =============================================================================

def consultar_direitos_trabalhistas(
    tipo_trabalho: Optional[str] = None,
    situacao: Optional[str] = None,
) -> dict:
    """Consulta direitos trabalhistas por tipo de trabalho ou situacao.

    Args:
        tipo_trabalho: Tipo de vinculo: CLT, DOMESTICO, MEI, INFORMAL, RURAL, PESCADOR.
                      Se nao informado, lista todos os tipos disponiveis.
        situacao: Situacao especifica: DEMITIDO, SEM_CARTEIRA, ASSEDIO, DIREITOS_NAO_PAGOS.
                 Se informado, retorna orientacao para a situacao.

    Returns:
        dict com direitos e orientacoes
    """
    logger.info(f"Consultando direitos trabalhistas: tipo={tipo_trabalho}, situacao={situacao}")

    # Se pediu orientacao para uma situacao
    if situacao:
        situacao_upper = situacao.upper().replace(" ", "_")
        info = _SITUACOES.get(situacao_upper)
        if info:
            return {
                "encontrado": True,
                "tipo": "situacao",
                "situacao": info,
            }
        return {
            "encontrado": False,
            "erro": f"Situacao '{situacao}' nao reconhecida.",
            "situacoes_disponiveis": list(_SITUACOES.keys()),
        }

    # Se pediu direitos de um tipo de trabalho
    if tipo_trabalho:
        tipo_upper = tipo_trabalho.upper().replace(" ", "_")
        # Mapeamentos comuns
        alias = {
            "CARTEIRA_ASSINADA": "CLT",
            "FORMAL": "CLT",
            "DOMESTICA": "DOMESTICO",
            "EMPREGADA_DOMESTICA": "DOMESTICO",
            "MICROEMPREENDEDOR": "MEI",
            "AUTONOMO": "MEI",
            "SEM_CARTEIRA": "INFORMAL",
            "BICO": "INFORMAL",
            "AGRICULTOR": "RURAL",
            "AGRICULTURA_FAMILIAR": "RURAL",
            "PESCA": "PESCADOR",
            "PESCADORA": "PESCADOR",
        }
        tipo_real = alias.get(tipo_upper, tipo_upper)
        info = _DIREITOS_POR_TIPO.get(tipo_real)
        if info:
            return {
                "encontrado": True,
                "tipo": "direitos",
                "tipo_trabalho": tipo_real,
                "info": info,
            }
        return {
            "encontrado": False,
            "erro": f"Tipo de trabalho '{tipo_trabalho}' nao reconhecido.",
            "tipos_disponiveis": list(_DIREITOS_POR_TIPO.keys()),
        }

    # Nenhum filtro: lista tipos disponiveis
    tipos = [
        {"codigo": k, "titulo": v["titulo"]}
        for k, v in _DIREITOS_POR_TIPO.items()
    ]
    return {
        "encontrado": True,
        "tipo": "lista",
        "tipos_disponiveis": tipos,
        "situacoes_disponiveis": [
            {"codigo": k, "titulo": v["titulo"]}
            for k, v in _SITUACOES.items()
        ],
        "mensagem": "Me conta que tipo de trabalho voce faz ou qual sua situacao que eu te oriento.",
    }


# =============================================================================
# Tool: calcular_rescisao
# =============================================================================

def calcular_rescisao(
    salario: float,
    meses_trabalhados: int,
    motivo: str = "SEM_JUSTA_CAUSA",
    tem_ferias_vencidas: bool = False,
    dias_trabalhados_mes_atual: int = 0,
    aviso_previo_indenizado: bool = True,
) -> dict:
    """Calcula rescisao trabalhista detalhada.

    Args:
        salario: Salario bruto mensal (R$)
        meses_trabalhados: Total de meses trabalhados na empresa
        motivo: Motivo da demissao:
            SEM_JUSTA_CAUSA - demitido pelo patrao sem justa causa
            JUSTA_CAUSA - demitido por justa causa
            PEDIDO_DEMISSAO - pediu demissao
            ACORDO - acordo entre as partes (reforma trabalhista)
        tem_ferias_vencidas: Se tem ferias vencidas (nao gozadas)
        dias_trabalhados_mes_atual: Dias trabalhados no mes da demissao
        aviso_previo_indenizado: Se o aviso previo sera indenizado (pago em dinheiro)

    Returns:
        dict com calculo detalhado de cada verba
    """
    logger.info(
        f"Calculando rescisao: salario={salario}, meses={meses_trabalhados}, "
        f"motivo={motivo}"
    )

    motivo = motivo.upper().replace(" ", "_")
    anos_trabalhados = meses_trabalhados / 12
    salario_dia = salario / 30

    resultado = {
        "salario_base": salario,
        "meses_trabalhados": meses_trabalhados,
        "motivo": motivo,
        "verbas": [],
        "total_bruto": 0.0,
        "descontos": [],
        "total_liquido": 0.0,
    }

    verbas = []
    descontos = []

    # 1. Saldo de salario (dias trabalhados no mes atual)
    if dias_trabalhados_mes_atual > 0:
        saldo = salario_dia * dias_trabalhados_mes_atual
        verbas.append({
            "nome": "Saldo de salario",
            "descricao": f"{dias_trabalhados_mes_atual} dias trabalhados no ultimo mes",
            "valor": round(saldo, 2),
        })

    # 2. Aviso previo
    if motivo in ("SEM_JUSTA_CAUSA", "ACORDO"):
        dias_aviso = min(90, 30 + int(anos_trabalhados) * 3)
        if aviso_previo_indenizado:
            valor_aviso = salario_dia * dias_aviso
            verbas.append({
                "nome": "Aviso previo indenizado",
                "descricao": f"{dias_aviso} dias (30 + 3 por ano trabalhado)",
                "valor": round(valor_aviso, 2),
            })
        else:
            verbas.append({
                "nome": "Aviso previo trabalhado",
                "descricao": f"{dias_aviso} dias (ja incluido no saldo de salario)",
                "valor": 0.0,
            })

    # 3. 13o salario proporcional
    meses_13o = meses_trabalhados % 12
    if meses_13o == 0 and meses_trabalhados > 0:
        meses_13o = 12
    if motivo != "JUSTA_CAUSA":
        valor_13o = (salario / 12) * meses_13o
        verbas.append({
            "nome": "13o salario proporcional",
            "descricao": f"{meses_13o}/12 avos",
            "valor": round(valor_13o, 2),
        })

    # 4. Ferias proporcionais + 1/3
    meses_ferias = meses_trabalhados % 12
    if meses_ferias == 0 and meses_trabalhados > 0:
        meses_ferias = 12
    if motivo != "JUSTA_CAUSA":
        valor_ferias = (salario / 12) * meses_ferias
        terco_ferias = valor_ferias / 3
        verbas.append({
            "nome": "Ferias proporcionais + 1/3",
            "descricao": f"{meses_ferias}/12 avos + 1/3 constitucional",
            "valor": round(valor_ferias + terco_ferias, 2),
        })

    # 5. Ferias vencidas + 1/3 (se houver)
    if tem_ferias_vencidas and motivo != "JUSTA_CAUSA":
        valor_ferias_vencidas = salario + (salario / 3)
        verbas.append({
            "nome": "Ferias vencidas + 1/3",
            "descricao": "Ferias nao gozadas do periodo anterior",
            "valor": round(valor_ferias_vencidas, 2),
        })

    # 6. FGTS + Multa
    saldo_fgts_estimado = salario * 0.08 * meses_trabalhados
    if motivo == "SEM_JUSTA_CAUSA":
        multa_fgts = saldo_fgts_estimado * 0.40
        verbas.append({
            "nome": "Multa FGTS (40%)",
            "descricao": f"40% sobre saldo FGTS estimado de R$ {saldo_fgts_estimado:.2f}",
            "valor": round(multa_fgts, 2),
        })
        verbas.append({
            "nome": "Saque FGTS",
            "descricao": "Saldo integral do FGTS liberado para saque",
            "valor": round(saldo_fgts_estimado, 2),
        })
    elif motivo == "ACORDO":
        multa_fgts = saldo_fgts_estimado * 0.20
        saque_fgts = saldo_fgts_estimado * 0.80
        verbas.append({
            "nome": "Multa FGTS (20%)",
            "descricao": "Acordo: multa reduzida para 20%",
            "valor": round(multa_fgts, 2),
        })
        verbas.append({
            "nome": "Saque FGTS (80%)",
            "descricao": "Acordo: saque de 80% do saldo",
            "valor": round(saque_fgts, 2),
        })

    # Calcular totais
    total_verbas = sum(v["valor"] for v in verbas)

    # Descontos
    if motivo == "PEDIDO_DEMISSAO" and not aviso_previo_indenizado:
        # Se pediu demissao e nao cumpriu aviso, desconta
        desconto_aviso = salario
        descontos.append({
            "nome": "Desconto aviso previo",
            "descricao": "Pedido de demissao sem cumprimento do aviso",
            "valor": round(desconto_aviso, 2),
        })

    total_descontos = sum(d["valor"] for d in descontos)
    total_liquido = total_verbas - total_descontos

    resultado["verbas"] = verbas
    resultado["descontos"] = descontos
    resultado["total_bruto"] = round(total_verbas, 2)
    resultado["total_liquido"] = round(total_liquido, 2)

    # Informacoes adicionais
    extras = {}
    if motivo == "SEM_JUSTA_CAUSA":
        extras["seguro_desemprego"] = (
            "Voce pode ter direito ao seguro-desemprego! "
            "Prazo: ate 120 dias apos a demissao."
        )
        extras["prazo_pagamento"] = (
            "A empresa tem 10 dias uteis para pagar a rescisao. "
            "Se atrasar, voce tem direito a multa de 1 salario."
        )
    elif motivo == "JUSTA_CAUSA":
        extras["alerta"] = (
            "Na justa causa voce so recebe saldo de salario e ferias vencidas. "
            "Se achar que a justa causa foi injusta, procure a Defensoria Publica."
        )
    elif motivo == "PEDIDO_DEMISSAO":
        extras["seguro_desemprego"] = "Quem pede demissao NAO tem direito ao seguro-desemprego."
        extras["fgts"] = "Quem pede demissao NAO pode sacar o FGTS (fica na conta)."

    resultado["informacoes_extras"] = extras

    return resultado


# =============================================================================
# Tool: calcular_seguro_desemprego
# =============================================================================

# Faixas do seguro-desemprego 2025
_FAIXAS_SEGURO = [
    {"ate": 2138.76, "fator": 0.8, "fixo": 0},
    {"ate": 3564.96, "fator": 0.5, "fixo": 1711.01},
    {"ate": float("inf"), "fator": 0, "fixo": 2424.11},
]

_SALARIO_MINIMO = 1518.00  # 2025


def calcular_seguro_desemprego(
    salario_medio: float,
    vezes_solicitado: int = 1,
    meses_trabalhados: int = 12,
) -> dict:
    """Calcula valor e parcelas do seguro-desemprego.

    Args:
        salario_medio: Media dos ultimos 3 salarios (R$)
        vezes_solicitado: Quantas vezes ja pediu seguro-desemprego:
            1 = primeira vez
            2 = segunda vez
            3 = terceira vez ou mais
        meses_trabalhados: Meses trabalhados nos ultimos 36 meses

    Returns:
        dict com valor da parcela, numero de parcelas, total e prazo
    """
    logger.info(
        f"Calculando seguro-desemprego: salario_medio={salario_medio}, "
        f"vezes={vezes_solicitado}, meses={meses_trabalhados}"
    )

    # Verificar elegibilidade por tempo de trabalho
    if vezes_solicitado == 1:
        meses_minimos = 12
        descricao_tempo = "12 meses nos ultimos 18 meses (primeira solicitacao)"
    elif vezes_solicitado == 2:
        meses_minimos = 9
        descricao_tempo = "9 meses nos ultimos 12 meses (segunda solicitacao)"
    else:
        meses_minimos = 6
        descricao_tempo = "6 meses anteriores a demissao (terceira solicitacao em diante)"

    if meses_trabalhados < meses_minimos:
        return {
            "elegivel": False,
            "motivo": (
                f"Para a {vezes_solicitado}a solicitacao, voce precisa ter "
                f"trabalhado pelo menos {meses_minimos} meses. "
                f"Voce informou {meses_trabalhados} meses."
            ),
            "requisito": descricao_tempo,
            "dica": "Se voce trabalhou informalmente, pode nao contar. Mas se tem provas de vinculo, procure a Defensoria.",
        }

    # Calcular valor da parcela
    valor_parcela = 0.0
    for faixa in _FAIXAS_SEGURO:
        if salario_medio <= faixa["ate"]:
            if faixa["fixo"] > 0:
                excedente = salario_medio - _FAIXAS_SEGURO[0]["ate"]
                valor_parcela = faixa["fixo"] + (excedente * faixa["fator"])
            else:
                valor_parcela = salario_medio * faixa["fator"]
            break

    # Valor minimo = salario minimo
    valor_parcela = max(valor_parcela, _SALARIO_MINIMO)

    # Valor maximo (teto)
    valor_parcela = min(valor_parcela, _FAIXAS_SEGURO[-1]["fixo"])

    # Numero de parcelas
    if vezes_solicitado == 1:
        if meses_trabalhados >= 24:
            num_parcelas = 5
        elif meses_trabalhados >= 12:
            num_parcelas = 4
        else:
            num_parcelas = 0
    elif vezes_solicitado == 2:
        if meses_trabalhados >= 24:
            num_parcelas = 5
        elif meses_trabalhados >= 12:
            num_parcelas = 4
        elif meses_trabalhados >= 9:
            num_parcelas = 3
        else:
            num_parcelas = 0
    else:
        if meses_trabalhados >= 24:
            num_parcelas = 5
        elif meses_trabalhados >= 12:
            num_parcelas = 4
        elif meses_trabalhados >= 6:
            num_parcelas = 3
        else:
            num_parcelas = 0

    total = round(valor_parcela * num_parcelas, 2)

    return {
        "elegivel": True,
        "valor_parcela": round(valor_parcela, 2),
        "num_parcelas": num_parcelas,
        "total_estimado": total,
        "salario_medio_informado": salario_medio,
        "prazo_para_pedir": "Ate 120 dias (4 meses) apos a demissao",
        "onde_pedir": [
            "Aplicativo Carteira de Trabalho Digital",
            "Site: gov.br/seguro-desemprego",
            "Posto do SINE (Sistema Nacional de Emprego)",
            "Superintendencia do Trabalho",
        ],
        "documentos_necessarios": [
            "Carteira de trabalho (fisica ou digital)",
            "Termo de rescisao (TRCT)",
            "Requerimento do seguro-desemprego (formulario verde/marrom)",
            "CPF",
            "Documento com foto",
        ],
        "dica": (
            f"Voce recebe {num_parcelas} parcelas de R$ {valor_parcela:.2f}, "
            f"totalizando R$ {total:.2f}. "
            "Nao esqueca: o prazo para pedir eh de 120 dias!"
        ),
    }
