"""Testes para relatorio de impacto social (impacto-esg)."""

import pytest
from app.services.relatorio_impacto import (
    gerar_relatorio_impacto,
    consultar_impacto_social,
)


# =============================================================================
# gerar_relatorio_impacto
# =============================================================================

class TestGerarRelatorioImpacto:
    def test_sem_parametros(self):
        result = gerar_relatorio_impacto()
        assert "referencia" in result
        assert "metricas" in result
        assert "ods_impactados" in result
        assert "anonimizacao" in result
        assert result["escopo"] == "nacional"

    def test_com_mes_ano(self):
        result = gerar_relatorio_impacto(mes=6, ano=2025)
        assert result["referencia"] == "2025-06"

    def test_com_municipio(self):
        result = gerar_relatorio_impacto(municipio_ibge="3550308")
        assert result["escopo"] == "3550308"
        # Municipio deve ter valores menores que nacional
        metricas = result["metricas"]
        assert metricas["acesso"]["cidadaos_atendidos"] < 150000

    def test_metricas_acesso(self):
        result = gerar_relatorio_impacto()
        acesso = result["metricas"]["acesso"]
        assert "cidadaos_atendidos" in acesso
        assert "consultas_realizadas" in acesso
        assert "beneficios_descobertos" in acesso
        assert "encaminhamentos_cras" in acesso
        assert "checklists_gerados" in acesso

    def test_metricas_financeiro(self):
        result = gerar_relatorio_impacto()
        fin = result["metricas"]["financeiro"]
        assert "valor_beneficios_conectados" in fin
        assert "valor_dinheiro_esquecido" in fin
        assert fin["valor_beneficios_conectados"] > 0

    def test_metricas_inclusao(self):
        result = gerar_relatorio_impacto()
        inc = result["metricas"]["inclusao"]
        assert "primeiro_acesso_digital" in inc
        assert "atendimentos_whatsapp" in inc

    def test_metricas_eficiencia(self):
        result = gerar_relatorio_impacto()
        efi = result["metricas"]["eficiencia"]
        assert "tempo_medio_consulta_min" in efi
        assert "reducao_fila_cras_pct" in efi

    def test_ods_impactados(self):
        result = gerar_relatorio_impacto()
        ods = result["ods_impactados"]
        assert "ODS_1" in ods
        assert "ODS_10" in ods

    def test_anonimizacao_conformidade(self):
        result = gerar_relatorio_impacto()
        anon = result["anonimizacao"]
        assert "LGPD" in anon["conformidade"]

    def test_formatos_disponiveis(self):
        result = gerar_relatorio_impacto()
        assert "json" in result["formatos_disponiveis"]
        assert "pdf" in result["formatos_disponiveis"]


# =============================================================================
# consultar_impacto_social
# =============================================================================

class TestConsultarImpactoSocial:
    def test_sem_tipo_retorna_resumo(self):
        result = consultar_impacto_social()
        assert "tipos_disponiveis" in result
        assert "resumo" in result
        assert "ods" in result

    def test_tipo_acesso(self):
        result = consultar_impacto_social(tipo="acesso")
        assert result["tipo"] == "acesso"
        assert "metricas" in result
        assert "dados" in result

    def test_tipo_financeiro(self):
        result = consultar_impacto_social(tipo="financeiro")
        assert result["tipo"] == "financeiro"

    def test_tipo_inclusao(self):
        result = consultar_impacto_social(tipo="inclusao")
        assert result["tipo"] == "inclusao"

    def test_tipo_eficiencia(self):
        result = consultar_impacto_social(tipo="eficiencia")
        assert result["tipo"] == "eficiencia"

    def test_tipo_invalido_retorna_resumo(self):
        result = consultar_impacto_social(tipo="invalido")
        assert "tipos_disponiveis" in result
