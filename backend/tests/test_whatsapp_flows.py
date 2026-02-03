"""
Testes para WhatsApp Flows.

Testa menus numerados, deteccao de selecao,
formatacao e pre-processamento de mensagens.
"""

import pytest
from app.agent.channels.whatsapp_flows import (
    WhatsAppFlowManager,
    formatar_menu_principal,
    formatar_menu_retorno,
    formatar_resposta_whatsapp,
    get_whatsapp_flow_manager,
)


class TestFormatarMenuPrincipal:
    """Testes para formatacao do menu principal."""

    def test_menu_tem_5_opcoes(self):
        """Menu deve ter 5 opcoes numeradas."""
        menu = formatar_menu_principal()

        assert "*1*" in menu
        assert "*2*" in menu
        assert "*3*" in menu
        assert "*4*" in menu
        assert "*5*" in menu

    def test_menu_tem_titulo(self):
        """Menu deve ter titulo."""
        menu = formatar_menu_principal()
        assert "Ta na Mao" in menu

    def test_menu_opcoes_corretas(self):
        """Menu deve ter as opcoes corretas."""
        menu = formatar_menu_principal()
        menu_lower = menu.lower()

        assert "beneficio" in menu_lower or "benefício" in menu_lower
        assert "farmacia" in menu_lower or "farmácia" in menu_lower
        assert "documento" in menu_lower
        assert "cadunico" in menu_lower or "cadúnico" in menu_lower
        assert "outro assunto" in menu_lower


class TestFormatarMenuRetorno:
    """Testes para formatacao do menu de retorno."""

    def test_menu_retorno_tem_opcoes(self):
        """Menu de retorno deve ter opcoes."""
        menu = formatar_menu_retorno()

        assert "*1*" in menu
        assert "*2*" in menu

    def test_menu_retorno_pergunta(self):
        """Menu de retorno deve perguntar se precisa de mais algo."""
        menu = formatar_menu_retorno()
        menu_lower = menu.lower()
        assert "ajudar" in menu_lower or "alguma coisa" in menu_lower


class TestFormatarRespostaWhatsapp:
    """Testes para formatacao de resposta."""

    def test_converte_markdown_bold(self):
        """Deve converter **bold** para *bold*."""
        result = formatar_resposta_whatsapp("Isso eh **importante**!")
        assert "*importante*" in result
        assert "**" not in result

    def test_limita_tamanho(self):
        """Deve limitar tamanho da mensagem."""
        texto_longo = "A" * 5000
        result = formatar_resposta_whatsapp(texto_longo)
        assert len(result) <= 4100

    def test_texto_curto_nao_muda(self):
        """Texto curto nao deve ser truncado."""
        texto = "Oi, tudo bem?"
        result = formatar_resposta_whatsapp(texto)
        assert result == texto


class TestWhatsAppFlowManager:
    """Testes para o gerenciador de fluxos WhatsApp."""

    def setup_method(self):
        self.manager = WhatsAppFlowManager()

    def test_selecao_opcao_1(self):
        """Opcao 1 deve mapear para consulta de beneficios."""
        msg, menu = self.manager.pre_process_message("1", "session1")
        assert msg is not None
        assert "beneficio" in msg.lower() or "benefício" in msg.lower()

    def test_selecao_opcao_2(self):
        """Opcao 2 deve mapear para farmacia popular."""
        msg, menu = self.manager.pre_process_message("2", "session1")
        assert msg is not None
        assert "remedio" in msg.lower() or "farmacia" in msg.lower()

    def test_selecao_opcao_3(self):
        """Opcao 3 deve mapear para documentos."""
        msg, menu = self.manager.pre_process_message("3", "session1")
        assert msg is not None
        assert "documento" in msg.lower()

    def test_selecao_opcao_4(self):
        """Opcao 4 deve mapear para cadunico."""
        msg, menu = self.manager.pre_process_message("4", "session1")
        assert msg is not None
        assert "cadunico" in msg.lower() or "cadúnico" in msg.lower()

    def test_selecao_opcao_5(self):
        """Opcao 5 (outro assunto) deve retornar None para usar texto original."""
        msg, menu = self.manager.pre_process_message("5", "session1")
        assert msg is None

    def test_selecao_com_ponto(self):
        """Aceitar formato '1.'."""
        msg, menu = self.manager.pre_process_message("1.", "session1")
        assert msg is not None
        assert "beneficio" in msg.lower() or "benefício" in msg.lower()

    def test_selecao_com_espacos(self):
        """Aceitar formato ' 1 '."""
        msg, menu = self.manager.pre_process_message(" 1 ", "session1")
        assert msg is not None

    def test_selecao_opcao_texto(self):
        """Aceitar formato 'opcao 1'."""
        msg, menu = self.manager.pre_process_message("opcao 1", "session1")
        assert msg is not None

    def test_numero_invalido_passa_direto(self):
        """Numeros fora do range (6, 7, ...) devem passar direto."""
        msg, menu = self.manager.pre_process_message("6", "session1")
        assert msg is None
        assert menu is None

    def test_texto_normal_passa_direto(self):
        """Texto normal nao deve ser interceptado."""
        msg, menu = self.manager.pre_process_message(
            "quero saber sobre bolsa familia", "session1"
        )
        assert msg is None
        assert menu is None

    def test_pedir_menu(self):
        """Pedir 'menu' deve retornar menu principal."""
        msg, menu = self.manager.pre_process_message("menu", "session1")
        assert menu is not None
        assert "*1*" in menu

    def test_pedir_voltar(self):
        """Pedir 'voltar' deve retornar menu principal."""
        msg, menu = self.manager.pre_process_message("voltar", "session1")
        assert menu is not None

    def test_pedir_inicio(self):
        """Pedir 'inicio' deve retornar menu principal."""
        msg, menu = self.manager.pre_process_message("inicio", "session1")
        assert menu is not None

    def test_should_show_return_menu_conclusao(self):
        """Deve mostrar menu de retorno quando resposta eh conclusao."""
        assert self.manager.should_show_return_menu(
            "Espero ter ajudado! Qualquer duvida eh so perguntar."
        ) is True

        assert self.manager.should_show_return_menu(
            "Pronto! Precisa de mais alguma coisa?"
        ) is True

    def test_should_not_show_return_menu_meio_fluxo(self):
        """Nao deve mostrar menu de retorno no meio do fluxo."""
        assert self.manager.should_show_return_menu(
            "Me fala seu CEP que eu mostro o CRAS perto de voce."
        ) is False

    def test_numero_multidigito_nao_intercepta(self):
        """Numeros com mais de 1 digito nao devem ser interceptados como menu."""
        msg, menu = self.manager.pre_process_message("12345678909", "session1")
        assert msg is None
        assert menu is None

    def test_cpf_nao_intercepta(self):
        """CPF nao deve ser interceptado como selecao de menu."""
        msg, menu = self.manager.pre_process_message("529.982.247-25", "session1")
        assert msg is None
        assert menu is None

    def test_cep_nao_intercepta(self):
        """CEP nao deve ser interceptado como selecao de menu."""
        msg, menu = self.manager.pre_process_message("04010-100", "session1")
        assert msg is None
        assert menu is None


class TestGetWhatsAppFlowManager:
    """Testes para o singleton do flow manager."""

    def test_retorna_instancia(self):
        """Deve retornar instancia do manager."""
        manager = get_whatsapp_flow_manager()
        assert isinstance(manager, WhatsAppFlowManager)

    def test_singleton(self):
        """Deve retornar mesma instancia."""
        m1 = get_whatsapp_flow_manager()
        m2 = get_whatsapp_flow_manager()
        assert m1 is m2
