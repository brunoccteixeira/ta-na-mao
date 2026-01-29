"""Router para Carta de Encaminhamento.

Endpoints:
- POST /api/v1/carta/gerar - Gera nova carta
- GET /api/v1/carta/{codigo} - Visualiza/valida carta
- GET /api/v1/carta/{codigo}/pdf - Download do PDF
- POST /api/v1/carta/{codigo}/validar - Marca carta como utilizada
"""

import hashlib
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import base64

from app.database import get_db
from app.models.carta_encaminhamento import CartaEncaminhamento, StatusCarta
from app.agent.tools.gerar_carta_encaminhamento import (
    gerar_carta_completa,
    mascarar_cpf,
)

router = APIRouter(prefix="/api/v1/carta", tags=["carta"])


# =============================================================================
# Schemas Pydantic
# =============================================================================

class DadosCidadaoInput(BaseModel):
    """Dados do cidadão para gerar carta."""
    nome: str = Field(..., min_length=2, max_length=200)
    cpf: Optional[str] = Field(None, min_length=11, max_length=14)
    municipio: str = Field(..., min_length=2, max_length=100)
    uf: str = Field(..., min_length=2, max_length=2)
    renda_familiar: float = Field(..., ge=0)
    pessoas_na_casa: int = Field(..., ge=1, le=20)
    tem_filhos_menores: bool = False
    tem_idoso_65_mais: bool = False
    tem_pcd: bool = False
    tem_gestante: bool = False


class BeneficioInput(BaseModel):
    """Benefício solicitado."""
    codigo: str
    nome: str
    valor_estimado: Optional[float] = None


class DocumentoInput(BaseModel):
    """Documento do checklist."""
    nome: str
    apresentado: bool = False


class CrasInput(BaseModel):
    """Dados do CRAS sugerido."""
    nome: str
    endereco: str
    telefone: Optional[str] = None


class GerarCartaRequest(BaseModel):
    """Request para gerar carta de encaminhamento."""
    cidadao: DadosCidadaoInput
    beneficios: List[BeneficioInput]
    documentos: List[DocumentoInput]
    cras: Optional[CrasInput] = None


class CartaResponse(BaseModel):
    """Response com dados da carta gerada."""
    codigo_validacao: str
    link_validacao: str
    qr_code_base64: Optional[str]
    validade: str
    beneficios: List[str]
    mensagem: str


class ValidarCartaRequest(BaseModel):
    """Request para validar carta."""
    atendente: str = Field(..., min_length=2, max_length=100)
    cras_atendimento: str = Field(..., min_length=2, max_length=200)


class CartaDetalheResponse(BaseModel):
    """Response com detalhes da carta."""
    codigo_validacao: str
    status: str
    valida: bool
    nome: Optional[str]
    cpf_masked: Optional[str]
    municipio: Optional[str]
    uf: Optional[str]
    beneficios: List[str]
    documentos: Optional[List[dict]]
    cras_sugerido: Optional[dict]
    criado_em: str
    validade: str
    utilizado_em: Optional[str]
    validado_por: Optional[str]


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/gerar", response_model=CartaResponse)
async def gerar_carta(
    request: GerarCartaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Gera nova carta de encaminhamento.

    A carta contém:
    - Dados pré-preenchidos do cidadão
    - Benefícios para os quais pode ser elegível
    - Checklist de documentos
    - CRAS sugerido
    - QR Code para validação
    """
    cidadao = request.cidadao

    # Mascarar CPF
    cpf_masked = mascarar_cpf(cidadao.cpf) if cidadao.cpf else None
    cpf_hash = hashlib.sha256(cidadao.cpf.encode()).hexdigest() if cidadao.cpf else None

    # Preparar dados para a tool
    beneficios_list = [{"codigo": b.codigo, "nome": b.nome, "valor_estimado": b.valor_estimado} for b in request.beneficios]
    documentos_list = [{"nome": d.nome, "apresentado": d.apresentado} for d in request.documentos]
    cras_info = {"nome": request.cras.nome, "endereco": request.cras.endereco, "telefone": request.cras.telefone} if request.cras else None

    # Gerar carta completa (HTML + PDF + QR)
    carta_completa = await gerar_carta_completa(
        nome=cidadao.nome,
        cpf_masked=cpf_masked or "Não informado",
        municipio=cidadao.municipio,
        uf=cidadao.uf,
        renda_familiar=cidadao.renda_familiar,
        qtd_pessoas=cidadao.pessoas_na_casa,
        programas_elegiveis=beneficios_list,
        documentos_checklist=documentos_list,
        cras_info=cras_info,
    )

    # Salvar no banco
    carta_db = CartaEncaminhamento(
        codigo_validacao=carta_completa.codigo_validacao,
        cpf_hash=cpf_hash,
        cpf_masked=cpf_masked,
        nome=cidadao.nome,
        municipio=cidadao.municipio,
        uf=cidadao.uf,
        dados_cidadao={
            "renda_familiar": cidadao.renda_familiar,
            "renda_per_capita": cidadao.renda_familiar / cidadao.pessoas_na_casa,
            "pessoas_na_casa": cidadao.pessoas_na_casa,
            "tem_filhos": cidadao.tem_filhos_menores,
            "tem_idoso": cidadao.tem_idoso_65_mais,
            "tem_pcd": cidadao.tem_pcd,
            "tem_gestante": cidadao.tem_gestante,
        },
        beneficios=[b.codigo for b in request.beneficios],
        documentos_checklist=documentos_list,
        cras_nome=request.cras.nome if request.cras else None,
        cras_endereco=request.cras.endereco if request.cras else None,
        cras_telefone=request.cras.telefone if request.cras else None,
        validade=datetime.utcnow() + timedelta(days=30),
        html_content=carta_completa.html_content,
        pdf_base64=carta_completa.pdf_base64,
    )

    db.add(carta_db)
    await db.commit()

    return CartaResponse(
        codigo_validacao=carta_completa.codigo_validacao,
        link_validacao=carta_completa.link_validacao,
        qr_code_base64=carta_completa.qr_code_base64,
        validade=carta_completa.validade,
        beneficios=[b.nome for b in request.beneficios],
        mensagem="Carta gerada com sucesso! Leve ao CRAS ou mostre no celular.",
    )


@router.get("/{codigo}", response_model=CartaDetalheResponse)
async def obter_carta(
    codigo: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtém detalhes de uma carta de encaminhamento.

    Usado para validação pelo atendente do CRAS.
    """
    # Buscar carta
    result = await db.execute(
        select(CartaEncaminhamento).where(CartaEncaminhamento.codigo_validacao == codigo)
    )
    carta = result.scalar_one_or_none()

    if not carta:
        raise HTTPException(status_code=404, detail="Carta não encontrada")

    # Verificar expiração
    if carta.status == StatusCarta.ATIVA.value and datetime.utcnow() > carta.validade:
        carta.marcar_expirada()
        await db.commit()

    return CartaDetalheResponse(
        codigo_validacao=carta.codigo_validacao,
        status=carta.status,
        valida=carta.esta_valida,
        nome=carta.nome,
        cpf_masked=carta.cpf_masked,
        municipio=carta.municipio,
        uf=carta.uf,
        beneficios=carta.beneficios or [],
        documentos=carta.documentos_checklist,
        cras_sugerido={
            "nome": carta.cras_nome,
            "endereco": carta.cras_endereco,
            "telefone": carta.cras_telefone,
        } if carta.cras_nome else None,
        criado_em=carta.criado_em.isoformat() if carta.criado_em else "",
        validade=carta.validade.isoformat() if carta.validade else "",
        utilizado_em=carta.utilizado_em.isoformat() if carta.utilizado_em else None,
        validado_por=carta.validado_por,
    )


@router.get("/{codigo}/html", response_class=HTMLResponse)
async def obter_carta_html(
    codigo: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna o HTML da carta para visualização.
    """
    result = await db.execute(
        select(CartaEncaminhamento).where(CartaEncaminhamento.codigo_validacao == codigo)
    )
    carta = result.scalar_one_or_none()

    if not carta:
        raise HTTPException(status_code=404, detail="Carta não encontrada")

    if not carta.html_content:
        raise HTTPException(status_code=404, detail="HTML da carta não disponível")

    return HTMLResponse(content=carta.html_content)


@router.get("/{codigo}/pdf")
async def obter_carta_pdf(
    codigo: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download do PDF da carta.
    """
    result = await db.execute(
        select(CartaEncaminhamento).where(CartaEncaminhamento.codigo_validacao == codigo)
    )
    carta = result.scalar_one_or_none()

    if not carta:
        raise HTTPException(status_code=404, detail="Carta não encontrada")

    if not carta.pdf_base64:
        raise HTTPException(status_code=404, detail="PDF não disponível. Instale reportlab para gerar PDFs.")

    # Decodificar base64
    pdf_bytes = base64.b64decode(carta.pdf_base64)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=carta_{codigo}.pdf"
        }
    )


@router.post("/{codigo}/validar")
async def validar_carta(
    codigo: str,
    request: ValidarCartaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Marca a carta como utilizada (validada pelo atendente).

    Este endpoint é usado pelo atendente do CRAS após escanear o QR Code.
    """
    result = await db.execute(
        select(CartaEncaminhamento).where(CartaEncaminhamento.codigo_validacao == codigo)
    )
    carta = result.scalar_one_or_none()

    if not carta:
        raise HTTPException(status_code=404, detail="Carta não encontrada")

    if not carta.esta_valida:
        raise HTTPException(
            status_code=400,
            detail=f"Carta não é válida. Status: {carta.status}"
        )

    # Marcar como utilizada
    carta.marcar_utilizada(
        atendente=request.atendente,
        cras=request.cras_atendimento,
    )
    await db.commit()

    return {
        "sucesso": True,
        "mensagem": "Carta validada com sucesso",
        "codigo": carta.codigo_validacao,
        "validado_em": carta.utilizado_em.isoformat(),
        "atendente": carta.validado_por,
    }
