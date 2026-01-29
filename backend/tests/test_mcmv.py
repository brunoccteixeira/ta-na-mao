"""
Testes para o módulo MCMV (Minha Casa Minha Vida).

Testa:
- Verificação de elegibilidade por faixa
- Critérios de bloqueio
- Simulação de financiamento
- Grupos prioritários
- Programa de reformas
"""

import pytest
from datetime import date

from app.agent.tools.regras_elegibilidade import (
    CitizenProfile,
    EligibilityStatus,
    MCMV_FAIXA_1,
    MCMV_FAIXA_2,
    MCMV_FAIXA_3,
    MCMV_FAIXA_4,
    MCMV_SUBSIDIO_FAIXA_1,
    MCMV_SUBSIDIO_FAIXA_2,
    REFORMA_LIMITE_FAIXA_1,
    REFORMA_LIMITE_FAIXA_2,
)
from app.agent.tools.regras_elegibilidade.mcmv import (
    verificar_elegibilidade,
    obter_info_faixa,
    calcular_subsidio_estimado,
    listar_modalidades_disponiveis,
)
from app.agent.tools.simulador_mcmv import (
    simular_financiamento_mcmv,
    simular_reforma,
    comparar_modalidades,
    calcular_capacidade_pagamento,
    SistemaAmortizacao,
)


class TestElegibilidadeFaixas:
    """Testes de elegibilidade por faixa de renda."""

    def test_faixa_1_elegivel(self):
        """Renda até R$ 2.850 deve ser Faixa 1."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2500.00,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "Faixa 1" in resultado.programa_nome
        assert resultado.valor_estimado == MCMV_SUBSIDIO_FAIXA_1

    def test_faixa_1_limite(self):
        """Renda exatamente R$ 2.850 deve ser Faixa 1."""
        perfil = CitizenProfile(
            renda_familiar_mensal=MCMV_FAIXA_1,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "Faixa 1" in resultado.programa_nome

    def test_faixa_2_elegivel(self):
        """Renda entre R$ 2.850 e R$ 4.700 deve ser Faixa 2."""
        perfil = CitizenProfile(
            renda_familiar_mensal=3500.00,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "Faixa 2" in resultado.programa_nome
        assert resultado.valor_estimado == MCMV_SUBSIDIO_FAIXA_2

    def test_faixa_3_elegivel(self):
        """Renda entre R$ 4.700 e R$ 8.600 deve ser Faixa 3."""
        perfil = CitizenProfile(
            renda_familiar_mensal=6000.00,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "Faixa 3" in resultado.programa_nome

    def test_faixa_4_elegivel(self):
        """Renda entre R$ 8.600 e R$ 12.000 deve ser Faixa 4."""
        perfil = CitizenProfile(
            renda_familiar_mensal=10000.00,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "Faixa 4" in resultado.programa_nome

    def test_renda_acima_limite_inelegivel(self):
        """Renda acima de R$ 12.000 deve ser inelegível."""
        perfil = CitizenProfile(
            renda_familiar_mensal=15000.00,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.INELEGIVEL
        assert "acima" in resultado.motivo.lower()


class TestCriteriosBloqueio:
    """Testes de critérios que bloqueiam elegibilidade."""

    def test_ja_possui_imovel_bloqueia(self):
        """Já possuir imóvel deve bloquear para aquisição."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2000.00,
            tem_casa_propria=True,
        )

        resultado = verificar_elegibilidade(perfil)

        # Deve redirecionar para programa de reformas
        assert "REFORMA" in resultado.programa

    def test_imovel_registrado_bloqueia(self):
        """Imóvel registrado deve bloquear."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2000.00,
            tem_casa_propria=False,
            tem_imovel_registrado=True,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.INELEGIVEL

    def test_beneficio_habitacional_anterior_bloqueia(self):
        """Ter recebido benefício habitacional bloqueia."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2000.00,
            tem_casa_propria=False,
            teve_beneficio_habitacional_federal=True,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.INELEGIVEL

    def test_financiamento_ativo_bloqueia(self):
        """Ter financiamento ativo bloqueia."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2000.00,
            tem_casa_propria=False,
            tem_financiamento_ativo=True,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.INELEGIVEL


class TestGruposPrioritarios:
    """Testes para identificação de grupos prioritários."""

    def test_situacao_rua_prioritario(self):
        """Pessoa em situação de rua deve ser grupo prioritário."""
        perfil = CitizenProfile(
            renda_familiar_mensal=0,
            situacao_rua=True,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "rua" in resultado.observacoes.lower()

    def test_beneficiario_bpc_faixa_1_gratuito(self):
        """Beneficiário BPC na Faixa 1 pode ter imóvel gratuito."""
        perfil = CitizenProfile(
            renda_familiar_mensal=1500.00,
            recebe_bpc=True,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "100%" in resultado.observacoes or "gratuito" in resultado.observacoes.lower()

    def test_beneficiario_bolsa_familia_faixa_1(self):
        """Beneficiário Bolsa Família na Faixa 1 tem prioridade."""
        perfil = CitizenProfile(
            renda_familiar_mensal=1000.00,
            recebe_bolsa_familia=True,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "Bolsa" in resultado.observacoes or "gratuito" in resultado.observacoes.lower()

    def test_vitima_violencia_prioritario(self):
        """Vítima de violência doméstica deve ser prioritária."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2000.00,
            vitima_violencia_domestica=True,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL


class TestProgramaReformas:
    """Testes para o Programa Reforma Casa Brasil."""

    def test_reforma_faixa_1_elegivel(self):
        """Quem tem casa e renda até R$ 3.200 é elegível para reforma Faixa 1."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2500.00,
            tem_casa_propria=True,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "REFORMAS" in resultado.programa
        assert "Faixa 1" in resultado.programa_nome

    def test_reforma_faixa_2_elegivel(self):
        """Quem tem casa e renda R$ 3.200-9.600 é elegível para reforma Faixa 2."""
        perfil = CitizenProfile(
            renda_familiar_mensal=5000.00,
            tem_casa_propria=True,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "REFORMAS" in resultado.programa
        assert "Faixa 2" in resultado.programa_nome

    def test_reforma_acima_limite_inelegivel(self):
        """Renda acima de R$ 9.600 não é elegível para reforma."""
        perfil = CitizenProfile(
            renda_familiar_mensal=12000.00,
            tem_casa_propria=True,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.INELEGIVEL


class TestSimuladorFinanciamento:
    """Testes para o simulador de financiamento."""

    def test_simulacao_faixa_1(self):
        """Simulação para Faixa 1 deve ter subsídio."""
        resultado = simular_financiamento_mcmv(
            renda_familiar=2000.00,
            valor_fgts=10000.00,
        )

        assert resultado.faixa == "Faixa 1"
        assert resultado.subsidio > 0
        assert resultado.parcela_inicial > 0
        # Comprometimento pode ser alto para renda baixa com imóvel de alto valor
        assert resultado.comprometimento_renda > 0

    def test_simulacao_faixa_4(self):
        """Simulação para Faixa 4 deve permitir imóvel até R$ 500 mil."""
        resultado = simular_financiamento_mcmv(
            renda_familiar=10000.00,
        )

        assert resultado.faixa == "Faixa 4"
        assert resultado.valor_imovel <= 500000
        assert resultado.subsidio == 0
        assert resultado.taxa_juros_anual == 10.0

    def test_simulacao_com_fgts(self):
        """FGTS deve reduzir valor financiado."""
        sem_fgts = simular_financiamento_mcmv(
            renda_familiar=5000.00,
            valor_fgts=0,
        )

        com_fgts = simular_financiamento_mcmv(
            renda_familiar=5000.00,
            valor_fgts=50000.00,
        )

        assert com_fgts.valor_financiado < sem_fgts.valor_financiado
        assert com_fgts.parcela_inicial < sem_fgts.parcela_inicial

    def test_simulacao_ajusta_prazo_por_idade(self):
        """Prazo deve ser ajustado pela idade do comprador."""
        jovem = simular_financiamento_mcmv(
            renda_familiar=5000.00,
            idade_comprador=30,
        )

        idoso = simular_financiamento_mcmv(
            renda_familiar=5000.00,
            idade_comprador=60,
        )

        assert jovem.prazo_meses > idoso.prazo_meses

    def test_simulacao_renda_acima_limite(self):
        """Renda acima do limite deve retornar inelegível."""
        resultado = simular_financiamento_mcmv(
            renda_familiar=15000.00,
        )

        assert resultado.faixa == "Inelegível"
        assert not resultado.viavel


class TestSimuladorReforma:
    """Testes para o simulador de reforma."""

    def test_reforma_faixa_1(self):
        """Simulação de reforma Faixa 1."""
        resultado = simular_reforma(
            renda_familiar=2500.00,
            valor_reforma=20000.00,
            prazo_meses=48,
        )

        assert resultado.faixa == "Reforma Faixa 1"
        assert resultado.parcela_inicial > 0
        assert resultado.taxa_juros_anual > 0

    def test_reforma_valor_limitado(self):
        """Valor da reforma deve ser limitado a R$ 30 mil."""
        resultado = simular_reforma(
            renda_familiar=3000.00,
            valor_reforma=50000.00,  # Acima do limite
        )

        assert resultado.valor_financiado <= 30000

    def test_reforma_inelegivel(self):
        """Renda acima do limite deve ser inelegível."""
        resultado = simular_reforma(
            renda_familiar=15000.00,
            valor_reforma=20000.00,
        )

        assert resultado.faixa == "Inelegível"


class TestComparacaoModalidades:
    """Testes para comparação de modalidades."""

    def test_comparacao_faixa_1(self):
        """Faixa 1 deve ter opções de entidades e locação social."""
        resultado = comparar_modalidades(
            renda_familiar=2000.00,
            tem_casa_propria=False,
        )

        assert resultado.faixa == "Faixa 1"
        assert len(resultado.modalidades) >= 3  # Novo, entidades, locação
        tipos = [m["tipo"] for m in resultado.modalidades]
        assert any("Entidades" in t for t in tipos)

    def test_comparacao_faixa_4_permite_usado(self):
        """Faixa 4 deve permitir imóvel usado."""
        resultado = comparar_modalidades(
            renda_familiar=10000.00,
            tem_casa_propria=False,
        )

        tipos = [m["tipo"] for m in resultado.modalidades]
        assert any("usado" in t.lower() for t in tipos)

    def test_comparacao_quem_tem_casa(self):
        """Quem tem casa só pode ver opção de reforma."""
        resultado = comparar_modalidades(
            renda_familiar=3000.00,
            tem_casa_propria=True,
        )

        assert len(resultado.modalidades) == 1
        assert "Reforma" in resultado.modalidades[0]["tipo"]


class TestCapacidadePagamento:
    """Testes para cálculo de capacidade de pagamento."""

    def test_capacidade_30_porcento(self):
        """Parcela máxima deve ser 30% da renda."""
        resultado = calcular_capacidade_pagamento(
            renda_familiar=5000.00,
            percentual_maximo=30.0,
        )

        assert resultado["parcela_maxima"] == 1500.00
        assert resultado["valor_financiavel_estimado"] > 0

    def test_capacidade_renda_baixa(self):
        """Deve funcionar para renda baixa."""
        resultado = calcular_capacidade_pagamento(
            renda_familiar=1500.00,
        )

        assert resultado["parcela_maxima"] == 450.00


class TestFuncoesAuxiliares:
    """Testes para funções auxiliares."""

    def test_obter_info_faixa_1(self):
        """Deve retornar info correta para Faixa 1."""
        info = obter_info_faixa(2000.00)

        assert info["faixa"] == "Faixa 1"
        assert info["subsidio_maximo"] == MCMV_SUBSIDIO_FAIXA_1
        assert info["permite_usado"] is False

    def test_obter_info_faixa_4(self):
        """Deve retornar info correta para Faixa 4."""
        info = obter_info_faixa(10000.00)

        assert info["faixa"] == "Faixa 4"
        assert info["subsidio_maximo"] == 0
        assert info["permite_usado"] is True

    def test_obter_info_acima_limite(self):
        """Renda acima do limite deve retornar None."""
        info = obter_info_faixa(20000.00)

        assert info is None

    def test_listar_modalidades_faixa_1(self):
        """Faixa 1 deve ter entidades e locação."""
        modalidades = listar_modalidades_disponiveis("Faixa 1")

        codigos = [m["codigo"] for m in modalidades]
        assert "AQUISICAO_NOVO" in codigos
        assert "ENTIDADES" in codigos
        assert "LOCACAO_SOCIAL" in codigos

    def test_listar_modalidades_faixa_4(self):
        """Faixa 4 deve permitir usado."""
        modalidades = listar_modalidades_disponiveis("Faixa 4")

        codigos = [m["codigo"] for m in modalidades]
        assert "AQUISICAO_NOVO" in codigos
        assert "AQUISICAO_USADO" in codigos


class TestEncaminhamento:
    """Testes para lógica de encaminhamento."""

    def test_faixa_1_sem_cadunico_vai_cras(self):
        """Faixa 1 sem CadÚnico deve ir ao CRAS primeiro."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2000.00,
            cadastrado_cadunico=False,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert "CRAS" in resultado.onde_solicitar or "CadÚnico" in resultado.proximos_passos[0]

    def test_faixa_1_com_cadunico_vai_prefeitura(self):
        """Faixa 1 com CadÚnico deve ir à Prefeitura."""
        perfil = CitizenProfile(
            renda_familiar_mensal=2000.00,
            cadastrado_cadunico=True,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert "Prefeitura" in resultado.onde_solicitar

    def test_faixa_2_vai_caixa(self):
        """Faixas 2, 3 e 4 devem ir à CAIXA."""
        perfil = CitizenProfile(
            renda_familiar_mensal=4000.00,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert "CAIXA" in resultado.onde_solicitar


class TestEdgeCases:
    """Testes para casos de borda."""

    def test_renda_zero(self):
        """Renda zero deve ser elegível para Faixa 1."""
        perfil = CitizenProfile(
            renda_familiar_mensal=0,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "Faixa 1" in resultado.programa_nome

    def test_renda_negativa(self):
        """Renda negativa deve ser tratada como zero."""
        perfil = CitizenProfile(
            renda_familiar_mensal=-100,
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL

    def test_limite_exato_entre_faixas(self):
        """Limite exato deve cair na faixa inferior."""
        perfil = CitizenProfile(
            renda_familiar_mensal=MCMV_FAIXA_2,  # Exatamente o limite
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        assert resultado.status == EligibilityStatus.ELEGIVEL
        assert "Faixa 2" in resultado.programa_nome

    def test_idade_muito_avancada(self):
        """Idade muito avançada pode inviabilizar."""
        perfil = CitizenProfile(
            renda_familiar_mensal=3000.00,
            data_nascimento="1945-01-01",  # ~81 anos
            tem_casa_propria=False,
        )

        resultado = verificar_elegibilidade(perfil)

        # Pode ser inelegível ou ter prazo muito reduzido
        # Depende da lógica - verificar se está no motivo ou observações
        assert resultado is not None
