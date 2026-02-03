"""
Sub-agente especializado em protecao social.

Gerencia o fluxo de acolhimento e encaminhamento para
situacoes de urgencia/vulnerabilidade:
1. Triagem - Detectar tipo e nivel de urgencia
2. Identificacao de risco - Entender melhor a situacao
3. Encaminhamento - Direcionar para servico apropriado
4. Acompanhamento - Verificar se conseguiu ajuda

SENSIBILIDADE: Mensagens acolhedoras, sem julgamento,
linguagem simples. Prioridade maxima.
"""

import logging
from typing import Optional

from ..context import (
    ConversationContext,
    FlowType,
)
from ..response_types import (
    AgentResponse,
    UIComponent,
    Action,
    ActionType,
    AlertData,
)
from ..tools.rede_protecao import (
    detectar_urgencia,
    buscar_servico_protecao,
    NivelUrgencia,
    TipoServico,
)

logger = logging.getLogger(__name__)


# Estados do fluxo de protecao
class ProtecaoState:
    TRIAGEM = "triagem"
    IDENTIFICACAO_RISCO = "identificacao_risco"
    ENCAMINHAMENTO = "encaminhamento"
    ACOMPANHAMENTO = "acompanhamento"


class ProtecaoSubAgent:
    """
    Sub-agente para rede de protecao social.

    Implementa maquina de estados para acolher e encaminhar
    cidadaos em situacoes de urgencia/vulnerabilidade.
    """

    def __init__(self, context: ConversationContext):
        self.context = context
        # Recuperar estado do fluxo ou iniciar novo
        if context.active_flow == FlowType.PROTECAO:
            self.flow_data = context.flow_data or {}
        else:
            self.flow_data = {}
        self.state = self.flow_data.get("state", ProtecaoState.TRIAGEM)

    def _save_state(self):
        """Salva estado do fluxo no contexto."""
        self.flow_data["state"] = self.state
        self.context.flow_data = self.flow_data

    async def process(self, message: str, image_base64: Optional[str] = None) -> AgentResponse:
        """Processa mensagem no fluxo de protecao."""
        logger.info(f"ProtecaoAgent: state={self.state}, msg={message[:50]}...")

        if self.state == ProtecaoState.TRIAGEM:
            return await self._handle_triagem(message)
        elif self.state == ProtecaoState.IDENTIFICACAO_RISCO:
            return await self._handle_identificacao(message)
        elif self.state == ProtecaoState.ENCAMINHAMENTO:
            return await self._handle_encaminhamento(message)
        elif self.state == ProtecaoState.ACOMPANHAMENTO:
            return await self._handle_acompanhamento(message)
        else:
            return await self._handle_triagem(message)

    async def _handle_triagem(self, message: str) -> AgentResponse:
        """Triagem inicial - detecta urgencia e acolhe."""
        resultado = detectar_urgencia(message)

        if not resultado["urgencia_detectada"]:
            # Nao detectou urgencia, mas chegou aqui por algum motivo
            return AgentResponse(
                text=(
                    "Entendi que voce pode estar precisando de ajuda. "
                    "Me conta um pouco mais sobre o que esta acontecendo?"
                ),
                suggested_actions=[
                    Action.send_message("Estou passando por dificuldades", "preciso de ajuda com uma situacao dificil"),
                    Action.send_message("Voltar ao inicio", "menu"),
                ],
            )

        nivel = resultado["nivel"]
        categorias = resultado["categorias"]
        servicos = resultado["servicos_recomendados"]

        # Salvar dados de urgencia no fluxo
        self.flow_data["urgencia"] = resultado
        self.flow_data["servicos"] = servicos

        # EMERGENCIA: resposta imediata com telefone
        if nivel == NivelUrgencia.EMERGENCIA:
            return self._responder_emergencia(categorias, servicos)

        # ALTA: acolhimento + encaminhamento direto
        if nivel == NivelUrgencia.ALTA:
            self.state = ProtecaoState.ENCAMINHAMENTO
            self._save_state()
            return self._responder_urgencia_alta(categorias, servicos)

        # MEDIA: acolhimento + perguntar mais
        self.state = ProtecaoState.IDENTIFICACAO_RISCO
        self._save_state()
        return self._responder_urgencia_media(categorias, servicos)

    def _responder_emergencia(self, categorias, servicos) -> AgentResponse:
        """Resposta para situacao de EMERGENCIA."""
        # Identificar se eh suicidio/autolesao
        eh_suicidio = any(c["categoria"] == "suicidio" for c in categorias)
        eh_medica = any(c["categoria"] == "emergencia_medica" for c in categorias)

        if eh_suicidio:
            text = (
                "Voce nao esta sozinho(a). Eu me importo com voce.\n\n"
                "LIGUE AGORA para o CVV: 188\n"
                "Funciona 24 horas, eh de graca e sigiloso.\n\n"
                "Voce tambem pode acessar o chat:\n"
                "https://www.cvv.org.br/chat/\n\n"
                "Se estiver em perigo imediato, ligue 192 (SAMU)."
            )
            actions = [
                Action(
                    label="Ligar CVV (188)",
                    action_type=ActionType.CALL_PHONE,
                    payload="188",
                    primary=True,
                ),
                Action(
                    label="Ligar SAMU (192)",
                    action_type=ActionType.CALL_PHONE,
                    payload="192",
                ),
            ]
        elif eh_medica:
            text = (
                "Entendi que eh uma emergencia medica!\n\n"
                "LIGUE AGORA para o SAMU: 192\n"
                "A ambulancia vai ate voce.\n\n"
                "Funciona 24 horas, eh de graca."
            )
            actions = [
                Action(
                    label="Ligar SAMU (192)",
                    action_type=ActionType.CALL_PHONE,
                    payload="192",
                    primary=True,
                ),
            ]
        else:
            telefone_principal = servicos[0]["telefone"] if servicos else "192"
            text = (
                "Entendi que voce precisa de ajuda urgente.\n\n"
                f"LIGUE AGORA: {telefone_principal}\n"
                "Funciona 24 horas e eh de graca.\n\n"
                "Se for emergencia medica, ligue 192 (SAMU)."
            )
            actions = [
                Action(
                    label=f"Ligar {telefone_principal}",
                    action_type=ActionType.CALL_PHONE,
                    payload=telefone_principal,
                    primary=True,
                ),
            ]

        ui_components = [
            UIComponent.alert(AlertData(
                type="error",
                title="Ajuda Urgente",
                message="Se voce esta em perigo, ligue agora para o numero indicado.",
                dismissable=False,
            ))
        ]

        self.state = ProtecaoState.ACOMPANHAMENTO
        self._save_state()

        return AgentResponse(
            text=text,
            ui_components=ui_components,
            suggested_actions=actions,
        )

    def _responder_urgencia_alta(self, categorias, servicos) -> AgentResponse:
        """Resposta para urgencia ALTA."""
        # Montar mensagem acolhedora com servicos
        servico_principal = servicos[0] if servicos else None

        text = "Eu entendo que voce esta passando por uma situacao muito dificil. Voce nao esta sozinho(a).\n\n"

        if servico_principal:
            text += f"O melhor lugar para te ajudar eh o {servico_principal['nome']}.\n"
            text += f"Telefone: {servico_principal['telefone']}\n"
            text += f"{servico_principal['descricao']}\n\n"

        if len(servicos) > 1:
            text += "Outros servicos que podem ajudar:\n"
            for s in servicos[1:]:
                text += f"- {s['nome']}: {s['telefone']}\n"
            text += "\n"

        text += "Todos esses servicos sao DE GRACA."

        actions = []
        for s in servicos[:2]:
            telefone = s["telefone"]
            # Apenas adicionar botao se o telefone for um numero simples
            if telefone.isdigit() or len(telefone) <= 5:
                actions.append(Action(
                    label=f"Ligar {telefone}",
                    action_type=ActionType.CALL_PHONE,
                    payload=telefone,
                    primary=(s == servicos[0]),
                ))

        actions.append(
            Action.send_message("Me conta mais", "quero contar mais sobre minha situacao")
        )

        return AgentResponse(
            text=text,
            suggested_actions=actions,
        )

    def _responder_urgencia_media(self, categorias, servicos) -> AgentResponse:
        """Resposta para urgencia MEDIA."""
        text = (
            "Entendi. Fico feliz que voce esta buscando ajuda.\n\n"
            "Pra eu poder te orientar melhor, me conta:\n"
            "Voce esta em algum perigo agora?"
        )

        return AgentResponse(
            text=text,
            suggested_actions=[
                Action.send_message("Sim, preciso de ajuda agora", "estou em perigo agora", primary=True),
                Action.send_message("Nao, mas preciso de orientacao", "nao estou em perigo mas preciso de ajuda"),
                Action.send_message("Quero saber sobre servicos", "quais servicos podem me ajudar"),
            ],
        )

    async def _handle_identificacao(self, message: str) -> AgentResponse:
        """Identificacao de risco - entender melhor a situacao."""
        message_lower = message.lower()

        # Verifica se escalou para emergencia
        resultado_urgencia = detectar_urgencia(message)
        if (resultado_urgencia["urgencia_detectada"]
                and resultado_urgencia["nivel"] in [NivelUrgencia.EMERGENCIA, NivelUrgencia.ALTA]):
            self.flow_data["urgencia"] = resultado_urgencia
            self.flow_data["servicos"] = resultado_urgencia["servicos_recomendados"]
            self.state = ProtecaoState.ENCAMINHAMENTO
            self._save_state()
            return self._responder_urgencia_alta(
                resultado_urgencia["categorias"],
                resultado_urgencia["servicos_recomendados"]
            )

        # Se diz que esta em perigo
        em_perigo = any(p in message_lower for p in [
            "sim", "perigo", "agora", "urgente", "socorro"
        ])

        if em_perigo:
            servicos = self.flow_data.get("servicos", [])
            self.state = ProtecaoState.ENCAMINHAMENTO
            self._save_state()
            return self._responder_urgencia_alta(
                self.flow_data.get("urgencia", {}).get("categorias", []),
                servicos
            )

        # Nao esta em perigo imediato - orientar servicos
        self.state = ProtecaoState.ENCAMINHAMENTO
        self._save_state()

        servicos = self.flow_data.get("servicos", [])
        if servicos:
            servico = servicos[0]
            text = (
                "Que bom que voce nao esta em perigo imediato.\n\n"
                f"Recomendo procurar o {servico['nome']}.\n"
                f"Telefone: {servico['telefone']}\n\n"
                f"{servico['descricao']}\n\n"
                "Eh de graca e sigiloso."
            )
        else:
            text = (
                "Recomendo ligar pro Disque Social: 121\n"
                "Eles vao te orientar sobre o melhor servico pra voce.\n\n"
                "Eh de graca!"
            )

        self.state = ProtecaoState.ACOMPANHAMENTO
        self._save_state()

        return AgentResponse(
            text=text,
            suggested_actions=[
                Action.send_message("Preciso de outro tipo de ajuda", "preciso de ajuda com outra coisa"),
                Action.send_message("Voltar ao inicio", "menu"),
            ],
        )

    async def _handle_encaminhamento(self, message: str) -> AgentResponse:
        """Encaminhamento - fornecer detalhes do servico."""
        message_lower = message.lower()

        # Verificar se quer detalhes de um servico especifico
        for tipo_servico in [
            TipoServico.CREAS, TipoServico.CAPS, TipoServico.SAMU,
            TipoServico.CENTRO_POP, TipoServico.CONSELHO_TUTELAR,
            TipoServico.CVV, TipoServico.DISQUE_100, TipoServico.LIGUE_180,
        ]:
            if tipo_servico.lower() in message_lower:
                resultado = buscar_servico_protecao(tipo_servico)
                if resultado["encontrado"]:
                    text = (
                        f"{resultado['nome']}\n\n"
                        f"Telefone: {resultado['telefone']}\n"
                        f"Horario: {resultado['horario']}\n\n"
                        f"{resultado['descricao']}\n\n"
                        "Eh de graca!"
                    )
                    self.state = ProtecaoState.ACOMPANHAMENTO
                    self._save_state()
                    return AgentResponse(
                        text=text,
                        suggested_actions=[
                            Action.send_message("Preciso de mais ajuda", "preciso de ajuda com outra coisa"),
                            Action.send_message("Voltar ao inicio", "menu"),
                        ],
                    )

        # Default: mostrar servicos recomendados
        self.state = ProtecaoState.ACOMPANHAMENTO
        self._save_state()

        servicos = self.flow_data.get("servicos", [])
        if servicos:
            text = "Aqui estao os servicos que podem te ajudar:\n\n"
            for s in servicos:
                text += f"- {s['nome']}: {s['telefone']}\n"
            text += "\nTodos sao de graca."
        else:
            text = (
                "Ligue pro Disque Social: 121\n"
                "Eles vao te orientar sobre o melhor servico.\n"
                "Eh de graca!"
            )

        return AgentResponse(
            text=text,
            suggested_actions=[
                Action.send_message("Voltar ao inicio", "menu"),
            ],
        )

    async def _handle_acompanhamento(self, message: str) -> AgentResponse:
        """Acompanhamento - verificar se conseguiu ajuda."""
        message_lower = message.lower()

        # Verificar se quer voltar ao inicio
        if any(w in message_lower for w in ["menu", "inicio", "voltar", "outra"]):
            self.context.end_flow()
            return AgentResponse(
                text="Certo! Estou aqui se precisar de mais alguma coisa.",
                suggested_actions=[
                    Action.send_message("Consultar beneficios", "quais beneficios eu tenho"),
                    Action.send_message("Pedir remedios", "quero pedir remedios"),
                    Action.send_message("Preciso de ajuda", "preciso de ajuda"),
                ],
            )

        # Verificar nova urgencia
        resultado = detectar_urgencia(message)
        if resultado["urgencia_detectada"]:
            self.state = ProtecaoState.TRIAGEM
            self._save_state()
            return await self._handle_triagem(message)

        # Continuar acompanhamento
        return AgentResponse(
            text=(
                "Estou aqui pra te ajudar. Voce conseguiu contato "
                "com o servico que indiquei?\n\n"
                "Se precisar de mais alguma coisa, eh so me falar."
            ),
            suggested_actions=[
                Action.send_message("Sim, consegui", "consegui ajuda obrigado"),
                Action.send_message("Nao consegui", "nao consegui contato preciso de ajuda"),
                Action.send_message("Voltar ao inicio", "menu"),
            ],
        )
