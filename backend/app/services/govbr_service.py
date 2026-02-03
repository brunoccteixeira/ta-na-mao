"""
Servico de integracao com Gov.br.

Implementa:
- OAuth 2.0 / OpenID Connect com Gov.br SSO
- Cliente para Conecta Gov.br APIs
- Gerenciamento de tokens e niveis de confianca

SEGURANCA: Tokens nunca sao logados. CPF eh hasheado para logs.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Constantes
# =============================================================================

GOVBR_AUTH_URL = "https://sso.acesso.gov.br/authorize"
GOVBR_TOKEN_URL = "https://sso.acesso.gov.br/token"
GOVBR_USERINFO_URL = "https://sso.acesso.gov.br/userinfo"
GOVBR_JWKS_URL = "https://sso.acesso.gov.br/jwk"

_HTTP_TIMEOUT = 15.0


class NivelConfianca(str, Enum):
    """Niveis de confianca do Gov.br."""
    BRONZE = "bronze"   # Cadastro basico (CPF + validacao facial)
    PRATA = "prata"     # Biometria bancaria ou DENATRAN
    OURO = "ouro"       # Biometria TSE ou certificado digital


# Permissoes por nivel
PERMISSOES_POR_NIVEL = {
    NivelConfianca.BRONZE: [
        "Consultar beneficios disponiveis",
        "Ver checklist de documentos",
        "Buscar CRAS e farmacias",
        "Ver informacoes gerais",
    ],
    NivelConfianca.PRATA: [
        "Tudo do nivel Bronze, mais:",
        "Consultar CadUnico",
        "Gerar cartas e requerimentos",
        "Solicitar medicamentos",
    ],
    NivelConfianca.OURO: [
        "Tudo do nivel Prata, mais:",
        "Assinar documentos digitalmente",
        "Atualizar cadastro",
        "Realizar portabilidade de beneficios",
    ],
}


# =============================================================================
# Helpers
# =============================================================================

def _hash_cpf(cpf: str) -> str:
    """Gera hash do CPF para logs seguros."""
    return hashlib.sha256(cpf.encode()).hexdigest()[:12]


def _get_govbr_config() -> Dict[str, str]:
    """Retorna configuracao do Gov.br a partir do settings."""
    try:
        from app.config import settings
        return {
            "client_id": getattr(settings, "GOVBR_CLIENT_ID", ""),
            "client_secret": getattr(settings, "GOVBR_CLIENT_SECRET", ""),
            "redirect_uri": getattr(settings, "GOVBR_REDIRECT_URI", ""),
            "conecta_url": getattr(settings, "CONECTA_GOVBR_URL", ""),
            "conecta_client_id": getattr(settings, "CONECTA_GOVBR_CLIENT_ID", ""),
            "conecta_client_secret": getattr(settings, "CONECTA_GOVBR_CLIENT_SECRET", ""),
        }
    except Exception:
        return {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "",
            "conecta_url": "",
            "conecta_client_id": "",
            "conecta_client_secret": "",
        }


def is_govbr_configured() -> bool:
    """Verifica se o Gov.br esta configurado."""
    config = _get_govbr_config()
    return bool(config["client_id"] and config["client_secret"])


# =============================================================================
# OAuth 2.0 Flow
# =============================================================================

def gerar_url_login(state: Optional[str] = None) -> Dict[str, str]:
    """Gera URL para iniciar login com Gov.br.

    Args:
        state: Token anti-CSRF. Se nao fornecido, gera automaticamente.

    Returns:
        dict com url de login e state para validacao
    """
    config = _get_govbr_config()

    if not config["client_id"]:
        return {
            "erro": "Gov.br nao configurado. Configure GOVBR_CLIENT_ID e GOVBR_CLIENT_SECRET.",
            "url": "",
            "state": "",
        }

    if not state:
        state = secrets.token_urlsafe(32)

    # PKCE: code_verifier e code_challenge
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = hashlib.sha256(code_verifier.encode()).hexdigest()

    params = {
        "response_type": "code",
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "scope": "openid profile email govbr_confiabilidades",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "nonce": secrets.token_urlsafe(16),
    }

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{GOVBR_AUTH_URL}?{query}"

    logger.info("URL de login Gov.br gerada")

    return {
        "url": url,
        "state": state,
        "code_verifier": code_verifier,
    }


def trocar_codigo_por_token(
    code: str,
    code_verifier: str,
) -> Optional[Dict[str, Any]]:
    """Troca codigo de autorizacao por access token.

    Args:
        code: Codigo de autorizacao recebido no callback
        code_verifier: PKCE code verifier usado na geracao da URL

    Returns:
        dict com access_token, id_token, etc. ou None se falhou
    """
    config = _get_govbr_config()

    if not config["client_id"]:
        logger.error("Gov.br nao configurado")
        return None

    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
            response = client.post(
                GOVBR_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": config["redirect_uri"],
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "code_verifier": code_verifier,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code == 200:
            data = response.json()
            logger.info("Token Gov.br obtido com sucesso")
            # NUNCA logar o token
            return {
                "access_token": data.get("access_token", ""),
                "id_token": data.get("id_token", ""),
                "token_type": data.get("token_type", "Bearer"),
                "expires_in": data.get("expires_in", 3600),
                "scope": data.get("scope", ""),
            }

        logger.error(f"Erro ao obter token Gov.br: status={response.status_code}")
        return None

    except Exception as e:
        logger.error(f"Erro ao trocar codigo por token: {e}")
        return None


def obter_dados_usuario(access_token: str) -> Optional[Dict[str, Any]]:
    """Obtem dados do usuario autenticado via Gov.br.

    Args:
        access_token: Token de acesso obtido no login

    Returns:
        dict com CPF, nome, email, nivel de confianca, etc.
    """
    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
            response = client.get(
                GOVBR_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if response.status_code == 200:
            data = response.json()
            cpf = data.get("sub", "")
            cpf_hash = _hash_cpf(cpf) if cpf else "unknown"
            logger.info(f"Dados usuario Gov.br obtidos: hash={cpf_hash}")

            # Determinar nivel de confianca
            confiabilidades = data.get("govbr_confiabilidades", [])
            nivel = _determinar_nivel(confiabilidades)

            return {
                "cpf": cpf,
                "nome": data.get("name", ""),
                "email": data.get("email", ""),
                "email_verificado": data.get("email_verified", False),
                "telefone": data.get("phone_number", ""),
                "data_nascimento": data.get("birthdate", ""),
                "nivel_confianca": nivel.value,
                "nivel_descricao": _descrever_nivel(nivel),
                "permissoes": PERMISSOES_POR_NIVEL.get(nivel, []),
            }

        logger.error(f"Erro ao obter dados usuario: status={response.status_code}")
        return None

    except Exception as e:
        logger.error(f"Erro ao obter dados do usuario: {e}")
        return None


def _determinar_nivel(confiabilidades: list) -> NivelConfianca:
    """Determina nivel de confianca a partir das confiabilidades."""
    confiabilidades_set = set(confiabilidades)

    # Ouro: biometria TSE ou certificado digital
    if confiabilidades_set & {"801", "802"}:  # TSE biometric, digital certificate
        return NivelConfianca.OURO

    # Prata: validacao bancaria ou DENATRAN
    if confiabilidades_set & {"501", "502", "503"}:  # Bank, DENATRAN
        return NivelConfianca.PRATA

    return NivelConfianca.BRONZE


def _descrever_nivel(nivel: NivelConfianca) -> str:
    """Retorna descricao simples do nivel."""
    descricoes = {
        NivelConfianca.BRONZE: "Conta basica - acesso limitado",
        NivelConfianca.PRATA: "Conta verificada - acesso intermediario",
        NivelConfianca.OURO: "Conta completa - acesso total",
    }
    return descricoes.get(nivel, "Nivel desconhecido")


# =============================================================================
# Conecta Gov.br APIs
# =============================================================================

def consultar_conecta_api(
    endpoint: str,
    cpf: str,
    access_token: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Consulta uma API do Conecta Gov.br.

    Args:
        endpoint: Endpoint da API (ex: /api-cpf-light/v2/)
        cpf: CPF para consulta
        access_token: Token de acesso do cidadao (para APIs que exigem)

    Returns:
        dict com dados da API ou None se falhou
    """
    config = _get_govbr_config()
    cpf_hash = _hash_cpf(cpf)

    if not config["conecta_url"]:
        logger.warning("Conecta Gov.br nao configurado")
        return None

    url = f"{config['conecta_url'].rstrip('/')}{endpoint}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Autenticacao: token do cidadao ou credenciais da aplicacao
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    else:
        # Client credentials para APIs que nao exigem token do cidadao
        token = _obter_token_aplicacao()
        if token:
            headers["Authorization"] = f"Bearer {token}"

    try:
        logger.info(f"Conecta API: endpoint={endpoint}, cpf_hash={cpf_hash}")

        with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
            response = client.get(
                url,
                params={"cpf": cpf},
                headers=headers,
            )

        if response.status_code == 200:
            logger.info(f"Conecta API: sucesso para cpf_hash={cpf_hash}")
            return response.json()

        logger.warning(
            f"Conecta API: status={response.status_code} "
            f"endpoint={endpoint} cpf_hash={cpf_hash}"
        )
        return None

    except Exception as e:
        logger.error(f"Conecta API: erro {e}")
        return None


def _obter_token_aplicacao() -> Optional[str]:
    """Obtem token de aplicacao (client credentials) para Conecta Gov.br."""
    config = _get_govbr_config()

    if not config["conecta_client_id"]:
        return None

    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
            response = client.post(
                GOVBR_TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": config["conecta_client_id"],
                    "client_secret": config["conecta_client_secret"],
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code == 200:
            return response.json().get("access_token")

        return None

    except Exception as e:
        logger.error(f"Erro ao obter token de aplicacao: {e}")
        return None


# =============================================================================
# Auto-preenchimento (Principio "Once-Only")
# =============================================================================

def auto_preencher_dados(
    cpf: str,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Auto-preenche dados do cidadao usando APIs do Gov.br.

    Principio "Nao peca ao cidadao dados que o governo ja tem"
    (Lei 13.726/2018).

    Args:
        cpf: CPF do cidadao
        access_token: Token de acesso Gov.br (para dados mais completos)

    Returns:
        dict com dados auto-preenchidos disponiveis
    """
    cpf_hash = _hash_cpf(cpf)
    logger.info(f"Auto-preenchendo dados para cpf_hash={cpf_hash}")

    dados = {
        "cpf": cpf,
        "preenchido_automaticamente": True,
        "fonte": "Gov.br Conecta",
    }

    if not is_govbr_configured():
        # Retorna mock para desenvolvimento
        return _mock_auto_preencher(cpf)

    # CPF Light: nome e data de nascimento
    cpf_data = consultar_conecta_api("/api-cpf-light/v2/", cpf, access_token)
    if cpf_data:
        dados["nome"] = cpf_data.get("nome", cpf_data.get("nomePessoaFisica", ""))
        dados["data_nascimento"] = cpf_data.get(
            "dataNascimento",
            cpf_data.get("data_nascimento", "")
        )
        dados["situacao_cpf"] = cpf_data.get(
            "situacaoCadastral",
            cpf_data.get("situacao", "")
        )

    # CadUnico: renda, composicao familiar
    cad_data = consultar_conecta_api("/api-cadunico-servicos/v1/", cpf, access_token)
    if cad_data:
        dados["cadunico"] = {
            "ativo": True,
            "renda_per_capita": cad_data.get("rendaPerCapita", 0),
            "composicao_familiar": cad_data.get("quantidadeMembros", 0),
            "municipio": cad_data.get("municipio", ""),
            "uf": cad_data.get("uf", ""),
        }

    return dados


def _mock_auto_preencher(cpf: str) -> Dict[str, Any]:
    """Mock para desenvolvimento quando Gov.br nao esta configurado."""
    # CPFs de teste
    mocks = {
        "52998224725": {
            "cpf": "52998224725",
            "nome": "MARIA DA SILVA SANTOS",
            "data_nascimento": "15/03/1985",
            "situacao_cpf": "REGULAR",
            "cadunico": {
                "ativo": True,
                "renda_per_capita": 266.67,
                "composicao_familiar": 3,
                "municipio": "SAO PAULO",
                "uf": "SP",
            },
            "preenchido_automaticamente": True,
            "fonte": "Mock (Gov.br nao configurado)",
        },
        "11144477735": {
            "cpf": "11144477735",
            "nome": "JOSE CARLOS OLIVEIRA",
            "data_nascimento": "20/07/1958",
            "situacao_cpf": "REGULAR",
            "cadunico": {
                "ativo": True,
                "renda_per_capita": 0,
                "composicao_familiar": 1,
                "municipio": "RECIFE",
                "uf": "PE",
            },
            "preenchido_automaticamente": True,
            "fonte": "Mock (Gov.br nao configurado)",
        },
    }

    if cpf in mocks:
        return mocks[cpf]

    return {
        "cpf": cpf,
        "preenchido_automaticamente": False,
        "fonte": "Mock (Gov.br nao configurado)",
        "mensagem": "CPF nao encontrado no mock. Configure Gov.br para consulta real.",
    }
