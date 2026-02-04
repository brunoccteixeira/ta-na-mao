"""
Tools de economia solidaria.

Catalogo de cooperativas, feiras solidarias, bancos comunitarios
e moedas sociais digitais.
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


# =============================================================================
# Dados de cooperativas e economia solidaria
# =============================================================================

TIPOS_COOPERATIVA = {
    "trabalho": "Cooperativas de trabalho (transporte, limpeza, entrega)",
    "producao": "Cooperativas de producao (agricultura, pesca, textil, reciclagem)",
    "servicos": "Cooperativas de servicos (saude, educacao, credito)",
    "catadores": "Cooperativas de catadores de material reciclavel",
    "habitacao": "Cooperativas habitacionais",
}

COOPERATIVAS_MOCK = [
    {
        "nome": "CoopTransp - Cooperativa de Transporte Solidario",
        "tipo": "trabalho",
        "atividade": "Transporte por aplicativo cooperativo",
        "municipio_ibge": "3550308",
        "municipio": "Sao Paulo",
        "uf": "SP",
        "contato": "(11) 3456-7890",
        "como_participar": "Seja motorista parceiro sem pagar taxa de 25%",
    },
    {
        "nome": "CoopRecicla - Cooperativa de Catadores",
        "tipo": "catadores",
        "atividade": "Coleta e venda de material reciclavel",
        "municipio_ibge": "3550308",
        "municipio": "Sao Paulo",
        "uf": "SP",
        "contato": "(11) 2345-6789",
        "como_participar": "Cadastro presencial na sede, leve CPF e comprovante de endereco",
    },
    {
        "nome": "Cooperativa da Agricultura Familiar do Nordeste",
        "tipo": "producao",
        "atividade": "Producao e venda de alimentos organicos",
        "municipio_ibge": "2927408",
        "municipio": "Salvador",
        "uf": "BA",
        "contato": "(71) 3456-7890",
        "como_participar": "Ter DAP/CAF e producao familiar",
    },
    {
        "nome": "Liga das Mulheres Artesas",
        "tipo": "producao",
        "atividade": "Artesanato e producao textil",
        "municipio_ibge": "2304400",
        "municipio": "Fortaleza",
        "uf": "CE",
        "contato": "(85) 3456-7890",
        "como_participar": "Cadastro aberto para artesas da regiao",
    },
]

MOEDAS_SOCIAIS = {
    "2304400": {"nome": "Palmas", "banco": "Banco Palmas", "plataforma": "E-dinheiro", "cidade": "Fortaleza"},
    "3302700": {"nome": "Mumbuca", "banco": "Banco Mumbuca", "plataforma": "Mumbuca Digital", "cidade": "Marica"},
    "3550308": {"nome": "Sampa", "banco": "Banco Comunitario Uniao Sampaio", "plataforma": "E-dinheiro", "cidade": "Sao Paulo"},
    "2611606": {"nome": "Capivari", "banco": "Banco Comunitario Capivari", "plataforma": "E-dinheiro", "cidade": "Recife"},
}

FEIRAS_SOLIDARIAS_MOCK = [
    {
        "nome": "Feira da Agricultura Familiar - Largo da Batata",
        "municipio_ibge": "3550308",
        "municipio": "Sao Paulo",
        "uf": "SP",
        "dia_semana": "sabado",
        "horario": "6h as 12h",
        "local": "Largo da Batata, Pinheiros",
        "produtos": ["frutas", "verduras", "queijos", "paes"],
    },
    {
        "nome": "Feira Organica do Produtor",
        "municipio_ibge": "3304557",
        "municipio": "Rio de Janeiro",
        "uf": "RJ",
        "dia_semana": "sabado",
        "horario": "7h as 13h",
        "local": "Praca XV, Centro",
        "produtos": ["hortalicas", "mel", "cafe", "artesanato"],
    },
]

PASSOS_CRIAR_COOPERATIVA = [
    {
        "passo": 1,
        "titulo": "Reunir pessoas",
        "descricao": "Junte pelo menos 7 pessoas com o mesmo objetivo de trabalho.",
        "dica": "Todos precisam ter CPF e ser maiores de 16 anos.",
    },
    {
        "passo": 2,
        "titulo": "Definir o tipo de cooperativa",
        "descricao": "Decidam qual atividade vao fazer juntos: producao, servicos, trabalho.",
        "dica": "O SEBRAE ajuda gratuitamente nessa fase.",
    },
    {
        "passo": 3,
        "titulo": "Elaborar o Estatuto",
        "descricao": "Documento com regras da cooperativa: como entrar, votar, dividir ganhos.",
        "dica": "A OCB (Organizacao das Cooperativas) tem modelos prontos.",
    },
    {
        "passo": 4,
        "titulo": "Assembleia de fundacao",
        "descricao": "Reuniao oficial para aprovar o estatuto e eleger a diretoria.",
        "dica": "Faca ata da assembleia - precisa para o registro.",
    },
    {
        "passo": 5,
        "titulo": "Registrar na Junta Comercial",
        "descricao": "Registre a cooperativa na Junta Comercial do estado.",
        "dica": "Custo medio: R$ 150 a R$ 500 dependendo do estado.",
    },
    {
        "passo": 6,
        "titulo": "Obter CNPJ",
        "descricao": "Cadastre na Receita Federal para obter o CNPJ.",
        "dica": "Com CNPJ, a cooperativa pode emitir nota fiscal e acessar credito.",
    },
]

PROGRAMAS_FOMENTO = [
    {
        "nome": "PAA - Programa de Aquisicao de Alimentos",
        "descricao": "Governo compra alimentos direto de agricultores familiares para doar.",
        "quem_pode": "Agricultores com DAP/CAF, cooperativas de producao",
        "valor": "Ate R$ 12.000/ano por agricultor",
    },
    {
        "nome": "PNAE - Merenda Escolar",
        "descricao": "Escolas publicas devem comprar 30% da merenda de agricultores familiares.",
        "quem_pode": "Cooperativas de agricultura familiar",
        "valor": "Varia por municipio - contratos diretos",
    },
    {
        "nome": "PRONAF - Credito Rural",
        "descricao": "Emprestimo com juros baixos para agricultura familiar.",
        "quem_pode": "Agricultores com DAP/CAF",
        "valor": "Ate R$ 250.000 com juros de 0,5% a 4% ao ano",
    },
]


def buscar_cooperativas(
    municipio_ibge: Optional[str] = None,
    uf: Optional[str] = None,
    tipo: Optional[str] = None,
) -> Dict[str, Any]:
    """Busca cooperativas e empreendimentos solidarios.

    Args:
        municipio_ibge: Codigo IBGE do municipio
        uf: Sigla do estado
        tipo: Tipo: trabalho, producao, servicos, catadores, habitacao

    Returns:
        dict com cooperativas encontradas
    """
    logger.info(f"Buscando cooperativas: municipio={municipio_ibge}, uf={uf}, tipo={tipo}")

    resultados = []
    for coop in COOPERATIVAS_MOCK:
        if municipio_ibge and coop["municipio_ibge"] != municipio_ibge:
            continue
        if uf and coop["uf"] != uf:
            continue
        if tipo and coop["tipo"] != tipo:
            continue
        resultados.append(coop)

    # Verificar moeda social
    moeda = MOEDAS_SOCIAIS.get(municipio_ibge) if municipio_ibge else None

    return {
        "total": len(resultados),
        "cooperativas": resultados,
        "moeda_social": moeda,
        "tipos_disponiveis": TIPOS_COOPERATIVA,
        "como_criar": "Use guia_criar_cooperativa() para ver o passo a passo.",
        "mensagem": (
            f"Encontrei {len(resultados)} cooperativa(s)!"
            if resultados
            else "Nao encontrei cooperativas na sua regiao, mas voce pode criar uma!"
        ),
    }


def buscar_feiras(
    municipio_ibge: Optional[str] = None,
    dia_semana: Optional[str] = None,
) -> Dict[str, Any]:
    """Busca feiras solidarias e da agricultura familiar.

    Args:
        municipio_ibge: Codigo IBGE do municipio
        dia_semana: Filtrar por dia (segunda, terca, ..., domingo)

    Returns:
        dict com feiras encontradas
    """
    resultados = []
    for feira in FEIRAS_SOLIDARIAS_MOCK:
        if municipio_ibge and feira["municipio_ibge"] != municipio_ibge:
            continue
        if dia_semana and feira["dia_semana"] != dia_semana.lower():
            continue
        resultados.append(feira)

    return {
        "total": len(resultados),
        "feiras": resultados,
        "mensagem": (
            f"Encontrei {len(resultados)} feira(s) perto de voce!"
            if resultados
            else "Nao encontrei feiras na sua regiao. Procure na prefeitura."
        ),
    }


def guia_criar_cooperativa() -> Dict[str, Any]:
    """Retorna guia passo a passo para criar uma cooperativa.

    Returns:
        dict com passos, requisitos e onde buscar ajuda
    """
    return {
        "titulo": "Como criar uma cooperativa em 6 passos",
        "passos": PASSOS_CRIAR_COOPERATIVA,
        "requisitos": [
            "Minimo 7 pessoas",
            "CPF de todos os membros",
            "Maiores de 16 anos",
            "Atividade economica em comum",
        ],
        "onde_pedir_ajuda": [
            "SEBRAE: 0800-570-0800 (gratuito)",
            "OCB - Organizacao das Cooperativas do Brasil",
            "Secretaria de Economia Solidaria da sua cidade",
            "SENAES - Secretaria Nacional de Economia Solidaria",
        ],
        "programas_fomento": PROGRAMAS_FOMENTO,
    }
