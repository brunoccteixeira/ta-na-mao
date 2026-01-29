"""
Testes para as tools do agente.

Testa validacao de CPF, busca de CEP, e outras utilidades.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx


class TestValidarCPF:
    """Testes para validar_cpf tool."""

    def test_cpf_valido(self):
        """CPF valido deve retornar valido=True."""
        from app.agent.tools.validar_cpf import validar_cpf

        # CPF valido de teste (gerado para testes)
        result = validar_cpf("529.982.247-25")

        assert result["valido"] is True
        assert result["cpf_formatado"] == "529.982.247-25"
        assert result["cpf_numerico"] == "52998224725"
        assert "válido" in result["mensagem"].lower()

    def test_cpf_valido_sem_formatacao(self):
        """CPF sem formatacao deve funcionar."""
        from app.agent.tools.validar_cpf import validar_cpf

        result = validar_cpf("52998224725")

        assert result["valido"] is True
        assert result["cpf_formatado"] == "529.982.247-25"

    def test_cpf_invalido_digito_errado(self):
        """CPF com digito verificador errado deve ser invalido."""
        from app.agent.tools.validar_cpf import validar_cpf

        # Ultimo digito errado
        result = validar_cpf("529.982.247-26")

        assert result["valido"] is False
        assert result["cpf_formatado"] is None
        assert "verificador" in result["mensagem"].lower()

    def test_cpf_todos_digitos_iguais(self):
        """CPF com todos digitos iguais deve ser invalido."""
        from app.agent.tools.validar_cpf import validar_cpf

        result = validar_cpf("111.111.111-11")

        assert result["valido"] is False
        assert "iguais" in result["mensagem"].lower()

    def test_cpf_menos_de_11_digitos(self):
        """CPF com menos de 11 digitos deve ser invalido."""
        from app.agent.tools.validar_cpf import validar_cpf

        result = validar_cpf("123456")

        assert result["valido"] is False
        assert "11 dígitos" in result["mensagem"]

    def test_cpf_mais_de_11_digitos(self):
        """CPF com mais de 11 digitos deve ser invalido."""
        from app.agent.tools.validar_cpf import validar_cpf

        result = validar_cpf("123456789012345")

        assert result["valido"] is False
        assert "11 dígitos" in result["mensagem"]

    def test_cpf_primeiro_digito_verificador_errado(self):
        """CPF com primeiro digito verificador errado."""
        from app.agent.tools.validar_cpf import validar_cpf

        # Altera o primeiro digito verificador (posicao 9)
        result = validar_cpf("529.982.247-15")  # 1 errado, deveria ser 2

        assert result["valido"] is False
        assert "primeiro dígito" in result["mensagem"].lower()


class TestBuscarCEP:
    """Testes para buscar_cep tool."""

    @pytest.mark.asyncio
    async def test_cep_valido(self):
        """CEP valido deve retornar endereco."""
        from app.agent.tools.buscar_cep import buscar_cep

        # Mock da resposta da API ViaCEP
        mock_response = {
            "cep": "01310-100",
            "logradouro": "Avenida Paulista",
            "complemento": "",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP",
            "ibge": "3550308",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = MagicMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            )

            result = await buscar_cep("01310-100")

        assert result["encontrado"] is True
        assert result["cep"] == "01310-100"
        assert result["logradouro"] == "Avenida Paulista"
        assert result["cidade"] == "São Paulo"
        assert result["uf"] == "SP"

    @pytest.mark.asyncio
    async def test_cep_invalido_formato(self):
        """CEP com formato invalido deve retornar erro."""
        from app.agent.tools.buscar_cep import buscar_cep

        result = await buscar_cep("123")

        assert result["encontrado"] is False
        assert "8 dígitos" in result["mensagem"]

    @pytest.mark.asyncio
    async def test_cep_nao_encontrado(self):
        """CEP inexistente deve retornar nao encontrado."""
        from app.agent.tools.buscar_cep import buscar_cep

        mock_response = {"erro": True}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = MagicMock(
                json=lambda: mock_response,
                raise_for_status=lambda: None
            )

            result = await buscar_cep("99999-999")

        assert result["encontrado"] is False
        assert "não encontrado" in result["mensagem"].lower()

    @pytest.mark.asyncio
    async def test_cep_timeout(self):
        """Timeout na API deve retornar erro."""
        from app.agent.tools.buscar_cep import buscar_cep

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = httpx.TimeoutException("Timeout")

            result = await buscar_cep("01310-100")

        assert result["encontrado"] is False
        assert "tempo esgotado" in result["mensagem"].lower()

    @pytest.mark.asyncio
    async def test_cep_erro_http(self):
        """Erro HTTP na API deve retornar erro."""
        from app.agent.tools.buscar_cep import buscar_cep

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = httpx.HTTPError("Erro de conexao")

            result = await buscar_cep("01310-100")

        assert result["encontrado"] is False
        assert "erro" in result["mensagem"].lower()


class TestChecklist:
    """Testes para checklist tool."""

    def test_gerar_checklist_bolsa_familia(self):
        """Deve gerar checklist para Bolsa Familia."""
        from app.agent.tools.checklist import gerar_checklist

        result = gerar_checklist("BOLSA_FAMILIA")

        assert result["beneficio"] == "Bolsa Família"
        assert "documentos_obrigatorios" in result
        assert len(result["documentos_obrigatorios"]) > 0

    def test_gerar_checklist_bpc(self):
        """Deve gerar checklist para BPC."""
        from app.agent.tools.checklist import gerar_checklist

        result = gerar_checklist("BPC_LOAS")

        assert "documentos_obrigatorios" in result
        assert len(result["documentos_obrigatorios"]) > 0

    def test_gerar_checklist_programa_desconhecido(self):
        """Programa desconhecido deve retornar erro."""
        from app.agent.tools.checklist import gerar_checklist

        result = gerar_checklist("programa_inexistente")

        # Deve retornar erro com beneficios disponiveis
        assert result is not None
        assert result.get("erro") is True or "beneficio" in result

    def test_listar_beneficios(self):
        """Deve listar beneficios disponiveis."""
        from app.agent.tools.checklist import listar_beneficios

        result = listar_beneficios()

        assert "beneficios" in result
        assert result["total"] > 0


class TestDinheiroEsquecido:
    """Testes para dinheiro_esquecido tool."""

    def test_consultar_dinheiro_esquecido_todos(self):
        """Deve retornar informacoes sobre todos os programas."""
        from app.agent.tools.dinheiro_esquecido import consultar_dinheiro_esquecido

        result = consultar_dinheiro_esquecido()

        assert result.success is True
        assert "programas" in result.data
        assert len(result.data["programas"]) > 0

    def test_consultar_dinheiro_esquecido_pis_pasep(self):
        """Deve retornar informacoes sobre PIS/PASEP."""
        from app.agent.tools.dinheiro_esquecido import consultar_dinheiro_esquecido

        result = consultar_dinheiro_esquecido(tipo="pis_pasep")

        assert result.success is True
        assert result.data["tipo"] == "pis_pasep"
        assert "programa" in result.data

    def test_guia_pis_pasep(self):
        """Deve retornar guia de PIS/PASEP."""
        from app.agent.tools.dinheiro_esquecido import guia_pis_pasep

        result = guia_pis_pasep()

        assert result.success is True
        assert "passo_a_passo" in result.data
        assert len(result.data["passo_a_passo"]) > 0

    def test_guia_svr(self):
        """Deve retornar guia de SVR."""
        from app.agent.tools.dinheiro_esquecido import guia_svr

        result = guia_svr()

        assert result.success is True
        assert "passo_a_passo" in result.data

    def test_guia_fgts(self):
        """Deve retornar guia de FGTS."""
        from app.agent.tools.dinheiro_esquecido import guia_fgts

        result = guia_fgts()

        assert result.success is True
        assert "passo_a_passo" in result.data

    def test_verificar_dinheiro_por_perfil(self):
        """Deve recomendar programas baseado no perfil."""
        from app.agent.tools.dinheiro_esquecido import verificar_dinheiro_por_perfil

        result = verificar_dinheiro_por_perfil(
            trabalhou_antes_1988=True,
            teve_carteira_assinada=True
        )

        assert result.success is True
        assert "recomendacoes" in result.data
        assert len(result.data["recomendacoes"]) > 0


class TestProcessarReceita:
    """Testes para processar_receita tool."""

    def test_validar_medicamento_encontrado(self):
        """Deve validar medicamento da Farmacia Popular."""
        from app.agent.tools.processar_receita import _validar_medicamento

        result = _validar_medicamento("Losartana")

        assert result["encontrado"] is True
        assert "nome_oficial" in result

    def test_validar_medicamento_nao_encontrado(self):
        """Medicamento inexistente deve retornar nao encontrado."""
        from app.agent.tools.processar_receita import _validar_medicamento

        result = _validar_medicamento("MedicamentoInexistente123")

        assert result["encontrado"] is False

    def test_extrair_dosagem(self):
        """Deve extrair dosagem de texto."""
        from app.agent.tools.processar_receita import _extrair_dosagem

        result = _extrair_dosagem("Losartana 50mg")

        assert result == "50mg"

    def test_extrair_dosagem_sem_dosagem(self):
        """Texto sem dosagem deve retornar None."""
        from app.agent.tools.processar_receita import _extrair_dosagem

        result = _extrair_dosagem("Losartana")

        assert result is None

    def test_extrair_quantidade(self):
        """Deve extrair quantidade de texto."""
        from app.agent.tools.processar_receita import _extrair_quantidade

        result = _extrair_quantidade("30 comprimidos")

        assert result == 30

    def test_extrair_quantidade_sem_quantidade(self):
        """Texto sem quantidade deve retornar None."""
        from app.agent.tools.processar_receita import _extrair_quantidade

        result = _extrair_quantidade("Losartana 50mg")

        assert result is None


class TestMedicamentosFarmaciaPopular:
    """Testes para dados de medicamentos da Farmacia Popular."""

    def test_buscar_medicamento_encontrado(self):
        """Deve buscar medicamento por nome."""
        from app.agent.data.medicamentos_farmacia_popular import buscar_medicamento

        result = buscar_medicamento("Losartana")

        assert result["encontrado"] is True
        assert result["nome"] == "Losartana"
        assert result["gratuito"] is True

    def test_buscar_medicamento_por_alias(self):
        """Deve encontrar medicamento por nome comercial."""
        from app.agent.data.medicamentos_farmacia_popular import buscar_medicamento

        result = buscar_medicamento("Glifage")  # alias para Metformina

        assert result["encontrado"] is True
        assert "Metformina" in result["nome"]

    def test_buscar_medicamento_nao_encontrado(self):
        """Medicamento nao cadastrado deve retornar nao encontrado."""
        from app.agent.data.medicamentos_farmacia_popular import buscar_medicamento

        result = buscar_medicamento("MedicamentoXYZ123")

        assert result["encontrado"] is False

    def test_medicamentos_disponiveis(self):
        """Deve ter medicamentos cadastrados."""
        from app.agent.data.medicamentos_farmacia_popular import (
            MEDICAMENTOS_FARMACIA_POPULAR
        )

        assert len(MEDICAMENTOS_FARMACIA_POPULAR) > 0
        assert "hipertensao" in MEDICAMENTOS_FARMACIA_POPULAR
        assert "diabetes" in MEDICAMENTOS_FARMACIA_POPULAR

    def test_normalizar_texto(self):
        """Deve normalizar texto removendo acentos."""
        from app.agent.data.medicamentos_farmacia_popular import normalizar_texto

        result = normalizar_texto("Losartana 50mg")

        assert result == "losartana 50mg"

    def test_similarity(self):
        """Deve calcular similaridade entre textos."""
        from app.agent.data.medicamentos_farmacia_popular import similarity

        result = similarity("Losartana", "losartan")

        assert result > 0.8  # Alta similaridade


class TestToolsBase:
    """Testes para a classe base de tools."""

    def test_tool_result_ok(self):
        """ToolResult.ok deve criar resultado de sucesso."""
        from app.agent.tools.base import ToolResult

        result = ToolResult.ok(data={"key": "value"})

        assert result.success is True
        assert result.data["key"] == "value"
        assert result.error is None

    def test_tool_result_fail(self):
        """ToolResult.fail deve criar resultado de erro."""
        from app.agent.tools.base import ToolResult

        result = ToolResult.fail(error="Algo deu errado")

        assert result.success is False
        assert result.error == "Algo deu errado"

    def test_ui_hint_enum(self):
        """UIHint deve ter valores definidos."""
        from app.agent.tools.base import UIHint

        assert UIHint.CHECKLIST.value == "checklist"
        assert UIHint.INFO.value == "info"
        assert UIHint.ERROR.value == "error"
        assert UIHint.PHARMACY_LIST.value == "pharmacy_list"
