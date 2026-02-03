"""
Router de autenticacao Gov.br.

Endpoints para OAuth 2.0 / OpenID Connect com Gov.br SSO.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.govbr_service import (
    gerar_url_login,
    trocar_codigo_por_token,
    obter_dados_usuario,
    is_govbr_configured,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginResponse(BaseModel):
    url: str
    state: str
    configurado: bool


class CallbackResponse(BaseModel):
    sucesso: bool
    nome: Optional[str] = None
    email: Optional[str] = None
    nivel_confianca: Optional[str] = None
    mensagem: str


@router.get("/login", response_model=LoginResponse)
async def iniciar_login():
    """Gera URL para login com Gov.br."""
    if not is_govbr_configured():
        return LoginResponse(
            url="",
            state="",
            configurado=False,
        )

    resultado = gerar_url_login()

    if resultado.get("erro"):
        raise HTTPException(status_code=500, detail=resultado["erro"])

    return LoginResponse(
        url=resultado["url"],
        state=resultado["state"],
        configurado=True,
    )


@router.get("/callback", response_model=CallbackResponse)
async def callback_govbr(
    code: str = Query(..., description="Codigo de autorizacao"),
    state: str = Query(..., description="Token anti-CSRF"),
):
    """Callback do Gov.br apos autenticacao.

    Recebe o codigo de autorizacao e troca por token de acesso.
    """
    # TODO: Validar state contra sessao do usuario (anti-CSRF)

    # Por enquanto, code_verifier fixo para simplificar
    # Em producao, recuperar do Redis pela sessao
    token_data = trocar_codigo_por_token(code, code_verifier="")

    if not token_data:
        return CallbackResponse(
            sucesso=False,
            mensagem="Nao foi possivel completar o login. Tente novamente.",
        )

    # Obter dados do usuario
    user_data = obter_dados_usuario(token_data["access_token"])

    if not user_data:
        return CallbackResponse(
            sucesso=False,
            mensagem="Login feito mas nao consegui obter seus dados. Tente novamente.",
        )

    return CallbackResponse(
        sucesso=True,
        nome=user_data.get("nome"),
        email=user_data.get("email"),
        nivel_confianca=user_data.get("nivel_confianca"),
        mensagem=f"Bem-vindo(a), {user_data.get('nome', '')}!",
    )


@router.get("/status")
async def status_govbr():
    """Verifica se o Gov.br esta configurado."""
    return {
        "configurado": is_govbr_configured(),
        "mensagem": (
            "Gov.br configurado e pronto para uso."
            if is_govbr_configured()
            else "Gov.br nao configurado. Configure as variaveis GOVBR_CLIENT_ID e GOVBR_CLIENT_SECRET."
        ),
    }
