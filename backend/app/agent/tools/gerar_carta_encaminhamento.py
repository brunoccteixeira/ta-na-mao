"""Tool para gerar Carta de Encaminhamento ao CRAS.

Gera um documento (HTML/PDF) que o cidadao pode levar ao CRAS
com informacoes pre-preenchidas, agilizando o atendimento.

A carta contem:
- Dados coletados do cidadao
- Programas para os quais pode ser elegivel
- QR Code para validacao
- Orientacoes sobre documentos necessarios

Formatos disponíveis:
- HTML (para visualização no celular)
- PDF (para impressão e envio)
- Link web + QR Code (para validação pelo atendente)

Inspirado no conceito de "pre-atendimento digital" para
reduzir barreiras de acesso a servicos sociais.
"""

import hashlib
import io
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from base64 import b64encode
from dataclasses import dataclass

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image as RLImage,
    )
    from reportlab.lib.enums import TA_CENTER
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from app.agent.tools.base import ToolResult, UIHint


class CartaEncaminhamentoResult(ToolResult):
    """Resultado da geracao de carta de encaminhamento."""

    @classmethod
    def gerada(
        cls,
        carta_html: str,
        codigo_validacao: str,
        programas: List[str],
        validade: str
    ) -> "CartaEncaminhamentoResult":
        return cls(
            success=True,
            data={
                "carta_html": carta_html,
                "codigo_validacao": codigo_validacao,
                "programas": programas,
                "validade": validade,
                "instrucoes": "Leve esta carta impressa ou mostre no celular ao CRAS"
            },
            ui_hint=UIHint.INFO
        )


def gerar_codigo_validacao(dados: Dict[str, Any]) -> str:
    """Gera codigo de validacao unico para a carta.

    O codigo permite que o CRAS valide que a carta foi gerada
    pelo sistema Ta na Mao e nao foi adulterada.
    """
    # Cria string com dados principais
    dados_str = json.dumps({
        "nome": dados.get("nome", ""),
        "data": datetime.now().strftime("%Y%m%d"),
        "programas": dados.get("programas", [])
    }, sort_keys=True)

    # Gera hash SHA256 e pega primeiros 8 caracteres
    hash_full = hashlib.sha256(dados_str.encode()).hexdigest()
    return hash_full[:8].upper()


def gerar_qr_code_url(codigo: str, dados_resumo: str) -> str:
    """Gera URL para QR Code via API publica.

    O QR Code contem:
    - Codigo de validacao
    - Link para verificacao online (futuro)
    """
    # Conteudo do QR Code
    conteudo = f"TANAMAO:{codigo}|{dados_resumo}"

    # Usa API publica do QRServer (gratuita)
    # Em producao, usar servico proprio ou biblioteca local
    conteudo_encoded = conteudo.replace(" ", "%20").replace("|", "%7C")
    return f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={conteudo_encoded}"


def gerar_carta_encaminhamento(
    # Dados do cidadao
    nome: str,
    idade: Optional[int] = None,
    municipio: Optional[str] = None,
    uf: Optional[str] = None,

    # Composicao familiar
    qtd_pessoas_familia: int = 1,
    tem_criancas: bool = False,
    tem_idoso: bool = False,
    tem_pcd: bool = False,
    tem_gestante: bool = False,

    # Situacao economica
    renda_total_familiar: float = 0,

    # Moradia
    situacao_moradia: Optional[str] = None,
    endereco_referencia: Optional[str] = None,

    # Documentacao atual
    documentos_que_tem: Optional[List[str]] = None,

    # Programas elegiveis (resultado da verificacao)
    programas_elegiveis: Optional[List[Dict[str, Any]]] = None,

    # CRAS destino (se conhecido)
    cras_nome: Optional[str] = None,
    cras_endereco: Optional[str] = None
) -> CartaEncaminhamentoResult:
    """Gera Carta de Encaminhamento ao CRAS.

    A carta serve como "pre-cadastro" para agilizar atendimento.
    O cidadao leva ao CRAS impressa ou mostra no celular.

    Args:
        nome: Nome do cidadao
        idade: Idade em anos
        municipio: Nome do municipio
        uf: UF do estado
        qtd_pessoas_familia: Total de pessoas na familia
        tem_criancas: Familia tem criancas
        tem_idoso: Familia tem idoso 65+
        tem_pcd: Familia tem pessoa com deficiencia
        tem_gestante: Familia tem gestante
        renda_total_familiar: Renda mensal total
        situacao_moradia: Tipo de moradia
        endereco_referencia: Endereco ou ponto de referencia
        documentos_que_tem: Lista de documentos que possui
        programas_elegiveis: Programas para os quais pode ser elegivel
        cras_nome: Nome do CRAS (se conhecido)
        cras_endereco: Endereco do CRAS

    Returns:
        CartaEncaminhamentoResult com HTML da carta e codigo de validacao
    """
    # Dados para validacao
    dados = {
        "nome": nome,
        "municipio": municipio,
        "programas": [p.get("codigo", "") for p in (programas_elegiveis or [])]
    }

    # Gera codigo de validacao
    codigo = gerar_codigo_validacao(dados)

    # Dados resumidos para QR
    dados_resumo = f"{nome[:20]}|{municipio or 'BR'}"
    qr_url = gerar_qr_code_url(codigo, dados_resumo)

    # Data e validade
    data_geracao = datetime.now()
    data_validade = "30 dias a partir da emissao"

    # Calcula renda per capita
    renda_per_capita = renda_total_familiar / qtd_pessoas_familia if qtd_pessoas_familia > 0 else 0

    # Monta lista de programas
    programas_texto = []
    if programas_elegiveis:
        for p in programas_elegiveis:
            nome_prog = p.get("nome", p.get("codigo", ""))
            valor = p.get("valor_estimado")
            if valor:
                programas_texto.append(f"{nome_prog} (estimado R$ {valor:.2f})")
            else:
                programas_texto.append(nome_prog)

    # Documentos que tem
    docs_texto = documentos_que_tem or ["Nao informado"]

    # Situacao especial
    situacao_especial = ""
    if situacao_moradia == "rua":
        situacao_especial = "PESSOA EM SITUACAO DE RUA - Atendimento prioritario"
    elif tem_pcd:
        situacao_especial = "PESSOA COM DEFICIENCIA NA FAMILIA - Verificar BPC"
    elif tem_idoso:
        situacao_especial = "IDOSO NA FAMILIA - Verificar BPC Idoso"

    # Gera HTML da carta
    carta_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carta de Encaminhamento - Ta na Mao</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.4;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #006B3F;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #006B3F;
            font-size: 18pt;
            margin-bottom: 5px;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 10pt;
        }}
        .codigo {{
            background: #f0f0f0;
            padding: 10px;
            text-align: center;
            font-family: monospace;
            font-size: 14pt;
            letter-spacing: 2px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .qr-container {{
            float: right;
            margin-left: 20px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .qr-container img {{
            border: 1px solid #ccc;
        }}
        .qr-container small {{
            display: block;
            margin-top: 5px;
            font-size: 8pt;
            color: #666;
        }}
        .section {{
            margin-bottom: 20px;
            clear: both;
        }}
        .section h2 {{
            color: #006B3F;
            font-size: 12pt;
            border-bottom: 1px solid #006B3F;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }}
        .field {{
            margin-bottom: 8px;
        }}
        .field label {{
            font-weight: bold;
            color: #333;
        }}
        .alert {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .alert.priority {{
            background: #f8d7da;
            border-color: #f5c6cb;
        }}
        .programs {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 10px;
            border-radius: 5px;
        }}
        .programs ul {{
            margin-left: 20px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ccc;
            font-size: 9pt;
            color: #666;
            text-align: center;
        }}
        .footer .validity {{
            font-weight: bold;
            color: #333;
        }}
        @media print {{
            body {{ padding: 10px; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CARTA DE ENCAMINHAMENTO</h1>
        <div class="subtitle">Sistema Ta na Mao - Acesso a Beneficios Sociais</div>
    </div>

    <div class="codigo">
        CODIGO: {codigo}
    </div>

    <div class="qr-container">
        <img src="{qr_url}" alt="QR Code de Validacao" width="120" height="120">
        <small>Validacao</small>
    </div>

    {f'<div class="alert priority"><strong>{situacao_especial}</strong></div>' if situacao_especial else ''}

    <div class="section">
        <h2>DADOS DO CIDADAO</h2>
        <div class="field"><label>Nome:</label> {nome}</div>
        <div class="field"><label>Idade:</label> {idade or 'Nao informada'} anos</div>
        <div class="field"><label>Municipio/UF:</label> {municipio or 'Nao informado'}/{uf or '--'}</div>
        <div class="field"><label>Endereco/Referencia:</label> {endereco_referencia or 'Nao informado'}</div>
        <div class="field"><label>Situacao de Moradia:</label> {_formatar_moradia(situacao_moradia)}</div>
    </div>

    <div class="section">
        <h2>COMPOSICAO FAMILIAR</h2>
        <div class="field"><label>Pessoas na familia:</label> {qtd_pessoas_familia}</div>
        <div class="field"><label>Renda familiar total:</label> R$ {renda_total_familiar:.2f}</div>
        <div class="field"><label>Renda per capita:</label> R$ {renda_per_capita:.2f}</div>
        <div class="field"><label>Criancas:</label> {'Sim' if tem_criancas else 'Nao'}</div>
        <div class="field"><label>Idosos (65+):</label> {'Sim' if tem_idoso else 'Nao'}</div>
        <div class="field"><label>Pessoa com Deficiencia:</label> {'Sim' if tem_pcd else 'Nao'}</div>
        <div class="field"><label>Gestante:</label> {'Sim' if tem_gestante else 'Nao'}</div>
    </div>

    <div class="section">
        <h2>DOCUMENTOS QUE POSSUI</h2>
        <ul>
            {''.join(f'<li>{doc}</li>' for doc in docs_texto)}
        </ul>
    </div>

    <div class="section">
        <h2>PROGRAMAS PARA VERIFICAR ELEGIBILIDADE</h2>
        <div class="programs">
            <ul>
                {''.join(f'<li>{prog}</li>' for prog in programas_texto) if programas_texto else '<li>A definir pelo CRAS</li>'}
            </ul>
        </div>
    </div>

    {f'''<div class="section">
        <h2>CRAS INDICADO</h2>
        <div class="field"><label>Nome:</label> {cras_nome}</div>
        <div class="field"><label>Endereco:</label> {cras_endereco}</div>
    </div>''' if cras_nome else ''}

    <div class="alert">
        <strong>ORIENTACOES PARA O CIDADAO:</strong><br>
        1. Leve esta carta impressa ou mostre no celular ao CRAS<br>
        2. Leve os documentos que possui (mesmo que incompletos)<br>
        3. O CRAS pode ajudar a tirar documentos faltantes<br>
        4. Pergunte sobre os proximos mutiroes de documentacao (Registre-se!)
    </div>

    <div class="footer">
        <p>Carta gerada em: {data_geracao.strftime('%d/%m/%Y as %H:%M')}</p>
        <p class="validity">Validade: {data_validade}</p>
        <p>Sistema Ta na Mao - Facilitando o acesso a direitos sociais</p>
        <p><small>Esta carta nao garante a concessao de beneficios. A elegibilidade sera verificada pelo CRAS.</small></p>
    </div>
</body>
</html>
"""

    return CartaEncaminhamentoResult.gerada(
        carta_html=carta_html,
        codigo_validacao=codigo,
        programas=[p.get("nome", "") for p in (programas_elegiveis or [])],
        validade=data_validade
    )


def _formatar_moradia(situacao: Optional[str]) -> str:
    """Formata situacao de moradia para exibicao."""
    mapa = {
        "proprio": "Proprio",
        "alugado": "Alugado",
        "cedido": "Cedido/Emprestado",
        "rua": "Situacao de Rua",
        "abrigo": "Abrigo/Albergue",
        "ocupacao": "Ocupacao"
    }
    return mapa.get(situacao, situacao or "Nao informado")


# =============================================================================
# Funcao para salvar carta como arquivo
# =============================================================================

def salvar_carta_arquivo(
    carta_html: str,
    nome_cidadao: str,
    diretorio: str = "/tmp"
) -> str:
    """Salva carta como arquivo HTML.

    Args:
        carta_html: Conteudo HTML da carta
        nome_cidadao: Nome do cidadao (para nome do arquivo)
        diretorio: Diretorio onde salvar

    Returns:
        Caminho completo do arquivo salvo
    """
    import re

    # Normaliza nome para nome de arquivo
    nome_arquivo = re.sub(r'[^a-zA-Z0-9]', '_', nome_cidadao.lower())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo = f"{diretorio}/carta_encaminhamento_{nome_arquivo}_{timestamp}.html"

    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(carta_html)

    return arquivo


# =============================================================================
# Funções para geração de PDF e QR Code local
# =============================================================================

@dataclass
class CartaCompleta:
    """Resultado completo da geração de carta (HTML + PDF + QR)."""
    codigo_validacao: str
    html_content: str
    pdf_base64: Optional[str]
    qr_code_base64: Optional[str]
    link_validacao: str
    validade: str


def gerar_codigo_unico() -> str:
    """Gera código único de validação no formato TNM-YYYY-XXXXXX."""
    ano = datetime.now().year
    aleatorio = secrets.token_hex(3).upper()
    return f"TNM-{ano}-{aleatorio}"


def gerar_qr_code_local(conteudo: str) -> Optional[str]:
    """
    Gera QR Code localmente e retorna como base64.

    Args:
        conteudo: String para codificar no QR

    Returns:
        String base64 do QR Code PNG, ou None se qrcode não estiver instalado
    """
    if not HAS_QRCODE:
        return None

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(conteudo)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return b64encode(buffer.getvalue()).decode("utf-8")


def gerar_pdf_carta(
    nome: str,
    cpf_masked: str,
    municipio: str,
    uf: str,
    renda_familiar: float,
    renda_per_capita: float,
    qtd_pessoas: int,
    programas: List[str],
    documentos: List[Dict[str, Any]],
    cras_info: Optional[Dict[str, str]],
    codigo_validacao: str,
    link_validacao: str,
) -> Optional[str]:
    """
    Gera PDF da carta de encaminhamento.

    Returns:
        String base64 do PDF, ou None se reportlab não estiver instalado
    """
    if not HAS_REPORTLAB:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "Titulo",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    subtitulo_style = ParagraphStyle(
        "Subtitulo",
        parent=styles["Heading2"],
        fontSize=12,
        spaceAfter=10,
        spaceBefore=15,
    )
    normal_style = styles["Normal"]
    info_style = ParagraphStyle(
        "Info",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.gray,
    )

    elements = []

    # Cabeçalho
    elements.append(Paragraph("CARTA DE ENCAMINHAMENTO", titulo_style))
    elements.append(Paragraph("Sistema Tá na Mão", normal_style))
    elements.append(Spacer(1, 10))

    # Data e código
    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    elements.append(Paragraph(f"Gerada em: {data_geracao}", info_style))
    elements.append(Paragraph(f"Código: <b>{codigo_validacao}</b>", normal_style))
    elements.append(Spacer(1, 20))

    # Dados do cidadão
    elements.append(Paragraph("DADOS DO CIDADÃO", subtitulo_style))
    dados_table = [
        ["Nome:", nome],
        ["CPF:", cpf_masked],
        ["Município:", f"{municipio} - {uf}"],
        ["Pessoas na família:", str(qtd_pessoas)],
        ["Renda familiar:", f"R$ {renda_familiar:.2f}"],
        ["Renda per capita:", f"R$ {renda_per_capita:.2f}"],
    ]
    table = Table(dados_table, colWidths=[4*cm, 12*cm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # Benefícios
    elements.append(Paragraph("BENEFÍCIOS SOLICITADOS", subtitulo_style))
    for prog in programas:
        elements.append(Paragraph(f"• {prog}", normal_style))
    elements.append(Spacer(1, 10))

    # Documentos
    elements.append(Paragraph("DOCUMENTOS", subtitulo_style))
    for doc in documentos:
        nome_doc = doc.get("nome", "")
        apresentado = doc.get("apresentado", False)
        check = "✓" if apresentado else "☐"
        elements.append(Paragraph(f"{check} {nome_doc}", normal_style))
    elements.append(Spacer(1, 10))

    # CRAS
    if cras_info:
        elements.append(Paragraph("CRAS SUGERIDO", subtitulo_style))
        elements.append(Paragraph(f"<b>{cras_info.get('nome', '')}</b>", normal_style))
        elements.append(Paragraph(cras_info.get("endereco", ""), normal_style))
        if cras_info.get("telefone"):
            elements.append(Paragraph(f"Tel: {cras_info.get('telefone')}", normal_style))
        elements.append(Spacer(1, 15))

    # Aviso
    elements.append(Paragraph(
        "<b>ATENÇÃO:</b> Dados autodeclarados. Valide: " + codigo_validacao,
        info_style
    ))

    # QR Code
    if HAS_QRCODE:
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(link_validacao)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        elements.append(Spacer(1, 10))
        elements.append(RLImage(qr_buffer, width=3*cm, height=3*cm))

    doc.build(elements)
    buffer.seek(0)

    return b64encode(buffer.getvalue()).decode("utf-8")


async def gerar_carta_completa(
    nome: str,
    cpf_masked: str,
    municipio: str,
    uf: str,
    renda_familiar: float,
    qtd_pessoas: int,
    programas_elegiveis: List[Dict[str, Any]],
    documentos_checklist: List[Dict[str, Any]],
    cras_info: Optional[Dict[str, str]] = None,
    base_url: str = "https://tanamao.app",
) -> CartaCompleta:
    """
    Gera carta de encaminhamento completa (HTML + PDF + QR Code).

    Args:
        nome: Nome do cidadão
        cpf_masked: CPF mascarado (***456.789-**)
        municipio: Nome do município
        uf: Sigla do estado
        renda_familiar: Renda familiar total
        qtd_pessoas: Quantidade de pessoas na família
        programas_elegiveis: Lista de programas elegíveis
        documentos_checklist: Lista de documentos com status
        cras_info: Dados do CRAS sugerido
        base_url: URL base para links

    Returns:
        CartaCompleta com HTML, PDF, QR Code e metadados
    """
    # Gerar código único
    codigo = gerar_codigo_unico()

    # Link de validação
    link = f"{base_url}/carta/{codigo}"

    # Calcular renda per capita
    renda_per_capita = renda_familiar / qtd_pessoas if qtd_pessoas > 0 else 0

    # Lista de nomes de programas
    programas_nomes = [p.get("nome", p.get("codigo", "")) for p in programas_elegiveis]

    # Gerar HTML usando função existente
    result = gerar_carta_encaminhamento(
        nome=nome,
        municipio=municipio,
        uf=uf,
        qtd_pessoas_familia=qtd_pessoas,
        renda_total_familiar=renda_familiar,
        documentos_que_tem=[d.get("nome", "") for d in documentos_checklist if d.get("apresentado")],
        programas_elegiveis=programas_elegiveis,
        cras_nome=cras_info.get("nome") if cras_info else None,
        cras_endereco=cras_info.get("endereco") if cras_info else None,
    )
    html_content = result.data.get("carta_html", "")

    # Gerar QR Code local
    qr_base64 = gerar_qr_code_local(link)

    # Gerar PDF
    pdf_base64 = gerar_pdf_carta(
        nome=nome,
        cpf_masked=cpf_masked,
        municipio=municipio,
        uf=uf,
        renda_familiar=renda_familiar,
        renda_per_capita=renda_per_capita,
        qtd_pessoas=qtd_pessoas,
        programas=programas_nomes,
        documentos=documentos_checklist,
        cras_info=cras_info,
        codigo_validacao=codigo,
        link_validacao=link,
    )

    # Validade
    validade = (datetime.now() + timedelta(days=30)).isoformat()

    return CartaCompleta(
        codigo_validacao=codigo,
        html_content=html_content,
        pdf_base64=pdf_base64,
        qr_code_base64=qr_base64,
        link_validacao=link,
        validade=validade,
    )


def mascarar_cpf(cpf: str) -> str:
    """Mascara CPF para exibição: ***456.789-**"""
    cpf_limpo = "".join(c for c in cpf if c.isdigit())
    if len(cpf_limpo) != 11:
        return "***.***.***-**"
    return f"***.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-**"
