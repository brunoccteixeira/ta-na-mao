"""
Tools de integracao Gov.br para o agente.

Nova arquitetura:
- Portal da Transparencia (gratuito): dados publicos de beneficios
- SERPRO (pago, opcional): validacao de CPF
- Login Gov.br (gratuito): autenticacao SSO

NOTA: Conecta Gov.br (CadUnico tempo real) NAO esta disponivel para startups.
"""

import logging
import re
from typing import Optional

from app.services.govbr_service import (
    gerar_url_login,
    is_govbr_configured,
    NivelConfianca,
    PERMISSOES_POR_NIVEL,
)

logger = logging.getLogger(__name__)


async def consultar_govbr(cpf: str) -> dict:
    """Auto-preenche dados do cidadao usando APIs disponiveis.

    Busca dados de forma inteligente usando as APIs que temos acesso:
    1. SERPRO (se habilitado): nome, nascimento, situacao CPF
    2. Portal da Transparencia: beneficios ativos
    3. Auto-declaracao: renda e composicao familiar (CadUnico nao disponivel)

    Args:
        cpf: CPF do cidadao (11 digitos, com ou sem formatacao)

    Returns:
        dict com dados auto-preenchidos
    """
    from app.services import serpro_service, transparencia_service

    cpf_limpo = re.sub(r'\D', '', cpf)

    if len(cpf_limpo) != 11:
        return {
            "encontrado": False,
            "erro": "CPF invalido. Precisa ter 11 digitos.",
        }

    # Validar formato do CPF localmente
    if not serpro_service.validar_formato_cpf(cpf_limpo):
        return {
            "encontrado": False,
            "erro": "CPF invalido. Verifique os digitos.",
        }

    logger.info("Consultando dados do cidadao via APIs disponiveis")

    resultado = {
        "encontrado": True,
        "cpf_valido": True,
        "fontes": [],
    }

    # 1. SERPRO (se habilitado) - validacao de CPF
    if serpro_service.is_serpro_configured():
        serpro_data = await serpro_service.consultar_cpf(cpf_limpo)
        if serpro_data.get("valido"):
            resultado["nome"] = serpro_data.get("nome", "")
            resultado["data_nascimento"] = serpro_data.get("nascimento", "")
            resultado["situacao_cpf"] = serpro_data.get("situacao", {}).get("descricao", "")
            resultado["cpf_regular"] = serpro_data.get("situacao", {}).get("regular", False)
            resultado["fontes"].append("SERPRO (validacao oficial)")
        else:
            # CPF invalido no SERPRO
            return {
                "encontrado": False,
                "cpf_valido": False,
                "erro": serpro_data.get("erro", "CPF nao encontrado"),
                "fonte": "SERPRO",
            }
    else:
        resultado["serpro_nao_habilitado"] = True
        resultado["fontes"].append("SERPRO nao habilitado (validacao nao realizada)")

    # 2. Portal da Transparencia - beneficios
    beneficios = await transparencia_service.consultar_beneficios_ou_mock(cpf_limpo)

    if beneficios.get("beneficiario_algum_programa"):
        resultado["eh_beneficiario"] = True
        resultado["beneficios"] = beneficios.get("beneficios_ativos", [])
        resultado["total_mensal"] = beneficios.get("total_mensal_estimado", 0)
        resultado["mensagem_beneficios"] = (
            f"Voce recebe {len(beneficios.get('beneficios_ativos', []))} "
            f"beneficio(s) totalizando R$ {beneficios.get('total_mensal_estimado', 0):.2f}/mes."
        )
    else:
        resultado["eh_beneficiario"] = False
        resultado["beneficios"] = []
        resultado["total_mensal"] = 0

    if "Mock" not in beneficios.get("fonte", ""):
        resultado["fontes"].append("Portal da Transparencia")
    else:
        resultado["fontes"].append("Mock (Portal da Transparencia nao configurado)")

    # 3. CadUnico - NAO DISPONIVEL
    resultado["cadunico"] = {
        "disponivel": False,
        "mensagem": (
            "Dados do CadUnico (renda, familia) nao estao disponiveis para consulta automatica. "
            "Voce pode informar esses dados manualmente."
        ),
    }

    # Montar mensagem final
    if not resultado.get("nome"):
        resultado["mensagem"] = (
            "Encontrei seus dados de beneficios, mas nao consegui validar seu nome. "
            "Pode me informar seu nome completo?"
        )
    else:
        resultado["mensagem"] = f"Ola, {resultado['nome'].split()[0].title()}! Encontrei seus dados."

    return resultado


def consultar_govbr_sync(cpf: str) -> dict:
    """Versao sincrona do consultar_govbr para compatibilidade.

    Usa dados de mock quando chamado de forma sincrona.
    """
    from app.services.govbr_service import auto_preencher_dados_sync

    cpf_limpo = re.sub(r'\D', '', cpf)

    if len(cpf_limpo) != 11:
        return {
            "encontrado": False,
            "erro": "CPF invalido. Precisa ter 11 digitos.",
        }

    logger.info("Consultando Gov.br (modo sincrono/mock)")

    dados = auto_preencher_dados_sync(cpf_limpo)

    if not dados.get("nome"):
        return {
            "encontrado": False,
            "cpf_valido": True,
            "mensagem": "Nao encontrei seus dados. Voce pode informar manualmente.",
        }

    return {
        "encontrado": True,
        "nome": dados.get("nome", ""),
        "data_nascimento": dados.get("data_nascimento", ""),
        "situacao_cpf": dados.get("situacao_cpf", {}),
        "beneficios": dados.get("beneficios", {}),
        "cadunico": dados.get("cadunico"),
        "fontes": dados.get("fontes", []),
    }


async def consultar_beneficios(cpf: str) -> dict:
    """Consulta beneficios ativos de um CPF via Portal da Transparencia.

    Esta eh uma funcao especifica para consultar beneficios quando
    o cidadao ja esta em atendimento e queremos atualizar os dados.

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com dados dos beneficios
    """
    from app.services import transparencia_service

    cpf_limpo = re.sub(r'\D', '', cpf)

    if len(cpf_limpo) != 11:
        return {
            "erro": "CPF invalido",
        }

    beneficios = await transparencia_service.consultar_beneficios_ou_mock(cpf_limpo)

    if beneficios.get("beneficiario_algum_programa"):
        return {
            "encontrou": True,
            "eh_beneficiario": True,
            "programas": beneficios.get("beneficios_ativos", []),
            "total_mensal": beneficios.get("total_mensal_estimado", 0),
            "detalhes": beneficios.get("detalhes", {}),
            "fonte": beneficios.get("fonte", "Portal da Transparencia"),
        }

    return {
        "encontrou": True,
        "eh_beneficiario": False,
        "mensagem": "CPF nao consta como beneficiario de programas sociais federais.",
        "fonte": beneficios.get("fonte", "Portal da Transparencia"),
        "aviso": (
            "Isso nao significa que voce nao tem direito! "
            "Posso ajudar a verificar sua elegibilidade."
        ),
    }


async def validar_cpf(cpf: str, nome: Optional[str] = None) -> dict:
    """Valida um CPF usando SERPRO (se habilitado).

    Args:
        cpf: CPF para validar
        nome: Nome informado pelo cidadao (para conferir)

    Returns:
        dict com resultado da validacao
    """
    from app.services import serpro_service

    cpf_limpo = re.sub(r'\D', '', cpf)

    if len(cpf_limpo) != 11:
        return {
            "valido": False,
            "erro": "CPF deve ter 11 digitos",
        }

    # Validacao local primeiro
    if not serpro_service.validar_formato_cpf(cpf_limpo):
        return {
            "valido": False,
            "erro": "CPF invalido (digitos verificadores nao conferem)",
        }

    # SERPRO se habilitado
    if serpro_service.is_serpro_configured():
        resultado = await serpro_service.validar_cpf(cpf_limpo, nome)

        if resultado.get("valido"):
            resposta = {
                "valido": True,
                "situacao_regular": resultado.get("situacao_regular", False),
                "fonte": "SERPRO (Receita Federal)",
            }

            if nome and resultado.get("nome_confere") is not None:
                resposta["nome_confere"] = resultado["nome_confere"]
                if not resultado["nome_confere"]:
                    resposta["aviso"] = (
                        "O nome informado nao confere com o cadastro. "
                        "Verifique se digitou corretamente."
                    )

            return resposta

        return {
            "valido": False,
            "erro": resultado.get("detalhes", {}).get("erro", "CPF nao encontrado"),
            "fonte": "SERPRO",
        }

    # Sem SERPRO, apenas validacao local
    return {
        "valido": True,
        "validacao_local": True,
        "aviso": "Validacao apenas do formato. SERPRO nao habilitado para validacao completa.",
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

    O Login Gov.br (SSO) ESTA disponivel para qualquer aplicacao,
    diferente do Conecta Gov.br que eh restrito.

    Returns:
        dict com URL de login ou instrucoes
    """
    if not is_govbr_configured():
        return {
            "configurado": False,
            "mensagem": (
                "O login com Gov.br ainda nao esta disponivel nesta versao. "
                "Por enquanto, voce pode informar seu CPF que eu consulto seus dados."
            ),
            "alternativa": "Informe seu CPF para consultar beneficios.",
            "nota": (
                "O Login Gov.br esta em processo de integracao. "
                "Diferente de outras APIs do governo, o login eh "
                "disponivel para qualquer aplicacao."
            ),
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
        "niveis": (
            "Ao entrar, saberei seu nivel de confianca no Gov.br "
            "(Bronze, Prata ou Ouro) para oferecer os servicos adequados."
        ),
    }


def explicar_apis_disponiveis() -> dict:
    """Explica quais APIs estao disponiveis e quais nao estao.

    Util para o agente entender os limites do sistema.

    Returns:
        dict com status das APIs
    """
    from app.services import serpro_service, transparencia_service

    return {
        "apis_disponiveis": {
            "portal_transparencia": {
                "configurado": transparencia_service.is_transparencia_configured(),
                "descricao": "Dados publicos de beneficios (Bolsa Familia, BPC, Auxilio Gas)",
                "custo": "Gratuito",
            },
            "serpro_cpf": {
                "configurado": serpro_service.is_serpro_configured(),
                "descricao": "Validacao de CPF (nome, nascimento, situacao)",
                "custo": "~R$ 0,66/consulta",
            },
            "login_govbr": {
                "configurado": is_govbr_configured(),
                "descricao": "Autenticacao SSO com Gov.br",
                "custo": "Gratuito",
            },
        },
        "apis_nao_disponiveis": {
            "conecta_govbr": {
                "descricao": "CadUnico em tempo real, CPF Light",
                "motivo": "Restrito a orgaos da administracao publica federal",
                "alternativa": "Parceria B2G (convenio com prefeitura) ou auto-declaracao",
            },
            "dataprev_nis": {
                "descricao": "Consulta NIS Dataprev",
                "motivo": "Acesso restrito",
                "alternativa": "Auto-declaracao do cidadao",
            },
        },
        "recomendacao": (
            "Para dados de renda e composicao familiar, use auto-declaracao "
            "do cidadao. Validamos o CPF e os beneficios que ele recebe."
        ),
    }
