"""
Tool para consulta de dinheiro esquecido: PIS/PASEP, SVR e FGTS.

Ajuda cidadãos a descobrirem e resgatarem valores que têm direito.
Total estimado: R$ 70+ bilhões disponíveis para resgate.

IMPACTO:
- PIS/PASEP antigo: R$ 26 bi para 10,5 milhões (prazo 2028!)
- Abono PIS/PASEP 2026: R$ 33,5 bi para 26,9 milhões
- FGTS: Bilhões retidos
- SVR: R$ 8+ bi para milhões de pessoas
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from app.agent.tools.base import ToolResult, UIHint


# =============================================================================
# Dados sobre os programas de dinheiro esquecido
# =============================================================================

PROGRAMAS_DINHEIRO = {
    "pis_pasep_antigo": {
        "nome": "PIS/PASEP Esquecido (1971-1988)",
        "valor_total": "R$ 26 bilhões",
        "beneficiarios": "10,5 milhões de pessoas",
        "media_por_pessoa": "R$ 2.800",
        "prazo": "Até 2028 - URGENTE! Depois o dinheiro vai pro governo!",
        "prazo_ano": 2028,
        "quem_tem_direito": [
            "Quem trabalhou com carteira assinada entre 1971 e 1988",
            "Quem era servidor público entre 1971 e 1988",
            "Herdeiros de trabalhadores que faleceram e tinham saldo"
        ],
        "como_consultar": {
            "online": "Acesse repiscidadao.fazenda.gov.br com seu Gov.br",
            "app": "Use o app FGTS da Caixa > Meus Saques > PIS/PASEP",
            "presencial": "Caixa (PIS) ou Banco do Brasil (PASEP) com RG e CPF"
        },
        "como_sacar": {
            "pix": "Se tem Pix cadastrado, o dinheiro pode cair automaticamente",
            "conta": "Transfere pra sua conta pelo site",
            "presencial": "Saque na Caixa ou BB com RG e CPF"
        },
        "documentos": ["RG ou CNH", "CPF", "Carteira de Trabalho (se tiver)"],
        "link": "https://repiscidadao.fazenda.gov.br",
        "link_app": "https://www.caixa.gov.br/atendimento/aplicativos/fgts/Paginas/default.aspx",
        "dica": "Se voce trabalhou antes de 1988, MUITO PROVAVELMENTE tem dinheiro!",
        "alerta_urgente": "ATENCAO: So 0,25% das pessoas sacaram ate agora! Nao perca o seu!"
    },
    "pis_pasep": {
        "nome": "PIS/PASEP Esquecido",
        "valor_total": "R$ 26 bilhões",
        "beneficiarios": "10,5 milhões de pessoas",
        "media_por_pessoa": "R$ 2.800",
        "prazo": "Até 2028 (depois o dinheiro vai para o Tesouro Nacional)",
        "quem_tem_direito": [
            "Quem trabalhou com carteira assinada entre 1971 e 1988",
            "Quem era servidor público entre 1971 e 1988",
            "Herdeiros de trabalhadores falecidos que tinham saldo"
        ],
        "como_consultar": {
            "online": "Acesse repiscidadao.fazenda.gov.br com seu Gov.br (nível prata ou ouro)",
            "app": "Use o app Gov.br e procure por 'PIS/PASEP'",
            "presencial": "Vá a uma agência da Caixa (PIS) ou Banco do Brasil (PASEP) com RG e CPF"
        },
        "como_sacar": {
            "pix": "Se você tiver Pix cadastrado, o dinheiro pode cair automaticamente",
            "conta": "Transfira para sua conta bancária pelo site",
            "presencial": "Saque na Caixa (PIS) ou BB (PASEP) com RG e CPF"
        },
        "documentos": ["RG ou CNH", "CPF", "Carteira de Trabalho (se tiver)"],
        "link": "https://repiscidadao.fazenda.gov.br",
        "dica": "Se você trabalhou antes de 1988, MUITO PROVAVELMENTE tem dinheiro esquecido!"
    },
    "svr": {
        "nome": "Valores a Receber (SVR) - Banco Central",
        "valor_total": "R$ 8 a 10 bilhões",
        "beneficiarios": "48 milhões de pessoas",
        "media_por_pessoa": "Varia de R$ 1 a R$ 10.000+",
        "prazo": "Consulte regularmente - novos valores são adicionados",
        "quem_tem_direito": [
            "Quem teve conta em banco que foi fechada com saldo",
            "Quem pagou tarifas indevidas",
            "Quem tem restituição de consórcio",
            "Quem tem cotas de cooperativas de crédito",
            "Herdeiros de pessoas falecidas"
        ],
        "como_consultar": {
            "online": "Acesse valoresareceber.bcb.gov.br com seu Gov.br",
            "importante": "Só existe consulta online, não tem atendimento presencial"
        },
        "como_sacar": {
            "pix": "Cadastre uma chave Pix e solicite o resgate - cai em alguns dias",
            "importante": "Você precisa informar uma chave Pix para receber"
        },
        "documentos": ["CPF", "Conta Gov.br (nível prata ou ouro)", "Chave Pix"],
        "link": "https://valoresareceber.bcb.gov.br",
        "dica": "Consulte a cada 3 meses - novos valores são adicionados frequentemente!",
        "alerta_golpe": "CUIDADO: O unico site oficial eh valoresareceber.bcb.gov.br - nao caia em golpes!"
    },
    "fgts": {
        "nome": "FGTS (Saldo Esquecido)",
        "valor_total": "Bilhões de reais",
        "beneficiarios": "Milhões de trabalhadores",
        "media_por_pessoa": "Varia conforme tempo de trabalho",
        "prazo": "Sem prazo para saldo normal",
        "quem_tem_direito": [
            "Quem tem saldo de empregos antigos que nunca sacou",
            "Quem foi demitido e nao sacou o FGTS",
            "Quem aderiu ao Saque-Aniversario e esqueceu de sacar"
        ],
        "como_consultar": {
            "app": "Baixe o app FGTS (da Caixa) - eh de graca!",
            "online": "Acesse fgts.caixa.gov.br",
            "presencial": "Agencia da Caixa com RG, CPF e Carteira de Trabalho"
        },
        "como_sacar": {
            "app": "Pelo app FGTS voce transfere pra sua conta",
            "caixa_tem": "Se tiver Caixa Tem, cai automaticamente",
            "presencial": "Na agencia da Caixa com documentos"
        },
        "documentos": ["RG ou CNH", "CPF", "Carteira de Trabalho"],
        "link": "https://www.fgts.gov.br",
        "link_app": "https://www.caixa.gov.br/atendimento/aplicativos/fgts/Paginas/default.aspx",
        "dica": "Mesmo sem Saque-Aniversario, voce pode ter FGTS de empregos antigos!"
    }
}

# =============================================================================
# Checklist de todas as fontes de dinheiro esquecido
# =============================================================================

FONTES_DINHEIRO_ESQUECIDO = [
    {
        "fonte": "PIS/PASEP Antigo",
        "onde_consultar": "App FGTS ou repiscidadao.fazenda.gov.br",
        "prazo": "Ate 2028",
        "urgente": True,
        "quem_pode_ter": "Quem trabalhou com carteira entre 1971 e 1988"
    },
    {
        "fonte": "FGTS de Empregos Antigos",
        "onde_consultar": "App FGTS",
        "prazo": "Sem prazo",
        "urgente": False,
        "quem_pode_ter": "Quem ja trabalhou com carteira assinada"
    },
    {
        "fonte": "Valores a Receber (Bancos)",
        "onde_consultar": "valoresareceber.bcb.gov.br",
        "prazo": "Continuo",
        "urgente": False,
        "quem_pode_ter": "Quem ja teve conta em banco"
    }
]


def consultar_dinheiro_esquecido(
    tipo: Optional[str] = None,
    cpf: Optional[str] = None
) -> ToolResult:
    """
    Consulta informações sobre dinheiro esquecido disponível para resgate.

    Args:
        tipo: Tipo específico (pis_pasep, svr, fgts) ou None para todos
        cpf: CPF do cidadão (opcional, para personalizar orientação)

    Returns:
        ToolResult com informações sobre como consultar e resgatar
    """
    if tipo and tipo.lower() in PROGRAMAS_DINHEIRO:
        programa = PROGRAMAS_DINHEIRO[tipo.lower()]
        return ToolResult.ok(
            data={
                "tipo": tipo.lower(),
                "programa": programa,
                "mensagem_simples": _formatar_mensagem_simples(programa)
            },
            ui_hint=UIHint.INFO,
            context_updates={"dinheiro_esquecido_consultado": tipo.lower()}
        )

    # Retorna todos os programas
    resumo = []
    for key, prog in PROGRAMAS_DINHEIRO.items():
        resumo.append({
            "tipo": key,
            "nome": prog["nome"],
            "valor_total": prog["valor_total"],
            "beneficiarios": prog["beneficiarios"],
            "link": prog["link"]
        })

    return ToolResult.ok(
        data={
            "programas": resumo,
            "total_disponivel": "R$ 42 bilhões",
            "mensagem": "Existem 3 tipos de dinheiro esquecido que você pode ter direito. Quer que eu explique cada um?"
        },
        ui_hint=UIHint.INFO
    )


def guia_pis_pasep() -> ToolResult:
    """
    Retorna guia completo para consultar e sacar PIS/PASEP.

    R$ 26 bilhões disponíveis para 10,5 milhões de pessoas.
    Prazo: até 2028.
    """
    programa = PROGRAMAS_DINHEIRO["pis_pasep"]

    passo_a_passo = [
        {
            "passo": 1,
            "titulo": "Verifique se você tem direito",
            "descricao": "Você trabalhou com carteira assinada ou foi servidor público entre 1971 e 1988?",
            "acao": "Se sim, você MUITO PROVAVELMENTE tem dinheiro para receber!"
        },
        {
            "passo": 2,
            "titulo": "Acesse o site do governo",
            "descricao": "Entre em repiscidadao.fazenda.gov.br",
            "acao": "Use seu login Gov.br (precisa ser nível prata ou ouro)"
        },
        {
            "passo": 3,
            "titulo": "Consulte seu saldo",
            "descricao": "O sistema vai mostrar se você tem valores a receber",
            "acao": "Anote o valor e a opção de saque"
        },
        {
            "passo": 4,
            "titulo": "Solicite o saque",
            "descricao": "Escolha como quer receber: Pix, transferência ou presencial",
            "acao": "Se tiver Pix, é a forma mais rápida!"
        },
        {
            "passo": 5,
            "titulo": "Aguarde o depósito",
            "descricao": "O dinheiro cai em alguns dias úteis",
            "acao": "Guarde o comprovante da solicitação"
        }
    ]

    return ToolResult.ok(
        data={
            "programa": programa,
            "passo_a_passo": passo_a_passo,
            "alerta_prazo": "IMPORTANTE: O prazo vai até 2028. Depois disso, o dinheiro vai para o governo!",
            "dica_herdeiros": "Se você é herdeiro de alguém que trabalhou nessa época, também pode ter direito!"
        },
        ui_hint=UIHint.CHECKLIST,
        context_updates={"guia_pis_pasep_mostrado": True}
    )


def guia_svr() -> ToolResult:
    """
    Retorna guia completo para consultar Valores a Receber (SVR).

    R$ 8-10 bilhões disponíveis para 48 milhões de pessoas.
    """
    programa = PROGRAMAS_DINHEIRO["svr"]

    passo_a_passo = [
        {
            "passo": 1,
            "titulo": "Acesse o site do Banco Central",
            "descricao": "Entre em valoresareceber.bcb.gov.br",
            "acao": "Use seu login Gov.br"
        },
        {
            "passo": 2,
            "titulo": "Faça a consulta",
            "descricao": "Digite seu CPF e data de nascimento",
            "acao": "O sistema vai mostrar se você tem valores"
        },
        {
            "passo": 3,
            "titulo": "Veja de onde vem o dinheiro",
            "descricao": "Pode ser de conta antiga, tarifa cobrada errada, consórcio...",
            "acao": "Clique em cada valor para ver os detalhes"
        },
        {
            "passo": 4,
            "titulo": "Solicite o resgate",
            "descricao": "Informe sua chave Pix para receber",
            "acao": "IMPORTANTE: Você precisa ter uma chave Pix cadastrada"
        },
        {
            "passo": 5,
            "titulo": "Aguarde o depósito",
            "descricao": "O banco tem até 12 dias úteis para depositar",
            "acao": "Acompanhe pelo mesmo site"
        }
    ]

    return ToolResult.ok(
        data={
            "programa": programa,
            "passo_a_passo": passo_a_passo,
            "dica": "Consulte a cada 3 meses! Novos valores são adicionados frequentemente.",
            "alerta": "CUIDADO com golpes! O único site oficial é valoresareceber.bcb.gov.br"
        },
        ui_hint=UIHint.CHECKLIST,
        context_updates={"guia_svr_mostrado": True}
    )


def guia_fgts() -> ToolResult:
    """
    Retorna guia completo para consultar e sacar FGTS.

    R$ 7,8 bilhões retidos de 14 milhões de trabalhadores.
    URGENTE: Prazo 30/12/2025 para Saque-Aniversário.
    """
    programa = PROGRAMAS_DINHEIRO["fgts"]

    passo_a_passo = [
        {
            "passo": 1,
            "titulo": "Baixe o app FGTS",
            "descricao": "Procure 'FGTS' na loja do seu celular (é da Caixa)",
            "acao": "É grátis e oficial"
        },
        {
            "passo": 2,
            "titulo": "Faça login",
            "descricao": "Use seu CPF e crie uma senha",
            "acao": "Você também pode usar o Gov.br"
        },
        {
            "passo": 3,
            "titulo": "Veja seu saldo",
            "descricao": "O app mostra todas as suas contas de FGTS",
            "acao": "Pode ter saldo de empregos antigos que você esqueceu!"
        },
        {
            "passo": 4,
            "titulo": "Verifique o Saque-Aniversário",
            "descricao": "Se você aderiu, veja se tem parcela para sacar",
            "acao": "PRAZO: até 30 de dezembro de 2025!"
        },
        {
            "passo": 5,
            "titulo": "Solicite o saque",
            "descricao": "Escolha a conta para receber (Caixa Tem é mais rápido)",
            "acao": "Ou vá a uma agência da Caixa com RG e CPF"
        }
    ]

    return ToolResult.ok(
        data={
            "programa": programa,
            "passo_a_passo": passo_a_passo,
            "alerta_urgente": "URGENTE: Se você aderiu ao Saque-Aniversário, precisa sacar até 30/12/2025!",
            "dica": "Mesmo sem Saque-Aniversário, você pode ter FGTS de empregos antigos"
        },
        ui_hint=UIHint.CHECKLIST,
        context_updates={"guia_fgts_mostrado": True}
    )


def verificar_dinheiro_por_perfil(
    trabalhou_antes_1988: Optional[bool] = None,
    teve_carteira_assinada: Optional[bool] = None,
    teve_conta_banco: Optional[bool] = None,
    idade: Optional[int] = None
) -> ToolResult:
    """
    Verifica quais tipos de dinheiro esquecido o cidadão pode ter direito
    baseado no seu perfil.

    Args:
        trabalhou_antes_1988: Se trabalhou com carteira entre 1971-1988
        teve_carteira_assinada: Se já trabalhou com carteira assinada
        teve_conta_banco: Se já teve conta em banco
        idade: Idade do cidadão

    Returns:
        Lista de programas que o cidadão provavelmente tem direito
    """
    recomendacoes = []

    # PIS/PASEP - quem trabalhou antes de 1988
    if trabalhou_antes_1988 or (idade and idade > 55):
        recomendacoes.append({
            "programa": "pis_pasep",
            "nome": "PIS/PASEP",
            "probabilidade": "ALTA" if trabalhou_antes_1988 else "MÉDIA",
            "motivo": "Você pode ter trabalhado no período 1971-1988",
            "valor_medio": "R$ 2.800",
            "acao": "Consulte em repiscidadao.fazenda.gov.br"
        })

    # SVR - todo mundo pode ter
    recomendacoes.append({
        "programa": "svr",
        "nome": "Valores a Receber",
        "probabilidade": "MÉDIA",
        "motivo": "Qualquer pessoa pode ter valores de contas antigas ou tarifas",
        "valor_medio": "Varia muito",
        "acao": "Consulte em valoresareceber.bcb.gov.br"
    })

    # FGTS - quem trabalhou com carteira
    if teve_carteira_assinada:
        recomendacoes.append({
            "programa": "fgts",
            "nome": "FGTS",
            "probabilidade": "ALTA",
            "motivo": "Você trabalhou com carteira e pode ter saldo esquecido",
            "valor_medio": "Depende do tempo de trabalho",
            "acao": "Baixe o app FGTS e consulte"
        })

    return ToolResult.ok(
        data={
            "recomendacoes": recomendacoes,
            "total_programas": len(recomendacoes),
            "mensagem": f"Encontrei {len(recomendacoes)} tipos de dinheiro que você pode ter direito!"
        },
        ui_hint=UIHint.BENEFIT_LIST
    )


def _formatar_mensagem_simples(programa: Dict[str, Any]) -> str:
    """Formata mensagem em linguagem simples sobre o programa."""
    return f"""
{programa['nome']}

Quanto tem disponível: {programa['valor_total']}
Quantas pessoas têm direito: {programa['beneficiarios']}
Valor médio por pessoa: {programa['media_por_pessoa']}

Prazo: {programa['prazo']}

Como consultar:
{programa['como_consultar'].get('online', programa['como_consultar'].get('app', ''))}

Link oficial: {programa['link']}

{programa.get('dica', programa.get('alerta', ''))}
""".strip()


# =============================================================================
# NOVAS FUNÇÕES: Fluxo Proativo de Descoberta
# =============================================================================

def iniciar_caca_ao_tesouro() -> ToolResult:
    """
    Inicia o fluxo "Caça ao Tesouro" - descoberta proativa de dinheiro esquecido.

    Retorna checklist das 3 fontes principais que o cidadão deve verificar.
    """
    checklist = []

    for fonte in FONTES_DINHEIRO_ESQUECIDO:
        checklist.append({
            "fonte": fonte["fonte"],
            "onde": fonte["onde_consultar"],
            "prazo": fonte["prazo"],
            "urgente": fonte["urgente"],
            "quem_pode_ter": fonte["quem_pode_ter"],
            "verificado": False
        })

    mensagem = """Voce sabia que pode ter dinheiro esquecido pra receber?

Existem 3 lugares onde voce pode ter dinheiro parado:

1. PIS/PASEP ANTIGO (URGENTE - prazo ate 2028!)
   Quem trabalhou com carteira de 1971 a 1988
   Valor medio: R$ 2.800

2. FGTS DE EMPREGOS ANTIGOS
   Quem ja trabalhou de carteira assinada
   Pode ter saldo que nunca sacou

3. VALORES A RECEBER (Banco Central)
   Quem ja teve conta em banco
   Pode ter dinheiro de conta antiga, tarifa cobrada errada...

Quer que eu te ensine a verificar cada um?"""

    return ToolResult.ok(
        data={
            "checklist": checklist,
            "total_fontes": len(checklist),
            "mensagem_simples": mensagem
        },
        ui_hint=UIHint.CHECKLIST,
        context_updates={"fluxo_dinheiro_esquecido": "iniciado"}
    )


def guia_passo_a_passo_pis_pasep_antigo() -> ToolResult:
    """
    Guia passo a passo para verificar PIS/PASEP antigo (1971-1988).

    R$ 26 bilhões disponíveis para 10,5 milhões de pessoas.
    Prazo: até 2028 - depois o dinheiro vai pro Tesouro!
    """
    passos = [
        {
            "passo": 1,
            "titulo": "Baixe o app FGTS",
            "descricao": "Procure 'FGTS' na loja do celular. E de graca e oficial da Caixa.",
            "acao": "Baixar app FGTS",
            "link": "https://www.caixa.gov.br/atendimento/aplicativos/fgts/Paginas/default.aspx"
        },
        {
            "passo": 2,
            "titulo": "Entre com sua conta Gov.br",
            "descricao": "Use seu CPF e senha do Gov.br. Se nao tiver conta, o app ajuda a criar.",
            "acao": "Fazer login",
            "dica": "Precisa ser nivel prata ou ouro. Se for bronze, o app explica como subir."
        },
        {
            "passo": 3,
            "titulo": "Va em 'Meus Saques'",
            "descricao": "No menu principal, clique em 'Meus Saques'.",
            "acao": "Abrir Meus Saques"
        },
        {
            "passo": 4,
            "titulo": "Procure 'PIS/PASEP'",
            "descricao": "Vai aparecer se voce tem dinheiro. Se nao aparecer nada, tambem pode consultar no site.",
            "acao": "Verificar saldo",
            "alternativa": "Site: repiscidadao.fazenda.gov.br"
        },
        {
            "passo": 5,
            "titulo": "Solicite o saque",
            "descricao": "Se tiver valor, escolha como quer receber: Pix e o mais rapido!",
            "acao": "Pedir saque",
            "opcoes": ["Pix (mais rapido)", "Conta bancaria", "Presencial na Caixa"]
        }
    ]

    return ToolResult.ok(
        data={
            "programa": "PIS/PASEP Antigo (1971-1988)",
            "passos": passos,
            "total_passos": len(passos),
            "prazo_limite": "2028",
            "alerta": "URGENTE: So 0,25% das pessoas sacaram! Depois de 2028, o dinheiro vai pro governo!",
            "valor_medio": "R$ 2.800",
            "dica_final": "Nao tem Gov.br? Va a uma agencia da Caixa com RG e CPF."
        },
        ui_hint=UIHint.CHECKLIST,
        context_updates={"guia_pis_pasep_antigo": True}
    )


def guia_passo_a_passo_svr() -> ToolResult:
    """
    Guia passo a passo para verificar Valores a Receber (SVR) do Banco Central.

    R$ 8-10 bilhões disponíveis para 48 milhões de pessoas.
    """
    passos = [
        {
            "passo": 1,
            "titulo": "Acesse o site oficial",
            "descricao": "Entre em valoresareceber.bcb.gov.br - esse eh o UNICO site oficial!",
            "acao": "Abrir site",
            "link": "https://valoresareceber.bcb.gov.br",
            "alerta": "CUIDADO COM GOLPES! Nao existe app, so o site!"
        },
        {
            "passo": 2,
            "titulo": "Faca login com Gov.br",
            "descricao": "Use seu CPF e senha do Gov.br.",
            "acao": "Fazer login",
            "dica": "Precisa ser nivel prata ou ouro."
        },
        {
            "passo": 3,
            "titulo": "Consulte seus valores",
            "descricao": "O sistema mostra se voce tem dinheiro em algum banco.",
            "acao": "Ver valores",
            "exemplos": ["Conta antiga fechada com saldo", "Tarifa cobrada errada", "Consorcio"]
        },
        {
            "passo": 4,
            "titulo": "Solicite o resgate",
            "descricao": "Informe sua chave Pix para receber. E a unica forma!",
            "acao": "Pedir resgate",
            "importante": "Voce PRECISA ter uma chave Pix cadastrada!"
        },
        {
            "passo": 5,
            "titulo": "Aguarde o deposito",
            "descricao": "O banco tem ate 12 dias uteis para depositar na sua conta.",
            "acao": "Acompanhar pelo site"
        }
    ]

    return ToolResult.ok(
        data={
            "programa": "Valores a Receber (SVR)",
            "passos": passos,
            "total_passos": len(passos),
            "link_oficial": "https://valoresareceber.bcb.gov.br",
            "alerta_golpe": "CUIDADO: Nao existe app! O unico site oficial eh valoresareceber.bcb.gov.br",
            "dica": "Consulte a cada 3 meses - novos valores sao adicionados!"
        },
        ui_hint=UIHint.CHECKLIST,
        context_updates={"guia_svr": True}
    )


def guia_passo_a_passo_fgts() -> ToolResult:
    """
    Guia passo a passo para verificar FGTS de empregos antigos.

    Milhões de brasileiros têm FGTS esquecido de empregos passados.
    """
    passos = [
        {
            "passo": 1,
            "titulo": "Baixe o app FGTS",
            "descricao": "Procure 'FGTS' na loja do celular. E de graca e oficial da Caixa.",
            "acao": "Baixar app FGTS",
            "link": "https://www.caixa.gov.br/atendimento/aplicativos/fgts/Paginas/default.aspx"
        },
        {
            "passo": 2,
            "titulo": "Faca login",
            "descricao": "Use seu CPF e crie uma senha. Ou use sua conta Gov.br.",
            "acao": "Fazer login"
        },
        {
            "passo": 3,
            "titulo": "Veja TODAS as suas contas",
            "descricao": "O app mostra todas as contas de FGTS que voce tem - ate de empregos que voce esqueceu!",
            "acao": "Ver minhas contas",
            "dica": "Olhe as contas 'inativas' - sao de empregos antigos!"
        },
        {
            "passo": 4,
            "titulo": "Verifique o Saque-Aniversario",
            "descricao": "Se voce aderiu, veja se tem parcela pra sacar.",
            "acao": "Verificar saque disponivel",
            "importante": "Quem aderiu ao Saque-Aniversario: o prazo pra sacar eh de 90 dias apos seu aniversario!"
        },
        {
            "passo": 5,
            "titulo": "Solicite o saque",
            "descricao": "Escolha pra qual conta quer receber. Caixa Tem eh mais rapido!",
            "acao": "Pedir saque",
            "opcoes": ["Caixa Tem", "Conta em outro banco", "Presencial na Caixa"]
        }
    ]

    return ToolResult.ok(
        data={
            "programa": "FGTS de Empregos Antigos",
            "passos": passos,
            "total_passos": len(passos),
            "link_app": "https://www.caixa.gov.br/atendimento/aplicativos/fgts/Paginas/default.aspx",
            "dica": "Mesmo sem Saque-Aniversario, voce pode ter FGTS de empregos antigos que nunca sacou!"
        },
        ui_hint=UIHint.CHECKLIST,
        context_updates={"guia_fgts_detalhado": True}
    )


def verificar_perfil_dinheiro_esquecido(
    idade: Optional[int] = None,
    trabalhou_carteira: Optional[bool] = None,
    trabalhou_antes_1988: Optional[bool] = None,
    teve_conta_banco: Optional[bool] = None
) -> ToolResult:
    """
    Analisa perfil do cidadão e indica quais fontes de dinheiro esquecido verificar.

    Args:
        idade: Idade do cidadão (ajuda a estimar se trabalhou antes de 1988)
        trabalhou_carteira: Se já trabalhou com carteira assinada
        trabalhou_antes_1988: Se trabalhou especificamente entre 1971-1988
        teve_conta_banco: Se já teve conta em banco

    Returns:
        Lista priorizada de fontes para verificar
    """
    fontes_verificar = []

    # PIS/PASEP Antigo - PRIORIDADE MÁXIMA (prazo 2028!)
    if trabalhou_antes_1988 is True:
        fontes_verificar.append({
            "fonte": "PIS/PASEP Antigo",
            "prioridade": "URGENTE",
            "motivo": "Voce trabalhou entre 1971 e 1988 - MUITO PROVAVELMENTE tem dinheiro!",
            "valor_estimado": "Ate R$ 2.800 em media",
            "prazo": "Ate 2028 - depois perde!",
            "onde": "App FGTS > Meus Saques > PIS/PASEP"
        })
    elif idade and idade >= 55:
        # Se tem mais de 55 anos, pode ter trabalhado antes de 1988
        fontes_verificar.append({
            "fonte": "PIS/PASEP Antigo",
            "prioridade": "ALTA",
            "motivo": "Pela sua idade, voce pode ter trabalhado entre 1971 e 1988. Vale verificar!",
            "valor_estimado": "Ate R$ 2.800 em media",
            "prazo": "Ate 2028 - depois perde!",
            "onde": "App FGTS > Meus Saques > PIS/PASEP"
        })

    # FGTS de empregos antigos
    if trabalhou_carteira is True:
        fontes_verificar.append({
            "fonte": "FGTS de Empregos Antigos",
            "prioridade": "MEDIA",
            "motivo": "Voce trabalhou de carteira. Pode ter saldo de empregos antigos!",
            "valor_estimado": "Depende do tempo de trabalho",
            "prazo": "Sem prazo",
            "onde": "App FGTS > Minhas Contas"
        })

    # SVR - todo mundo pode ter
    fontes_verificar.append({
        "fonte": "Valores a Receber (Banco Central)",
        "prioridade": "MEDIA" if teve_conta_banco else "BAIXA",
        "motivo": "Qualquer pessoa pode ter. Verifica so pra garantir!",
        "valor_estimado": "Varia muito",
        "prazo": "Sem prazo",
        "onde": "valoresareceber.bcb.gov.br"
    })

    # Calcular potencial total
    potencial_total = "Pode ser de R$ 1 ate mais de R$ 30.000!"
    if trabalhou_antes_1988:
        potencial_total = "Pode ter ate R$ 3.000 ou mais!"

    return ToolResult.ok(
        data={
            "fontes_verificar": fontes_verificar,
            "total_fontes": len(fontes_verificar),
            "potencial_total": potencial_total,
            "mensagem": f"Encontrei {len(fontes_verificar)} lugares onde voce pode ter dinheiro esquecido!"
        },
        ui_hint=UIHint.BENEFIT_LIST,
        context_updates={"perfil_dinheiro_analisado": True}
    )


def resumo_caca_ao_tesouro() -> ToolResult:
    """
    Retorna resumo de todas as fontes de dinheiro esquecido com dados atualizados.

    Útil para dar uma visão geral ao cidadão.
    """
    resumo = {
        "total_disponivel": "Mais de R$ 70 bilhoes",
        "fontes": [
            {
                "nome": "PIS/PASEP Antigo (1971-1988)",
                "valor": "R$ 26 bilhoes",
                "pessoas": "10,5 milhoes",
                "sacaram": "Menos de 0,25%",
                "prazo": "2028",
                "urgente": True
            },
            {
                "nome": "Abono PIS/PASEP 2026",
                "valor": "R$ 33,5 bilhoes",
                "pessoas": "26,9 milhoes",
                "prazo": "Dezembro 2026",
                "urgente": False
            },
            {
                "nome": "FGTS Esquecido",
                "valor": "Bilhoes",
                "pessoas": "Milhoes",
                "prazo": "Sem prazo",
                "urgente": False
            },
            {
                "nome": "Valores a Receber (SVR)",
                "valor": "R$ 8 a 10 bilhoes",
                "pessoas": "48 milhoes",
                "prazo": "Continuo",
                "urgente": False
            }
        ],
        "mensagem": """TEM DINHEIRO ESQUECIDO NO BRASIL!

R$ 26 BILHOES em PIS/PASEP antigo - e so 0,25% das pessoas sacaram!

Se voce trabalhou com carteira antes de 1988, MUITO PROVAVELMENTE tem dinheiro pra receber.

Prazo: ate 2028. Depois disso, o dinheiro vai pro governo!

Quer que eu te ensine a verificar?"""
    }

    return ToolResult.ok(
        data=resumo,
        ui_hint=UIHint.INFO
    )
