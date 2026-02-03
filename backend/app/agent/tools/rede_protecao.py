"""
Tools de Rede de Protecao Social.

Detecta situacoes de urgencia/vulnerabilidade e roteia para
servicos de protecao apropriados (CREAS, CAPS, SAMU, etc).

SENSIBILIDADE: Este modulo lida com situacoes de risco.
Mensagens devem ser acolhedoras e em linguagem simples.
"""

import re
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


# =============================================================================
# Constantes de urgencia
# =============================================================================

class NivelUrgencia:
    """Niveis de urgencia para triagem."""
    EMERGENCIA = "EMERGENCIA"       # Risco imediato de vida
    ALTA = "ALTA"                   # Situacao grave, precisa de ajuda rapida
    MEDIA = "MEDIA"                 # Vulnerabilidade que precisa atencao
    BAIXA = "BAIXA"                 # Orientacao preventiva


class TipoServico:
    """Tipos de servico de protecao."""
    SAMU = "SAMU"                    # Emergencia medica
    CREAS = "CREAS"                  # Violencia, abuso, exploracao
    CAPS = "CAPS"                    # Saude mental, dependencia quimica
    CENTRO_POP = "CENTRO_POP"        # Populacao de rua
    CONSELHO_TUTELAR = "CONSELHO_TUTELAR"  # Criancas e adolescentes
    CVV = "CVV"                      # Centro de Valorizacao da Vida
    DISQUE_100 = "DISQUE_100"        # Direitos humanos
    LIGUE_180 = "LIGUE_180"          # Violencia contra mulher


# Keywords de deteccao de urgencia por categoria
_KEYWORDS_URGENCIA = {
    "violencia": {
        "keywords": [
            "violência", "violencia", "batendo", "apanhando", "apanho",
            "agredido", "agredida", "agressão", "agressao", "espancamento",
            "ameaça", "ameaca", "ameacando", "marido bate", "pai bate",
            "mae bate", "abuso", "abusando", "estupro", "assédio",
            "assedio", "medo de ir pra casa", "medo do marido",
            "medo do pai", "me machuca", "me machucando",
        ],
        "servico_principal": TipoServico.CREAS,
        "nivel_padrao": NivelUrgencia.ALTA,
    },
    "violencia_mulher": {
        "keywords": [
            "meu marido me bate", "meu namorado me bate",
            "sofro violência doméstica", "violencia domestica",
            "ele me agride", "me tranca em casa", "não me deixa sair",
            "nao me deixa sair", "feminicidio",
        ],
        "servico_principal": TipoServico.LIGUE_180,
        "nivel_padrao": NivelUrgencia.ALTA,
    },
    "suicidio": {
        "keywords": [
            "suicídio", "suicidio", "me matar", "quero morrer",
            "nao quero mais viver", "não quero mais viver",
            "acabar com tudo", "nao aguento mais", "não aguento mais",
            "sem saida", "sem saída", "desistir de tudo",
            "pensando em morrer", "vontade de morrer",
        ],
        "servico_principal": TipoServico.CVV,
        "nivel_padrao": NivelUrgencia.EMERGENCIA,
    },
    "fome": {
        "keywords": [
            "fome", "passando fome", "sem comida", "nao tem comida",
            "não tem comida", "filhos com fome", "nada pra comer",
            "nao como", "não como", "dias sem comer",
            "crianca com fome", "criança com fome",
        ],
        "servico_principal": TipoServico.CREAS,
        "nivel_padrao": NivelUrgencia.ALTA,
    },
    "situacao_rua": {
        "keywords": [
            "morando na rua", "situação de rua", "situacao de rua",
            "sem teto", "desabrigado", "desabrigada", "sem moradia",
            "dormindo na rua", "perdi minha casa", "sem casa",
            "fui despejado", "fui despejada", "despejo",
        ],
        "servico_principal": TipoServico.CENTRO_POP,
        "nivel_padrao": NivelUrgencia.ALTA,
    },
    "crianca_risco": {
        "keywords": [
            "crianca abandonada", "criança abandonada",
            "menino na rua", "menina na rua",
            "trabalho infantil", "crianca trabalhando",
            "criança trabalhando", "menor abandonado",
            "filho sozinho", "filha sozinha",
            "nao tem quem cuide", "não tem quem cuide",
        ],
        "servico_principal": TipoServico.CONSELHO_TUTELAR,
        "nivel_padrao": NivelUrgencia.ALTA,
    },
    "saude_mental": {
        "keywords": [
            "depressão", "depressao", "ansiedade",
            "crise de ansiedade", "crise de panico", "pânico",
            "dependência", "dependencia", "drogas", "alcool",
            "álcool", "alcoolismo", "vicio", "vício",
            "surto", "alucinação", "alucinacao",
        ],
        "servico_principal": TipoServico.CAPS,
        "nivel_padrao": NivelUrgencia.MEDIA,
    },
    "emergencia_medica": {
        "keywords": [
            "passando mal", "desmaiou", "infarto", "derrame",
            "convulsão", "convulsao", "sangramento",
            "machucado grave", "acidente",
        ],
        "servico_principal": TipoServico.SAMU,
        "nivel_padrao": NivelUrgencia.EMERGENCIA,
    },
}

# Servicos de protecao com informacoes de contato
_SERVICOS_PROTECAO: Dict[str, Dict[str, Any]] = {
    TipoServico.SAMU: {
        "nome": "SAMU - Servico de Atendimento Movel de Urgencia",
        "telefone": "192",
        "descricao": "Atendimento medico de emergencia. Ambulancia vai ate voce.",
        "horario": "24 horas, todos os dias",
        "gratuito": True,
        "tipo_atendimento": "Emergencia medica",
    },
    TipoServico.CREAS: {
        "nome": "CREAS - Centro de Referencia Especializado de Assistencia Social",
        "telefone": "Varia por cidade (ligue 121 para saber)",
        "descricao": (
            "Atende pessoas em situacao de violencia, abuso, "
            "trabalho infantil, abandono. Equipe especializada te ajuda."
        ),
        "horario": "Segunda a sexta, horario comercial",
        "gratuito": True,
        "tipo_atendimento": "Protecao social especial",
    },
    TipoServico.CAPS: {
        "nome": "CAPS - Centro de Atencao Psicossocial",
        "telefone": "Varia por cidade (ligue 121 para saber)",
        "descricao": (
            "Atendimento gratuito de saude mental. Psicologos, "
            "psiquiatras e assistentes sociais te ajudam."
        ),
        "horario": "Segunda a sexta (alguns funcionam 24h)",
        "gratuito": True,
        "tipo_atendimento": "Saude mental e dependencia quimica",
    },
    TipoServico.CENTRO_POP: {
        "nome": "Centro POP - Centro de Referencia para Populacao de Rua",
        "telefone": "Varia por cidade (ligue 121 para saber)",
        "descricao": (
            "Oferece alimentacao, higiene pessoal, endereco para documentos, "
            "e ajuda para encontrar moradia e trabalho."
        ),
        "horario": "Varia por cidade",
        "gratuito": True,
        "tipo_atendimento": "Acolhimento para populacao de rua",
    },
    TipoServico.CONSELHO_TUTELAR: {
        "nome": "Conselho Tutelar",
        "telefone": "Varia por cidade (ligue Disque 100)",
        "descricao": (
            "Protege criancas e adolescentes. Atende denuncias de "
            "maus-tratos, abandono, trabalho infantil."
        ),
        "horario": "24 horas para emergencias",
        "gratuito": True,
        "tipo_atendimento": "Protecao de criancas e adolescentes",
    },
    TipoServico.CVV: {
        "nome": "CVV - Centro de Valorizacao da Vida",
        "telefone": "188",
        "descricao": (
            "Apoio emocional e prevencao do suicidio. "
            "Voce pode ligar, mandar mensagem ou acessar o chat. "
            "Tudo eh confidencial."
        ),
        "horario": "24 horas, todos os dias",
        "gratuito": True,
        "tipo_atendimento": "Apoio emocional",
        "chat": "https://www.cvv.org.br/chat/",
    },
    TipoServico.DISQUE_100: {
        "nome": "Disque 100 - Direitos Humanos",
        "telefone": "100",
        "descricao": (
            "Canal para denuncias de violacao de direitos humanos. "
            "Funciona para criancas, idosos, pessoas com deficiencia, "
            "populacao de rua e LGBTQIA+."
        ),
        "horario": "24 horas, todos os dias",
        "gratuito": True,
        "tipo_atendimento": "Denuncia de violacao de direitos",
    },
    TipoServico.LIGUE_180: {
        "nome": "Ligue 180 - Central de Atendimento a Mulher",
        "telefone": "180",
        "descricao": (
            "Atendimento para mulheres em situacao de violencia. "
            "Orienta sobre direitos, acolhe e encaminha para servicos."
        ),
        "horario": "24 horas, todos os dias",
        "gratuito": True,
        "tipo_atendimento": "Violencia contra mulher",
    },
}


# =============================================================================
# Tools
# =============================================================================

def detectar_urgencia(mensagem: str) -> dict:
    """Detecta situacoes de urgencia/vulnerabilidade na mensagem.

    Analisa a mensagem do cidadao buscando indicadores de risco
    como violencia, fome, desabrigo, ideacao suicida, etc.

    Args:
        mensagem: Texto da mensagem do cidadao

    Returns:
        dict com nivel de urgencia, categorias detectadas e servicos recomendados
    """
    mensagem_lower = mensagem.lower()
    categorias_detectadas = []

    for categoria, config in _KEYWORDS_URGENCIA.items():
        keywords_encontradas = [
            kw for kw in config["keywords"]
            if kw in mensagem_lower
        ]
        if keywords_encontradas:
            categorias_detectadas.append({
                "categoria": categoria,
                "keywords_encontradas": keywords_encontradas,
                "servico_principal": config["servico_principal"],
                "nivel": config["nivel_padrao"],
            })

    if not categorias_detectadas:
        return {
            "urgencia_detectada": False,
            "nivel": None,
            "categorias": [],
            "servicos_recomendados": [],
        }

    # Determinar nivel mais alto de urgencia
    niveis_ordem = {
        NivelUrgencia.EMERGENCIA: 4,
        NivelUrgencia.ALTA: 3,
        NivelUrgencia.MEDIA: 2,
        NivelUrgencia.BAIXA: 1,
    }
    nivel_maximo = max(
        categorias_detectadas,
        key=lambda c: niveis_ordem.get(c["nivel"], 0)
    )["nivel"]

    # Coletar servicos unicos recomendados
    servicos_recomendados = []
    servicos_vistos = set()
    for cat in categorias_detectadas:
        servico_id = cat["servico_principal"]
        if servico_id not in servicos_vistos:
            servicos_vistos.add(servico_id)
            servico_info = _SERVICOS_PROTECAO.get(servico_id, {})
            servicos_recomendados.append({
                "tipo": servico_id,
                "nome": servico_info.get("nome", servico_id),
                "telefone": servico_info.get("telefone", ""),
                "descricao": servico_info.get("descricao", ""),
            })

    logger.warning(
        f"URGENCIA DETECTADA: nivel={nivel_maximo}, "
        f"categorias={[c['categoria'] for c in categorias_detectadas]}"
    )

    return {
        "urgencia_detectada": True,
        "nivel": nivel_maximo,
        "categorias": [
            {
                "categoria": c["categoria"],
                "nivel": c["nivel"],
            }
            for c in categorias_detectadas
        ],
        "servicos_recomendados": servicos_recomendados,
    }


def buscar_servico_protecao(
    tipo_servico: str,
    cidade: Optional[str] = None,
    uf: Optional[str] = None,
) -> dict:
    """Busca informacoes de um servico de protecao social.

    Retorna dados de contato, horario e descricao do servico.

    Args:
        tipo_servico: Tipo do servico (CREAS, CAPS, SAMU, CENTRO_POP, etc)
        cidade: Cidade do cidadao (para servicos locais)
        uf: Estado do cidadao

    Returns:
        dict com informacoes do servico
    """
    tipo_upper = tipo_servico.upper().strip()

    servico = _SERVICOS_PROTECAO.get(tipo_upper)
    if not servico:
        # Tentar busca flexivel
        for key, info in _SERVICOS_PROTECAO.items():
            if tipo_upper in key or tipo_upper in info["nome"].upper():
                servico = info
                tipo_upper = key
                break

    if not servico:
        return {
            "encontrado": False,
            "erro": f"Servico '{tipo_servico}' nao encontrado.",
            "servicos_disponiveis": list(_SERVICOS_PROTECAO.keys()),
        }

    resultado = {
        "encontrado": True,
        "tipo": tipo_upper,
        "nome": servico["nome"],
        "telefone": servico["telefone"],
        "descricao": servico["descricao"],
        "horario": servico["horario"],
        "gratuito": servico["gratuito"],
        "tipo_atendimento": servico["tipo_atendimento"],
    }

    if "chat" in servico:
        resultado["chat"] = servico["chat"]

    if cidade:
        resultado["orientacao_local"] = (
            f"Em {cidade}, ligue para o numero informado ou procure "
            f"o {servico['nome'].split(' - ')[0]} mais perto de voce."
        )

    return resultado
