"""
Testes para as tools de consulta ao CadUnico.

Testa consulta por CPF, verificacao de atualizacao,
mascaramento de CPF, tratamento de erros, e integracao com API.
"""

import pytest
from unittest.mock import patch, MagicMock
import httpx
from app.agent.tools.consultar_cadunico import (
    consultar_cadunico,
    verificar_atualizacao_cadunico,
    _mascarar_cpf,
    _limpar_cpf,
    _hash_cpf,
    _normalizar_resposta_api,
    _consultar_api,
    _is_api_configured,
)


class TestMascararCPF:
    """Testes para mascaramento de CPF."""

    def test_mascara_cpf_valido(self):
        """CPF valido deve ser mascarado corretamente."""
        result = _mascarar_cpf("52998224725")
        assert result == "***.982.247-**"

    def test_mascara_cpf_formatado(self):
        """CPF com formatacao deve ser mascarado."""
        result = _mascarar_cpf("529.982.247-25")
        assert result == "***.982.247-**"

    def test_mascara_cpf_curto(self):
        """CPF com menos de 11 digitos retorna mascara generica."""
        result = _mascarar_cpf("12345")
        assert result == "***.***.***-**"


class TestLimparCPF:
    """Testes para limpeza de CPF."""

    def test_limpar_cpf_formatado(self):
        result = _limpar_cpf("529.982.247-25")
        assert result == "52998224725"

    def test_limpar_cpf_numerico(self):
        result = _limpar_cpf("52998224725")
        assert result == "52998224725"


class TestHashCPF:
    """Testes para hash de CPF."""

    def test_hash_cpf_retorna_string(self):
        result = _hash_cpf("52998224725")
        assert isinstance(result, str)
        assert len(result) == 12

    def test_hash_cpf_deterministico(self):
        """Mesmo CPF deve gerar mesmo hash."""
        h1 = _hash_cpf("52998224725")
        h2 = _hash_cpf("52998224725")
        assert h1 == h2

    def test_hash_cpf_diferente_para_cpfs_diferentes(self):
        h1 = _hash_cpf("52998224725")
        h2 = _hash_cpf("11144477735")
        assert h1 != h2


class TestConsultarCadunico:
    """Testes para consultar_cadunico tool."""

    def test_cpf_encontrado(self):
        """CPF cadastrado deve retornar dados completos."""
        result = consultar_cadunico("529.982.247-25")

        assert result["encontrado"] is True
        assert result["cpf_masked"] == "***.982.247-**"
        assert result["responsavel"] == "MARIA DA SILVA SANTOS"
        assert result["composicao_familiar"]["total_membros"] == 3
        assert result["renda"]["renda_per_capita"] == 266.67
        assert result["renda"]["faixa"] == "POBREZA"
        assert len(result["programas_vinculados"]) == 2
        assert result["situacao_cadastral"] == "CADASTRADO"

    def test_cpf_encontrado_sem_formatacao(self):
        """CPF sem formatacao deve funcionar."""
        result = consultar_cadunico("52998224725")
        assert result["encontrado"] is True

    def test_cpf_nao_encontrado(self):
        """CPF nao cadastrado deve retornar nao encontrado."""
        result = consultar_cadunico("00000000000")

        assert result["encontrado"] is False
        assert "mensagem" in result
        assert "sugestao" in result

    def test_cpf_invalido(self):
        """CPF invalido (menos de 11 digitos) deve retornar erro."""
        result = consultar_cadunico("12345")

        assert result["encontrado"] is False
        assert "erro" in result

    def test_cpf_idoso_bpc(self):
        """CPF de idoso com BPC deve retornar dados corretos."""
        result = consultar_cadunico("11144477735")

        assert result["encontrado"] is True
        assert result["composicao_familiar"]["total_membros"] == 1
        assert result["renda"]["faixa"] == "EXTREMA_POBREZA"

        # Verificar BPC nos programas
        programas = result["programas_vinculados"]
        bpc = [p for p in programas if "Prestacao Continuada" in p["nome"]]
        assert len(bpc) == 1
        assert bpc[0]["ativo"] is True
        assert bpc[0]["valor_mensal"] == 1412.00

    def test_composicao_familiar_membros(self):
        """Composicao familiar deve listar membros com nome, parentesco e idade."""
        result = consultar_cadunico("52998224725")
        membros = result["composicao_familiar"]["membros"]

        assert len(membros) == 3
        assert membros[0]["parentesco"] == "RESPONSAVEL"
        assert membros[1]["parentesco"] == "FILHO"
        assert membros[2]["parentesco"] == "FILHA"

    def test_faixa_renda_descricao(self):
        """Faixa de renda deve incluir descricao simples."""
        result = consultar_cadunico("52998224725")
        assert "faixa_descricao" in result["renda"]
        assert len(result["renda"]["faixa_descricao"]) > 0

    def test_cpf_nunca_em_texto_claro_no_resultado(self):
        """CPF nunca deve aparecer em texto claro no resultado."""
        result = consultar_cadunico("52998224725")
        result_str = str(result)
        assert "52998224725" not in result_str
        assert "529.982.247-25" not in result_str


class TestVerificarAtualizacaoCadunico:
    """Testes para verificar_atualizacao_cadunico tool."""

    def test_cadastro_recente_atualizado(self):
        """Cadastro atualizado recentemente deve estar em dia."""
        # CPF com atualizacao em 2025-01-08 (recente)
        result = verificar_atualizacao_cadunico("12345678909")

        assert result["encontrado"] is True
        assert result["atualizado"] is True
        assert result["urgencia"] in ["OK", "ATENCAO"]

    def test_cadastro_antigo_desatualizado(self):
        """Cadastro com mais de 2 anos deve estar desatualizado."""
        # CPF com atualizacao em 2023-06-10 (mais de 2 anos)
        result = verificar_atualizacao_cadunico("11144477735")

        assert result["encontrado"] is True
        assert result["atualizado"] is False
        assert result["urgencia"] == "URGENTE"
        assert len(result["programas_em_risco"]) > 0
        assert "orientacao" in result
        assert len(result["orientacao"]) > 0

    def test_cpf_nao_encontrado(self):
        """CPF nao cadastrado deve retornar nao encontrado."""
        result = verificar_atualizacao_cadunico("00000000000")

        assert result["encontrado"] is False
        assert "mensagem" in result

    def test_cpf_invalido(self):
        """CPF invalido deve retornar erro."""
        result = verificar_atualizacao_cadunico("123")

        assert result["encontrado"] is False
        assert "erro" in result

    def test_dias_desde_atualizacao(self):
        """Deve retornar numero de dias desde ultima atualizacao."""
        result = verificar_atualizacao_cadunico("52998224725")

        assert result["encontrado"] is True
        assert "dias_desde_atualizacao" in result
        assert isinstance(result["dias_desde_atualizacao"], int)
        assert result["dias_desde_atualizacao"] > 0

    def test_mensagem_sempre_presente(self):
        """Resultado sempre deve ter mensagem orientativa."""
        result = verificar_atualizacao_cadunico("52998224725")
        assert "mensagem" in result
        assert len(result["mensagem"]) > 0


class TestNormalizarRespostaAPI:
    """Testes para normalizacao de resposta da API real."""

    def test_normaliza_formato_padrao(self):
        """Resposta no formato padrao deve ser normalizada."""
        api_data = {
            "codigo_familiar": "9999999999999",
            "responsavel_familiar": {
                "nome": "TESTE DA SILVA",
                "nis": "99999999999",
                "data_nascimento": "01/01/1990",
                "sexo": "F",
            },
            "composicao_familiar": [
                {
                    "nome": "TESTE DA SILVA",
                    "parentesco": "RESPONSAVEL",
                    "data_nascimento": "01/01/1990",
                    "idade": 36,
                    "nis": "99999999999",
                },
            ],
            "endereco": {
                "logradouro": "RUA TESTE",
                "numero": "1",
                "bairro": "CENTRO",
                "cidade": "BRASILIA",
                "uf": "DF",
                "cep": "70000000",
            },
            "renda": {
                "renda_familiar_total": 500.0,
                "renda_per_capita": 500.0,
                "faixa": "BAIXA_RENDA",
            },
            "programas_vinculados": [
                {
                    "codigo": "BOLSA_FAMILIA",
                    "nome": "Bolsa Familia",
                    "ativo": True,
                    "valor_mensal": 600.0,
                }
            ],
            "data_cadastro": "2022-01-01",
            "data_ultima_atualizacao": "2025-06-01",
            "situacao_cadastral": "CADASTRADO",
        }

        result = _normalizar_resposta_api(api_data)

        assert result["codigo_familiar"] == "9999999999999"
        assert result["responsavel_familiar"]["nome"] == "TESTE DA SILVA"
        assert len(result["composicao_familiar"]) == 1
        assert result["renda"]["renda_per_capita"] == 500.0
        assert result["renda"]["faixa"] == "BAIXA_RENDA"
        assert len(result["programas_vinculados"]) == 1
        assert result["data_ultima_atualizacao"] == "2025-06-01"

    def test_normaliza_formato_dataprev(self):
        """Resposta com nomes estilo DATAPREV deve ser normalizada."""
        api_data = {
            "cd_familiar_fam": "8888888888888",
            "responsavel": {
                "no_pessoa": "JOAO TESTE",
                "nu_nis_pessoa": "88888888888",
                "dt_nasc_pessoa": "15/05/1975",
                "co_sexo_pessoa": "M",
            },
            "componentes_familiares": [
                {
                    "no_pessoa": "JOAO TESTE",
                    "co_parentesco": "RESPONSAVEL",
                    "dt_nasc_pessoa": "15/05/1975",
                    "nu_nis_pessoa": "88888888888",
                },
            ],
            "endereco": {
                "no_localidade_fam": "RUA DATAPREV",
                "nu_logradouro_fam": "100",
                "no_municipio": "SAO PAULO",
                "sg_uf": "SP",
                "nu_cep_logradouro_fam": "01001000",
            },
            "renda": {
                "vl_renda_total_fam": 200,
                "vl_renda_per_capita_fam": 200,
            },
            "beneficios": [
                {
                    "cd_programa": "BOLSA_FAMILIA",
                    "no_programa": "Bolsa Familia",
                    "in_ativo": True,
                    "vl_beneficio": 600,
                }
            ],
            "dt_cadastro_fam": "2020-01-01",
            "dt_atualizacao_fam": "2024-06-01",
            "co_situacao_cadastral": "CADASTRADO",
        }

        result = _normalizar_resposta_api(api_data)

        assert result["codigo_familiar"] == "8888888888888"
        assert result["responsavel_familiar"]["nome"] == "JOAO TESTE"
        assert result["responsavel_familiar"]["nis"] == "88888888888"
        assert len(result["composicao_familiar"]) == 1
        assert result["composicao_familiar"][0]["nome"] == "JOAO TESTE"
        assert result["endereco"]["cidade"] == "SAO PAULO"
        assert result["renda"]["renda_per_capita"] == 200.0
        assert result["programas_vinculados"][0]["nome"] == "Bolsa Familia"
        assert result["data_ultima_atualizacao"] == "2024-06-01"

    def test_infere_faixa_renda_extrema_pobreza(self):
        """Deve inferir faixa EXTREMA_POBREZA quando renda_pc <= 105."""
        api_data = {
            "responsavel_familiar": {"nome": "TESTE"},
            "composicao_familiar": [],
            "endereco": {},
            "renda": {"renda_familiar_total": 100, "renda_per_capita": 50},
            "programas_vinculados": [],
        }
        result = _normalizar_resposta_api(api_data)
        assert result["renda"]["faixa"] == "EXTREMA_POBREZA"

    def test_infere_faixa_renda_pobreza(self):
        """Deve inferir faixa POBREZA quando renda_pc entre 105 e 218."""
        api_data = {
            "responsavel_familiar": {"nome": "TESTE"},
            "composicao_familiar": [],
            "endereco": {},
            "renda": {"renda_familiar_total": 150, "renda_per_capita": 150},
            "programas_vinculados": [],
        }
        result = _normalizar_resposta_api(api_data)
        assert result["renda"]["faixa"] == "POBREZA"

    def test_calcula_idade_quando_ausente(self):
        """Deve calcular idade a partir de data_nascimento quando idade=0."""
        api_data = {
            "responsavel_familiar": {"nome": "TESTE"},
            "composicao_familiar": [
                {
                    "nome": "CRIANCA TESTE",
                    "parentesco": "FILHO",
                    "data_nascimento": "01/01/2020",
                    "idade": 0,
                },
            ],
            "endereco": {},
            "renda": {"renda_familiar_total": 0, "renda_per_capita": 0},
            "programas_vinculados": [],
        }
        result = _normalizar_resposta_api(api_data)
        # Crianca nascida em 2020 deve ter 5-6 anos
        assert result["composicao_familiar"][0]["idade"] >= 5


class TestConsultarAPIReal:
    """Testes para o cliente HTTP da API real do CadUnico."""

    def test_api_nao_configurada_usa_mock(self):
        """Quando CADUNICO_API_URL esta vazio, deve usar mock."""
        with patch(
            "app.agent.tools.consultar_cadunico._get_api_config",
            return_value=("", "")
        ):
            assert _is_api_configured() is False
            result = consultar_cadunico("52998224725")
            assert result["encontrado"] is True
            assert result["responsavel"] == "MARIA DA SILVA SANTOS"

    def test_api_configurada_sucesso(self):
        """Quando API configurada e retorna 200, deve usar dados da API."""
        api_response_data = {
            "codigo_familiar": "7777777777777",
            "responsavel_familiar": {
                "nome": "CIDADAO DA API",
                "nis": "77777777777",
                "data_nascimento": "10/10/1980",
                "sexo": "M",
            },
            "composicao_familiar": [
                {
                    "nome": "CIDADAO DA API",
                    "parentesco": "RESPONSAVEL",
                    "data_nascimento": "10/10/1980",
                    "idade": 45,
                    "nis": "77777777777",
                },
            ],
            "endereco": {
                "logradouro": "RUA API",
                "numero": "1",
                "bairro": "CENTRO",
                "cidade": "BRASILIA",
                "uf": "DF",
                "cep": "70000000",
            },
            "renda": {
                "renda_familiar_total": 300.0,
                "renda_per_capita": 300.0,
                "faixa": "BAIXA_RENDA",
            },
            "programas_vinculados": [],
            "data_cadastro": "2023-01-01",
            "data_ultima_atualizacao": "2025-10-01",
            "situacao_cadastral": "CADASTRADO",
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response_data

        with patch(
            "app.agent.tools.consultar_cadunico._get_api_config",
            return_value=("https://api.cadunico.gov.br/v1", "test-key"),
        ), patch(
            "app.agent.tools.consultar_cadunico.httpx.Client"
        ) as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = consultar_cadunico("52998224725")

            assert result["encontrado"] is True
            assert result["responsavel"] == "CIDADAO DA API"
            mock_client.post.assert_called_once()

    def test_api_configurada_404_retorna_nao_encontrado(self):
        """Quando API retorna 404, deve retornar nao encontrado."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch(
            "app.agent.tools.consultar_cadunico._get_api_config",
            return_value=("https://api.cadunico.gov.br/v1", "test-key"),
        ), patch(
            "app.agent.tools.consultar_cadunico.httpx.Client"
        ) as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = consultar_cadunico("52998224725")

            assert result["encontrado"] is False

    def test_api_timeout_retorna_nao_encontrado(self):
        """Quando API da timeout, deve retornar nao encontrado."""
        with patch(
            "app.agent.tools.consultar_cadunico._get_api_config",
            return_value=("https://api.cadunico.gov.br/v1", "test-key"),
        ), patch(
            "app.agent.tools.consultar_cadunico.httpx.Client"
        ) as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = httpx.TimeoutException("timeout")
            mock_client_cls.return_value = mock_client

            result = consultar_cadunico("52998224725")

            assert result["encontrado"] is False

    def test_api_connection_error_retorna_nao_encontrado(self):
        """Quando API da erro de conexao, deve retornar nao encontrado."""
        with patch(
            "app.agent.tools.consultar_cadunico._get_api_config",
            return_value=("https://api.cadunico.gov.br/v1", "test-key"),
        ), patch(
            "app.agent.tools.consultar_cadunico.httpx.Client"
        ) as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = httpx.ConnectError("connection refused")
            mock_client_cls.return_value = mock_client

            result = consultar_cadunico("52998224725")

            assert result["encontrado"] is False

    def test_api_auth_headers(self):
        """Deve enviar Bearer token no header Authorization."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch(
            "app.agent.tools.consultar_cadunico._get_api_config",
            return_value=("https://api.cadunico.gov.br/v1", "my-secret-key"),
        ), patch(
            "app.agent.tools.consultar_cadunico.httpx.Client"
        ) as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            _consultar_api("52998224725")

            call_kwargs = mock_client.post.call_args
            headers = call_kwargs.kwargs.get("headers", call_kwargs[1].get("headers", {}))
            assert headers["Authorization"] == "Bearer my-secret-key"

    def test_api_envia_cpf_no_body(self):
        """Deve enviar CPF no body JSON (nao na URL)."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch(
            "app.agent.tools.consultar_cadunico._get_api_config",
            return_value=("https://api.cadunico.gov.br/v1", "test-key"),
        ), patch(
            "app.agent.tools.consultar_cadunico.httpx.Client"
        ) as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            _consultar_api("52998224725")

            call_kwargs = mock_client.post.call_args
            json_body = call_kwargs.kwargs.get("json", call_kwargs[1].get("json", {}))
            assert json_body["cpf"] == "52998224725"

    def test_api_verificar_atualizacao_com_api(self):
        """verificar_atualizacao deve funcionar com API real tambem."""
        api_response_data = {
            "codigo_familiar": "7777777777777",
            "responsavel_familiar": {"nome": "TESTE API"},
            "composicao_familiar": [
                {
                    "nome": "TESTE API",
                    "parentesco": "RESPONSAVEL",
                    "data_nascimento": "10/10/1980",
                    "idade": 45,
                },
            ],
            "endereco": {},
            "renda": {"renda_familiar_total": 300, "renda_per_capita": 300},
            "programas_vinculados": [
                {"codigo": "BF", "nome": "Bolsa Familia", "ativo": True, "valor_mensal": 600},
            ],
            "data_cadastro": "2023-01-01",
            "data_ultima_atualizacao": "2025-10-01",
            "situacao_cadastral": "CADASTRADO",
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = api_response_data

        with patch(
            "app.agent.tools.consultar_cadunico._get_api_config",
            return_value=("https://api.cadunico.gov.br/v1", "test-key"),
        ), patch(
            "app.agent.tools.consultar_cadunico.httpx.Client"
        ) as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = verificar_atualizacao_cadunico("52998224725")

            assert result["encontrado"] is True
            assert result["atualizado"] is True
            assert "mensagem" in result
