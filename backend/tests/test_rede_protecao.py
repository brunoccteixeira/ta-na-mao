"""
Testes para a Rede de Protecao Social.

Testa deteccao de urgencia, roteamento para servicos,
e sub-agente de protecao.
"""

import pytest
from app.agent.tools.rede_protecao import (
    detectar_urgencia,
    buscar_servico_protecao,
    NivelUrgencia,
    TipoServico,
)
from app.agent.subagents.protecao_agent import ProtecaoSubAgent, ProtecaoState
from app.agent.context import ConversationContext, FlowType
from app.agent.intent_classifier import IntentClassifier, IntentCategory


class TestDetectarUrgencia:
    """Testes para deteccao de urgencia."""

    def test_detecta_violencia(self):
        """Deve detectar mensagem sobre violencia."""
        result = detectar_urgencia("meu marido esta me batendo")

        assert result["urgencia_detectada"] is True
        assert result["nivel"] in [NivelUrgencia.ALTA, NivelUrgencia.EMERGENCIA]
        categorias = [c["categoria"] for c in result["categorias"]]
        assert any("violencia" in c for c in categorias)

    def test_detecta_suicidio(self):
        """Deve detectar ideacao suicida com nivel EMERGENCIA."""
        result = detectar_urgencia("nao quero mais viver")

        assert result["urgencia_detectada"] is True
        assert result["nivel"] == NivelUrgencia.EMERGENCIA
        categorias = [c["categoria"] for c in result["categorias"]]
        assert "suicidio" in categorias

    def test_detecta_fome(self):
        """Deve detectar situacao de fome."""
        result = detectar_urgencia("estamos passando fome, nao tem comida")

        assert result["urgencia_detectada"] is True
        categorias = [c["categoria"] for c in result["categorias"]]
        assert "fome" in categorias

    def test_detecta_situacao_rua(self):
        """Deve detectar situacao de rua."""
        result = detectar_urgencia("estou morando na rua com meus filhos")

        assert result["urgencia_detectada"] is True
        categorias = [c["categoria"] for c in result["categorias"]]
        assert "situacao_rua" in categorias

    def test_detecta_crianca_risco(self):
        """Deve detectar crianca em risco."""
        result = detectar_urgencia("tem uma crianca abandonada na rua")

        assert result["urgencia_detectada"] is True
        categorias = [c["categoria"] for c in result["categorias"]]
        assert "crianca_risco" in categorias

    def test_detecta_saude_mental(self):
        """Deve detectar questoes de saude mental."""
        result = detectar_urgencia("estou com depressao muito forte")

        assert result["urgencia_detectada"] is True
        categorias = [c["categoria"] for c in result["categorias"]]
        assert "saude_mental" in categorias

    def test_detecta_emergencia_medica(self):
        """Deve detectar emergencia medica."""
        result = detectar_urgencia("meu pai desmaiou e nao acorda")

        assert result["urgencia_detectada"] is True
        assert result["nivel"] == NivelUrgencia.EMERGENCIA

    def test_nao_detecta_mensagem_normal(self):
        """Mensagem normal nao deve ser detectada como urgencia."""
        result = detectar_urgencia("quero consultar meu bolsa familia")

        assert result["urgencia_detectada"] is False
        assert result["nivel"] is None

    def test_servicos_recomendados_violencia(self):
        """Violencia deve recomendar CREAS."""
        result = detectar_urgencia("sofro violencia em casa")
        servicos = [s["tipo"] for s in result["servicos_recomendados"]]
        assert TipoServico.CREAS in servicos

    def test_servicos_recomendados_suicidio(self):
        """Suicidio deve recomendar CVV."""
        result = detectar_urgencia("quero me matar")
        servicos = [s["tipo"] for s in result["servicos_recomendados"]]
        assert TipoServico.CVV in servicos

    def test_servicos_recomendados_mulher(self):
        """Violencia contra mulher deve recomendar Ligue 180."""
        result = detectar_urgencia("meu marido me bate, sofro violencia domestica")
        servicos = [s["tipo"] for s in result["servicos_recomendados"]]
        assert TipoServico.LIGUE_180 in servicos

    def test_multiplas_categorias(self):
        """Mensagem com multiplos indicadores deve detectar todos."""
        result = detectar_urgencia("estou passando fome e morando na rua")

        assert result["urgencia_detectada"] is True
        categorias = [c["categoria"] for c in result["categorias"]]
        assert "fome" in categorias
        assert "situacao_rua" in categorias

    def test_nivel_mais_alto_prevalece(self):
        """O nivel mais alto de urgencia deve prevalecer."""
        result = detectar_urgencia("quero morrer, nao aguento mais a depressao")

        assert result["nivel"] == NivelUrgencia.EMERGENCIA


class TestBuscarServicoProtecao:
    """Testes para busca de servicos de protecao."""

    def test_buscar_samu(self):
        """Deve retornar dados do SAMU."""
        result = buscar_servico_protecao("SAMU")

        assert result["encontrado"] is True
        assert result["telefone"] == "192"
        assert result["gratuito"] is True

    def test_buscar_cvv(self):
        """Deve retornar dados do CVV."""
        result = buscar_servico_protecao("CVV")

        assert result["encontrado"] is True
        assert result["telefone"] == "188"
        assert "chat" in result

    def test_buscar_ligue_180(self):
        """Deve retornar dados do Ligue 180."""
        result = buscar_servico_protecao("LIGUE_180")

        assert result["encontrado"] is True
        assert result["telefone"] == "180"

    def test_buscar_disque_100(self):
        """Deve retornar dados do Disque 100."""
        result = buscar_servico_protecao("DISQUE_100")

        assert result["encontrado"] is True
        assert result["telefone"] == "100"

    def test_buscar_creas(self):
        """Deve retornar dados do CREAS."""
        result = buscar_servico_protecao("CREAS")

        assert result["encontrado"] is True
        assert result["gratuito"] is True

    def test_buscar_caps(self):
        """Deve retornar dados do CAPS."""
        result = buscar_servico_protecao("CAPS")

        assert result["encontrado"] is True

    def test_buscar_centro_pop(self):
        """Deve retornar dados do Centro POP."""
        result = buscar_servico_protecao("CENTRO_POP")

        assert result["encontrado"] is True

    def test_buscar_conselho_tutelar(self):
        """Deve retornar dados do Conselho Tutelar."""
        result = buscar_servico_protecao("CONSELHO_TUTELAR")

        assert result["encontrado"] is True

    def test_servico_nao_encontrado(self):
        """Servico inexistente deve retornar erro."""
        result = buscar_servico_protecao("SERVICO_INEXISTENTE")

        assert result["encontrado"] is False
        assert "servicos_disponiveis" in result

    def test_buscar_com_cidade(self):
        """Busca com cidade deve incluir orientacao local."""
        result = buscar_servico_protecao("CREAS", cidade="Sao Paulo")

        assert result["encontrado"] is True
        assert "orientacao_local" in result
        assert "Sao Paulo" in result["orientacao_local"]

    def test_todos_servicos_gratuitos(self):
        """Todos os servicos devem ser gratuitos."""
        for tipo in [
            TipoServico.SAMU, TipoServico.CREAS, TipoServico.CAPS,
            TipoServico.CENTRO_POP, TipoServico.CONSELHO_TUTELAR,
            TipoServico.CVV, TipoServico.DISQUE_100, TipoServico.LIGUE_180,
        ]:
            result = buscar_servico_protecao(tipo)
            assert result["gratuito"] is True, f"{tipo} deveria ser gratuito"


class TestProtecaoSubAgent:
    """Testes para o sub-agente de protecao."""

    def _create_context(self) -> ConversationContext:
        """Cria contexto de teste."""
        ctx = ConversationContext()
        ctx.start_flow(FlowType.PROTECAO)
        return ctx

    @pytest.mark.asyncio
    async def test_triagem_emergencia_suicidio(self):
        """Suicidio deve gerar resposta imediata com CVV."""
        ctx = self._create_context()
        agent = ProtecaoSubAgent(ctx)

        response = await agent.process("nao quero mais viver, quero morrer")

        assert "188" in response.text or "CVV" in response.text.upper()
        assert len(response.suggested_actions) > 0

    @pytest.mark.asyncio
    async def test_triagem_violencia(self):
        """Violencia deve gerar acolhimento e encaminhamento."""
        ctx = self._create_context()
        agent = ProtecaoSubAgent(ctx)

        response = await agent.process("meu marido ta me batendo")

        assert "sozinho" in response.text.lower() or "ajudar" in response.text.lower()
        assert len(response.text) > 20  # Resposta substancial

    @pytest.mark.asyncio
    async def test_triagem_sem_urgencia(self):
        """Mensagem sem urgencia deve pedir mais informacoes."""
        ctx = self._create_context()
        agent = ProtecaoSubAgent(ctx)

        response = await agent.process("oi, preciso de ajuda")

        assert "conta" in response.text.lower() or "ajudar" in response.text.lower()

    @pytest.mark.asyncio
    async def test_acompanhamento_volta_menu(self):
        """No acompanhamento, pedir menu deve encerrar fluxo."""
        ctx = self._create_context()
        agent = ProtecaoSubAgent(ctx)
        agent.state = ProtecaoState.ACOMPANHAMENTO
        agent.flow_data["state"] = ProtecaoState.ACOMPANHAMENTO
        ctx.flow_data = agent.flow_data

        response = await agent.process("voltar ao inicio")

        assert "alguma coisa" in response.text.lower() or "aqui" in response.text.lower()

    @pytest.mark.asyncio
    async def test_emergencia_medica(self):
        """Emergencia medica deve recomendar SAMU."""
        ctx = self._create_context()
        agent = ProtecaoSubAgent(ctx)

        response = await agent.process("meu pai desmaiou e nao acorda")

        assert "192" in response.text or "SAMU" in response.text


class TestIntentClassifierProtecao:
    """Testes para classificacao de intencao PROTECAO."""

    def test_classifica_violencia(self):
        """Mensagem sobre violencia deve classificar como PROTECAO."""
        classifier = IntentClassifier()
        intent = classifier.classify("estou sofrendo violencia")
        assert intent.category == IntentCategory.PROTECAO

    def test_classifica_fome(self):
        """Mensagem sobre fome deve classificar como PROTECAO."""
        classifier = IntentClassifier()
        intent = classifier.classify("estamos passando fome")
        assert intent.category == IntentCategory.PROTECAO

    def test_classifica_suicidio(self):
        """Mensagem sobre suicidio deve classificar como PROTECAO."""
        classifier = IntentClassifier()
        intent = classifier.classify("quero morrer")
        assert intent.category == IntentCategory.PROTECAO

    def test_mensagem_normal_nao_classifica_protecao(self):
        """Mensagem normal nao deve ser classificada como PROTECAO."""
        classifier = IntentClassifier()
        intent = classifier.classify("quero consultar meu bolsa familia")
        assert intent.category != IntentCategory.PROTECAO
