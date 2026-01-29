"""
Carta de Encaminhamento para Habitação - MCMV.

Gera carta específica para programas habitacionais com:
- Simulação de financiamento incluída
- Checklist de documentos por faixa
- Encaminhamento correto (CRAS vs Prefeitura vs CAIXA)
- Identificação de grupo prioritário
- QR Code para validação

Lógica de encaminhamento:
- Faixa 1 sem CadÚnico → CRAS (fazer CadÚnico primeiro)
- Faixa 1 com CadÚnico → Prefeitura (Secretaria de Habitação)
- Faixas 2, 3, 4 → CAIXA (direto no banco)
"""

import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

from app.agent.tools.base import ToolResult, UIHint
from app.agent.tools.simulador_mcmv import (
    simular_financiamento_mcmv,
    SimulacaoResultado,
)
from app.agent.tools.regras_elegibilidade import (
    MCMV_FAIXA_1,
    MCMV_FAIXA_2,
    MCMV_FAIXA_3,
    MCMV_FAIXA_4,
)


@dataclass
class CartaHabitacaoResult:
    """Resultado da carta de encaminhamento habitacional."""
    codigo_validacao: str
    html_content: str
    faixa: str
    destino: str
    simulacao: Optional[SimulacaoResultado]
    documentos_checklist: List[Dict[str, Any]]
    grupo_prioritario: Optional[str]
    validade: str


class CartaHabitacaoToolResult(ToolResult):
    """ToolResult para carta de habitação."""

    @classmethod
    def gerada(
        cls,
        carta: CartaHabitacaoResult,
    ) -> "CartaHabitacaoToolResult":
        return cls(
            success=True,
            data={
                "carta_html": carta.html_content,
                "codigo_validacao": carta.codigo_validacao,
                "faixa": carta.faixa,
                "destino": carta.destino,
                "simulacao": _simulacao_to_dict(carta.simulacao) if carta.simulacao else None,
                "documentos": carta.documentos_checklist,
                "grupo_prioritario": carta.grupo_prioritario,
                "validade": carta.validade,
                "instrucoes": f"Leve esta carta ao {carta.destino}"
            },
            ui_hint=UIHint.INFO
        )


def _simulacao_to_dict(sim: SimulacaoResultado) -> Dict[str, Any]:
    """Converte simulação para dicionário."""
    return {
        "faixa": sim.faixa,
        "valor_imovel": sim.valor_imovel,
        "subsidio": sim.subsidio,
        "valor_financiado": sim.valor_financiado,
        "parcela": sim.parcela_inicial,
        "juros": sim.taxa_juros_anual,
        "prazo_anos": sim.prazo_meses // 12,
    }


def gerar_carta_habitacao(
    # Dados do cidadão
    nome: str,
    cpf: Optional[str] = None,
    idade: Optional[int] = None,
    municipio: Optional[str] = None,
    uf: Optional[str] = None,

    # Renda e família
    renda_familiar: float = 0,
    qtd_pessoas_familia: int = 1,

    # Situação habitacional
    tem_casa_propria: bool = False,
    situacao_moradia: Optional[str] = None,

    # CadÚnico
    cadastrado_cadunico: bool = False,
    nis: Optional[str] = None,

    # Grupos prioritários
    tem_criancas: bool = False,
    tem_idoso: bool = False,
    tem_pcd: bool = False,
    tem_gestante: bool = False,
    vitima_violencia: bool = False,
    em_area_risco: bool = False,
    situacao_rua: bool = False,

    # Benefícios
    recebe_bolsa_familia: bool = False,
    recebe_bpc: bool = False,

    # FGTS
    valor_fgts: float = 0,

    # Região
    regiao_metropolitana: bool = False,

    # Documentos já apresentados
    documentos_que_tem: Optional[List[str]] = None,
) -> CartaHabitacaoToolResult:
    """
    Gera Carta de Encaminhamento específica para programas habitacionais.

    Args:
        nome: Nome do cidadão
        cpf: CPF (será mascarado)
        idade: Idade em anos
        municipio: Nome do município
        uf: Sigla do estado
        renda_familiar: Renda mensal total da família
        qtd_pessoas_familia: Quantidade de pessoas na família
        tem_casa_propria: Se já possui casa própria
        situacao_moradia: Tipo de moradia atual
        cadastrado_cadunico: Se tem CadÚnico
        nis: Número do NIS
        tem_criancas: Família tem crianças
        tem_idoso: Família tem idoso 65+
        tem_pcd: Família tem pessoa com deficiência
        tem_gestante: Família tem gestante
        vitima_violencia: Vítima de violência doméstica
        em_area_risco: Mora em área de risco
        situacao_rua: Em situação de rua
        recebe_bolsa_familia: Recebe Bolsa Família
        recebe_bpc: Recebe BPC
        valor_fgts: Saldo de FGTS disponível
        regiao_metropolitana: Se está em região metropolitana
        documentos_que_tem: Lista de documentos que possui

    Returns:
        CartaHabitacaoToolResult com carta em HTML e metadados
    """
    # Determinar faixa
    faixa = _determinar_faixa(renda_familiar)

    # Determinar grupo prioritário
    grupo_prioritario = _identificar_grupo_prioritario(
        situacao_rua=situacao_rua,
        vitima_violencia=vitima_violencia,
        em_area_risco=em_area_risco,
        recebe_bpc=recebe_bpc,
        recebe_bolsa_familia=recebe_bolsa_familia,
        tem_pcd=tem_pcd,
        tem_idoso=tem_idoso,
        tem_criancas=tem_criancas,
        faixa=faixa,
    )

    # Determinar destino de encaminhamento
    destino = _determinar_destino(faixa, cadastrado_cadunico, tem_casa_propria)

    # Executar simulação se elegível
    simulacao = None
    if faixa and not tem_casa_propria:
        simulacao = simular_financiamento_mcmv(
            renda_familiar=renda_familiar,
            valor_fgts=valor_fgts,
            idade_comprador=idade,
            regiao_metropolitana=regiao_metropolitana,
        )

    # Obter checklist de documentos
    documentos_checklist = _gerar_checklist_documentos(
        faixa=faixa,
        cadastrado_cadunico=cadastrado_cadunico,
        tem_casa_propria=tem_casa_propria,
        documentos_que_tem=documentos_que_tem or [],
    )

    # Gerar código de validação
    codigo = _gerar_codigo_validacao(nome, municipio, faixa)

    # Gerar HTML da carta
    html = _gerar_html_carta(
        nome=nome,
        cpf_mascarado=_mascarar_cpf(cpf) if cpf else None,
        idade=idade,
        municipio=municipio,
        uf=uf,
        renda_familiar=renda_familiar,
        qtd_pessoas=qtd_pessoas_familia,
        faixa=faixa,
        destino=destino,
        grupo_prioritario=grupo_prioritario,
        simulacao=simulacao,
        documentos_checklist=documentos_checklist,
        cadastrado_cadunico=cadastrado_cadunico,
        nis=nis,
        codigo=codigo,
        tem_casa_propria=tem_casa_propria,
    )

    # Validade
    validade = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")

    carta = CartaHabitacaoResult(
        codigo_validacao=codigo,
        html_content=html,
        faixa=faixa or "Não aplicável",
        destino=destino,
        simulacao=simulacao,
        documentos_checklist=documentos_checklist,
        grupo_prioritario=grupo_prioritario,
        validade=validade,
    )

    return CartaHabitacaoToolResult.gerada(carta)


def _determinar_faixa(renda_familiar: float) -> Optional[str]:
    """Determina a faixa MCMV."""
    if renda_familiar <= MCMV_FAIXA_1:
        return "Faixa 1"
    elif renda_familiar <= MCMV_FAIXA_2:
        return "Faixa 2"
    elif renda_familiar <= MCMV_FAIXA_3:
        return "Faixa 3"
    elif renda_familiar <= MCMV_FAIXA_4:
        return "Faixa 4"
    return None


def _identificar_grupo_prioritario(
    situacao_rua: bool,
    vitima_violencia: bool,
    em_area_risco: bool,
    recebe_bpc: bool,
    recebe_bolsa_familia: bool,
    tem_pcd: bool,
    tem_idoso: bool,
    tem_criancas: bool,
    faixa: Optional[str],
) -> Optional[str]:
    """Identifica grupo prioritário com ordem de prioridade."""
    if situacao_rua:
        return "PESSOA EM SITUAÇÃO DE RUA - Atendimento Prioritário"

    if vitima_violencia:
        return "VÍTIMA DE VIOLÊNCIA DOMÉSTICA - Atendimento Prioritário"

    if em_area_risco:
        return "FAMÍLIA EM ÁREA DE RISCO - Atendimento Prioritário"

    if faixa == "Faixa 1" and (recebe_bpc or recebe_bolsa_familia):
        return "BENEFICIÁRIO BPC/BOLSA FAMÍLIA - Pode ter imóvel 100% gratuito"

    if tem_pcd:
        return "FAMÍLIA COM PESSOA COM DEFICIÊNCIA - Prioridade"

    if tem_idoso:
        return "FAMÍLIA COM IDOSO 65+ - Prioridade"

    if tem_criancas:
        return "FAMÍLIA COM CRIANÇAS - Prioridade"

    return None


def _determinar_destino(
    faixa: Optional[str],
    cadastrado_cadunico: bool,
    tem_casa_propria: bool,
) -> str:
    """Determina o local correto de encaminhamento."""
    if tem_casa_propria:
        return "CAIXA Econômica Federal (Programa de Reformas)"

    if faixa is None:
        return "Sistema Financeiro de Habitação - Bancos"

    if faixa == "Faixa 1":
        if not cadastrado_cadunico:
            return "CRAS - Fazer CadÚnico primeiro"
        return "Prefeitura - Secretaria de Habitação"

    return "CAIXA Econômica Federal"


def _gerar_checklist_documentos(
    faixa: Optional[str],
    cadastrado_cadunico: bool,
    tem_casa_propria: bool,
    documentos_que_tem: List[str],
) -> List[Dict[str, Any]]:
    """Gera checklist de documentos por faixa."""
    docs_tem_lower = [d.lower() for d in documentos_que_tem]

    def _check(nome: str) -> bool:
        return any(nome.lower() in d for d in docs_tem_lower)

    # Documentos básicos para todos
    documentos = [
        {"nome": "CPF", "obrigatorio": True, "tem": _check("cpf")},
        {"nome": "RG ou documento com foto", "obrigatorio": True, "tem": _check("rg")},
        {"nome": "Comprovante de residência", "obrigatorio": True, "tem": _check("residência") or _check("endereco")},
        {"nome": "Certidão de casamento ou nascimento", "obrigatorio": True, "tem": _check("certidão")},
        {"nome": "CPF de todos da família", "obrigatorio": True, "tem": False},
    ]

    if tem_casa_propria:
        # Documentos para reforma
        documentos.extend([
            {"nome": "Documento do imóvel (escritura/matrícula)", "obrigatorio": True, "tem": _check("escritura")},
            {"nome": "Orçamento das reformas", "obrigatorio": True, "tem": _check("orçamento")},
            {"nome": "Comprovante de renda", "obrigatorio": True, "tem": _check("renda")},
        ])
        return documentos

    if faixa == "Faixa 1":
        if not cadastrado_cadunico:
            documentos.insert(0, {
                "nome": "CadÚnico (NIS)",
                "obrigatorio": True,
                "tem": False,
                "alerta": "Faça o CadÚnico no CRAS antes de prosseguir"
            })
        else:
            documentos.insert(0, {"nome": "CadÚnico atualizado (NIS)", "obrigatorio": True, "tem": True})

        documentos.extend([
            {"nome": "Comprovante de renda ou declaração", "obrigatorio": True, "tem": _check("renda")},
        ])

    else:  # Faixas 2, 3, 4
        documentos.extend([
            {"nome": "Comprovante de renda (3 últimos meses)", "obrigatorio": True, "tem": _check("renda")},
            {"nome": "Carteira de trabalho", "obrigatorio": True, "tem": _check("carteira")},
            {"nome": "Declaração de Imposto de Renda", "obrigatorio": False, "tem": _check("imposto")},
            {"nome": "Extrato de FGTS", "obrigatorio": True, "tem": _check("fgts")},
            {"nome": "Certidões negativas (SPC/Serasa)", "obrigatorio": True, "tem": False},
        ])

    return documentos


def _gerar_codigo_validacao(nome: str, municipio: Optional[str], faixa: Optional[str]) -> str:
    """Gera código único de validação."""
    dados = json.dumps({
        "nome": nome[:20] if nome else "",
        "municipio": municipio or "",
        "faixa": faixa or "",
        "data": datetime.now().strftime("%Y%m%d"),
        "salt": secrets.token_hex(4),
    }, sort_keys=True)

    hash_code = hashlib.sha256(dados.encode()).hexdigest()[:8].upper()
    return f"HAB-{hash_code}"


def _mascarar_cpf(cpf: str) -> str:
    """Mascara CPF para exibição."""
    cpf_limpo = "".join(c for c in cpf if c.isdigit())
    if len(cpf_limpo) != 11:
        return "***.***.***-**"
    return f"***.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-**"


def _gerar_qr_code_url(codigo: str) -> str:
    """Gera URL do QR Code."""
    conteudo = f"TANAMAO:HAB:{codigo}"
    conteudo_encoded = conteudo.replace(" ", "%20")
    return f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={conteudo_encoded}"


def _gerar_html_carta(
    nome: str,
    cpf_mascarado: Optional[str],
    idade: Optional[int],
    municipio: Optional[str],
    uf: Optional[str],
    renda_familiar: float,
    qtd_pessoas: int,
    faixa: Optional[str],
    destino: str,
    grupo_prioritario: Optional[str],
    simulacao: Optional[SimulacaoResultado],
    documentos_checklist: List[Dict[str, Any]],
    cadastrado_cadunico: bool,
    nis: Optional[str],
    codigo: str,
    tem_casa_propria: bool,
) -> str:
    """Gera o HTML completo da carta."""
    renda_per_capita = renda_familiar / qtd_pessoas if qtd_pessoas > 0 else 0
    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    qr_url = _gerar_qr_code_url(codigo)

    # Tipo de programa
    if tem_casa_propria:
        programa_nome = "Reforma Casa Brasil"
        programa_tipo = "REFORMA"
    else:
        programa_nome = f"Minha Casa Minha Vida - {faixa}" if faixa else "Habitação"
        programa_tipo = "AQUISIÇÃO"

    # Seção de simulação
    simulacao_html = ""
    if simulacao and simulacao.viavel:
        simulacao_html = f"""
        <div class="simulacao">
            <h2>SIMULAÇÃO DO FINANCIAMENTO</h2>
            <div class="sim-grid">
                <div class="sim-item">
                    <span class="label">Valor do imóvel:</span>
                    <span class="valor">R$ {simulacao.valor_imovel:,.0f}</span>
                </div>
                {"<div class='sim-item'><span class='label'>Subsídio:</span><span class='valor destaque'>R$ " + f"{simulacao.subsidio:,.0f}" + "</span></div>" if simulacao.subsidio > 0 else ""}
                <div class="sim-item">
                    <span class="label">Valor financiado:</span>
                    <span class="valor">R$ {simulacao.valor_financiado:,.0f}</span>
                </div>
                <div class="sim-item">
                    <span class="label">Parcela estimada:</span>
                    <span class="valor">R$ {simulacao.parcela_inicial:,.0f}</span>
                </div>
                <div class="sim-item">
                    <span class="label">Prazo:</span>
                    <span class="valor">{simulacao.prazo_meses // 12} anos</span>
                </div>
                <div class="sim-item">
                    <span class="label">Juros:</span>
                    <span class="valor">{simulacao.taxa_juros_anual:.1f}% a.a.</span>
                </div>
            </div>
            <p class="aviso-sim">* Simulação estimativa. Valores finais dependem da análise de crédito.</p>
        </div>
        """

    # Seção de documentos
    docs_html = ""
    for doc in documentos_checklist:
        status = "✓" if doc.get("tem") else "☐"
        classe = "tem" if doc.get("tem") else "falta"
        obrig = " (obrigatório)" if doc.get("obrigatorio") else ""
        alerta = f"<span class='alerta'>{doc['alerta']}</span>" if doc.get("alerta") else ""
        docs_html += f"<li class='{classe}'>{status} {doc['nome']}{obrig} {alerta}</li>"

    # Seção de alerta prioritário
    alerta_html = ""
    if grupo_prioritario:
        alerta_html = f'<div class="alerta-prioritario">{grupo_prioritario}</div>'

    # Seção CadÚnico
    cadunico_html = ""
    if not cadastrado_cadunico and faixa == "Faixa 1":
        cadunico_html = """
        <div class="aviso-cadunico">
            <strong>ATENÇÃO:</strong> Você precisa fazer o CadÚnico no CRAS antes de se inscrever no programa habitacional.
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carta de Encaminhamento - Habitação</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            padding: 15px;
            max-width: 800px;
            margin: 0 auto;
            color: #333;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #006B3F;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }}
        .header h1 {{
            color: #006B3F;
            font-size: 16pt;
            margin-bottom: 5px;
        }}
        .header .programa {{
            font-size: 12pt;
            color: #333;
            font-weight: bold;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 9pt;
        }}
        .codigo-qr {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f5f5f5;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .codigo {{
            font-family: monospace;
            font-size: 14pt;
            letter-spacing: 2px;
            color: #006B3F;
            font-weight: bold;
        }}
        .qr img {{
            border: 1px solid #ccc;
        }}
        .alerta-prioritario {{
            background: #dc3545;
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .aviso-cadunico {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .section {{
            margin-bottom: 15px;
        }}
        .section h2 {{
            color: #006B3F;
            font-size: 11pt;
            border-bottom: 1px solid #006B3F;
            padding-bottom: 3px;
            margin-bottom: 8px;
        }}
        .dados-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 5px;
        }}
        .field {{
            margin-bottom: 5px;
        }}
        .field label {{
            font-weight: bold;
            color: #555;
            font-size: 9pt;
        }}
        .field .valor {{
            font-size: 10pt;
        }}
        .destino {{
            background: #d4edda;
            border: 2px solid #28a745;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 15px;
        }}
        .destino h3 {{
            color: #155724;
            margin-bottom: 5px;
        }}
        .destino .local {{
            font-size: 14pt;
            font-weight: bold;
            color: #006B3F;
        }}
        .simulacao {{
            background: #e8f4fd;
            border: 1px solid #0056b3;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .simulacao h2 {{
            color: #0056b3;
            font-size: 11pt;
            margin-bottom: 10px;
        }}
        .sim-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }}
        .sim-item {{
            text-align: center;
        }}
        .sim-item .label {{
            display: block;
            font-size: 8pt;
            color: #666;
        }}
        .sim-item .valor {{
            display: block;
            font-size: 11pt;
            font-weight: bold;
        }}
        .sim-item .destaque {{
            color: #28a745;
        }}
        .aviso-sim {{
            font-size: 8pt;
            color: #666;
            margin-top: 8px;
            text-align: center;
        }}
        .documentos ul {{
            list-style: none;
            padding: 0;
        }}
        .documentos li {{
            padding: 3px 0;
            font-size: 10pt;
        }}
        .documentos li.tem {{
            color: #28a745;
        }}
        .documentos li.falta {{
            color: #333;
        }}
        .documentos .alerta {{
            color: #dc3545;
            font-size: 8pt;
            display: block;
            margin-left: 20px;
        }}
        .orientacoes {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .orientacoes ol {{
            margin-left: 20px;
            font-size: 10pt;
        }}
        .footer {{
            border-top: 1px solid #ccc;
            padding-top: 10px;
            font-size: 8pt;
            color: #666;
            text-align: center;
        }}
        @media print {{
            body {{ padding: 10px; font-size: 10pt; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CARTA DE ENCAMINHAMENTO - HABITAÇÃO</h1>
        <div class="programa">{programa_nome}</div>
        <div class="subtitle">Sistema Tá na Mão - Acesso a Benefícios Sociais</div>
    </div>

    <div class="codigo-qr">
        <div class="codigo">CÓDIGO: {codigo}</div>
        <div class="qr">
            <img src="{qr_url}" alt="QR Code" width="100" height="100">
        </div>
    </div>

    {alerta_html}
    {cadunico_html}

    <div class="destino">
        <h3>ENCAMINHAR PARA:</h3>
        <div class="local">{destino}</div>
    </div>

    <div class="section">
        <h2>DADOS DO CIDADÃO</h2>
        <div class="dados-grid">
            <div class="field">
                <label>Nome:</label>
                <span class="valor">{nome}</span>
            </div>
            <div class="field">
                <label>CPF:</label>
                <span class="valor">{cpf_mascarado or 'Não informado'}</span>
            </div>
            <div class="field">
                <label>Idade:</label>
                <span class="valor">{idade or 'N/I'} anos</span>
            </div>
            <div class="field">
                <label>Município/UF:</label>
                <span class="valor">{municipio or 'N/I'}/{uf or '--'}</span>
            </div>
            <div class="field">
                <label>Pessoas na família:</label>
                <span class="valor">{qtd_pessoas}</span>
            </div>
            <div class="field">
                <label>NIS:</label>
                <span class="valor">{nis or 'Não cadastrado'}</span>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>SITUAÇÃO ECONÔMICA</h2>
        <div class="dados-grid">
            <div class="field">
                <label>Renda familiar:</label>
                <span class="valor">R$ {renda_familiar:,.2f}</span>
            </div>
            <div class="field">
                <label>Renda per capita:</label>
                <span class="valor">R$ {renda_per_capita:,.2f}</span>
            </div>
            <div class="field">
                <label>Faixa MCMV:</label>
                <span class="valor">{faixa or 'Acima do limite'}</span>
            </div>
            <div class="field">
                <label>Tipo:</label>
                <span class="valor">{programa_tipo}</span>
            </div>
        </div>
    </div>

    {simulacao_html}

    <div class="section documentos">
        <h2>DOCUMENTOS NECESSÁRIOS</h2>
        <ul>
            {docs_html}
        </ul>
    </div>

    <div class="orientacoes">
        <strong>PRÓXIMOS PASSOS:</strong>
        <ol>
            {"<li>Faça o CadÚnico no CRAS (necessário para Faixa 1)</li>" if not cadastrado_cadunico and faixa == "Faixa 1" else ""}
            <li>Reúna todos os documentos da lista acima</li>
            <li>Vá ao {destino} com esta carta</li>
            <li>Apresente o código {codigo} para validação</li>
        </ol>
    </div>

    <div class="footer">
        <p>Carta gerada em: {data_geracao}</p>
        <p>Válida por 30 dias | Código: {codigo}</p>
        <p>Sistema Tá na Mão - Esta carta não garante a concessão do benefício</p>
    </div>
</body>
</html>
"""
