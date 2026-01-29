"""Tool para buscar mutiroes de documentacao (Registre-se!).

Busca proximos mutiroes de emissao gratuita de documentos,
promovidos pelo CNJ, Arpen, e Tribunais de Justica estaduais.

Os mutiroes "Registre-se!" emitem gratuitamente:
- Certidao de Nascimento (1a e 2a via)
- RG
- CPF
- Carteira de Trabalho Digital
- Outros documentos

Publico-alvo prioritario:
- Pessoas em situacao de rua
- Indigenas
- Quilombolas
- Populacao carceraria e egressos
- Pessoas em extrema vulnerabilidade

Fontes de dados:
- CNJ (Conselho Nacional de Justica)
- Arpen Brasil (Associacao dos Registradores de Pessoas Naturais)
- Tribunais de Justica estaduais
"""

import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pathlib import Path

from app.agent.tools.base import ToolResult, UIHint


class MutiraoResult(ToolResult):
    """Resultado de busca de mutiroes."""

    @classmethod
    def encontrados(
        cls,
        mutiroes: List[Dict[str, Any]],
        total: int
    ) -> "MutiraoResult":
        return cls(
            success=True,
            data={
                "encontrados": len(mutiroes),
                "total_disponiveis": total,
                "mutiroes": mutiroes
            },
            ui_hint=UIHint.INFO
        )

    @classmethod
    def nenhum_encontrado(
        cls,
        uf: Optional[str] = None,
        mensagem: str = None
    ) -> "MutiraoResult":
        msg = mensagem or (
            f"Nao encontrei mutiroes proximos em {uf}. "
            if uf else
            "Nao encontrei mutiroes proximos. "
        )
        msg += "Os mutiroes geralmente acontecem em maio (Semana Registre-se!) e em datas especiais."

        return cls(
            success=True,
            data={
                "encontrados": 0,
                "mutiroes": [],
                "mensagem": msg,
                "dica": "Pergunte no CRAS sobre proximos eventos de documentacao na sua cidade."
            },
            ui_hint=UIHint.INFO
        )


# Caminho para arquivo de dados de mutiroes
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
MUTIROES_FILE = DATA_DIR / "mutiroes_registrese.json"


def carregar_mutiroes() -> List[Dict[str, Any]]:
    """Carrega dados de mutiroes do arquivo JSON."""
    if MUTIROES_FILE.exists():
        with open(MUTIROES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("mutiroes", [])

    # Dados de exemplo/fallback se arquivo nao existe
    return _get_mutiroes_exemplo()


def _get_mutiroes_exemplo() -> List[Dict[str, Any]]:
    """Retorna dados de exemplo de mutiroes.

    Estes dados sao usados para demonstracao.
    Em producao, devem ser substituidos por dados reais via scraping.
    """
    return [
        {
            "id": "registrese-2025-maio",
            "nome": "Semana Nacional Registre-se! 2025",
            "data_inicio": "2025-05-12",
            "data_fim": "2025-05-16",
            "nacional": True,
            "estados": ["todos"],
            "descricao": "Mutirao nacional do CNJ para emissao gratuita de documentos",
            "servicos": [
                "Certidao de Nascimento (1a e 2a via)",
                "RG",
                "CPF",
                "Carteira de Trabalho Digital",
                "Cadastro no CadUnico"
            ],
            "publico_alvo": [
                "Pessoas em situacao de rua",
                "Indigenas",
                "Quilombolas",
                "Pessoas privadas de liberdade",
                "Pessoas em vulnerabilidade social"
            ],
            "como_participar": "Procure o CRAS ou Cartorio mais proximo durante a semana do evento",
            "fonte": "CNJ",
            "url_fonte": "https://www.cnj.jus.br/programas-e-acoes/registre-se/",
            "atualizado_em": "2025-01-15"
        },
        {
            "id": "registrese-sp-2025",
            "nome": "Mutirao de Documentacao - Sao Paulo Capital",
            "data_inicio": "2025-02-10",
            "data_fim": "2025-02-14",
            "nacional": False,
            "estados": ["SP"],
            "municipios": ["Sao Paulo"],
            "locais": [
                {
                    "nome": "Poupatempo Se",
                    "endereco": "Praca da Se, s/n - Centro",
                    "horario": "7h as 19h"
                },
                {
                    "nome": "CRAS Republica",
                    "endereco": "Rua do Arouche, 24 - Republica",
                    "horario": "8h as 17h"
                }
            ],
            "descricao": "Mutirao especial para populacao em situacao de rua",
            "servicos": [
                "Certidao de Nascimento",
                "RG",
                "CPF",
                "Cadastro no CadUnico"
            ],
            "publico_alvo": ["Pessoas em situacao de rua", "Populacao vulneravel"],
            "como_participar": "Comparecer a um dos locais com qualquer documento que possuir",
            "fonte": "TJSP",
            "url_fonte": "https://www.tjsp.jus.br/",
            "atualizado_em": "2025-01-10"
        },
        {
            "id": "registrese-rj-2025",
            "nome": "Mutirao Cidadania - Rio de Janeiro",
            "data_inicio": "2025-03-03",
            "data_fim": "2025-03-07",
            "nacional": False,
            "estados": ["RJ"],
            "municipios": ["Rio de Janeiro", "Niteroi", "Duque de Caxias"],
            "locais": [
                {
                    "nome": "Central do Brasil - Acao Social",
                    "endereco": "Praca Cristiano Ottoni, s/n - Centro, Rio de Janeiro",
                    "horario": "8h as 17h"
                }
            ],
            "descricao": "Emissao de documentos para populacao vulneravel",
            "servicos": [
                "Certidao de Nascimento",
                "RG",
                "CPF",
                "Titulo de Eleitor"
            ],
            "publico_alvo": ["Populacao em vulnerabilidade social"],
            "como_participar": "Levar foto 3x4 e qualquer documento que possuir",
            "fonte": "TJRJ",
            "url_fonte": "https://www.tjrj.jus.br/",
            "atualizado_em": "2025-01-08"
        },
        {
            "id": "registrese-ba-indigenas-2025",
            "nome": "Mutirao Registre-se! - Povos Indigenas da Bahia",
            "data_inicio": "2025-04-19",
            "data_fim": "2025-04-19",
            "nacional": False,
            "estados": ["BA"],
            "municipios": ["Porto Seguro", "Santa Cruz Cabralia"],
            "descricao": "Mutirao especial para povos indigenas em comemoracao ao Dia do Indio",
            "servicos": [
                "Certidao de Nascimento com nome indigena",
                "RG",
                "CPF"
            ],
            "publico_alvo": ["Povos indigenas"],
            "como_participar": "Procurar a FUNAI local ou CRAS",
            "fonte": "TJBA/FUNAI",
            "url_fonte": "https://www.tjba.jus.br/",
            "atualizado_em": "2025-01-05"
        }
    ]


def buscar_mutirao(
    uf: Optional[str] = None,
    municipio: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    apenas_futuros: bool = True,
    limite: int = 5
) -> MutiraoResult:
    """Busca proximos mutiroes de documentacao.

    Args:
        uf: Filtrar por UF (ex: "SP", "RJ")
        municipio: Filtrar por municipio
        data_inicio: Data minima (YYYY-MM-DD)
        data_fim: Data maxima (YYYY-MM-DD)
        apenas_futuros: Retornar apenas eventos futuros
        limite: Maximo de resultados

    Returns:
        MutiraoResult com lista de mutiroes
    """
    mutiroes = carregar_mutiroes()
    hoje = date.today()

    resultados = []

    for m in mutiroes:
        # Filtra por data
        try:
            data_evento_inicio = date.fromisoformat(m.get("data_inicio", "2099-12-31"))
            data_evento_fim = date.fromisoformat(m.get("data_fim", m.get("data_inicio", "2099-12-31")))
        except ValueError:
            continue

        # Apenas futuros
        if apenas_futuros and data_evento_fim < hoje:
            continue

        # Filtro por data inicio
        if data_inicio:
            try:
                filtro_inicio = date.fromisoformat(data_inicio)
                if data_evento_fim < filtro_inicio:
                    continue
            except ValueError:
                pass

        # Filtro por data fim
        if data_fim:
            try:
                filtro_fim = date.fromisoformat(data_fim)
                if data_evento_inicio > filtro_fim:
                    continue
            except ValueError:
                pass

        # Filtro por UF
        if uf:
            estados = m.get("estados", [])
            if "todos" not in estados and uf.upper() not in [e.upper() for e in estados]:
                continue

        # Filtro por municipio
        if municipio:
            municipios = m.get("municipios", [])
            if municipios:  # Se tem lista de municipios especificos
                municipio_normalizado = municipio.upper().strip()
                if not any(municipio_normalizado in mun.upper() for mun in municipios):
                    continue

        # Formata para retorno
        resultado = {
            "nome": m.get("nome"),
            "data_inicio": m.get("data_inicio"),
            "data_fim": m.get("data_fim"),
            "nacional": m.get("nacional", False),
            "estados": m.get("estados", []),
            "municipios": m.get("municipios", []),
            "locais": m.get("locais", []),
            "descricao": m.get("descricao"),
            "servicos": m.get("servicos", []),
            "publico_alvo": m.get("publico_alvo", []),
            "como_participar": m.get("como_participar"),
            "fonte": m.get("fonte"),
            "url_fonte": m.get("url_fonte")
        }
        resultados.append(resultado)

    # Ordena por data mais proxima
    resultados.sort(key=lambda x: x.get("data_inicio", "2099-12-31"))

    # Aplica limite
    resultados = resultados[:limite]

    if resultados:
        return MutiraoResult.encontrados(
            mutiroes=resultados,
            total=len(mutiroes)
        )
    else:
        return MutiraoResult.nenhum_encontrado(uf=uf)


def formatar_mutirao_texto(mutirao: Dict[str, Any]) -> str:
    """Formata um mutirao para exibicao em texto.

    Args:
        mutirao: Dados do mutirao

    Returns:
        Texto formatado para exibicao
    """
    partes = []

    partes.append(f"**{mutirao.get('nome', 'Mutirao')}**")

    # Datas
    data_inicio = mutirao.get("data_inicio", "")
    data_fim = mutirao.get("data_fim", data_inicio)
    if data_inicio:
        if data_inicio == data_fim:
            partes.append(f"Data: {_formatar_data(data_inicio)}")
        else:
            partes.append(f"Periodo: {_formatar_data(data_inicio)} a {_formatar_data(data_fim)}")

    # Local
    if mutirao.get("nacional"):
        partes.append("Abrangencia: Nacional (todo o Brasil)")
    elif mutirao.get("estados"):
        estados = mutirao["estados"]
        if "todos" not in estados:
            partes.append(f"Estados: {', '.join(estados)}")

    if mutirao.get("municipios"):
        partes.append(f"Municipios: {', '.join(mutirao['municipios'][:3])}")

    # Locais especificos
    if mutirao.get("locais"):
        partes.append("Locais de atendimento:")
        for local in mutirao["locais"][:2]:
            partes.append(f"  - {local.get('nome')}: {local.get('endereco')}")
            if local.get("horario"):
                partes.append(f"    Horario: {local['horario']}")

    # Servicos
    if mutirao.get("servicos"):
        partes.append("Documentos emitidos: " + ", ".join(mutirao["servicos"][:4]))

    # Como participar
    if mutirao.get("como_participar"):
        partes.append(f"Como participar: {mutirao['como_participar']}")

    return "\n".join(partes)


def _formatar_data(data_str: str) -> str:
    """Formata data ISO para formato brasileiro."""
    try:
        d = date.fromisoformat(data_str)
        return d.strftime("%d/%m/%Y")
    except ValueError:
        return data_str


# =============================================================================
# Funcao para criar arquivo de dados inicial
# =============================================================================

def criar_arquivo_mutiroes_inicial():
    """Cria arquivo JSON com dados iniciais de mutiroes.

    Execute uma vez para criar o arquivo de dados.
    """
    dados = {
        "versao": "1.0",
        "atualizado_em": datetime.now().isoformat(),
        "fonte": "Dados de demonstracao - atualizar via scraping",
        "mutiroes": _get_mutiroes_exemplo()
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(MUTIROES_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return str(MUTIROES_FILE)
