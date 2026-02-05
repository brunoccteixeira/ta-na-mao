"""
Servico de integracao com SERPRO Consulta CPF.

API paga para validacao de CPF:
- Nome do titular
- Situacao cadastral (regular/irregular)
- Data de nascimento

Contratacao: https://loja.serpro.gov.br/pin
Custo: ~R$ 0,66/consulta (pacote inicial de 1000 consultas)

SEGURANCA: CPF e tokens nunca sao logados diretamente.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Constantes
# =============================================================================

SERPRO_TOKEN_URL = "https://gateway.apiserpro.serpro.gov.br/token"
SERPRO_CPF_URL = "https://gateway.apiserpro.serpro.gov.br/consulta-cpf-df/v1/cpf"

_HTTP_TIMEOUT = 15.0

# Cache do token em memoria (simplificado - usar Redis em producao)
_token_cache: dict[str, Any] = {}


# =============================================================================
# Helpers
# =============================================================================

def _hash_cpf(cpf: str) -> str:
    """Gera hash do CPF para logs seguros."""
    return hashlib.sha256(cpf.encode()).hexdigest()[:12]


def _limpar_cpf(cpf: str) -> str:
    """Remove formatacao do CPF."""
    return "".join(c for c in cpf if c.isdigit())


def _get_serpro_config() -> dict[str, str]:
    """Retorna configuracao do SERPRO."""
    try:
        from app.config import settings
        return {
            "consumer_key": getattr(settings, "SERPRO_CONSUMER_KEY", ""),
            "consumer_secret": getattr(settings, "SERPRO_CONSUMER_SECRET", ""),
            "enabled": getattr(settings, "SERPRO_ENABLED", False),
        }
    except Exception:
        return {
            "consumer_key": "",
            "consumer_secret": "",
            "enabled": False,
        }


def is_serpro_configured() -> bool:
    """Verifica se o SERPRO esta configurado e habilitado."""
    config = _get_serpro_config()
    return bool(
        config["enabled"]
        and config["consumer_key"]
        and config["consumer_secret"]
    )


# =============================================================================
# Autenticacao OAuth2
# =============================================================================

async def _obter_token() -> Optional[str]:
    """Obtem token de acesso via OAuth2 client credentials.

    Implementa cache simples para evitar requisicoes desnecessarias.

    Returns:
        Token de acesso ou None se falhou
    """
    global _token_cache

    # Verificar cache
    if _token_cache.get("token") and _token_cache.get("expires_at"):
        if datetime.now() < _token_cache["expires_at"]:
            logger.debug("Usando token SERPRO em cache")
            return _token_cache["token"]

    config = _get_serpro_config()

    if not config["consumer_key"]:
        logger.warning("SERPRO nao configurado")
        return None

    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            response = await client.post(
                SERPRO_TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(config["consumer_key"], config["consumer_secret"]),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            expires_in = int(data.get("expires_in", 3600))

            # Cache com margem de seguranca
            _token_cache = {
                "token": token,
                "expires_at": datetime.now() + timedelta(seconds=expires_in - 60),
            }

            logger.info("Token SERPRO obtido com sucesso")
            return token

        logger.error(f"Erro ao obter token SERPRO: status={response.status_code}")
        return None

    except Exception as e:
        logger.error(f"Erro ao obter token SERPRO: {e}")
        return None


# =============================================================================
# Consulta CPF
# =============================================================================

async def consultar_cpf(cpf: str) -> dict[str, Any]:
    """Consulta dados de um CPF no SERPRO.

    Args:
        cpf: CPF para consulta

    Returns:
        dict com:
            - valido: bool indicando se CPF existe e esta regular
            - nome: nome do titular
            - nascimento: data de nascimento
            - situacao: situacao cadastral
            - erro: mensagem de erro (se houver)
    """
    cpf_limpo = _limpar_cpf(cpf)
    cpf_hash = _hash_cpf(cpf_limpo)

    if not is_serpro_configured():
        logger.info("SERPRO nao configurado, usando mock")
        return _mock_consultar_cpf(cpf_limpo)

    token = await _obter_token()
    if not token:
        return {
            "valido": False,
            "erro": "Erro de autenticacao com SERPRO",
            "fonte": "SERPRO",
        }

    try:
        logger.info(f"SERPRO: consultando cpf_hash={cpf_hash}")

        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            response = await client.get(
                f"{SERPRO_CPF_URL}/{cpf_limpo}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
            )

        if response.status_code == 200:
            data = response.json()
            logger.info(f"SERPRO: sucesso para cpf_hash={cpf_hash}")

            situacao = data.get("situacao", {})
            situacao_codigo = situacao.get("codigo", "")
            situacao_descricao = situacao.get("descricao", "")

            return {
                "valido": True,
                "cpf": cpf_limpo,
                "nome": data.get("nome", ""),
                "nascimento": data.get("nascimento", ""),
                "situacao": {
                    "codigo": situacao_codigo,
                    "descricao": situacao_descricao,
                    "regular": situacao_codigo == "0",
                },
                "fonte": "SERPRO",
            }

        if response.status_code == 400:
            logger.warning(f"SERPRO: CPF invalido cpf_hash={cpf_hash}")
            return {
                "valido": False,
                "erro": "CPF invalido ou nao encontrado",
                "fonte": "SERPRO",
            }

        if response.status_code == 404:
            logger.warning(f"SERPRO: CPF nao encontrado cpf_hash={cpf_hash}")
            return {
                "valido": False,
                "erro": "CPF nao encontrado na base da Receita Federal",
                "fonte": "SERPRO",
            }

        logger.error(f"SERPRO: erro status={response.status_code}")
        return {
            "valido": False,
            "erro": f"Erro na consulta: status {response.status_code}",
            "fonte": "SERPRO",
        }

    except httpx.TimeoutException:
        logger.error(f"SERPRO: timeout para cpf_hash={cpf_hash}")
        return {
            "valido": False,
            "erro": "Tempo de resposta excedido",
            "fonte": "SERPRO",
        }
    except Exception as e:
        logger.error(f"SERPRO: erro {e}")
        return {
            "valido": False,
            "erro": "Erro de conexao com SERPRO",
            "fonte": "SERPRO",
        }


async def validar_cpf(cpf: str, nome_esperado: Optional[str] = None) -> dict[str, Any]:
    """Valida CPF e opcionalmente verifica se nome confere.

    Args:
        cpf: CPF para validar
        nome_esperado: Nome informado pelo usuario (para comparacao)

    Returns:
        dict com resultado da validacao:
            - valido: bool
            - nome_confere: bool (se nome_esperado foi informado)
            - situacao_regular: bool
            - detalhes: dados completos
    """
    resultado = await consultar_cpf(cpf)

    if not resultado.get("valido"):
        return {
            "valido": False,
            "nome_confere": None,
            "situacao_regular": False,
            "detalhes": resultado,
        }

    situacao_regular = resultado.get("situacao", {}).get("regular", False)

    nome_confere = None
    if nome_esperado:
        nome_cadastrado = resultado.get("nome", "").upper()
        nome_esperado_upper = nome_esperado.upper()

        # Comparacao simples: nome esperado esta contido no cadastrado
        nome_confere = (
            nome_esperado_upper in nome_cadastrado
            or nome_cadastrado in nome_esperado_upper
        )

    return {
        "valido": True,
        "nome_confere": nome_confere,
        "situacao_regular": situacao_regular,
        "detalhes": resultado,
    }


# =============================================================================
# Mock para Desenvolvimento
# =============================================================================

def _mock_consultar_cpf(cpf: str) -> dict[str, Any]:
    """Mock para desenvolvimento quando SERPRO nao esta configurado."""
    cpf_limpo = _limpar_cpf(cpf)

    # CPFs de teste
    mocks = {
        "52998224725": {
            "valido": True,
            "cpf": "52998224725",
            "nome": "MARIA DA SILVA SANTOS",
            "nascimento": "15/03/1985",
            "situacao": {
                "codigo": "0",
                "descricao": "Regular",
                "regular": True,
            },
            "fonte": "Mock (SERPRO nao configurado)",
        },
        "11144477735": {
            "valido": True,
            "cpf": "11144477735",
            "nome": "JOSE CARLOS OLIVEIRA",
            "nascimento": "20/07/1958",
            "situacao": {
                "codigo": "0",
                "descricao": "Regular",
                "regular": True,
            },
            "fonte": "Mock (SERPRO nao configurado)",
        },
        "00000000000": {
            "valido": False,
            "erro": "CPF invalido",
            "fonte": "Mock (SERPRO nao configurado)",
        },
    }

    if cpf_limpo in mocks:
        return mocks[cpf_limpo]

    # CPF desconhecido no mock
    return {
        "valido": False,
        "erro": "CPF nao encontrado no mock. Configure SERPRO para consulta real.",
        "fonte": "Mock (SERPRO nao configurado)",
    }


# =============================================================================
# Utilitarios
# =============================================================================

def validar_formato_cpf(cpf: str) -> bool:
    """Valida formato do CPF (algoritmo local, sem consulta externa).

    Args:
        cpf: CPF para validar

    Returns:
        True se formato eh valido
    """
    cpf_limpo = _limpar_cpf(cpf)

    if len(cpf_limpo) != 11:
        return False

    # Rejeitar CPFs com todos digitos iguais
    if len(set(cpf_limpo)) == 1:
        return False

    # Validar primeiro digito verificador
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto

    if int(cpf_limpo[9]) != dv1:
        return False

    # Validar segundo digito verificador
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto

    if int(cpf_limpo[10]) != dv2:
        return False

    return True


def formatar_cpf(cpf: str) -> str:
    """Formata CPF no padrao XXX.XXX.XXX-XX."""
    cpf_limpo = _limpar_cpf(cpf)
    if len(cpf_limpo) != 11:
        return cpf
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
