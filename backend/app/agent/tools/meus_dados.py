"""
Tool para consulta consolidada "Meus Dados".

Permite ao cidadão ver todos os seus dados em um só lugar:
- Benefícios ativos
- Alertas importantes
- Próximos passos recomendados
- Dinheiro esquecido que pode ter direito
"""

import re
from datetime import date
from typing import Dict, Any, List
from dateutil.relativedelta import relativedelta

from app.database import SessionLocal
from app.models.beneficiario import Beneficiario, mask_cpf
from app.agent.tools.base import ToolResult, UIHint


def meus_dados(cpf: str) -> ToolResult:
    """
    Retorna visão consolidada de todos os dados do cidadão.

    Inclui:
    - Benefícios ativos e valores
    - Alertas importantes (CadÚnico desatualizado, etc)
    - Sugestões de outros benefícios
    - Indicação de dinheiro esquecido

    Args:
        cpf: CPF do cidadão (11 dígitos, com ou sem formatação)

    Returns:
        ToolResult com dados consolidados
    """
    # Limpa CPF
    cpf_limpo = re.sub(r'\D', '', cpf)

    if len(cpf_limpo) != 11:
        return ToolResult.fail(
            error=f"CPF precisa ter 11 números. Você informou {len(cpf_limpo)}.",
            error_code="CPF_INVALIDO"
        )

    if cpf_limpo == cpf_limpo[0] * 11:
        return ToolResult.fail(
            error="CPF inválido: todos os dígitos são iguais.",
            error_code="CPF_INVALIDO"
        )

    db = SessionLocal()
    try:
        beneficiario = Beneficiario.buscar_por_cpf(db, cpf_limpo)

        if not beneficiario:
            # Cidadão não encontrado - ainda assim pode ter dinheiro esquecido
            return ToolResult.ok(
                data={
                    "encontrado": False,
                    "cpf_masked": mask_cpf(cpf_limpo),
                    "beneficios_ativos": [],
                    "alertas": [],
                    "sugestoes": [
                        {
                            "tipo": "DINHEIRO_ESQUECIDO",
                            "titulo": "Você pode ter dinheiro esquecido!",
                            "descricao": "Mesmo sem benefícios cadastrados, você pode ter PIS/PASEP, FGTS ou Valores a Receber no Banco Central.",
                            "acao": "Quer que eu te ajude a consultar?"
                        },
                        {
                            "tipo": "CADUNICO",
                            "titulo": "Faça seu CadÚnico",
                            "descricao": "O CadÚnico é a porta de entrada para vários benefícios do governo.",
                            "acao": "Posso te mostrar os documentos necessários."
                        }
                    ],
                    "mensagem_simples": _gerar_mensagem_nao_encontrado()
                },
                ui_hint=UIHint.INFO
            )

        # Monta dados consolidados
        beneficios_ativos = _extrair_beneficios_ativos(beneficiario)
        alertas = _gerar_alertas(beneficiario)
        sugestoes = _gerar_sugestoes(beneficiario)
        resumo_valores = _calcular_resumo_valores(beneficiario)

        return ToolResult.ok(
            data={
                "encontrado": True,
                "cpf_masked": beneficiario.cpf_masked,
                "nome": beneficiario.nome,
                "uf": beneficiario.uf,
                "beneficios_ativos": beneficios_ativos,
                "resumo_valores": resumo_valores,
                "alertas": alertas,
                "sugestoes": sugestoes,
                "ultima_atualizacao": beneficiario.atualizado_em.isoformat() if beneficiario.atualizado_em else None,
                "mensagem_simples": _gerar_mensagem_encontrado(beneficiario, beneficios_ativos, alertas)
            },
            ui_hint=UIHint.BENEFIT_LIST,
            context_updates={
                "cpf": cpf_limpo,
                "meus_dados_consultado": True,
                "tem_beneficios": len(beneficios_ativos) > 0
            }
        )

    finally:
        db.close()


def gerar_alertas_beneficios(cpf: str) -> ToolResult:
    """
    Gera alertas proativos sobre benefícios do cidadão.

    Verifica:
    - CadÚnico desatualizado (>2 anos)
    - Benefícios próximos de expirar
    - Documentos que podem estar vencidos
    - Oportunidades de novos benefícios

    Args:
        cpf: CPF do cidadão

    Returns:
        ToolResult com lista de alertas
    """
    cpf_limpo = re.sub(r'\D', '', cpf)

    if len(cpf_limpo) != 11:
        return ToolResult.fail(
            error="CPF inválido",
            error_code="CPF_INVALIDO"
        )

    db = SessionLocal()
    try:
        beneficiario = Beneficiario.buscar_por_cpf(db, cpf_limpo)

        alertas = []

        if not beneficiario:
            # Alertas genéricos para quem não tem cadastro
            alertas.append({
                "tipo": "OPORTUNIDADE",
                "urgencia": "media",
                "titulo": "Você pode ter dinheiro esquecido",
                "descricao": "R$ 42 bilhões estão esquecidos em PIS/PASEP, Valores a Receber e FGTS.",
                "acao": "Consulte agora"
            })
            alertas.append({
                "tipo": "CADASTRO",
                "urgencia": "baixa",
                "titulo": "Faça seu CadÚnico",
                "descricao": "O CadÚnico dá acesso a vários benefícios do governo.",
                "acao": "Veja os documentos necessários"
            })
        else:
            alertas = _gerar_alertas(beneficiario)

        # Sempre adicionar alerta de FGTS se for final de ano
        hoje = date.today()
        if hoje.month >= 10:  # Outubro em diante
            alertas.append({
                "tipo": "URGENTE",
                "urgencia": "alta",
                "titulo": "FGTS Saque-Aniversário",
                "descricao": f"Se você aderiu ao Saque-Aniversário, o prazo para sacar é 30/12/{hoje.year}!",
                "acao": "Consulte seu FGTS"
            })

        return ToolResult.ok(
            data={
                "cpf_masked": mask_cpf(cpf_limpo),
                "alertas": alertas,
                "total_alertas": len(alertas),
                "tem_urgentes": any(a.get("urgencia") == "alta" for a in alertas)
            },
            ui_hint=UIHint.WARNING if alertas else UIHint.INFO
        )

    finally:
        db.close()


def _extrair_beneficios_ativos(beneficiario: Beneficiario) -> List[Dict[str, Any]]:
    """Extrai lista de benefícios ativos do cidadão."""
    beneficios = []

    if beneficiario.bf_ativo:
        valor = float(beneficiario.bf_valor) if beneficiario.bf_valor else 0
        beneficios.append({
            "programa": "BOLSA_FAMILIA",
            "nome": "Bolsa Família",
            "nome_simples": "Bolsa Família",
            "ativo": True,
            "valor": valor,
            "valor_formatado": f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "frequencia": "mensal",
            "referencia": beneficiario.bf_parcela_mes,
            "icone": "💰"
        })

    if beneficiario.bpc_ativo:
        valor = float(beneficiario.bpc_valor) if beneficiario.bpc_valor else 0
        tipo = beneficiario.bpc_tipo or "BPC"
        nome_simples = "Ajuda para idosos" if "IDOSO" in tipo.upper() else "Ajuda para pessoas com deficiência"
        beneficios.append({
            "programa": "BPC",
            "nome": f"BPC ({tipo})",
            "nome_simples": nome_simples,
            "ativo": True,
            "valor": valor,
            "valor_formatado": f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "frequencia": "mensal",
            "referencia": beneficiario.bpc_data_referencia.isoformat() if beneficiario.bpc_data_referencia else None,
            "icone": "🤝"
        })

    if beneficiario.cadunico_ativo:
        faixa = beneficiario.cadunico_faixa_renda or "Cadastrado"
        # Traduz faixa para linguagem simples
        faixa_simples = {
            "EXTREMA_POBREZA": "renda muito baixa",
            "POBREZA": "renda baixa",
            "BAIXA_RENDA": "renda média-baixa"
        }.get(faixa, faixa.lower().replace("_", " "))

        beneficios.append({
            "programa": "CADUNICO",
            "nome": "CadÚnico",
            "nome_simples": "Cadastro do Governo",
            "ativo": True,
            "valor": None,
            "valor_formatado": None,
            "faixa_renda": faixa,
            "faixa_simples": faixa_simples,
            "ultima_atualizacao": beneficiario.cadunico_data_atualizacao.isoformat() if beneficiario.cadunico_data_atualizacao else None,
            "icone": "📋"
        })

    return beneficios


def _gerar_alertas(beneficiario: Beneficiario) -> List[Dict[str, Any]]:
    """Gera alertas baseados na situação do cidadão."""
    alertas = []
    hoje = date.today()

    # Alerta de CadÚnico desatualizado (>2 anos)
    if beneficiario.cadunico_ativo and beneficiario.cadunico_data_atualizacao:
        tempo_desde_atualizacao = relativedelta(hoje, beneficiario.cadunico_data_atualizacao)
        meses = tempo_desde_atualizacao.years * 12 + tempo_desde_atualizacao.months

        if meses >= 24:
            alertas.append({
                "tipo": "CADUNICO_DESATUALIZADO",
                "urgencia": "alta",
                "titulo": "CadÚnico precisa ser atualizado!",
                "descricao": f"Seu cadastro está sem atualização há {meses} meses. O prazo é de 2 anos.",
                "acao": "Vá ao CRAS para atualizar",
                "icone": "⚠️"
            })
        elif meses >= 18:
            alertas.append({
                "tipo": "CADUNICO_ATENCAO",
                "urgencia": "media",
                "titulo": "CadÚnico vai precisar de atualização em breve",
                "descricao": f"Seu cadastro foi atualizado há {meses} meses. Atualize antes de completar 2 anos.",
                "acao": "Planeje ir ao CRAS nos próximos meses",
                "icone": "📋"
            })

    # Alerta de Bolsa Família sem pagamento recente
    if beneficiario.bf_ativo and beneficiario.bf_parcela_mes:
        try:
            ano_mes = beneficiario.bf_parcela_mes.split("-")
            if len(ano_mes) == 2:
                ultima_parcela = date(int(ano_mes[0]), int(ano_mes[1]), 1)
                meses_sem_pagamento = relativedelta(hoje, ultima_parcela).months + relativedelta(hoje, ultima_parcela).years * 12
                if meses_sem_pagamento >= 2:
                    alertas.append({
                        "tipo": "BF_PAGAMENTO_ATRASADO",
                        "urgencia": "alta",
                        "titulo": "Bolsa Família pode estar bloqueado",
                        "descricao": f"Última parcela registrada: {beneficiario.bf_parcela_mes}. Verifique se há pendências.",
                        "acao": "Consulte no app Bolsa Família ou vá ao CRAS",
                        "icone": "🚨"
                    })
        except (ValueError, IndexError):
            pass

    # Sugestão de Tarifa Social se tem CadÚnico mas não tem benefício registrado
    if beneficiario.cadunico_ativo:
        faixa = (beneficiario.cadunico_faixa_renda or "").upper()
        if "EXTREMA" in faixa or "POBREZA" in faixa:
            alertas.append({
                "tipo": "OPORTUNIDADE",
                "urgencia": "baixa",
                "titulo": "Você pode ter desconto na conta de luz",
                "descricao": "Com seu CadÚnico, você pode solicitar a Tarifa Social de Energia Elétrica.",
                "acao": "Solicite na sua empresa de luz",
                "icone": "💡"
            })

    # Sempre sugerir consultar dinheiro esquecido
    alertas.append({
        "tipo": "DINHEIRO_ESQUECIDO",
        "urgencia": "baixa",
        "titulo": "Consulte dinheiro esquecido",
        "descricao": "Você pode ter PIS/PASEP, FGTS ou Valores a Receber no Banco Central.",
        "acao": "Consulte agora",
        "icone": "💰"
    })

    return alertas


def _gerar_sugestoes(beneficiario: Beneficiario) -> List[Dict[str, Any]]:
    """Gera sugestões de benefícios baseadas no perfil."""
    sugestoes = []

    # Se tem CadÚnico mas não tem Bolsa Família
    if beneficiario.cadunico_ativo and not beneficiario.bf_ativo:
        sugestoes.append({
            "programa": "BOLSA_FAMILIA",
            "titulo": "Você pode ter direito ao Bolsa Família",
            "descricao": "Você tem CadÚnico ativo. Verifique se sua família atende aos critérios.",
            "acao": "Verificar elegibilidade"
        })

    # Farmácia Popular para todos
    sugestoes.append({
        "programa": "FARMACIA_POPULAR",
        "titulo": "Remédios de graça ou com desconto",
        "descricao": "O Farmácia Popular oferece medicamentos gratuitos para hipertensão, diabetes e mais.",
        "acao": "Ver lista de remédios"
    })

    # Dignidade Menstrual se CadÚnico ativo
    if beneficiario.cadunico_ativo:
        sugestoes.append({
            "programa": "DIGNIDADE_MENSTRUAL",
            "titulo": "Absorventes gratuitos",
            "descricao": "Mulheres com CadÚnico podem receber absorventes gratuitos nas farmácias.",
            "acao": "Saiba como retirar"
        })

    return sugestoes


def _calcular_resumo_valores(beneficiario: Beneficiario) -> Dict[str, Any]:
    """Calcula resumo de valores recebidos."""
    total_mensal = 0

    if beneficiario.bf_ativo and beneficiario.bf_valor:
        total_mensal += float(beneficiario.bf_valor)

    if beneficiario.bpc_ativo and beneficiario.bpc_valor:
        total_mensal += float(beneficiario.bpc_valor)

    return {
        "total_mensal": total_mensal,
        "total_mensal_formatado": f"R$ {total_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "estimativa_anual": total_mensal * 12,
        "estimativa_anual_formatado": f"R$ {total_mensal * 12:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    }


def _gerar_mensagem_nao_encontrado() -> str:
    """Gera mensagem para cidadão não encontrado."""
    return """
Não encontrei seus dados nos registros de benefícios.

Isso pode significar:
• Você ainda não está no CadÚnico
• Seu CPF foi digitado incorretamente
• Os dados ainda não foram atualizados

MAS ATENÇÃO: Mesmo sem benefícios, você pode ter DINHEIRO ESQUECIDO!

Quer que eu te ajude a consultar:
• PIS/PASEP (quem trabalhou antes de 1988)
• Valores a Receber no Banco Central
• FGTS de empregos antigos
""".strip()


def _gerar_mensagem_encontrado(
    beneficiario: Beneficiario,
    beneficios: List[Dict],
    alertas: List[Dict]
) -> str:
    """Gera mensagem resumida para cidadão encontrado."""
    partes = [f"Olá, {beneficiario.nome or 'cidadão'}!"]
    partes.append("")

    if beneficios:
        partes.append("Seus benefícios ativos:")
        for b in beneficios:
            if b.get("valor_formatado"):
                partes.append(f"• {b['nome_simples']}: {b['valor_formatado']}/mês")
            else:
                partes.append(f"• {b['nome_simples']}")
    else:
        partes.append("Você não tem benefícios ativos no momento.")

    # Alertas importantes
    alertas_urgentes = [a for a in alertas if a.get("urgencia") == "alta"]
    if alertas_urgentes:
        partes.append("")
        partes.append("⚠️ ATENÇÃO:")
        for a in alertas_urgentes:
            partes.append(f"• {a['titulo']}")

    return "\n".join(partes)
