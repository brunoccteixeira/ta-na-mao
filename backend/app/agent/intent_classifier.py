"""
Classificador de intenção para rotear mensagens.

Classifica mensagens do usuário em categorias de fluxo:
- farmacia: pedido de medicamentos
- beneficio: consulta de benefícios
- documentacao: checklist e CRAS
- geral: conversa geral

Usa primeiro keywords simples, fallback para LLM se necessário.
"""

import re
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from .context import FlowType

logger = logging.getLogger(__name__)


class IntentCategory(str, Enum):
    """Categorias de intenção."""

    FARMACIA = "farmacia"
    BENEFICIO = "beneficio"
    DOCUMENTACAO = "documentacao"
    GERAL = "geral"

    def to_flow_type(self) -> Optional[FlowType]:
        """Converte para FlowType."""
        mapping = {
            IntentCategory.FARMACIA: FlowType.FARMACIA,
            IntentCategory.BENEFICIO: FlowType.BENEFICIO,
            IntentCategory.DOCUMENTACAO: FlowType.DOCUMENTACAO,
            IntentCategory.GERAL: FlowType.GERAL,
        }
        return mapping.get(self)


@dataclass
class Intent:
    """Resultado da classificação de intenção."""

    category: IntentCategory
    confidence: float
    matched_keywords: List[str]
    subcategory: Optional[str] = None

    @property
    def flow_type(self) -> Optional[FlowType]:
        return self.category.to_flow_type()


class IntentClassifier:
    """
    Classificador de intenção baseado em keywords e padrões.

    Prioriza velocidade e previsibilidade sobre flexibilidade.
    Usa LLM apenas como fallback para casos ambíguos.
    """

    # Keywords por categoria
    KEYWORDS = {
        IntentCategory.FARMACIA: {
            "primary": [
                "remédio", "remedio", "medicamento", "medicamentos",
                "receita", "farmácia", "farmacia", "farmacêutico",
                "pedir remédio", "pegar remédio", "buscar remédio",
                "farmácia popular", "farmacia popular"
            ],
            "secondary": [
                "losartana", "metformina", "omeprazol", "sinvastatina",
                "atenolol", "hidroclorotiazida", "captopril", "enalapril",
                "insulina", "glibenclamida", "glicazida", "propranolol",
                "comprimido", "cápsula", "capsula", "dosagem", "mg", "mcg",
                "hipertensão", "hipertensao", "diabetes", "pressão", "pressao"
            ],
            "status": [
                "meu pedido", "status pedido", "ped-", "pedido"
            ]
        },
        IntentCategory.BENEFICIO: {
            "primary": [
                "bolsa família", "bolsa familia", "bpc", "loas",
                "benefício", "beneficio", "benefícios", "beneficios",
                "auxílio", "auxilio", "programa social", "programas sociais",
                "recebo", "tenho direito", "elegível", "elegivel",
                "quanto recebo", "valor do benefício", "consultar cpf"
            ],
            "secondary": [
                "tarifa social", "luz", "energia", "tsee",
                "auxílio gás", "auxilio gas", "gas", "gás",
                "seguro defeso", "pescador", "pesca",
                "garantia safra", "agricultor", "seca"
            ],
            "cpf": [
                "meu cpf", "consultar cpf", "meus benefícios"
            ]
        },
        IntentCategory.DOCUMENTACAO: {
            "primary": [
                "documento", "documentos", "documentação",
                "checklist", "lista de documentos",
                "cras", "assistência social", "assistencia social",
                "cadastro único", "cadastro unico", "cadunico", "cadúnico"
            ],
            "secondary": [
                "onde fazer", "onde ir", "endereço", "endereco",
                "horário", "horario", "telefone", "atendimento",
                "agendar", "agendamento", "marcar"
            ]
        }
    }

    # Padrões regex por categoria
    PATTERNS = {
        IntentCategory.FARMACIA: [
            r"quero\s+(?:pedir|buscar|pegar)\s+(?:meus?\s+)?rem[eé]dios?",
            r"preciso\s+de\s+rem[eé]dio",
            r"(?:minha|a)\s+receita",
            r"PED-\d+",  # Número de pedido
        ],
        IntentCategory.BENEFICIO: [
            r"(?:tenho|t[ôo]|posso ter)\s+direito\s+a",
            r"quanto\s+(?:eu\s+)?recebo",
            r"(?:meu|o)\s+(?:bolsa|bpc|benefício|auxílio)",
            r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",  # CPF
        ],
        IntentCategory.DOCUMENTACAO: [
            r"(?:quais?|que)\s+documentos?\s+(?:eu\s+)?preciso",
            r"(?:onde|como)\s+(?:é|fica|faz(?:er)?)\s+(?:o\s+)?(?:cadastro|cras)",
            r"(?:lista|checklist)\s+(?:de\s+)?documentos?",
        ]
    }

    # Peso por tipo de match
    WEIGHTS = {
        "primary": 1.0,
        "secondary": 0.6,
        "status": 0.8,
        "cpf": 0.7,
        "pattern": 0.9
    }

    def __init__(self, use_llm_fallback: bool = True):
        """
        Inicializa o classificador.

        Args:
            use_llm_fallback: Se deve usar LLM para casos ambíguos
        """
        self.use_llm_fallback = use_llm_fallback
        self._compile_patterns()

    def _compile_patterns(self):
        """Compila padrões regex."""
        self._compiled_patterns = {}
        for category, patterns in self.PATTERNS.items():
            self._compiled_patterns[category] = [
                re.compile(p, re.IGNORECASE)
                for p in patterns
            ]

    def classify(self, message: str) -> Intent:
        """
        Classifica a intenção da mensagem.

        Args:
            message: Texto da mensagem do usuário

        Returns:
            Intent com categoria, confiança e keywords matched
        """
        message_lower = message.lower()
        scores: dict[IntentCategory, Tuple[float, List[str]]] = {}

        # Pontuar cada categoria
        for category in [IntentCategory.FARMACIA, IntentCategory.BENEFICIO, IntentCategory.DOCUMENTACAO]:
            score, matched = self._score_category(message_lower, category)
            if score > 0:
                scores[category] = (score, matched)

        # Verificar padrões regex
        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    current_score, current_matched = scores.get(category, (0, []))
                    scores[category] = (
                        current_score + self.WEIGHTS["pattern"],
                        current_matched + [f"pattern:{pattern.pattern[:30]}"]
                    )

        # Selecionar categoria com maior score
        if scores:
            best_category = max(scores, key=lambda c: scores[c][0])
            best_score, matched = scores[best_category]

            # Normalizar confiança (max = 2.0, ideal = 1.0)
            confidence = min(1.0, best_score / 1.5)

            return Intent(
                category=best_category,
                confidence=confidence,
                matched_keywords=matched
            )

        # Nenhuma categoria identificada
        return Intent(
            category=IntentCategory.GERAL,
            confidence=0.5,
            matched_keywords=[]
        )

    def _score_category(
        self,
        message: str,
        category: IntentCategory
    ) -> Tuple[float, List[str]]:
        """
        Pontua mensagem para uma categoria.

        Returns:
            (score, lista de keywords encontradas)
        """
        keywords = self.KEYWORDS.get(category, {})
        total_score = 0.0
        matched = []

        for keyword_type, keyword_list in keywords.items():
            weight = self.WEIGHTS.get(keyword_type, 0.5)
            for keyword in keyword_list:
                if keyword in message:
                    total_score += weight
                    matched.append(keyword)
                    # Bonus para match exato
                    if f" {keyword} " in f" {message} ":
                        total_score += 0.1

        return total_score, matched

    async def classify_with_llm(self, message: str) -> Intent:
        """
        Classifica usando LLM (Gemini) para casos ambíguos.

        Args:
            message: Texto da mensagem

        Returns:
            Intent classificado pelo LLM
        """
        # Primeiro tenta classificação local
        local_intent = self.classify(message)

        # Se confiança alta, retorna direto
        if local_intent.confidence >= 0.7:
            return local_intent

        # Se não usa LLM fallback, retorna local
        if not self.use_llm_fallback:
            return local_intent

        # Chama LLM para classificar
        try:
            import google.generativeai as genai
            from app.config import settings

            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            prompt = f"""Classifique a intenção desta mensagem em português:

Mensagem: "{message}"

Categorias possíveis:
1. FARMACIA - Quer pedir medicamentos, saber sobre Farmácia Popular, enviar receita
2. BENEFICIO - Quer consultar benefícios (Bolsa Família, BPC, auxílios), saber se tem direito
3. DOCUMENTACAO - Quer saber documentos necessários, localizar CRAS, fazer CadÚnico
4. GERAL - Saudação, pergunta geral, outro assunto

Responda APENAS com a categoria (uma palavra): FARMACIA, BENEFICIO, DOCUMENTACAO ou GERAL"""

            response = model.generate_content(prompt)
            categoria_texto = response.text.strip().upper()

            # Mapear para enum
            categoria_map = {
                "FARMACIA": IntentCategory.FARMACIA,
                "BENEFICIO": IntentCategory.BENEFICIO,
                "DOCUMENTACAO": IntentCategory.DOCUMENTACAO,
                "GERAL": IntentCategory.GERAL
            }

            categoria = categoria_map.get(categoria_texto, IntentCategory.GERAL)

            return Intent(
                category=categoria,
                confidence=0.8,  # Confiança do LLM
                matched_keywords=["llm_classification"]
            )

        except Exception as e:
            logger.error(f"Erro ao classificar com LLM: {e}")
            return local_intent

    def is_greeting(self, message: str) -> bool:
        """Verifica se é uma saudação."""
        greetings = [
            "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite",
            "hey", "e aí", "e ai", "tudo bem", "opa", "fala"
        ]
        message_lower = message.lower().strip()
        return any(g == message_lower or message_lower.startswith(g + " ") for g in greetings)

    def is_thanks(self, message: str) -> bool:
        """Verifica se é agradecimento."""
        thanks = [
            "obrigado", "obrigada", "valeu", "vlw", "thanks",
            "muito obrigado", "muito obrigada", "brigado", "brigada"
        ]
        message_lower = message.lower()
        return any(t in message_lower for t in thanks)

    def is_help(self, message: str) -> bool:
        """Verifica se está pedindo ajuda."""
        help_words = [
            "ajuda", "help", "o que você faz", "o que voce faz",
            "como funciona", "me ajuda", "preciso de ajuda"
        ]
        message_lower = message.lower()
        return any(h in message_lower for h in help_words)

    def is_restart(self, message: str) -> bool:
        """Verifica se quer voltar ao início/recomeçar."""
        restart_words = [
            "voltar ao início", "voltar ao inicio", "começar de novo",
            "comecar de novo", "recomeçar", "recomecar", "reiniciar",
            "menu principal", "início", "inicio", "voltar",
            "menu", "sair", "cancelar tudo", "novo atendimento"
        ]
        message_lower = message.lower().strip()
        return any(r in message_lower for r in restart_words)
