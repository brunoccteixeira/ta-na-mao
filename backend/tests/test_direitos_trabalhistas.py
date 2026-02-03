"""
Testes para direitos trabalhistas.

Testa consulta de direitos por tipo de trabalho,
calculadora de rescisao e calculadora de seguro-desemprego.
"""

import pytest
from app.agent.tools.direitos_trabalhistas import (
    consultar_direitos_trabalhistas,
    calcular_rescisao,
    calcular_seguro_desemprego,
)


class TestConsultarDireitosTrabalhistas:
    """Testes para consulta de direitos."""

    def test_lista_tipos_disponiveis(self):
        """Sem filtro deve listar tipos disponiveis."""
        result = consultar_direitos_trabalhistas()
        assert result["encontrado"] is True
        assert result["tipo"] == "lista"
        assert len(result["tipos_disponiveis"]) >= 6

    def test_direitos_clt(self):
        """CLT deve retornar direitos basicos."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="CLT")
        assert result["encontrado"] is True
        nomes = [d["nome"] for d in result["info"]["direitos"]]
        assert "13o salario" in nomes
        assert "FGTS (8%)" in nomes
        assert "Seguro-desemprego" in nomes

    def test_direitos_domestico(self):
        """Domestico deve ter carteira obrigatoria."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="DOMESTICO")
        assert result["encontrado"] is True
        nomes = [d["nome"] for d in result["info"]["direitos"]]
        assert "Carteira assinada obrigatoria" in nomes

    def test_direitos_mei(self):
        """MEI deve ter obrigacoes."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="MEI")
        assert result["encontrado"] is True
        assert "obrigacoes" in result["info"]
        obrig_nomes = [o["nome"] for o in result["info"]["obrigacoes"]]
        assert "DAS mensal" in obrig_nomes

    def test_direitos_informal(self):
        """Informal deve ter alerta sobre guardar provas."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="INFORMAL")
        assert result["encontrado"] is True
        assert "alerta" in result["info"]
        assert "prova" in result["info"]["alerta"].lower()

    def test_direitos_rural(self):
        """Rural deve ter aposentadoria especial."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="RURAL")
        assert result["encontrado"] is True
        nomes = [d["nome"] for d in result["info"]["direitos"]]
        assert any("aposentadoria" in n.lower() for n in nomes)

    def test_direitos_pescador(self):
        """Pescador deve ter seguro-defeso."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="PESCADOR")
        assert result["encontrado"] is True
        nomes = [d["nome"] for d in result["info"]["direitos"]]
        assert any("defeso" in n.lower() for n in nomes)

    def test_alias_carteira_assinada(self):
        """carteira_assinada deve mapear para CLT."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="carteira_assinada")
        assert result["encontrado"] is True
        assert result["tipo_trabalho"] == "CLT"

    def test_alias_domestica(self):
        """domestica deve mapear para DOMESTICO."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="domestica")
        assert result["encontrado"] is True
        assert result["tipo_trabalho"] == "DOMESTICO"

    def test_situacao_demitido(self):
        """Situacao demitido deve retornar passos."""
        result = consultar_direitos_trabalhistas(situacao="DEMITIDO")
        assert result["encontrado"] is True
        assert result["tipo"] == "situacao"
        assert len(result["situacao"]["passos"]) >= 3

    def test_situacao_sem_carteira(self):
        """Situacao sem_carteira deve ter alerta sobre prazo."""
        result = consultar_direitos_trabalhistas(situacao="SEM_CARTEIRA")
        assert result["encontrado"] is True
        assert "2 anos" in result["situacao"]["alerta"].lower() or "2 ANOS" in result["situacao"]["alerta"]

    def test_situacao_assedio(self):
        """Situacao assedio deve ter servicos de ajuda."""
        result = consultar_direitos_trabalhistas(situacao="ASSEDIO")
        assert result["encontrado"] is True
        assert "servicos" in result["situacao"]

    def test_tipo_invalido(self):
        """Tipo invalido deve retornar erro."""
        result = consultar_direitos_trabalhistas(tipo_trabalho="INVALIDO")
        assert result["encontrado"] is False
        assert "tipos_disponiveis" in result

    def test_situacao_invalida(self):
        """Situacao invalida deve retornar erro."""
        result = consultar_direitos_trabalhistas(situacao="INVALIDA")
        assert result["encontrado"] is False
        assert "situacoes_disponiveis" in result


class TestCalcularRescisao:
    """Testes para calculadora de rescisao."""

    def test_rescisao_sem_justa_causa_basica(self):
        """Rescisao sem justa causa com valores basicos."""
        result = calcular_rescisao(
            salario=2000.0,
            meses_trabalhados=24,
            motivo="SEM_JUSTA_CAUSA",
        )
        assert result["salario_base"] == 2000.0
        assert result["total_bruto"] > 0
        assert result["total_liquido"] > 0
        # Deve ter FGTS + multa 40%
        nomes_verbas = [v["nome"] for v in result["verbas"]]
        assert "Multa FGTS (40%)" in nomes_verbas
        assert "Saque FGTS" in nomes_verbas

    def test_rescisao_justa_causa(self):
        """Justa causa nao tem 13o, ferias proporcionais, FGTS."""
        result = calcular_rescisao(
            salario=2000.0,
            meses_trabalhados=12,
            motivo="JUSTA_CAUSA",
        )
        nomes_verbas = [v["nome"] for v in result["verbas"]]
        assert "Multa FGTS (40%)" not in nomes_verbas
        assert "13o salario proporcional" not in nomes_verbas
        assert "alerta" in result["informacoes_extras"]

    def test_rescisao_pedido_demissao(self):
        """Pedido de demissao nao tem seguro-desemprego."""
        result = calcular_rescisao(
            salario=3000.0,
            meses_trabalhados=18,
            motivo="PEDIDO_DEMISSAO",
        )
        assert "seguro_desemprego" in result["informacoes_extras"]
        assert "NAO" in result["informacoes_extras"]["seguro_desemprego"]

    def test_rescisao_acordo(self):
        """Acordo tem multa FGTS de 20% e saque de 80%."""
        result = calcular_rescisao(
            salario=2000.0,
            meses_trabalhados=24,
            motivo="ACORDO",
        )
        nomes_verbas = [v["nome"] for v in result["verbas"]]
        assert "Multa FGTS (20%)" in nomes_verbas
        assert "Saque FGTS (80%)" in nomes_verbas

    def test_aviso_previo_calculado(self):
        """Aviso previo deve considerar anos trabalhados."""
        result = calcular_rescisao(
            salario=2000.0,
            meses_trabalhados=60,  # 5 anos
            motivo="SEM_JUSTA_CAUSA",
        )
        # 30 + 5*3 = 45 dias
        aviso = [v for v in result["verbas"] if "Aviso previo" in v["nome"]]
        assert len(aviso) > 0
        assert "45 dias" in aviso[0]["descricao"]

    def test_ferias_vencidas(self):
        """Com ferias vencidas, deve adicionar verba extra."""
        result = calcular_rescisao(
            salario=2000.0,
            meses_trabalhados=24,
            tem_ferias_vencidas=True,
        )
        nomes = [v["nome"] for v in result["verbas"]]
        assert "Ferias vencidas + 1/3" in nomes

    def test_saldo_salario_dias(self):
        """Deve calcular saldo de salario por dias trabalhados."""
        result = calcular_rescisao(
            salario=3000.0,
            meses_trabalhados=12,
            dias_trabalhados_mes_atual=15,
        )
        saldo = [v for v in result["verbas"] if "Saldo de salario" in v["nome"]]
        assert len(saldo) == 1
        assert saldo[0]["valor"] == round(3000.0 / 30 * 15, 2)

    def test_resultado_tem_informacoes_extras(self):
        """Resultado deve ter informacoes extras."""
        result = calcular_rescisao(
            salario=2000.0,
            meses_trabalhados=12,
        )
        assert "informacoes_extras" in result
        assert "seguro_desemprego" in result["informacoes_extras"]


class TestCalcularSeguroDesemprego:
    """Testes para calculadora de seguro-desemprego."""

    def test_primeira_solicitacao_elegivel(self):
        """Primeira solicitacao com 12+ meses deve ser elegivel."""
        result = calcular_seguro_desemprego(
            salario_medio=2000.0,
            vezes_solicitado=1,
            meses_trabalhados=12,
        )
        assert result["elegivel"] is True
        assert result["num_parcelas"] >= 3
        assert result["valor_parcela"] > 0
        assert result["total_estimado"] > 0

    def test_primeira_solicitacao_inelegivel(self):
        """Primeira solicitacao com menos de 12 meses deve ser inelegivel."""
        result = calcular_seguro_desemprego(
            salario_medio=2000.0,
            vezes_solicitado=1,
            meses_trabalhados=6,
        )
        assert result["elegivel"] is False
        assert "12 meses" in result["motivo"]

    def test_segunda_solicitacao_elegivel(self):
        """Segunda solicitacao com 9+ meses deve ser elegivel."""
        result = calcular_seguro_desemprego(
            salario_medio=2000.0,
            vezes_solicitado=2,
            meses_trabalhados=9,
        )
        assert result["elegivel"] is True

    def test_terceira_solicitacao_elegivel(self):
        """Terceira solicitacao com 6+ meses deve ser elegivel."""
        result = calcular_seguro_desemprego(
            salario_medio=2000.0,
            vezes_solicitado=3,
            meses_trabalhados=6,
        )
        assert result["elegivel"] is True

    def test_valor_minimo_salario_minimo(self):
        """Valor nao pode ser menor que salario minimo."""
        result = calcular_seguro_desemprego(
            salario_medio=500.0,  # Abaixo do minimo
            vezes_solicitado=1,
            meses_trabalhados=24,
        )
        assert result["elegivel"] is True
        assert result["valor_parcela"] >= 1518.00

    def test_parcelas_por_tempo(self):
        """24+ meses deve dar 5 parcelas."""
        result = calcular_seguro_desemprego(
            salario_medio=2000.0,
            vezes_solicitado=1,
            meses_trabalhados=24,
        )
        assert result["num_parcelas"] == 5

    def test_documentos_necessarios(self):
        """Deve listar documentos necessarios."""
        result = calcular_seguro_desemprego(
            salario_medio=2000.0,
            meses_trabalhados=12,
        )
        assert "documentos_necessarios" in result
        assert len(result["documentos_necessarios"]) >= 3

    def test_onde_pedir(self):
        """Deve informar onde pedir."""
        result = calcular_seguro_desemprego(
            salario_medio=2000.0,
            meses_trabalhados=12,
        )
        assert "onde_pedir" in result
        assert len(result["onde_pedir"]) >= 2

    def test_prazo_para_pedir(self):
        """Deve informar prazo de 120 dias."""
        result = calcular_seguro_desemprego(
            salario_medio=2000.0,
            meses_trabalhados=12,
        )
        assert "120" in result["prazo_para_pedir"]
