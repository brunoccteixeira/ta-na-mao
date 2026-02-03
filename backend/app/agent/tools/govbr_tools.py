"""
Tools de integracao Gov.br para o agente.

Wrappers das funcionalidades do govbr_service.py
expostos como tools para o agente Gemini.
"""

import logging
from typing import Optional

from app.services.govbr_service import (
    auto_preencher_dados,
    gerar_url_login,
    is_govbr_configured,
    NivelConfianca,
    PERMISSOES_POR_NIVEL,
)

logger = logging.getLogger(__name__)


def consultar_govbr(cpf: str) -> dict:
    """Auto-preenche dados do cidadao usando Gov.br (principio once-only).

    Busca dados que o governo ja tem para nao pedir ao cidadao novamente:
    - Nome completo e data de nascimento (CPF Light)
    - Dados do CadUnico (renda, composicao familiar)

    Args:
        cpf: CPF do cidadao (11 digitos, com ou sem formatacao)

    Returns:
        dict com dados auto-preenchidos
    """
    import re
    cpf_limpo = re.sub(r'\D', '', cpf)

    if len(cpf_limpo) != 11:
        return {
            "encontrado": False,
            "erro": "CPF invalido. Precisa ter 11 digitos.",
        }

    logger.info("Consultando Gov.br para auto-preenchimento")

    dados = auto_preencher_dados(cpf_limpo)

    if not dados.get("nome"):
        return {
            "encontrado": False,
            "cpf_valido": True,
            "mensagem": "Nao encontrei seus dados no Gov.br. Voce pode informar manualmente.",
            "govbr_configurado": is_govbr_configured(),
        }

    return {
        "encontrado": True,
        "nome": dados.get("nome", ""),
        "data_nascimento": dados.get("data_nascimento", ""),
        "situacao_cpf": dados.get("situacao_cpf", ""),
        "cadunico": dados.get("cadunico"),
        "fonte": dados.get("fonte", "Gov.br"),
        "preenchido_automaticamente": dados.get("preenchido_automaticamente", False),
    }


def verificar_nivel_govbr(nivel: Optional[str] = None) -> dict:
    """Verifica nivel de confianca do Gov.br e permissoes.

    Explica ao cidadao o que pode fazer com cada nivel
    e como subir de nivel.

    Args:
        nivel: Nivel atual do cidadao: bronze, prata, ouro.
              Se nao informado, retorna todos os niveis.

    Returns:
        dict com permissoes e orientacoes
    """
    if nivel:
        try:
            nivel_enum = NivelConfianca(nivel.lower())
        except ValueError:
            return {
                "erro": f"Nivel '{nivel}' nao reconhecido.",
                "niveis_disponiveis": ["bronze", "prata", "ouro"],
            }

        permissoes = PERMISSOES_POR_NIVEL.get(nivel_enum, [])

        como_subir = ""
        if nivel_enum == NivelConfianca.BRONZE:
            como_subir = (
                "Para subir para PRATA, voce pode:\n"
                "- Validar pelo banco (app do banco que voce usa)\n"
                "- Validar pelo DENATRAN (se tem CNH)\n\n"
                "Para subir para OURO:\n"
                "- Validar biometria no TSE (se ja fez cadastro biometrico na Justica Eleitoral)\n"
                "- Usar certificado digital"
            )
        elif nivel_enum == NivelConfianca.PRATA:
            como_subir = (
                "Para subir para OURO:\n"
                "- Validar biometria no TSE (se ja fez cadastro biometrico)\n"
                "- Usar certificado digital (e-CPF)"
            )
        else:
            como_subir = "Voce ja esta no nivel maximo!"

        return {
            "nivel": nivel_enum.value,
            "titulo": nivel_enum.value.title(),
            "permissoes": permissoes,
            "como_subir": como_subir,
        }

    # Retornar todos os niveis
    return {
        "niveis": [
            {
                "nivel": n.value,
                "titulo": n.value.title(),
                "permissoes": PERMISSOES_POR_NIVEL.get(n, []),
            }
            for n in NivelConfianca
        ],
        "mensagem": "O Gov.br tem 3 niveis. Quanto maior o nivel, mais coisas voce pode fazer online.",
    }


def gerar_login_govbr() -> dict:
    """Gera link para login com Gov.br.

    Returns:
        dict com URL de login ou instrucoes
    """
    if not is_govbr_configured():
        return {
            "configurado": False,
            "mensagem": (
                "O login com Gov.br ainda nao esta disponivel nesta versao. "
                "Por enquanto, voce pode informar seu CPF diretamente que eu consulto seus dados."
            ),
            "alternativa": "Informe seu CPF para consultar beneficios.",
        }

    resultado = gerar_url_login()

    if resultado.get("erro"):
        return resultado

    return {
        "configurado": True,
        "url_login": resultado["url"],
        "instrucoes": (
            "Clique no link para entrar com sua conta Gov.br. "
            "Depois de entrar, seus dados serao preenchidos automaticamente."
        ),
    }
