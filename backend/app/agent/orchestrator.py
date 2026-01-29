"""
Orquestrador principal do agente Tá na Mão.

Responsabilidades:
1. Classificar intenção da mensagem
2. Rotear para sub-agente apropriado
3. Gerenciar contexto da conversa
4. Formatar resposta estruturada (A2UI)

Pattern: Hierarchical Multi-Agent com Sub-agents
- Orquestrador é stateless (state está no contexto)
- Sub-agents são especializados e stateful
"""

import logging
from typing import Optional, Dict, Type
import google.generativeai as genai

from .context import (
    ConversationContext,
    FlowType,
    MessageRole,
    session_manager
)
from .response_types import (
    AgentResponse,
    Action,
    UIComponent,
    AlertData
)
from .intent_classifier import IntentClassifier
from .subagents import FarmaciaSubAgent, BeneficioSubAgent, DocumentacaoSubAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orquestrador principal do agente.

    Classifica intenção e delega para sub-agentes especializados.
    Mantém fallback para Gemini em casos gerais.
    """

    # Mapeamento de categorias para sub-agentes
    SUBAGENT_MAP: Dict[FlowType, Type] = {
        FlowType.FARMACIA: FarmaciaSubAgent,
        FlowType.BENEFICIO: BeneficioSubAgent,
        FlowType.DOCUMENTACAO: DocumentacaoSubAgent,
    }

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Inicializa o orquestrador.

        Args:
            model_name: Nome do modelo Gemini para fallback
        """
        self.model_name = model_name
        self.intent_classifier = IntentClassifier(use_llm_fallback=True)
        self._setup_gemini()

    def _setup_gemini(self):
        """Configura modelo Gemini para fallback."""
        try:
            from app.config import settings
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self._get_system_prompt()
            )
        except Exception as e:
            logger.error(f"Erro ao configurar Gemini: {e}")
            self.gemini_model = None

    def _get_system_prompt(self) -> str:
        """Retorna system prompt para Gemini fallback."""
        return """Você é o Tá na Mão, assistente de benefícios sociais do governo brasileiro.

Seu objetivo é AJUDAR cidadãos a:
- Entender quais benefícios têm direito
- Pedir medicamentos pelo Farmácia Popular
- Saber quais documentos precisam
- Encontrar o CRAS mais próximo

REGRAS:
1. Use linguagem SIMPLES, frases CURTAS
2. Uma informação por vez
3. Sempre ofereça PRÓXIMO PASSO claro
4. Seja empático mas objetivo

PROGRAMAS QUE VOCÊ CONHECE:
- Bolsa Família: transferência de renda para famílias em situação de pobreza
- BPC/LOAS: benefício para idosos e pessoas com deficiência
- Farmácia Popular: medicamentos gratuitos ou com desconto
- Tarifa Social de Energia: desconto na conta de luz
- CadÚnico: cadastro para acessar programas sociais

Se não souber algo específico, oriente a procurar o CRAS."""

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """
        Processa mensagem do usuário.

        Args:
            message: Texto da mensagem
            session_id: ID da sessão (opcional, cria nova se não existir)
            image_base64: Imagem anexada (opcional)

        Returns:
            AgentResponse estruturado
        """
        # Obter ou criar contexto
        context = session_manager.get_or_create(session_id)

        # Registrar mensagem do usuário
        context.add_message(MessageRole.USER, message)

        try:
            response = await self._route_message(message, context, image_base64)
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            response = AgentResponse(
                text="Ops, tive um problema aqui. Pode tentar de novo?",
                ui_components=[
                    UIComponent.alert(AlertData(
                        type="error",
                        title="Erro",
                        message="Tente novamente em alguns segundos",
                        dismissable=True
                    ))
                ]
            )

        # Registrar resposta do assistente
        context.add_message(MessageRole.ASSISTANT, response.text)

        return response

    async def _route_message(
        self,
        message: str,
        context: ConversationContext,
        image_base64: Optional[str] = None
    ) -> AgentResponse:
        """
        Roteia mensagem para handler apropriado.

        Lógica:
        1. Se já está em um fluxo, continua nele
        2. Se não, classifica intenção e inicia fluxo
        3. Se intenção é geral, usa Gemini fallback
        """

        # 1. Verificar mensagens especiais
        if self.intent_classifier.is_greeting(message):
            return self._handle_greeting(context)

        if self.intent_classifier.is_thanks(message):
            return self._handle_thanks()

        if self.intent_classifier.is_help(message):
            return self._handle_help()

        if self.intent_classifier.is_restart(message):
            return self._handle_restart(context)

        # 2. Se já está em um fluxo ativo, continua nele
        if context.active_flow and context.active_flow in self.SUBAGENT_MAP:
            subagent_class = self.SUBAGENT_MAP[context.active_flow]
            subagent = subagent_class(context)
            return await subagent.process(message, image_base64)

        # 3. Classificar intenção
        intent = self.intent_classifier.classify(message)
        logger.info(f"Intent classificado: {intent.category} (conf={intent.confidence:.2f})")

        # 4. Se confiança baixa, tenta LLM
        if intent.confidence < 0.5:
            intent = await self.intent_classifier.classify_with_llm(message)

        # 5. Rotear para sub-agente se categoria conhecida
        flow_type = intent.category.to_flow_type()

        if flow_type and flow_type in self.SUBAGENT_MAP:
            # Iniciar novo fluxo
            context.start_flow(flow_type)
            subagent_class = self.SUBAGENT_MAP[flow_type]
            subagent = subagent_class(context)
            return await subagent.process(message, image_base64)

        # 6. Fallback para Gemini
        return await self._gemini_fallback(message, context)

    def _handle_greeting(self, context: ConversationContext) -> AgentResponse:
        """Responde saudação."""

        # Se é primeira mensagem
        if len(context.history) <= 1:
            return AgentResponse(
                text="Oi! Sou o Tá na Mão, seu assistente de benefícios sociais.\n\n"
                     "Posso te ajudar a:\n"
                     "- Pedir remédios pelo Farmácia Popular\n"
                     "- Consultar seus benefícios\n"
                     "- Saber quais documentos você precisa\n\n"
                     "O que você precisa hoje?",
                suggested_actions=[
                    Action.send_message("Pedir remédios", "quero pedir remédios", primary=True),
                    Action.send_message("Ver meus benefícios", "quais benefícios eu tenho"),
                    Action.send_message("Preciso de documentos", "que documentos preciso"),
                ]
            )

        # Saudação durante conversa
        return AgentResponse(
            text="Oi! Em que posso ajudar?",
            suggested_actions=[
                Action.send_message("Pedir remédios", "quero pedir remédios"),
                Action.send_message("Outra dúvida", "preciso de ajuda"),
            ]
        )

    def _handle_thanks(self) -> AgentResponse:
        """Responde agradecimento."""
        return AgentResponse(
            text="De nada! Fico feliz em ajudar.\n\n"
                 "Precisa de mais alguma coisa?",
            suggested_actions=[
                Action.send_message("Sim", "preciso de mais ajuda"),
                Action.send_message("Não, obrigado", "não preciso"),
            ]
        )

    def _handle_help(self) -> AgentResponse:
        """Responde pedido de ajuda."""
        return AgentResponse(
            text="Claro! Eu sou o Tá na Mão e posso te ajudar com:\n\n"
                 "**REMÉDIOS**\n"
                 "Manda a receita que eu acho farmácias perto de você\n\n"
                 "**BENEFÍCIOS**\n"
                 "Me fala seu CPF que eu mostro o que você recebe\n\n"
                 "**DOCUMENTOS**\n"
                 "Te falo quais documentos precisa e onde ir\n\n"
                 "Escolhe uma opção ou me conta o que precisa!",
            suggested_actions=[
                Action.send_message("Quero remédios", "quero pedir remédios"),
                Action.send_message("Consultar CPF", "consultar meus benefícios"),
                Action.send_message("Lista de documentos", "que documentos preciso"),
            ]
        )

    def _handle_restart(self, context: ConversationContext) -> AgentResponse:
        """Volta ao início e reseta o fluxo ativo."""
        # Resetar fluxo ativo
        context.end_flow()

        return AgentResponse(
            text="Certo! Voltamos ao início.\n\n"
                 "O que você precisa agora?",
            suggested_actions=[
                Action.send_message("Pedir remédios", "quero pedir remédios", primary=True),
                Action.send_message("Consultar benefícios", "consultar meus benefícios"),
                Action.send_message("Ver documentos", "que documentos preciso"),
            ]
        )

    async def _gemini_fallback(
        self,
        message: str,
        context: ConversationContext
    ) -> AgentResponse:
        """
        Usa Gemini para responder mensagem geral.

        Fallback quando não há sub-agente específico.
        """
        if not self.gemini_model:
            return AgentResponse(
                text="Desculpa, não entendi. Pode explicar de outra forma?\n\n"
                     "Ou escolhe uma opção:",
                suggested_actions=[
                    Action.send_message("Pedir remédios", "quero pedir remédios"),
                    Action.send_message("Ver benefícios", "quais benefícios tenho"),
                    Action.send_message("Falar com atendente", "quero falar com pessoa"),
                ]
            )

        try:
            # Montar histórico para Gemini
            history = []
            for msg in context.history[-10:]:  # Últimas 10 mensagens
                role = "user" if msg.role == MessageRole.USER else "model"
                history.append({"role": role, "parts": [msg.content]})

            # Criar chat com histórico
            chat = self.gemini_model.start_chat(history=history[:-1])

            # Enviar mensagem atual
            response = chat.send_message(message)
            response_text = response.text

            # Tentar identificar próximos passos
            actions = self._extract_actions_from_response(response_text)

            return AgentResponse(
                text=response_text,
                suggested_actions=actions
            )

        except Exception as e:
            logger.error(f"Erro no Gemini fallback: {e}")
            return AgentResponse(
                text="Tive um problema para responder. Tenta de novo?",
                suggested_actions=[
                    Action.send_message("Tentar novamente", message[:50])
                ]
            )

    def _extract_actions_from_response(self, response: str) -> list:
        """Extrai ações sugeridas do texto da resposta."""
        actions = []
        response_lower = response.lower()

        # Detectar se é sobre DINHEIRO ESQUECIDO
        palavras_dinheiro_esquecido = [
            "dinheiro esquecido", "pis", "pasep", "valores a receber",
            "svr", "fgts", "saque-aniversário", "saque aniversario",
            "conta antiga", "dinheiro parado", "repis"
        ]

        if any(p in response_lower for p in palavras_dinheiro_esquecido):
            # Mostrar opções de tipos de dinheiro esquecido
            actions.append(Action.send_message("Ver PIS/PASEP", "como consultar meu PIS PASEP esquecido"))
            actions.append(Action.send_message("Ver Valores a Receber", "como consultar valores a receber no banco central"))
            actions.append(Action.send_message("Ver FGTS", "como consultar meu FGTS"))
            return actions[:3]

        # Detectar se está perguntando qual programa/ajuda verificar
        # Nesse caso, mostrar opções de programas específicos
        perguntas_qual_programa = [
            "qual ajuda",
            "qual benefício",
            "qual programa",
            "me fala qual",
            "principais ajudas",
            "você pode receber",
            "tem direito",
        ]

        if any(p in response_lower for p in perguntas_qual_programa):
            # Mostrar opções de programas específicos
            actions.append(Action.send_message("Dinheiro esquecido", "quero ver se tenho dinheiro esquecido"))
            actions.append(Action.send_message("Bolsa Família", "quero saber se tenho direito ao Bolsa Família"))
            actions.append(Action.send_message("Remédio de graça", "quero remédio de graça pelo Farmácia Popular"))
            actions.append(Action.send_message("BPC/Idosos", "quero saber sobre BPC para idosos"))
            return actions[:4]  # Máximo 4 opções de programas

        # Prioridade: farmácia > CRAS (não misturar os dois)
        if any(word in response_lower for word in ["farmácia", "remédio", "medicamento", "receita", "insulina"]):
            actions.append(Action.send_message("Encontrar Farmácia", "onde tem farmácia popular perto de mim"))
            actions.append(Action.send_message("Enviar receita", "quero enviar foto da receita"))
        elif any(word in response_lower for word in ["cras", "cadastro", "cadunico", "cadúnico", "posto"]):
            # Só mostra CRAS se NÃO for sobre farmácia
            actions.append(Action.send_message("Onde fica o posto?", "onde fica o posto de assistência social"))

        # Ação padrão se não encontrou nenhuma
        if not actions:
            actions.append(Action.send_message("Continuar", "me conta mais"))

        return actions[:3]  # Máximo 3 ações

    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Obtém contexto da sessão."""
        return session_manager.get(session_id)

    def reset_session(self, session_id: str) -> bool:
        """Reseta sessão."""
        return session_manager.reset(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Remove sessão."""
        return session_manager.delete(session_id)

    def get_welcome_message(self, session_id: Optional[str] = None) -> AgentResponse:
        """Retorna mensagem de boas-vindas."""
        context = session_manager.get_or_create(session_id)

        return AgentResponse(
            text="Oi! Sou o **Tá na Mão**, seu assistente de benefícios sociais.\n\n"
                 "Como posso ajudar você hoje?",
            suggested_actions=[
                Action.send_message("Dinheiro esquecido", "quero ver se tenho dinheiro esquecido para receber", primary=True),
                Action.send_message("Pedir remédios", "quero pedir remédios pelo Farmácia Popular"),
                Action.send_message("Ver meus benefícios", "quais benefícios eu recebo"),
                Action.send_message("Documentos necessários", "que documentos preciso"),
            ],
            context={"session_id": context.session_id}
        )


# Singleton para uso global
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Obtém instância singleton do orquestrador."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
