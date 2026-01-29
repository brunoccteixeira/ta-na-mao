"""
Tool para consulta de dinheiro esquecido: PIS/PASEP, SVR e FGTS.

Ajuda cidadãos a descobrirem e resgatarem valores que têm direito.
Total estimado: R$ 42 bilhões disponíveis para resgate.
"""

from typing import Dict, Any, Optional
from app.agent.tools.base import ToolResult, UIHint


# =============================================================================
# Dados sobre os programas de dinheiro esquecido
# =============================================================================

PROGRAMAS_DINHEIRO = {
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
        "dica": "Consulte a cada 3 meses - novos valores são adicionados frequentemente!"
    },
    "fgts": {
        "nome": "FGTS Retido (Saque-Aniversário)",
        "valor_total": "R$ 7,8 bilhões",
        "beneficiarios": "14 milhões de trabalhadores",
        "media_por_pessoa": "Varia conforme saldo na conta",
        "prazo": "30 de dezembro de 2025 (primeira parcela)",
        "quem_tem_direito": [
            "Quem aderiu ao Saque-Aniversário e não sacou",
            "Quem tem saldo de FGTS de empregos antigos",
            "Quem foi demitido e não sacou o FGTS"
        ],
        "como_consultar": {
            "app": "Baixe o app FGTS (da Caixa) e faça login com seu CPF",
            "online": "Acesse fgts.caixa.gov.br",
            "presencial": "Vá a uma agência da Caixa com RG, CPF e Carteira de Trabalho"
        },
        "como_sacar": {
            "app": "Pelo app FGTS você pode transferir para sua conta",
            "caixa_tem": "Se tiver Caixa Tem, cai automaticamente",
            "presencial": "Na agência da Caixa com documentos"
        },
        "documentos": ["RG ou CNH", "CPF", "Carteira de Trabalho"],
        "link": "https://www.fgts.gov.br",
        "alerta": "ATENÇÃO: Se você aderiu ao Saque-Aniversário, precisa sacar até 30/12/2025!"
    }
}


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
