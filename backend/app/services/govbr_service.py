"""
Servico de integracao com Gov.br.

Implementa:
- OAuth 2.0 / OpenID Connect com Gov.br SSO (Login unico - disponivel para qualquer app)
- Integracao com Portal da Transparencia (dados publicos de beneficios)
- Integracao com SERPRO (validacao de CPF - pago)

IMPORTANTE: Conecta Gov.br (CadUnico tempo real, CPF Light) NAO esta disponivel
para startups/empresas privadas. Acesso restrito a orgaos da administracao publica.
Para acessar, necessario parceria B2G (convenio com prefeitura ou MDS).

SEGURANCA: Tokens nunca sao logados. CPF eh hasheado para logs.
"""

import hashlib
import logging
import secrets
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


def _limpar_cpf(cpf: str) -> str:
    """Remove formatacao do CPF."""
    return "".join(c for c in cpf if c.isdigit())


def _get_govbr_config() -> Dict[str, str]:
    """Retorna configuracao do Gov.br a partir do settings."""
    try:
        from app.config import settings
        return {
            "client_id": getattr(settings, "GOVBR_CLIENT_ID", ""),
            "client_secret": getattr(settings, "GOVBR_CLIENT_SECRET", ""),
            "redirect_uri": getattr(settings, "GOVBR_REDIRECT_URI", ""),
        }
    except Exception:
        return {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "",
        }


def is_govbr_configured() -> bool:
    """Verifica se o Gov.br esta configurado."""
    config = _get_govbr_config()
    return bool(config["client_id"] and config["client_secret"])


# =============================================================================
# OAuth 2.0 Flow (Login Gov.br - disponivel para qualquer app)
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
# Auto-preenchimento (Principio "Once-Only") - Nova Arquitetura
# =============================================================================

async def auto_preencher_dados(cpf: str) -> Dict[str, Any]:
    """Auto-preenche dados do cidadao usando APIs disponiveis.

    Principio "Nao peca ao cidadao dados que o governo ja tem"
    (Lei 13.726/2018).

    ARQUITETURA:
    1. SERPRO (se habilitado): valida CPF, nome, data nascimento
    2. Portal da Transparencia (gratuito): dados de beneficios
    3. Auto-declaracao: renda e composicao familiar (CadUnico nao disponivel)

    Args:
        cpf: CPF do cidadao

    Returns:
        dict com dados auto-preenchidos disponiveis
    """
    from app.services import serpro_service, transparencia_service

    cpf_limpo = _limpar_cpf(cpf)
    cpf_hash = _hash_cpf(cpf_limpo)
    logger.info(f"Auto-preenchendo dados para cpf_hash={cpf_hash}")

    dados: Dict[str, Any] = {
        "cpf": cpf_limpo,
        "preenchido_automaticamente": True,
        "fontes": [],
    }

    # 1. Validacao do CPF via SERPRO (se habilitado)
    if serpro_service.is_serpro_configured():
        serpro_data = await serpro_service.consultar_cpf(cpf_limpo)
        if serpro_data.get("valido"):
            dados["nome"] = serpro_data.get("nome", "")
            dados["data_nascimento"] = serpro_data.get("nascimento", "")
            dados["situacao_cpf"] = serpro_data.get("situacao", {})
            dados["fontes"].append("SERPRO")
            logger.info(f"Dados SERPRO obtidos para cpf_hash={cpf_hash}")
    else:
        # Sem SERPRO, nao conseguimos validar automaticamente
        dados["serpro_nao_configurado"] = True
        dados["fontes"].append("Auto-declaracao (SERPRO nao habilitado)")

    # 2. Beneficios via Portal da Transparencia (gratuito)
    beneficios = await transparencia_service.consultar_beneficios_ou_mock(cpf_limpo)
    if beneficios.get("cpf_consultado"):
        dados["beneficios"] = {
            "eh_beneficiario": beneficios.get("beneficiario_algum_programa", False),
            "programas": beneficios.get("beneficios_ativos", []),
            "total_mensal": beneficios.get("total_mensal_estimado", 0),
        }
        if "Mock" not in beneficios.get("fonte", ""):
            dados["fontes"].append("Portal da Transparencia")
        else:
            dados["fontes"].append("Mock (Portal da Transparencia nao configurado)")

    # 3. CadUnico: NAO DISPONIVEL para startups
    # Adiciona aviso e sugere auto-declaracao
    dados["cadunico"] = {
        "disponivel": False,
        "motivo": "Conecta Gov.br nao disponivel para aplicacoes privadas",
        "alternativa": "Auto-declaracao do cidadao ou parceria B2G",
    }

    return dados


def auto_preencher_dados_sync(cpf: str) -> Dict[str, Any]:
    """Versao sincrona do auto_preencher_dados para compatibilidade.

    Usa mock quando em modo sincrono.
    """
    return _mock_auto_preencher(cpf)


def _mock_auto_preencher(cpf: str) -> Dict[str, Any]:
    """Mock para desenvolvimento quando APIs nao estao configuradas."""
    cpf_limpo = _limpar_cpf(cpf)

    # CPFs de teste
    mocks = {
        "52998224725": {
            "cpf": "52998224725",
            "nome": "MARIA DA SILVA SANTOS",
            "data_nascimento": "15/03/1985",
            "situacao_cpf": {"codigo": "0", "descricao": "Regular", "regular": True},
            "beneficios": {
                "eh_beneficiario": True,
                "programas": [
                    {"programa": "Bolsa Familia / Auxilio Brasil", "valor_mensal": 600.0},
                    {"programa": "Auxilio Gas", "valor_mensal": 104.0},
                ],
                "total_mensal": 704.0,
            },
            "cadunico": {
                "disponivel": False,
                "motivo": "Conecta Gov.br nao disponivel para aplicacoes privadas",
                "alternativa": "Auto-declaracao do cidadao ou parceria B2G",
                # Dados simulados para UX (viriam de auto-declaracao)
                "auto_declaracao": {
                    "renda_per_capita": 266.67,
                    "composicao_familiar": 3,
                    "municipio": "SAO PAULO",
                    "uf": "SP",
                },
            },
            "preenchido_automaticamente": True,
            "fontes": ["Mock (APIs nao configuradas)"],
        },
        "11144477735": {
            "cpf": "11144477735",
            "nome": "JOSE CARLOS OLIVEIRA",
            "data_nascimento": "20/07/1958",
            "situacao_cpf": {"codigo": "0", "descricao": "Regular", "regular": True},
            "beneficios": {
                "eh_beneficiario": True,
                "programas": [
                    {"programa": "BPC - Beneficio de Prestacao Continuada", "valor_mensal": 1412.0},
                ],
                "total_mensal": 1412.0,
            },
            "cadunico": {
                "disponivel": False,
                "motivo": "Conecta Gov.br nao disponivel para aplicacoes privadas",
                "alternativa": "Auto-declaracao do cidadao ou parceria B2G",
                "auto_declaracao": {
                    "renda_per_capita": 0,
                    "composicao_familiar": 1,
                    "municipio": "RECIFE",
                    "uf": "PE",
                },
            },
            "preenchido_automaticamente": True,
            "fontes": ["Mock (APIs nao configuradas)"],
        },
    }

    if cpf_limpo in mocks:
        return mocks[cpf_limpo]

    return {
        "cpf": cpf_limpo,
        "preenchido_automaticamente": False,
        "fontes": ["Mock (APIs nao configuradas)"],
        "mensagem": "CPF nao encontrado no mock. Configure SERPRO e/ou Portal da Transparencia.",
        "cadunico": {
            "disponivel": False,
            "motivo": "Conecta Gov.br nao disponivel para aplicacoes privadas",
            "alternativa": "Auto-declaracao do cidadao ou parceria B2G",
        },
    }


# =============================================================================
# Funcoes de Compatibilidade (deprecated)
# =============================================================================

def consultar_conecta_api(
    endpoint: str,
    cpf: str,
    access_token: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """DEPRECATED: Conecta Gov.br NAO esta disponivel para startups.

    Esta funcao eh mantida apenas para compatibilidade.
    Use transparencia_service ou serpro_service.

    Returns:
        None sempre - API nao disponivel
    """
    logger.warning(
        "consultar_conecta_api() chamada, mas Conecta Gov.br "
        "NAO esta disponivel para startups. "
        "Use transparencia_service ou serpro_service."
    )
    return None
