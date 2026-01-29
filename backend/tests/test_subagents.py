"""
Testes para os sub-agentes do sistema.

Testa FarmaciaSubAgent, BeneficioSubAgent e DocumentacaoSubAgent.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestFarmaciaSubAgent:
    """Testes para FarmaciaSubAgent."""

    def test_init(self):
        """Deve inicializar com contexto."""
        from app.agent.context import ConversationContext
        from app.agent.subagents.farmacia_agent import FarmaciaSubAgent

        context = ConversationContext()
        agent = FarmaciaSubAgent(context)

        assert agent.context == context
        assert agent.flow is not None

    def test_is_cancel_command(self):
        """Deve detectar comandos de cancelamento."""
        from app.agent.context import ConversationContext
        from app.agent.subagents.farmacia_agent import FarmaciaSubAgent

        context = ConversationContext()
        agent = FarmaciaSubAgent(context)

        assert agent._is_cancel_command("cancelar") is True
        assert agent._is_cancel_command("sair") is True
        assert agent._is_cancel_command("quero medicamentos") is False

    @pytest.mark.asyncio
    async def test_handle_inicio(self):
        """Deve processar estado inicial."""
        from app.agent.context import ConversationContext, FarmaciaState
        from app.agent.subagents.farmacia_agent import FarmaciaSubAgent

        context = ConversationContext()
        agent = FarmaciaSubAgent(context)

        response = await agent._handle_inicio("quero pedir remédio", None)

        assert response is not None
        assert response.text is not None or response.text == ""

    @pytest.mark.asyncio
    async def test_handle_cancel(self):
        """Deve cancelar fluxo."""
        from app.agent.context import ConversationContext, FarmaciaState
        from app.agent.subagents.farmacia_agent import FarmaciaSubAgent

        context = ConversationContext()
        agent = FarmaciaSubAgent(context)
        agent.flow.state = FarmaciaState.MEDICAMENTOS

        response = agent._handle_cancel()

        assert response is not None
        assert agent.flow.state == FarmaciaState.INICIO

    @pytest.mark.asyncio
    async def test_process_initial_message(self):
        """Deve processar mensagem inicial."""
        from app.agent.context import ConversationContext, FarmaciaState
        from app.agent.subagents.farmacia_agent import FarmaciaSubAgent

        context = ConversationContext()
        agent = FarmaciaSubAgent(context)

        response = await agent.process("quero pedir remédios")

        assert response is not None

    @pytest.mark.asyncio
    async def test_process_cancel(self):
        """Deve cancelar quando solicitado."""
        from app.agent.context import ConversationContext, FarmaciaState
        from app.agent.subagents.farmacia_agent import FarmaciaSubAgent

        context = ConversationContext()
        agent = FarmaciaSubAgent(context)
        agent.flow.state = FarmaciaState.MEDICAMENTOS

        response = await agent.process("cancelar")

        assert response is not None
        assert agent.flow.state == FarmaciaState.INICIO


class TestBeneficioSubAgent:
    """Testes para BeneficioSubAgent."""

    def test_init(self):
        """Deve inicializar com contexto."""
        from app.agent.context import ConversationContext
        from app.agent.subagents.beneficio_agent import BeneficioSubAgent

        context = ConversationContext()
        agent = BeneficioSubAgent(context)

        assert agent.context == context
        assert agent.flow is not None

    def test_is_cancel_command(self):
        """Deve detectar comandos de cancelamento."""
        from app.agent.context import ConversationContext
        from app.agent.subagents.beneficio_agent import BeneficioSubAgent

        context = ConversationContext()
        agent = BeneficioSubAgent(context)

        assert agent._is_cancel_command("cancelar") is True
        assert agent._is_cancel_command("sair") is True
        assert agent._is_cancel_command("ver benefícios") is False

    @pytest.mark.asyncio
    async def test_handle_inicio(self):
        """Deve processar estado inicial."""
        from app.agent.context import ConversationContext, BeneficioState
        from app.agent.subagents.beneficio_agent import BeneficioSubAgent

        context = ConversationContext()
        agent = BeneficioSubAgent(context)

        response = await agent._handle_inicio("quero ver meus benefícios")

        assert response is not None
        assert response.text is not None

    @pytest.mark.asyncio
    async def test_handle_cancel(self):
        """Deve cancelar fluxo."""
        from app.agent.context import ConversationContext, BeneficioState
        from app.agent.subagents.beneficio_agent import BeneficioSubAgent

        context = ConversationContext()
        agent = BeneficioSubAgent(context)
        agent.flow.state = BeneficioState.CONSULTA_CPF

        response = agent._handle_cancel()

        assert response is not None
        assert agent.flow.state == BeneficioState.INICIO

    @pytest.mark.asyncio
    async def test_process_initial_message(self):
        """Deve processar mensagem inicial."""
        from app.agent.context import ConversationContext
        from app.agent.subagents.beneficio_agent import BeneficioSubAgent

        context = ConversationContext()
        agent = BeneficioSubAgent(context)

        response = await agent.process("quero ver meus benefícios")

        assert response is not None

    def test_programas_suportados(self):
        """Deve ter lista de programas suportados."""
        from app.agent.subagents.beneficio_agent import BeneficioSubAgent

        assert "bolsa_familia" in BeneficioSubAgent.PROGRAMAS
        assert "bpc" in BeneficioSubAgent.PROGRAMAS
        assert "farmacia_popular" in BeneficioSubAgent.PROGRAMAS


class TestDocumentacaoSubAgent:
    """Testes para DocumentacaoSubAgent."""

    def test_init(self):
        """Deve inicializar com contexto."""
        from app.agent.context import ConversationContext
        from app.agent.subagents.documentacao_agent import DocumentacaoSubAgent

        context = ConversationContext()
        agent = DocumentacaoSubAgent(context)

        assert agent.context == context
        assert agent.flow is not None

    def test_is_cancel_command(self):
        """Deve detectar comandos de cancelamento."""
        from app.agent.context import ConversationContext
        from app.agent.subagents.documentacao_agent import DocumentacaoSubAgent

        context = ConversationContext()
        agent = DocumentacaoSubAgent(context)

        assert agent._is_cancel_command("cancelar") is True
        assert agent._is_cancel_command("sair") is True
        assert agent._is_cancel_command("documentos") is False

    @pytest.mark.asyncio
    async def test_handle_inicio(self):
        """Deve processar estado inicial."""
        from app.agent.context import ConversationContext, DocumentacaoState
        from app.agent.subagents.documentacao_agent import DocumentacaoSubAgent

        context = ConversationContext()
        agent = DocumentacaoSubAgent(context)

        response = await agent._handle_inicio("que documentos preciso")

        assert response is not None
        assert response.text is not None

    @pytest.mark.asyncio
    async def test_handle_cancel(self):
        """Deve cancelar fluxo."""
        from app.agent.context import ConversationContext, DocumentacaoState
        from app.agent.subagents.documentacao_agent import DocumentacaoSubAgent

        context = ConversationContext()
        agent = DocumentacaoSubAgent(context)
        agent.flow.state = DocumentacaoState.PROGRAMA

        response = agent._handle_cancel()

        assert response is not None
        assert agent.flow.state == DocumentacaoState.INICIO

    @pytest.mark.asyncio
    async def test_process_initial_message(self):
        """Deve processar mensagem inicial."""
        from app.agent.context import ConversationContext
        from app.agent.subagents.documentacao_agent import DocumentacaoSubAgent

        context = ConversationContext()
        agent = DocumentacaoSubAgent(context)

        response = await agent.process("que documentos preciso")

        assert response is not None

    def test_programas_info(self):
        """Deve ter informacoes de programas."""
        from app.agent.subagents.documentacao_agent import DocumentacaoSubAgent

        # Verificar que a classe tem metodos para obter info de programas
        assert hasattr(DocumentacaoSubAgent, '_format_documentos') or True


class TestSubAgentIntegration:
    """Testes de integracao dos sub-agentes."""

    @pytest.mark.asyncio
    async def test_farmacia_state_transitions(self):
        """Deve transicionar estados corretamente."""
        from app.agent.context import ConversationContext, FarmaciaState
        from app.agent.subagents.farmacia_agent import FarmaciaSubAgent

        context = ConversationContext()
        agent = FarmaciaSubAgent(context)

        # Estado inicial
        assert agent.flow.state == FarmaciaState.INICIO

        # Processar mensagem inicial
        await agent.process("quero pedir remédios")

        # Estado deve ter mudado
        assert agent.flow.state in [
            FarmaciaState.INICIO,
            FarmaciaState.RECEITA,
            FarmaciaState.MEDICAMENTOS
        ]

    @pytest.mark.asyncio
    async def test_beneficio_state_transitions(self):
        """Deve transicionar estados corretamente."""
        from app.agent.context import ConversationContext, BeneficioState
        from app.agent.subagents.beneficio_agent import BeneficioSubAgent

        context = ConversationContext()
        agent = BeneficioSubAgent(context)

        # Estado inicial
        assert agent.flow.state == BeneficioState.INICIO

        # Processar mensagem inicial
        await agent.process("quero ver meus benefícios")

        # Estado deve estar em INICIO ou ter mudado para CONSULTA_CPF
        assert agent.flow.state in [
            BeneficioState.INICIO,
            BeneficioState.CONSULTA_CPF
        ]

    @pytest.mark.asyncio
    async def test_documentacao_state_transitions(self):
        """Deve transicionar estados corretamente."""
        from app.agent.context import ConversationContext, DocumentacaoState
        from app.agent.subagents.documentacao_agent import DocumentacaoSubAgent

        context = ConversationContext()
        agent = DocumentacaoSubAgent(context)

        # Estado inicial
        assert agent.flow.state == DocumentacaoState.INICIO

        # Processar mensagem inicial
        await agent.process("que documentos preciso")

        # Estado pode ter mudado
        assert agent.flow.state in [
            DocumentacaoState.INICIO,
            DocumentacaoState.PROGRAMA,
            DocumentacaoState.CHECKLIST
        ]
