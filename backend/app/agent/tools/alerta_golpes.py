"""
Tools de educacao financeira e alerta de golpes.

Detecta tentativas de golpes comuns contra publico de baixa renda,
simulador de orcamento familiar e micro-licoes financeiras.
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# Golpes comuns
# =============================================================================

GOLPES_COMUNS = [
    {
        "nome": "PIX falso / comprovante falso",
        "como_funciona": (
            "O golpista manda um comprovante de PIX falso dizendo que pagou. "
            "Mas o dinheiro nunca caiu na sua conta. Ele pode pedir troco ou "
            "enviar produto antes de voce conferir."
        ),
        "como_evitar": [
            "SEMPRE confira no APP do banco se o dinheiro CAIU na conta",
            "Nunca confie em prints de comprovante - podem ser editados",
            "Nao de troco antes de confirmar no app",
            "Desconfie de pressa para fechar negocio",
        ],
        "palavras_chave": [
            "pix", "comprovante", "transferencia", "pagamento",
            "troco", "caiu", "deposito", "recibo",
        ],
    },
    {
        "nome": "Emprestimo consignado abusivo",
        "como_funciona": (
            "Ligam oferecendo emprestimo facil, especialmente para aposentados. "
            "Pedem dados pessoais e fazem emprestimo sem voce saber. "
            "Descontam direto do beneficio todo mes."
        ),
        "como_evitar": [
            "NUNCA passe CPF ou dados por telefone",
            "Nao aceite emprestimo que voce nao pediu",
            "Consulte o INSS (135) se descontaram sem autorizacao",
            "Nao assine nada que nao entendeu",
        ],
        "palavras_chave": [
            "emprestimo", "consignado", "credito", "aprovado",
            "ligaram", "ofereceram", "desconto no beneficio",
            "aposentadoria", "taxa baixa", "sem consulta",
        ],
    },
    {
        "nome": "Cadastro falso / golpe do CadUnico",
        "como_funciona": (
            "Alguem oferece fazer seu CadUnico 'rapido' cobrando dinheiro. "
            "Ou manda link falso pedindo dados. O CadUnico eh GRATUITO e so "
            "pode ser feito no CRAS."
        ),
        "como_evitar": [
            "CadUnico eh 100% GRATUITO - ninguem pode cobrar",
            "So faca no CRAS (presencial) - nao tem online",
            "NUNCA clique em links de WhatsApp sobre CadUnico",
            "Na duvida, ligue para o CRAS da sua cidade",
        ],
        "palavras_chave": [
            "cadastro rapido", "cadunico online", "pagar cadastro",
            "link", "clique aqui", "atualizar cadastro",
            "taxa", "cobrar", "pagar para cadastrar",
        ],
    },
    {
        "nome": "Piramide financeira / renda extra falsa",
        "como_funciona": (
            "Prometem renda extra facil: 'invista R$100 e ganhe R$1000'. "
            "Pedem para voce convidar mais pessoas. Quem entra primeiro ganha, "
            "mas a maioria perde tudo."
        ),
        "como_evitar": [
            "Se promete lucro garantido, eh GOLPE",
            "Dinheiro nao multiplica sozinho",
            "Se precisa convidar pessoas para ganhar, eh piramide",
            "Denuncie no Procon ou Policia Civil",
        ],
        "palavras_chave": [
            "renda extra", "investimento", "lucro garantido",
            "multiplique", "ganhe dinheiro", "convide amigos",
            "dobrar", "rendimento", "oportunidade unica",
        ],
    },
    {
        "nome": "Golpe do falso beneficio",
        "como_funciona": (
            "Mandam mensagem dizendo que voce tem 'beneficio aprovado' ou "
            "'dinheiro para receber'. Pedem CPF, senha ou taxa para liberar. "
            "Nenhum beneficio do governo cobra taxa."
        ),
        "como_evitar": [
            "Nenhum beneficio cobra taxa - se pedir dinheiro, eh golpe",
            "O governo nao manda link por WhatsApp",
            "Confira no app Caixa Tem ou ligue 121 (Disque Social)",
            "Nunca passe senha ou dados por mensagem",
        ],
        "palavras_chave": [
            "beneficio aprovado", "dinheiro para receber",
            "liberar beneficio", "taxa", "pagar para receber",
            "saque disponivel", "clique para receber",
        ],
    },
]


# =============================================================================
# Microlições financeiras
# =============================================================================

MICROLECOES = [
    {
        "titulo": "Divida boa vs divida ruim",
        "conteudo": (
            "Divida BOA: te ajuda a ganhar mais (curso, ferramenta de trabalho, MEI).\n"
            "Divida RUIM: compra coisa que perde valor (roupa cara, celular parcelado em 24x).\n\n"
            "Regra de ouro: se a parcela passa de 30% da sua renda, NAO parcele!"
        ),
        "dica": "Antes de comprar, pergunte: isso vai me ajudar a ganhar dinheiro?",
    },
    {
        "titulo": "Reserva de emergencia",
        "conteudo": (
            "Guarde pelo menos R$ 50 por mes, mesmo que pouco.\n"
            "Meta: ter 3 meses de despesas guardados.\n"
            "Guarde na POUPANCA ou no Caixa Tem (rende mais que debaixo do colchao!).\n\n"
            "Comece hoje: separe qualquer valor antes de gastar."
        ),
        "dica": "R$ 2 por dia = R$ 60 por mes = R$ 720 por ano!",
    },
    {
        "titulo": "Cuidado com parcelas",
        "conteudo": (
            "12x de R$ 50 parece pouco, mas sao R$ 600!\n"
            "Juros do cartao: ate 400% ao ano.\n"
            "Cheque especial: ate 300% ao ano.\n\n"
            "Sempre pergunte: qual o preco A VISTA? Se for muito diferente, nao parcele."
        ),
        "dica": "Se nao pode pagar a vista, pense se realmente precisa.",
    },
    {
        "titulo": "Seus direitos como consumidor",
        "conteudo": (
            "Comprou e se arrependeu? Tem 7 dias para devolver (compra online/telefone).\n"
            "Produto com defeito? Loja TEM que trocar em 30 dias.\n"
            "Cobranca indevida? Tem que devolver o DOBRO.\n\n"
            "Procon: ligue 151 (gratuito na maioria das cidades)."
        ),
        "dica": "Guarde notas fiscais e comprovantes de pagamento!",
    },
]


# =============================================================================
# Microcrédito
# =============================================================================

OPCOES_MICROCREDITO = [
    {
        "nome": "CrediAmigo (Banco do Nordeste)",
        "descricao": "Emprestimo para pequenos negocios no Nordeste",
        "publico": "Empreendedores informais e MEI da regiao Nordeste",
        "juros": "1,6% ao mes (muito abaixo de banco comum)",
        "valor": "R$ 100 a R$ 21.000",
        "como_pedir": "Va a uma agencia do Banco do Nordeste com CPF e comprovante de endereco",
    },
    {
        "nome": "Agroamigo (Banco do Nordeste)",
        "descricao": "Credito para agricultura familiar no semiarido",
        "publico": "Agricultores familiares com DAP/CAF",
        "juros": "0,5% ao mes",
        "valor": "R$ 300 a R$ 6.000",
        "como_pedir": "Procure um assessor do Agroamigo na sua regiao",
    },
    {
        "nome": "PRONAF (Banco do Brasil / Caixa)",
        "descricao": "Credito rural para agricultura familiar",
        "publico": "Agricultores com DAP/CAF e faturamento ate R$ 500.000/ano",
        "juros": "0,5% a 4% ao ano (muito baixo!)",
        "valor": "Ate R$ 250.000 dependendo da linha",
        "como_pedir": "Va ao banco com DAP/CAF, CPF e projeto de investimento",
    },
    {
        "nome": "Microcredito Produtivo (Caixa/BB)",
        "descricao": "Emprestimo para empreendedores de baixa renda",
        "publico": "Empreendedores informais e MEI com renda ate 3 salarios minimos",
        "juros": "Ate 4% ao mes",
        "valor": "R$ 300 a R$ 20.000",
        "como_pedir": "Procure uma agencia ou correspondente bancario",
    },
]


# =============================================================================
# Tool: verificar_golpe
# =============================================================================

def verificar_golpe(mensagem: str) -> dict:
    """Verifica se uma mensagem contem indicios de golpe.

    Analisa keywords comuns em golpes contra publico de baixa renda.
    Dispara alerta quando 2+ keywords sao encontradas.

    Args:
        mensagem: Texto da mensagem para analisar

    Returns:
        dict com alerta (bool), golpe detectado e orientacoes
    """
    logger.info("Verificando possivel golpe em mensagem")

    mensagem_lower = mensagem.lower()
    golpes_detectados = []

    for golpe in GOLPES_COMUNS:
        matches = [kw for kw in golpe["palavras_chave"] if kw in mensagem_lower]
        if len(matches) >= 2:
            golpes_detectados.append({
                "nome": golpe["nome"],
                "como_funciona": golpe["como_funciona"],
                "como_evitar": golpe["como_evitar"],
                "keywords_detectadas": matches,
                "confianca": min(1.0, len(matches) / 4),
            })

    if golpes_detectados:
        # Ordenar por confianca
        golpes_detectados.sort(key=lambda g: g["confianca"], reverse=True)
        principal = golpes_detectados[0]

        return {
            "alerta": True,
            "golpe_principal": principal["nome"],
            "explicacao": principal["como_funciona"],
            "como_evitar": principal["como_evitar"],
            "confianca": principal["confianca"],
            "total_golpes_detectados": len(golpes_detectados),
            "mensagem_cidadao": (
                f"CUIDADO! Isso parece o golpe '{principal['nome']}'.\n\n"
                f"{principal['como_funciona']}\n\n"
                "O que fazer:\n" +
                "\n".join(f"- {dica}" for dica in principal["como_evitar"][:3])
            ),
        }

    return {
        "alerta": False,
        "mensagem": "Nao detectei sinais de golpe nesta mensagem.",
        "dica": "Na duvida, nunca passe dados pessoais por telefone ou WhatsApp.",
    }


# =============================================================================
# Tool: simular_orcamento
# =============================================================================

def simular_orcamento(
    renda_total: float,
    aluguel: float = 0,
    alimentacao: float = 0,
    transporte: float = 0,
    luz_agua_gas: float = 0,
    saude: float = 0,
    educacao: float = 0,
    outros: float = 0,
) -> dict:
    """Simula orcamento familiar e da orientacoes.

    Metodo simples: "Para onde vai meu dinheiro?"

    Args:
        renda_total: Renda total da familia (todos os ganhos, incluindo beneficios)
        aluguel: Gasto com moradia
        alimentacao: Gasto com comida
        transporte: Gasto com transporte
        luz_agua_gas: Contas de luz, agua, gas
        saude: Remedios, consultas
        educacao: Material escolar, cursos
        outros: Outros gastos

    Returns:
        dict com analise do orcamento e orientacoes
    """
    logger.info(f"Simulando orcamento: renda={renda_total}")

    total_gastos = aluguel + alimentacao + transporte + luz_agua_gas + saude + educacao + outros
    sobra = renda_total - total_gastos

    categorias = []
    if aluguel > 0:
        categorias.append({"nome": "Moradia", "valor": aluguel, "percentual": round(aluguel / renda_total * 100, 1)})
    if alimentacao > 0:
        categorias.append({"nome": "Alimentacao", "valor": alimentacao, "percentual": round(alimentacao / renda_total * 100, 1)})
    if transporte > 0:
        categorias.append({"nome": "Transporte", "valor": transporte, "percentual": round(transporte / renda_total * 100, 1)})
    if luz_agua_gas > 0:
        categorias.append({"nome": "Luz/Agua/Gas", "valor": luz_agua_gas, "percentual": round(luz_agua_gas / renda_total * 100, 1)})
    if saude > 0:
        categorias.append({"nome": "Saude", "valor": saude, "percentual": round(saude / renda_total * 100, 1)})
    if educacao > 0:
        categorias.append({"nome": "Educacao", "valor": educacao, "percentual": round(educacao / renda_total * 100, 1)})
    if outros > 0:
        categorias.append({"nome": "Outros", "valor": outros, "percentual": round(outros / renda_total * 100, 1)})

    # Orientacoes baseadas na situacao
    orientacoes = []
    alertas = []

    if aluguel > 0 and aluguel / renda_total > 0.30:
        alertas.append(
            f"Moradia esta tomando {aluguel / renda_total * 100:.0f}% da renda. "
            "O ideal eh no maximo 30%. Voce pode ter direito a programas de moradia."
        )

    if sobra < 0:
        alertas.append(
            f"Voce esta gastando R$ {abs(sobra):.2f} a MAIS do que ganha! "
            "Isso leva a dividas. Precisa cortar gastos urgente."
        )
        orientacoes.append("Anote TODOS os gastos por 1 semana para encontrar onde cortar")
        orientacoes.append("Corte primeiro o que nao eh essencial (streaming, delivery)")
    elif sobra < renda_total * 0.05:
        orientacoes.append("Sua renda esta bem apertada. Tente economizar pelo menos R$ 50/mes.")
        orientacoes.append("Verifique se tem direito a Tarifa Social de energia (desconto na luz)")
    else:
        orientacoes.append(f"Voce consegue guardar R$ {sobra:.2f}/mes. Otimo!")
        orientacoes.append("Coloque na poupanca ou Caixa Tem para ir rendendo")

    # Beneficios que podem ajudar
    beneficios_sugeridos = []
    if renda_total / max(1, 1) <= 218:  # Simplified - per capita depends on family
        beneficios_sugeridos.append("Bolsa Familia")
    if luz_agua_gas > 0:
        beneficios_sugeridos.append("Tarifa Social de Energia (desconto na luz)")
    if saude > 0:
        beneficios_sugeridos.append("Farmacia Popular (remedios de graca)")

    return {
        "renda_total": renda_total,
        "total_gastos": round(total_gastos, 2),
        "sobra": round(sobra, 2),
        "situacao": "no_vermelho" if sobra < 0 else "apertado" if sobra < renda_total * 0.1 else "ok",
        "categorias": categorias,
        "alertas": alertas,
        "orientacoes": orientacoes,
        "beneficios_sugeridos": beneficios_sugeridos,
        "microlecao": MICROLECOES[1] if sobra >= 0 else MICROLECOES[2],  # Reserva ou parcelas
    }


# =============================================================================
# Tool: consultar_educacao_financeira
# =============================================================================

def consultar_educacao_financeira(
    tema: Optional[str] = None,
) -> dict:
    """Retorna microlecoes de educacao financeira ou opcoes de microcredito.

    Args:
        tema: Tema especifico: golpes, orcamento, dividas, reserva, consumidor,
              microcredito. Se nao informado, lista temas disponiveis.

    Returns:
        dict com conteudo educacional
    """
    logger.info(f"Consulta educacao financeira: tema={tema}")

    if tema:
        tema_lower = tema.lower()

        if "golpe" in tema_lower or "fraude" in tema_lower:
            return {
                "tema": "golpes",
                "titulo": "Cuidado com golpes!",
                "golpes": [
                    {"nome": g["nome"], "resumo": g["como_funciona"][:100] + "..."}
                    for g in GOLPES_COMUNS
                ],
                "dica_geral": "Na duvida, NUNCA passe dados pessoais por telefone ou WhatsApp.",
            }

        if "credito" in tema_lower or "emprestimo" in tema_lower:
            return {
                "tema": "microcredito",
                "titulo": "Opcoes de credito com juros baixos",
                "opcoes": OPCOES_MICROCREDITO,
                "alerta": "Cuidado com emprestimos com juros altos! Compare sempre antes de aceitar.",
            }

        # Buscar microlição por tema
        for licao in MICROLECOES:
            if tema_lower in licao["titulo"].lower():
                return {
                    "tema": tema_lower,
                    "licao": licao,
                }

    # Lista temas
    return {
        "temas_disponiveis": [
            {"tema": "golpes", "descricao": "Como se proteger de golpes comuns"},
            {"tema": "orcamento", "descricao": "Para onde vai meu dinheiro?"},
            {"tema": "dividas", "descricao": "Divida boa vs divida ruim"},
            {"tema": "reserva", "descricao": "Como comecar a guardar dinheiro"},
            {"tema": "consumidor", "descricao": "Seus direitos como consumidor"},
            {"tema": "microcredito", "descricao": "Emprestimos com juros baixos"},
        ],
        "mensagem": "Sobre qual tema voce quer aprender?",
    }
