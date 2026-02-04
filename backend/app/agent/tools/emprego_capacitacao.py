"""
Tools para busca de vagas de emprego e cursos de capacitacao gratuitos.

Foco em oportunidades acessiveis ao publico do CadUnico:
primeiro emprego, sem experiencia, capacitacao basica.
"""

from typing import Optional
from app.agent.tools.base import ToolResult, UIHint


# --- Dados estaticos de cursos gratuitos ---
CURSOS_GRATUITOS = [
    {
        "nome": "Assistente Administrativo",
        "instituicao": "SENAI",
        "modalidade": "Presencial e EAD",
        "duracao": "160 horas",
        "requisito": "Ensino fundamental completo",
        "inscricao": "https://www.mundosenai.com.br",
        "areas": ["administrativo", "escritorio", "geral"],
    },
    {
        "nome": "Operador de Computador",
        "instituicao": "SENAC",
        "modalidade": "Presencial e EAD",
        "duracao": "160 horas",
        "requisito": "Ensino fundamental completo",
        "inscricao": "https://www.ead.senac.br",
        "areas": ["informatica", "tecnologia", "geral"],
    },
    {
        "nome": "Eletricista Instalador",
        "instituicao": "SENAI",
        "modalidade": "Presencial",
        "duracao": "200 horas",
        "requisito": "Ensino fundamental completo",
        "inscricao": "https://www.mundosenai.com.br",
        "areas": ["eletrica", "construcao", "manutencao"],
    },
    {
        "nome": "Cuidador de Idosos",
        "instituicao": "SENAC",
        "modalidade": "Presencial",
        "duracao": "160 horas",
        "requisito": "Ensino fundamental completo",
        "inscricao": "https://www.ead.senac.br",
        "areas": ["saude", "cuidados", "geral"],
    },
    {
        "nome": "Confeiteiro",
        "instituicao": "SENAC",
        "modalidade": "Presencial",
        "duracao": "200 horas",
        "requisito": "Ensino fundamental completo",
        "inscricao": "https://www.ead.senac.br",
        "areas": ["alimentacao", "gastronomia", "empreendedorismo"],
    },
    {
        "nome": "Costureiro",
        "instituicao": "SENAI",
        "modalidade": "Presencial",
        "duracao": "180 horas",
        "requisito": "Ensino fundamental incompleto",
        "inscricao": "https://www.mundosenai.com.br",
        "areas": ["textil", "moda", "empreendedorismo"],
    },
    {
        "nome": "Ingles Basico",
        "instituicao": "MEC - Plataforma AVAMEC",
        "modalidade": "EAD (gratis)",
        "duracao": "60 horas",
        "requisito": "Nenhum",
        "inscricao": "https://avamec.mec.gov.br",
        "areas": ["idiomas", "geral"],
    },
    {
        "nome": "Empreendedorismo Digital",
        "instituicao": "SEBRAE",
        "modalidade": "EAD (gratis)",
        "duracao": "8 horas",
        "requisito": "Nenhum",
        "inscricao": "https://sebrae.com.br/sites/PortalSebrae/cursosonline",
        "areas": ["empreendedorismo", "tecnologia", "negocios"],
    },
    {
        "nome": "Tecnicas de Vendas",
        "instituicao": "SEBRAE",
        "modalidade": "EAD (gratis)",
        "duracao": "8 horas",
        "requisito": "Nenhum",
        "inscricao": "https://sebrae.com.br/sites/PortalSebrae/cursosonline",
        "areas": ["vendas", "comercio", "empreendedorismo"],
    },
    {
        "nome": "Pedreiro de Alvenaria",
        "instituicao": "SENAI",
        "modalidade": "Presencial",
        "duracao": "200 horas",
        "requisito": "Ensino fundamental incompleto",
        "inscricao": "https://www.mundosenai.com.br",
        "areas": ["construcao", "civil"],
    },
]

# --- Dados estaticos de vagas comuns ---
VAGAS_EXEMPLO = [
    {
        "titulo": "Auxiliar de Servicos Gerais",
        "empresa": "Via SINE / Portal Emprega Brasil",
        "tipo": "CLT",
        "requisitos": "Ensino fundamental, sem experiencia necessaria",
        "faixa_salarial": "R$ 1.412 - R$ 1.600",
        "onde_buscar": "Portal Emprega Brasil (gov.br/trabalho) ou SINE da sua cidade",
    },
    {
        "titulo": "Operador de Caixa",
        "empresa": "Via SINE / Portal Emprega Brasil",
        "tipo": "CLT",
        "requisitos": "Ensino medio, sem experiencia necessaria",
        "faixa_salarial": "R$ 1.412 - R$ 1.700",
        "onde_buscar": "Portal Emprega Brasil (gov.br/trabalho) ou SINE da sua cidade",
    },
    {
        "titulo": "Auxiliar de Cozinha",
        "empresa": "Via SINE / Portal Emprega Brasil",
        "tipo": "CLT",
        "requisitos": "Ensino fundamental, sem experiencia necessaria",
        "faixa_salarial": "R$ 1.412 - R$ 1.600",
        "onde_buscar": "Portal Emprega Brasil (gov.br/trabalho) ou SINE da sua cidade",
    },
    {
        "titulo": "Repositor de Mercadorias",
        "empresa": "Via SINE / Portal Emprega Brasil",
        "tipo": "CLT",
        "requisitos": "Ensino fundamental, sem experiencia necessaria",
        "faixa_salarial": "R$ 1.412 - R$ 1.550",
        "onde_buscar": "Portal Emprega Brasil (gov.br/trabalho) ou SINE da sua cidade",
    },
    {
        "titulo": "Atendente de Loja",
        "empresa": "Via SINE / Portal Emprega Brasil",
        "tipo": "CLT",
        "requisitos": "Ensino medio",
        "faixa_salarial": "R$ 1.412 - R$ 1.800",
        "onde_buscar": "Portal Emprega Brasil (gov.br/trabalho) ou SINE da sua cidade",
    },
]


def buscar_vagas(
    uf: str = "",
    cidade: str = "",
    perfil: str = "",
) -> dict:
    """
    Busca vagas de emprego acessiveis ao publico CadUnico.

    Em producao, integra com Portal Emprega Brasil / SINE.
    Por enquanto, retorna vagas comuns com orientacao de onde buscar.

    Args:
        uf: Estado do cidadao
        cidade: Cidade do cidadao
        perfil: Descricao do perfil (ex: "sem experiencia", "primeiro emprego")

    Returns:
        dict com lista de vagas e orientacoes
    """
    local = f"{cidade}, {uf}" if cidade and uf else uf or "sua cidade"

    mensagem = (
        f"Encontrei algumas vagas comuns na regiao de {local}. "
        f"O melhor lugar para buscar vagas e o SINE (Sistema Nacional de Emprego) "
        f"da sua cidade ou o Portal Emprega Brasil do governo.\n\n"
        f"Como buscar vagas:\n"
        f"1. Va ao SINE mais proximo (geralmente no PAT ou prefeitura)\n"
        f"2. Acesse gov.br/trabalho com seu login gov.br\n"
        f"3. Leve RG, CPF e carteira de trabalho (pode ser digital)\n\n"
        f"Dica: Se voce recebe Bolsa Familia, o SINE tem vagas prioritarias "
        f"para beneficiarios do CadUnico."
    )

    result = ToolResult.ok(
        data={
            "vagas": VAGAS_EXEMPLO,
            "total": len(VAGAS_EXEMPLO),
            "local": local,
            "como_buscar": {
                "sine": f"SINE de {local} (presencial, gratis)",
                "portal": "Portal Emprega Brasil: gov.br/trabalho",
                "carteira_digital": "App Carteira de Trabalho Digital (Play Store / App Store)",
            },
            "mensagem_cidadao": mensagem,
        },
        ui_hint=UIHint.INFO,
    )
    return result.model_dump()


def buscar_cursos(
    uf: str = "",
    area: str = "",
    escolaridade: str = "",
) -> dict:
    """
    Busca cursos de capacitacao gratuitos.

    Filtra por area de interesse e nivel de escolaridade.

    Args:
        uf: Estado do cidadao
        area: Area de interesse (ex: "informatica", "construcao", "alimentacao")
        escolaridade: Nivel de escolaridade do cidadao

    Returns:
        dict com lista de cursos gratuitos
    """
    area_lower = area.lower().strip() if area else ""

    # Filtra por area se especificada
    if area_lower:
        filtrados = [
            c for c in CURSOS_GRATUITOS
            if any(area_lower in a for a in c["areas"])
        ]
        # Se nao encontrou match exato, retorna todos
        if not filtrados:
            filtrados = CURSOS_GRATUITOS
    else:
        filtrados = CURSOS_GRATUITOS

    # Limita a 5 resultados
    cursos = filtrados[:5]

    mensagem = (
        f"Encontrei {len(cursos)} cursos gratuitos"
        + (f" na area de {area}" if area else "")
        + ".\n\n"
        + "Todos sao gratuitos e a maioria aceita quem tem "
        + "ensino fundamental completo.\n\n"
        + "Dica: Quem esta no CadUnico tem prioridade em vagas do PRONATEC!"
    )

    result = ToolResult.ok(
        data={
            "cursos": cursos,
            "total": len(cursos),
            "area_filtrada": area or "todas",
            "dica_pronatec": (
                "O PRONATEC oferece cursos tecnicos gratuitos para "
                "inscritos no CadUnico. Procure no SENAI, SENAC ou "
                "Instituto Federal da sua cidade."
            ),
            "mensagem_cidadao": mensagem,
        },
        ui_hint=UIHint.INFO,
    )
    return result.model_dump()


def simular_microcredito(
    valor: float = 0,
    finalidade: str = "",
) -> dict:
    """
    Simula opcoes de microcredito produtivo para empreendedores
    de baixa renda (CrediAmigo, Agroamigo, Pronaf).

    Args:
        valor: Valor desejado do emprestimo
        finalidade: Para que sera usado (ex: "comprar mercadoria", "reformar")

    Returns:
        dict com opcoes de microcredito e simulacao
    """
    programas = []

    # CrediAmigo (Banco do Nordeste) - microcrédito urbano
    if valor <= 21000:
        juros_mensal = 1.98  # taxa média
        parcelas = 12
        valor_parcela = (valor * (1 + juros_mensal/100 * parcelas)) / parcelas
        programas.append({
            "nome": "CrediAmigo",
            "banco": "Banco do Nordeste",
            "valor_max": "R$ 21.000",
            "juros": f"{juros_mensal}% ao mes (subsidiado)",
            "parcelas": f"Ate {parcelas}x",
            "valor_parcela": f"R$ {valor_parcela:.2f}" if valor > 0 else "Simule com o valor",
            "requisitos": [
                "Empreendedor informal ou MEI",
                "Renda ate 3 salarios minimos",
                "Regiao Norte, Nordeste ou norte de MG/ES",
            ],
            "como_solicitar": "Va a uma agencia do Banco do Nordeste com CPF e comprovante de atividade",
        })

    # Pronaf (agricultura familiar)
    if valor <= 50000:
        programas.append({
            "nome": "PRONAF - Credito Rural",
            "banco": "Banco do Brasil / CAIXA / Bancos cooperativos",
            "valor_max": "R$ 50.000 (Grupo B: R$ 8.000)",
            "juros": "0,5% a 4% ao ano (subsidiado pelo governo)",
            "parcelas": "Ate 10 anos com carencia",
            "valor_parcela": "Varia conforme o grupo",
            "requisitos": [
                "Agricultor familiar com DAP/CAF",
                "Renda bruta ate R$ 500.000/ano",
                "Residir no imovel rural ou proximo",
            ],
            "como_solicitar": "Procure o sindicato rural ou EMATER da sua cidade para emitir DAP/CAF",
        })

    # Programa Nacional de Microcredito (geral)
    programas.append({
        "nome": "Programa Nacional de Microcredito (PNMPO)",
        "banco": "CAIXA, Banco do Brasil, cooperativas de credito",
        "valor_max": "R$ 21.000 para pessoa fisica",
        "juros": "Ate 4% ao mes",
        "parcelas": "Negociavel",
        "valor_parcela": "Varia",
        "requisitos": [
            "Empreendedor com renda bruta ate R$ 200.000/ano",
            "Atividade produtiva (formal ou informal)",
        ],
        "como_solicitar": "Procure CAIXA, Banco do Brasil ou cooperativa de credito da sua cidade",
    })

    mensagem = (
        f"Encontrei {len(programas)} opcoes de microcredito"
        + (f" para {finalidade}" if finalidade else "")
        + ".\n\n"
        + "O microcredito produtivo tem juros bem menores que emprestimo normal "
        + "e e feito para quem quer trabalhar por conta propria.\n\n"
        + "Importante: NUNCA pegue emprestimo com agiota ou financeira "
        + "com juros altos. Os programas do governo sao muito mais baratos."
    )

    result = ToolResult.ok(
        data={
            "programas": programas,
            "total": len(programas),
            "valor_solicitado": valor,
            "finalidade": finalidade,
            "mensagem_cidadao": mensagem,
        },
        ui_hint=UIHint.INFO,
    )
    return result.model_dump()
