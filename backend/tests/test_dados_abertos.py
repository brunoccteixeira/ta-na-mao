"""Testes para pipeline ETL de dados abertos."""

import pytest
from app.jobs.dados_abertos.extrator import (
    ExtratorDadosAbertos,
    FonteDados,
    PROGRAMA_FONTE,
    ResultadoExtracao,
)
from app.jobs.dados_abertos.transformador import (
    TransformadorDados,
    ResultadoTransformacao,
    RegistroTransformado,
)
from app.jobs.dados_abertos.carregador import (
    CarregadorDados,
    ResultadoCarga,
)
from app.jobs.dados_abertos.orquestrador import (
    OrquestradorETL,
    consultar_dados_abertos,
    AGENDA_PROGRAMAS,
)


# =============================================================================
# ExtratorDadosAbertos
# =============================================================================

class TestExtrator:
    def test_extrair_bolsa_familia(self):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        result = extrator.extrair("BOLSA_FAMILIA", 1, 2026)
        assert result.sucesso is True
        assert result.total_registros > 0
        assert result.programa == "BOLSA_FAMILIA"
        assert result.referencia == "2026-01"

    def test_extrair_bpc(self):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        result = extrator.extrair("BPC", 6, 2025)
        assert result.sucesso is True
        assert result.total_registros > 0

    def test_extrair_programa_invalido(self):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        result = extrator.extrair("INVALIDO", 1, 2026)
        assert result.sucesso is False
        assert result.erro is not None

    def test_listar_programas(self):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        programas = extrator.listar_programas()
        assert len(programas) >= 5
        nomes = [p["programa"] for p in programas]
        assert "BOLSA_FAMILIA" in nomes
        assert "BPC" in nomes

    def test_verificar_disponibilidade(self):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        result = extrator.verificar_disponibilidade("BOLSA_FAMILIA")
        assert result["disponivel"] is True

    def test_registros_tem_campos_corretos(self):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        result = extrator.extrair("BOLSA_FAMILIA", 1, 2026)
        for reg in result.registros:
            assert "municipio_ibge" in reg
            assert "municipio_nome" in reg
            assert "uf" in reg
            assert "programa" in reg
            assert "beneficiarios" in reg
            assert "valor_total" in reg

    def test_programa_fonte_mapeamento(self):
        assert PROGRAMA_FONTE["BOLSA_FAMILIA"] == FonteDados.PORTAL_TRANSPARENCIA
        assert PROGRAMA_FONTE["FARMACIA_POPULAR"] == FonteDados.OPENDATASUS
        assert PROGRAMA_FONTE["TSEE"] == FonteDados.ANEEL


# =============================================================================
# TransformadorDados
# =============================================================================

class TestTransformador:
    def test_transformar_extracao_valida(self):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        extracao = extrator.extrair("BOLSA_FAMILIA", 1, 2026)

        transformador = TransformadorDados()
        result = transformador.transformar(extracao)

        assert result.sucesso is True
        assert result.total_validos > 0
        assert result.total_invalidos == 0

    def test_transformar_extracao_falha(self):
        extracao = ResultadoExtracao(
            fonte=FonteDados.PORTAL_TRANSPARENCIA,
            programa="TESTE",
            referencia="2026-01",
            sucesso=False,
            erro="Fonte indisponivel",
        )
        transformador = TransformadorDados()
        result = transformador.transformar(extracao)
        assert result.sucesso is False

    def test_registros_normalizados(self):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        extracao = extrator.extrair("BPC", 1, 2026)

        transformador = TransformadorDados()
        result = transformador.transformar(extracao)

        for reg in result.registros:
            assert isinstance(reg, RegistroTransformado)
            assert len(reg.municipio_ibge) == 7
            assert len(reg.uf) == 2
            assert reg.uf == reg.uf.upper()
            assert reg.beneficiarios >= 0
            assert reg.valor_total >= 0

    def test_validacao_ibge_invalido(self):
        extracao = ResultadoExtracao(
            fonte=FonteDados.PORTAL_TRANSPARENCIA,
            programa="TESTE",
            referencia="2026-01",
            registros=[{
                "municipio_ibge": "123",  # invalido (nao tem 7 digitos)
                "municipio_nome": "Teste",
                "uf": "SP",
                "programa": "TESTE",
                "referencia": "2026-01",
                "beneficiarios": 100,
                "valor_total": 1000.0,
            }],
            total_registros=1,
        )
        transformador = TransformadorDados()
        result = transformador.transformar(extracao)
        assert result.total_invalidos == 1

    def test_agregacao_duplicatas(self):
        extracao = ResultadoExtracao(
            fonte=FonteDados.PORTAL_TRANSPARENCIA,
            programa="TESTE",
            referencia="2026-01",
            registros=[
                {
                    "municipio_ibge": "3550308",
                    "municipio_nome": "Sao Paulo",
                    "uf": "SP",
                    "programa": "TESTE",
                    "referencia": "2026-01",
                    "beneficiarios": 100,
                    "valor_total": 1000.0,
                },
                {
                    "municipio_ibge": "3550308",
                    "municipio_nome": "Sao Paulo",
                    "uf": "SP",
                    "programa": "TESTE",
                    "referencia": "2026-01",
                    "beneficiarios": 200,
                    "valor_total": 2000.0,
                },
            ],
            total_registros=2,
        )
        transformador = TransformadorDados()
        result = transformador.transformar(extracao)
        # Deve agregar em 1 registro
        assert result.total_validos == 1
        assert result.registros[0].beneficiarios == 300
        assert result.registros[0].valor_total == 3000.0


# =============================================================================
# CarregadorDados
# =============================================================================

class TestCarregador:
    def test_carregar_em_arquivo(self, tmp_path):
        extrator = ExtratorDadosAbertos(modo_mock=True)
        transformador = TransformadorDados()
        carregador = CarregadorDados(modo_mock=True, diretorio_saida=str(tmp_path))

        extracao = extrator.extrair("BOLSA_FAMILIA", 1, 2026)
        transformacao = transformador.transformar(extracao)
        result = carregador.carregar(transformacao)

        assert result.sucesso is True
        assert result.inseridos > 0
        assert result.modo == "arquivo"

        # Verifica arquivo criado
        arquivo = tmp_path / "BOLSA_FAMILIA_2026-01.json"
        assert arquivo.exists()

    def test_carregar_transformacao_falha(self):
        carregador = CarregadorDados(modo_mock=True)
        transformacao = ResultadoTransformacao(
            programa="TESTE",
            referencia="2026-01",
            sucesso=False,
        )
        result = carregador.carregar(transformacao)
        assert result.sucesso is False

    def test_carregar_sem_registros(self):
        carregador = CarregadorDados(modo_mock=True)
        transformacao = ResultadoTransformacao(
            programa="TESTE",
            referencia="2026-01",
            sucesso=True,
        )
        result = carregador.carregar(transformacao)
        assert result.sucesso is True
        assert result.inseridos == 0


# =============================================================================
# OrquestradorETL
# =============================================================================

class TestOrquestrador:
    def test_pipeline_completo(self):
        orq = OrquestradorETL(modo_mock=True)
        result = orq.executar_pipeline("BOLSA_FAMILIA", 1, 2026)
        assert result.sucesso is True
        assert result.extracao_ok is True
        assert result.transformacao_ok is True
        assert result.carga_ok is True
        assert result.registros_validos > 0

    def test_pipeline_dry_run(self):
        orq = OrquestradorETL(modo_mock=True)
        result = orq.executar_pipeline("BPC", 1, 2026, dry_run=True)
        assert result.sucesso is True
        assert result.carga_ok is True
        assert result.registros_carregados == 0  # Nao carregou (dry run)

    def test_pipeline_programa_invalido(self):
        orq = OrquestradorETL(modo_mock=True)
        result = orq.executar_pipeline("INVALIDO", 1, 2026)
        assert result.sucesso is False

    def test_executar_todos(self):
        orq = OrquestradorETL(modo_mock=True)
        resultados = orq.executar_todos(1, 2026, dry_run=True)
        assert len(resultados) == len(AGENDA_PROGRAMAS)
        assert all(r.sucesso for r in resultados)

    def test_consultar_status(self):
        orq = OrquestradorETL(modo_mock=True)
        orq.executar_pipeline("BOLSA_FAMILIA", 1, 2026, dry_run=True)
        status = orq.consultar_status()
        assert status["total_execucoes"] == 1
        assert status["sucessos"] == 1
        assert status["ultima_execucao"]["programa"] == "BOLSA_FAMILIA"

    def test_historico_acumula(self):
        orq = OrquestradorETL(modo_mock=True)
        orq.executar_pipeline("BOLSA_FAMILIA", 1, 2026, dry_run=True)
        orq.executar_pipeline("BPC", 1, 2026, dry_run=True)
        assert len(orq.historico) == 2

    def test_agenda_programas(self):
        assert "BOLSA_FAMILIA" in AGENDA_PROGRAMAS
        assert "BPC" in AGENDA_PROGRAMAS
        for prog, config in AGENDA_PROGRAMAS.items():
            assert "dia" in config
            assert "hora" in config


# =============================================================================
# consultar_dados_abertos (tool para agente)
# =============================================================================

class TestConsultarDadosAbertos:
    def test_consultar_programa_especifico(self):
        result = consultar_dados_abertos(programa="BOLSA_FAMILIA")
        assert result["programa"] == "BOLSA_FAMILIA"
        assert result["status"] == "disponivel"

    def test_consultar_sem_programa(self):
        result = consultar_dados_abertos()
        assert "programas_disponiveis" in result
        assert len(result["programas_disponiveis"]) >= 5

    def test_consultar_com_mes_ano(self):
        result = consultar_dados_abertos(programa="BPC", mes=6, ano=2025)
        assert result["programa"] == "BPC"
        assert result["referencia"] == "2025-06"
