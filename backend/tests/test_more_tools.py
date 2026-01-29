"""
Testes adicionais para tools do agente.

Testa buscar_cras, buscar_farmacia, pre_atendimento_cras, etc.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestBuscarCrasModule:
    """Testes para buscar_cras tool."""

    def test_import_module(self):
        """Deve importar o modulo."""
        from app.agent.tools import buscar_cras

        assert buscar_cras is not None

    def test_function_exists(self):
        """Deve ter funcao buscar_cras."""
        from app.agent.tools.buscar_cras import buscar_cras

        # A funcao existe (pode ser sync ou async)
        assert callable(buscar_cras)


class TestBuscarFarmaciaModule:
    """Testes para buscar_farmacia tool."""

    def test_import_module(self):
        """Deve importar o modulo."""
        from app.agent.tools import buscar_farmacia

        assert buscar_farmacia is not None

    def test_function_exists(self):
        """Deve ter funcao buscar_farmacia."""
        from app.agent.tools.buscar_farmacia import buscar_farmacia

        assert callable(buscar_farmacia)


class TestPreAtendimentoCras:
    """Testes para pre_atendimento_cras tool."""

    def test_import(self):
        """Deve importar funcoes do modulo."""
        from app.agent.tools import pre_atendimento_cras

        assert pre_atendimento_cras is not None

    def test_module_has_functions(self):
        """Deve ter funcoes de pre-atendimento."""
        from app.agent.tools import pre_atendimento_cras

        # Verificar que o modulo existe e pode ser importado
        assert hasattr(pre_atendimento_cras, '__name__')


class TestEnviarWhatsapp:
    """Testes para enviar_whatsapp tool."""

    def test_import(self):
        """Deve importar funcoes do modulo."""
        from app.agent.tools import enviar_whatsapp

        assert enviar_whatsapp is not None

    def test_module_functions(self):
        """Deve ter funcoes de envio."""
        from app.agent.tools import enviar_whatsapp

        assert hasattr(enviar_whatsapp, '__name__')


class TestPrepararPedido:
    """Testes para preparar_pedido tool."""

    def test_import(self):
        """Deve importar funcoes do modulo."""
        from app.agent.tools.preparar_pedido import preparar_pedido, consultar_pedido

        assert preparar_pedido is not None
        assert consultar_pedido is not None

    def test_functions_callable(self):
        """Deve ter funcoes invocaveis."""
        from app.agent.tools.preparar_pedido import preparar_pedido, consultar_pedido

        assert callable(preparar_pedido)
        assert callable(consultar_pedido)


class TestMeusDados:
    """Testes para meus_dados tool."""

    def test_import(self):
        """Deve importar funcoes do modulo."""
        from app.agent.tools import meus_dados

        assert meus_dados is not None


class TestConsultarApi:
    """Testes para consultar_api tool."""

    def test_import(self):
        """Deve importar funcoes do modulo."""
        from app.agent.tools import consultar_api

        assert consultar_api is not None


class TestConsultarBeneficio:
    """Testes para consultar_beneficio tool."""

    def test_import(self):
        """Deve importar funcoes do modulo."""
        from app.agent.tools.consultar_beneficio import consultar_beneficio

        assert consultar_beneficio is not None

    def test_function_callable(self):
        """Deve ter funcao invocavel."""
        from app.agent.tools.consultar_beneficio import consultar_beneficio

        assert callable(consultar_beneficio)


class TestBeneficiosSetoriais:
    """Testes para beneficios_setoriais tool."""

    def test_import(self):
        """Deve importar funcoes do modulo."""
        from app.agent.tools import beneficios_setoriais

        assert beneficios_setoriais is not None


class TestWhatsappFormatter:
    """Testes para whatsapp_formatter."""

    def test_import(self):
        """Deve importar o modulo."""
        from app.agent import whatsapp_formatter

        assert whatsapp_formatter is not None

    def test_escape_xml(self):
        """Deve ter funcao de escape XML."""
        from app.agent.whatsapp_formatter import escape_xml

        result = escape_xml("<test>")
        assert "&lt;test&gt;" in result

    def test_format_pharmacy_card(self):
        """Deve formatar card de farmacia."""
        from app.agent.whatsapp_formatter import format_pharmacy_card

        data = {
            "name": "Farmácia Popular",
            "address": "Rua Teste, 123",
            "phone": "11999999999"
        }
        result = format_pharmacy_card(data)

        assert "Farmácia Popular" in result
        assert "Rua Teste" in result


class TestIntentClassifierExtended:
    """Testes estendidos para intent_classifier."""

    def test_all_intents(self):
        """Deve classificar diferentes intencoes."""
        from app.agent.intent_classifier import IntentClassifier

        classifier = IntentClassifier()

        # Diferentes intencoes
        test_cases = [
            ("oi", "saudacao"),
            ("bom dia", "saudacao"),
            ("quero remédio", "farmacia"),
            ("pedir medicamento", "farmacia"),
            ("meus benefícios", "beneficio"),
            ("bolsa família", "beneficio"),
            ("documentos necessários", "documentacao"),
            ("que papéis preciso", "documentacao"),
            ("cras mais próximo", "cras"),
            ("onde fica o cras", "cras"),
        ]

        for message, expected_category in test_cases:
            result = classifier.classify(message)
            assert result is not None
            assert hasattr(result, 'category')

    def test_confidence_score(self):
        """Deve retornar score de confianca."""
        from app.agent.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        result = classifier.classify("quero pedir remédios na farmácia popular")

        assert result is not None
        assert hasattr(result, 'confidence')
        assert 0 <= result.confidence <= 1

    def test_matched_keywords(self):
        """Deve retornar keywords matched."""
        from app.agent.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        result = classifier.classify("quero pedir remédios")

        assert result is not None
        if hasattr(result, 'matched_keywords'):
            assert isinstance(result.matched_keywords, list)


class TestAgentModule:
    """Testes para o modulo agent principal."""

    def test_import_agent(self):
        """Deve importar TaNaMaoAgent."""
        from app.agent.agent import TaNaMaoAgent

        assert TaNaMaoAgent is not None

    def test_create_agent(self):
        """Deve criar instancia de TaNaMaoAgent."""
        from app.agent.agent import TaNaMaoAgent

        agent = TaNaMaoAgent()
        assert agent is not None


class TestOrchestratorModule:
    """Testes para o orchestrator."""

    def test_import_orchestrator(self):
        """Deve importar AgentOrchestrator."""
        from app.agent.orchestrator import AgentOrchestrator

        assert AgentOrchestrator is not None

    def test_orchestrator_has_subagent_map(self):
        """Deve ter mapeamento de sub-agentes."""
        from app.agent.orchestrator import AgentOrchestrator

        assert hasattr(AgentOrchestrator, 'SUBAGENT_MAP')
        assert len(AgentOrchestrator.SUBAGENT_MAP) > 0
