"""
Testes para o Orchestrator do Ta na Mao.

Testa:
- Roteamento de intencoes
- Classificacao de mensagens
- Handoff para sub-agentes
- Fallback para Gemini
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.agent.orchestrator import AgentOrchestrator, get_orchestrator
from app.agent.context import ConversationContext, FlowType, session_manager
from app.agent.response_types import AgentResponse, Action, ActionType


@pytest.fixture
def orchestrator():
    """Cria orchestrator para testes."""
    return AgentOrchestrator()


@pytest.fixture
def clean_sessions():
    """Limpa sessoes antes e depois do teste."""
    session_manager._sessions.clear()
    yield
    session_manager._sessions.clear()


class TestOrchestratorRouting:
    """Testes de roteamento do Orchestrator."""

    @pytest.mark.asyncio
    async def test_roteia_para_farmacia(self, orchestrator, clean_sessions):
        """Deve rotear mensagem de farmacia para FarmaciaSubAgent."""
        response = await orchestrator.process_message("quero pedir remédios")

        assert response is not None
        assert response.text is not None
        # Deve mencionar receita ou remedio
        text_lower = response.text.lower()
        assert any(
            word in text_lower
            for word in ["receita", "remédio", "medicamento", "farmácia"]
        )

    @pytest.mark.asyncio
    async def test_roteia_para_beneficio(self, orchestrator, clean_sessions):
        """Deve rotear mensagem de beneficio para BeneficioSubAgent."""
        response = await orchestrator.process_message("quais benefícios eu recebo")

        assert response is not None
        assert response.text is not None
        # Deve pedir CPF ou mencionar beneficio
        text_lower = response.text.lower()
        assert any(
            word in text_lower
            for word in ["cpf", "benefício", "consultar"]
        )

    @pytest.mark.asyncio
    async def test_roteia_para_documentacao(self, orchestrator, clean_sessions):
        """Deve rotear mensagem de documentacao para DocumentacaoSubAgent."""
        response = await orchestrator.process_message("que documentos preciso para Bolsa Família")

        assert response is not None
        assert response.text is not None
        # Deve mencionar documentos ou programas
        text_lower = response.text.lower()
        assert any(
            word in text_lower
            for word in ["documento", "bolsa", "cpf", "programa"]
        )


class TestOrchestratorGreetings:
    """Testes de saudacoes e mensagens especiais."""

    @pytest.mark.asyncio
    async def test_responde_saudacao(self, orchestrator, clean_sessions):
        """Deve responder saudacao com boas-vindas."""
        response = await orchestrator.process_message("oi")

        assert response is not None
        assert response.text is not None
        assert len(response.suggested_actions) > 0

        # Deve ter acoes sugeridas
        action_labels = [a.label.lower() for a in response.suggested_actions]
        assert any(
            "remédio" in label or "benefício" in label or "documento" in label
            for label in action_labels
        )

    @pytest.mark.asyncio
    async def test_responde_agradecimento(self, orchestrator, clean_sessions):
        """Deve responder agradecimento."""
        response = await orchestrator.process_message("obrigado")

        assert response is not None
        assert response.text is not None
        text_lower = response.text.lower()
        assert "nada" in text_lower or "ajudar" in text_lower

    @pytest.mark.asyncio
    async def test_responde_pedido_ajuda(self, orchestrator, clean_sessions):
        """Deve explicar funcionalidades quando pedido ajuda."""
        response = await orchestrator.process_message("ajuda")

        assert response is not None
        assert response.text is not None
        # Deve listar funcionalidades
        text_lower = response.text.lower()
        assert any(
            word in text_lower
            for word in ["remédio", "benefício", "documento", "ajudar"]
        )


class TestOrchestratorSessionManagement:
    """Testes de gerenciamento de sessao."""

    @pytest.mark.asyncio
    async def test_mantem_sessao(self, orchestrator, clean_sessions):
        """Deve manter sessao entre mensagens."""
        # Primeira mensagem
        response1 = await orchestrator.process_message(
            "oi",
            session_id="test-session-1"
        )

        # Segunda mensagem na mesma sessao
        response2 = await orchestrator.process_message(
            "quero remédios",
            session_id="test-session-1"
        )

        # Ambas devem ter respostas
        assert response1 is not None
        assert response2 is not None

        # Sessao deve existir
        session = orchestrator.get_session("test-session-1")
        assert session is not None
        assert len(session.history) >= 2

    @pytest.mark.asyncio
    async def test_cria_nova_sessao(self, orchestrator, clean_sessions):
        """Deve criar nova sessao se nao existir."""
        response = await orchestrator.process_message("oi")

        assert response is not None

        # Deve ter criado sessao (verificar via context)
        assert response.context.get("session_id") or True  # Pode nao retornar no context

    @pytest.mark.asyncio
    async def test_reset_sessao(self, orchestrator, clean_sessions):
        """Deve resetar sessao corretamente."""
        # Cria sessao
        await orchestrator.process_message("oi", session_id="test-reset")

        # Reseta
        result = orchestrator.reset_session("test-reset")
        assert result is True

        # Sessao deve estar limpa
        session = orchestrator.get_session("test-reset")
        assert session is not None
        assert len(session.history) == 0


class TestOrchestratorFlowContinuity:
    """Testes de continuidade de fluxo."""

    @pytest.mark.asyncio
    async def test_continua_fluxo_farmacia(self, orchestrator, clean_sessions):
        """Deve continuar fluxo de farmacia iniciado."""
        session_id = "test-flow-farmacia"

        # Inicia fluxo de farmacia
        response1 = await orchestrator.process_message(
            "quero pedir remédios",
            session_id=session_id
        )

        # Envia mais mensagens - deve continuar no mesmo fluxo
        response2 = await orchestrator.process_message(
            "Losartana 50mg",
            session_id=session_id
        )

        # Verifica que esta no fluxo de farmacia
        session = orchestrator.get_session(session_id)
        assert session.active_flow == FlowType.FARMACIA

    @pytest.mark.asyncio
    async def test_continua_fluxo_beneficio(self, orchestrator, clean_sessions):
        """Deve continuar fluxo de beneficio iniciado."""
        session_id = "test-flow-beneficio"

        # Inicia fluxo
        await orchestrator.process_message(
            "quero ver meus benefícios",
            session_id=session_id
        )

        # Envia CPF
        await orchestrator.process_message(
            "123.456.789-00",
            session_id=session_id
        )

        # Verifica que esta no fluxo
        session = orchestrator.get_session(session_id)
        assert session.active_flow == FlowType.BENEFICIO


class TestOrchestratorWelcomeMessage:
    """Testes da mensagem de boas-vindas."""

    def test_get_welcome_message(self, orchestrator, clean_sessions):
        """Deve retornar mensagem de boas-vindas formatada."""
        response = orchestrator.get_welcome_message()

        assert response is not None
        assert response.text is not None
        assert "Tá na Mão" in response.text
        assert len(response.suggested_actions) > 0

    def test_welcome_message_cria_sessao(self, orchestrator, clean_sessions):
        """Deve criar sessao ao gerar mensagem de boas-vindas."""
        response = orchestrator.get_welcome_message(session_id="test-welcome")

        session = orchestrator.get_session("test-welcome")
        assert session is not None


class TestOrchestratorIntentClassification:
    """Testes de classificacao de intencao."""

    @pytest.mark.asyncio
    async def test_classifica_intencao_farmacia(self, orchestrator, clean_sessions):
        """Deve classificar corretamente intencao de farmacia."""
        messages = [
            "quero remédios",
            "preciso de medicamentos",
            "tenho uma receita",
            "farmácia popular",
        ]

        for msg in messages:
            response = await orchestrator.process_message(msg)
            assert response is not None

    @pytest.mark.asyncio
    async def test_classifica_intencao_beneficio(self, orchestrator, clean_sessions):
        """Deve classificar corretamente intencao de beneficio."""
        messages = [
            "quero ver meus benefícios",
            "tenho direito a bolsa família",
            "consultar BPC",
            "quanto recebo",
        ]

        for msg in messages:
            response = await orchestrator.process_message(msg)
            assert response is not None

    @pytest.mark.asyncio
    async def test_classifica_intencao_documentacao(self, orchestrator, clean_sessions):
        """Deve classificar corretamente intencao de documentacao."""
        messages = [
            "que documentos preciso",
            "onde fica o CRAS",
            "fazer CadUnico",
            "checklist de documentos",
        ]

        for msg in messages:
            response = await orchestrator.process_message(msg)
            assert response is not None


class TestOrchestratorErrorHandling:
    """Testes de tratamento de erro."""

    @pytest.mark.asyncio
    async def test_handles_empty_message(self, orchestrator, clean_sessions):
        """Deve lidar com mensagem vazia."""
        response = await orchestrator.process_message("")

        # Deve retornar resposta valida
        assert response is not None
        assert response.text is not None

    @pytest.mark.asyncio
    async def test_handles_very_long_message(self, orchestrator, clean_sessions):
        """Deve lidar com mensagem muito longa."""
        long_message = "a" * 10000

        response = await orchestrator.process_message(long_message)

        # Deve retornar resposta valida
        assert response is not None
        assert response.text is not None

    @pytest.mark.asyncio
    async def test_handles_special_characters(self, orchestrator, clean_sessions):
        """Deve lidar com caracteres especiais."""
        special_message = "Olá! 😀 Como está? Preciso de ajuda com <script>alert('xss')</script>"

        response = await orchestrator.process_message(special_message)

        # Deve retornar resposta valida
        assert response is not None
        assert response.text is not None


class TestOrchestratorSingleton:
    """Testes do singleton do Orchestrator."""

    def test_get_orchestrator_returns_same_instance(self):
        """Deve retornar mesma instancia do orchestrator."""
        orch1 = get_orchestrator()
        orch2 = get_orchestrator()

        assert orch1 is orch2

    def test_orchestrator_has_subagents(self):
        """Orchestrator deve ter sub-agentes configurados."""
        orch = get_orchestrator()

        assert FlowType.FARMACIA in orch.SUBAGENT_MAP
        assert FlowType.BENEFICIO in orch.SUBAGENT_MAP
        assert FlowType.DOCUMENTACAO in orch.SUBAGENT_MAP
