"""Tool para consulta de beneficios por CPF.

Consulta a tabela beneficiarios que contem dados indexados
do Portal da Transparencia (Bolsa Familia, BPC, etc).
"""

import re

from app.database import SessionLocal
from app.models.beneficiario import Beneficiario, mask_cpf


def consultar_beneficio(cpf: str) -> dict:
    """Consulta beneficios de um cidadao por CPF.

    Busca na tabela de beneficiarios indexados do Portal da Transparencia.
    CPF e armazenado como hash SHA256 para privacidade.

    Args:
        cpf: CPF do cidadao (11 digitos, com ou sem formatacao)

    Returns:
        dict: {
            "encontrado": bool,
            "cpf_masked": str,  # ***456.789-**
            "beneficios": {
                "bolsa_familia": {...},
                "bpc": {...},
                "cadunico": {...}
            },
            "texto_resumo": str,  # Resumo amigavel para o agente
            "mensagem": str
        }
    """
    # Limpa CPF
    cpf_limpo = re.sub(r'\D', '', cpf)

    # Valida tamanho
    if len(cpf_limpo) != 11:
        return {
            "encontrado": False,
            "cpf_masked": None,
            "beneficios": None,
            "texto_resumo": None,
            "mensagem": f"CPF invalido: deve ter 11 digitos, voce informou {len(cpf_limpo)}."
        }

    # Valida digitos iguais
    if cpf_limpo == cpf_limpo[0] * 11:
        return {
            "encontrado": False,
            "cpf_masked": None,
            "beneficios": None,
            "texto_resumo": None,
            "mensagem": "CPF invalido: todos os digitos sao iguais."
        }

    # Busca no banco
    db = SessionLocal()
    try:
        beneficiario = Beneficiario.buscar_por_cpf(db, cpf_limpo)

        if not beneficiario:
            return {
                "encontrado": False,
                "cpf_masked": mask_cpf(cpf_limpo),
                "beneficios": None,
                "texto_resumo": None,
                "mensagem": "Nenhum beneficio encontrado para este CPF nos dados do Portal da Transparencia. "
                           "Isso pode significar que: (1) o cidadao nao recebe Bolsa Familia ou BPC, "
                           "(2) os dados ainda nao foram atualizados, ou "
                           "(3) o CPF informado esta incorreto."
            }

        # Monta resposta
        dados = beneficiario.to_dict()
        resumo = beneficiario.gerar_resumo_texto()

        # Gera mensagem amigavel
        beneficios_ativos = []
        if beneficiario.bf_ativo:
            valor = f"R$ {beneficiario.bf_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            beneficios_ativos.append(f"Bolsa Familia ({valor})")
        if beneficiario.bpc_ativo:
            valor = f"R$ {beneficiario.bpc_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tipo = beneficiario.bpc_tipo or "BPC"
            beneficios_ativos.append(f"BPC {tipo} ({valor})")
        if beneficiario.cadunico_ativo:
            beneficios_ativos.append("CadUnico ativo")

        if beneficios_ativos:
            msg = f"Encontrei! Beneficios ativos: {', '.join(beneficios_ativos)}."
        else:
            msg = "CPF encontrado na base, mas sem beneficios ativos no momento."

        return {
            "encontrado": True,
            "cpf_masked": beneficiario.cpf_masked,
            "nome": beneficiario.nome,
            "uf": beneficiario.uf,
            "beneficios": dados.get("beneficios", {}),
            "texto_resumo": resumo,
            "mensagem": msg,
            "atualizado_em": dados.get("atualizado_em")
        }

    finally:
        db.close()


def verificar_elegibilidade(cpf: str, programa: str) -> dict:
    """Verifica se cidadao e elegivel para um programa especifico.

    Args:
        cpf: CPF do cidadao
        programa: Codigo do programa (BOLSA_FAMILIA, BPC, FARMACIA_POPULAR, etc)

    Returns:
        dict: {
            "elegivel": bool,
            "ja_recebe": bool,
            "motivo": str,
            "proximos_passos": str
        }
    """
    # Primeiro consulta beneficios atuais
    resultado = consultar_beneficio(cpf)

    if not resultado["encontrado"]:
        # Sem dados - pode ser elegivel
        return {
            "elegivel": None,  # Inconclusivo
            "ja_recebe": False,
            "motivo": "Nao temos dados deste CPF na base. Pode ser elegivel.",
            "proximos_passos": _get_proximos_passos(programa)
        }

    beneficios = resultado.get("beneficios", {})

    if programa == "BOLSA_FAMILIA":
        bf = beneficios.get("bolsa_familia", {})
        if bf.get("ativo"):
            return {
                "elegivel": True,
                "ja_recebe": True,
                "motivo": f"Ja recebe Bolsa Familia: R$ {bf.get('valor', 0):.2f}",
                "proximos_passos": "Continuar atendendo as condicionalidades (frequencia escolar, vacinas, etc)."
            }
        else:
            return {
                "elegivel": None,
                "ja_recebe": False,
                "motivo": "Nao recebe Bolsa Familia atualmente.",
                "proximos_passos": _get_proximos_passos(programa)
            }

    elif programa == "BPC":
        bpc = beneficios.get("bpc", {})
        if bpc.get("ativo"):
            return {
                "elegivel": True,
                "ja_recebe": True,
                "motivo": f"Ja recebe BPC ({bpc.get('tipo', '')}): R$ {bpc.get('valor', 0):.2f}",
                "proximos_passos": "Manter inscricao no CadUnico atualizada."
            }
        else:
            return {
                "elegivel": None,
                "ja_recebe": False,
                "motivo": "Nao recebe BPC atualmente.",
                "proximos_passos": _get_proximos_passos(programa)
            }

    elif programa in ["FARMACIA_POPULAR", "DIGNIDADE_MENSTRUAL"]:
        # Farmacia Popular nao depende de cadastro previo
        cadunico = beneficios.get("cadunico", {})
        if cadunico.get("ativo"):
            return {
                "elegivel": True,
                "ja_recebe": False,  # Nao e beneficio continuo
                "motivo": "Tem CadUnico ativo. Pode ter direito a gratuidade total.",
                "proximos_passos": _get_proximos_passos(programa)
            }
        else:
            return {
                "elegivel": True,
                "ja_recebe": False,
                "motivo": "Qualquer brasileiro pode usar o Farmacia Popular (com ou sem CadUnico).",
                "proximos_passos": _get_proximos_passos(programa)
            }

    elif programa == "TSEE":
        # Tarifa Social de Energia
        cadunico = beneficios.get("cadunico", {})
        bf = beneficios.get("bolsa_familia", {})
        bpc = beneficios.get("bpc", {})

        if bf.get("ativo") or bpc.get("ativo"):
            return {
                "elegivel": True,
                "ja_recebe": None,  # Nao sabemos se ja tem TSEE
                "motivo": "Recebe Bolsa Familia ou BPC. Tem direito a Tarifa Social.",
                "proximos_passos": _get_proximos_passos(programa)
            }
        elif cadunico.get("ativo"):
            faixa = cadunico.get("faixa_renda", "").upper()
            if "EXTREMA" in faixa or "POBREZA" in faixa:
                return {
                    "elegivel": True,
                    "ja_recebe": None,
                    "motivo": f"CadUnico na faixa '{faixa}'. Pode ter direito a Tarifa Social.",
                    "proximos_passos": _get_proximos_passos(programa)
                }

        return {
            "elegivel": None,
            "ja_recebe": False,
            "motivo": "Nao foi possivel determinar elegibilidade para Tarifa Social.",
            "proximos_passos": _get_proximos_passos(programa)
        }

    else:
        return {
            "elegivel": None,
            "ja_recebe": None,
            "motivo": f"Programa {programa} nao suportado para verificacao automatica.",
            "proximos_passos": "Procure o CRAS mais proximo para mais informacoes."
        }


def _get_proximos_passos(programa: str) -> str:
    """Retorna orientacao de proximos passos por programa."""
    passos = {
        "BOLSA_FAMILIA": (
            "1. Atualizar ou fazer inscricao no CadUnico\n"
            "2. Levar documentos ao CRAS\n"
            "3. Aguardar avaliacao do governo federal"
        ),
        "BPC": (
            "1. Fazer inscricao no CadUnico (se nao tiver)\n"
            "2. Agendar pericia medica no INSS (para PCD)\n"
            "3. Comprovar renda familiar de ate 1/4 do salario minimo por pessoa"
        ),
        "FARMACIA_POPULAR": (
            "1. Ir a uma farmacia credenciada com receita medica\n"
            "2. Apresentar CPF e receita\n"
            "3. Se tiver CadUnico, pode ter gratuidade total"
        ),
        "DIGNIDADE_MENSTRUAL": (
            "1. Estar inscrita no CadUnico\n"
            "2. Ir a uma farmacia credenciada ou UBS\n"
            "3. Apresentar CPF"
        ),
        "TSEE": (
            "1. Estar inscrito no CadUnico com renda ate meio salario minimo\n"
            "2. OU receber BPC/Bolsa Familia\n"
            "3. Solicitar na concessionaria de energia (conta de luz)"
        ),
        "CADUNICO": (
            "1. Reunir documentos (RG, CPF, comprovante de residencia)\n"
            "2. Ir ao CRAS do seu municipio\n"
            "3. Fazer a inscricao ou atualizacao"
        )
    }
    return passos.get(programa, "Procure o CRAS mais proximo para mais informacoes.")
