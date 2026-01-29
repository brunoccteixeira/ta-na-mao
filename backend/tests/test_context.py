"""
Testes para o modulo de contexto do agente.

Testa ConversationContext, CitizenProfile, e FlowData.
"""

import pytest


class TestCitizenProfile:
    """Testes para CitizenProfile."""

    def test_create_empty_profile(self):
        """Deve criar perfil vazio."""
        from app.agent.context import CitizenProfile

        profile = CitizenProfile()

        assert profile.cpf is None
        assert profile.nome is None
        assert profile.latitude is None
        assert profile.longitude is None

    def test_update_from_geolocation(self):
        """Deve atualizar localizacao."""
        from app.agent.context import CitizenProfile

        profile = CitizenProfile()
        profile.update_from_geolocation(
            latitude=-23.5505,
            longitude=-46.6333,
            accuracy=10.0
        )

        assert profile.latitude == -23.5505
        assert profile.longitude == -46.6333
        assert profile.geo_accuracy == 10.0

    def test_has_geolocation(self):
        """Deve verificar se tem localizacao."""
        from app.agent.context import CitizenProfile

        profile = CitizenProfile()
        assert profile.has_geolocation() is False

        profile.latitude = -23.5505
        profile.longitude = -46.6333
        assert profile.has_geolocation() is True

    def test_set_cpf(self):
        """Deve setar CPF e mascara."""
        from app.agent.context import CitizenProfile

        profile = CitizenProfile()
        profile.cpf = "12345678900"
        profile.cpf_masked = "123.***.***-00"

        assert profile.cpf == "12345678900"
        assert profile.cpf_masked == "123.***.***-00"

    def test_update_from_cep_result(self):
        """Deve atualizar localizacao a partir de CEP."""
        from app.agent.context import CitizenProfile

        profile = CitizenProfile()
        profile.update_from_cep_result({
            "cep": "01310-100",
            "ibge": "3550308",
            "localidade": "São Paulo",
            "uf": "SP",
            "bairro": "Bela Vista",
            "logradouro": "Avenida Paulista"
        })

        assert profile.cep == "01310-100"
        assert profile.ibge_code == "3550308"
        assert profile.cidade == "São Paulo"
        assert profile.uf == "SP"


class TestConversationContext:
    """Testes para ConversationContext."""

    def test_create_context(self):
        """Deve criar contexto vazio."""
        from app.agent.context import ConversationContext

        context = ConversationContext()

        assert context.active_flow is None
        assert context.citizen is not None
        assert context.session_id is not None

    def test_add_message(self):
        """Deve adicionar mensagem ao historico."""
        from app.agent.context import ConversationContext, MessageRole

        context = ConversationContext()
        initial_len = len(context.history)

        context.add_message(MessageRole.USER, "Ola")

        assert len(context.history) == initial_len + 1
        assert context.history[-1].content == "Ola"

    def test_add_tool_usage(self):
        """Deve registrar uso de tool."""
        from app.agent.context import ConversationContext

        context = ConversationContext()

        context.add_tool_usage("validar_cpf")
        context.add_tool_usage("buscar_cep")
        context.add_tool_usage("validar_cpf")  # Duplicata

        assert "validar_cpf" in context.tools_used
        assert "buscar_cep" in context.tools_used
        assert len(context.tools_used) == 2  # Sem duplicata

    def test_start_flow(self):
        """Deve iniciar fluxo."""
        from app.agent.context import ConversationContext, FlowType

        context = ConversationContext()
        context.start_flow(FlowType.FARMACIA)

        assert context.active_flow == FlowType.FARMACIA

    def test_end_flow(self):
        """Deve encerrar fluxo."""
        from app.agent.context import ConversationContext, FlowType

        context = ConversationContext()
        context.start_flow(FlowType.FARMACIA)
        context.end_flow()

        assert context.active_flow is None

    def test_get_farmacia_flow(self):
        """Deve retornar FarmaciaFlowData."""
        from app.agent.context import ConversationContext, FarmaciaState

        context = ConversationContext()
        flow = context.get_farmacia_flow()

        assert flow is not None
        assert flow.state == FarmaciaState.INICIO

    def test_get_beneficio_flow(self):
        """Deve retornar BeneficioFlowData."""
        from app.agent.context import ConversationContext, BeneficioState

        context = ConversationContext()
        flow = context.get_beneficio_flow()

        assert flow is not None
        assert flow.state == BeneficioState.INICIO

    def test_get_documentacao_flow(self):
        """Deve retornar DocumentacaoFlowData."""
        from app.agent.context import ConversationContext, DocumentacaoState

        context = ConversationContext()
        flow = context.get_documentacao_flow()

        assert flow is not None
        assert flow.state == DocumentacaoState.INICIO

    def test_set_farmacia_flow(self):
        """Deve atualizar FarmaciaFlowData."""
        from app.agent.context import (
            ConversationContext, FarmaciaFlowData, FarmaciaState, FlowType
        )

        context = ConversationContext()
        context.active_flow = FlowType.FARMACIA

        flow = FarmaciaFlowData()
        flow.state = FarmaciaState.MEDICAMENTOS
        flow.medicamentos = [{"nome": "Losartana"}]
        context.set_farmacia_flow(flow)

        retrieved = context.get_farmacia_flow()
        assert retrieved.state == FarmaciaState.MEDICAMENTOS
        assert len(retrieved.medicamentos) == 1


class TestFlowData:
    """Testes para FlowData classes."""

    def test_farmacia_flow_initial_state(self):
        """FarmaciaFlowData deve iniciar no estado INICIO."""
        from app.agent.context import FarmaciaFlowData, FarmaciaState

        flow = FarmaciaFlowData()

        assert flow.state == FarmaciaState.INICIO
        assert flow.medicamentos == []
        assert flow.farmacia_selecionada is None

    def test_beneficio_flow_initial_state(self):
        """BeneficioFlowData deve iniciar no estado INICIO."""
        from app.agent.context import BeneficioFlowData, BeneficioState

        flow = BeneficioFlowData()

        assert flow.state == BeneficioState.INICIO

    def test_documentacao_flow_initial_state(self):
        """DocumentacaoFlowData deve iniciar no estado INICIO."""
        from app.agent.context import DocumentacaoFlowData, DocumentacaoState

        flow = DocumentacaoFlowData()

        assert flow.state == DocumentacaoState.INICIO
        assert flow.programa_selecionado is None


class TestFlowType:
    """Testes para FlowType enum."""

    def test_flow_types_exist(self):
        """Deve ter todos os tipos de fluxo."""
        from app.agent.context import FlowType

        assert FlowType.GERAL is not None
        assert FlowType.FARMACIA is not None
        assert FlowType.BENEFICIO is not None
        assert FlowType.DOCUMENTACAO is not None


class TestMessage:
    """Testes para Message class."""

    def test_create_message(self):
        """Deve criar mensagem."""
        from app.agent.context import Message, MessageRole

        msg = Message(role=MessageRole.USER, content="Ola")

        assert msg.role == MessageRole.USER
        assert msg.content == "Ola"
        assert msg.timestamp is not None
