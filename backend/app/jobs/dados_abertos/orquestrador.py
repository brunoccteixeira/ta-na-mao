"""
Orquestrador do pipeline ETL de dados abertos.

Coordena extracao -> transformacao -> carga para cada programa.
Gerencia agendamento e monitoramento.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .extrator import ExtratorDadosAbertos, PROGRAMA_FONTE
from .transformador import TransformadorDados
from .carregador import CarregadorDados, ResultadoCarga

logger = logging.getLogger(__name__)


# Agenda de execucao (dia do mes, hora)
AGENDA_PROGRAMAS = {
    "BOLSA_FAMILIA": {"dia": 5, "hora": 3},
    "BPC": {"dia": 6, "hora": 3},
    "FARMACIA_POPULAR": {"dia": 7, "hora": 4},
    "TSEE": {"dia": 8, "hora": 4},
    "AUXILIO_GAS": {"dia": 9, "hora": 4},
    "SEGURO_DEFESO": {"dia": 10, "hora": 4},
}


@dataclass
class ResultadoPipeline:
    """Resultado completo de um pipeline ETL."""
    programa: str
    referencia: str
    extracao_ok: bool = False
    transformacao_ok: bool = False
    carga_ok: bool = False
    registros_extraidos: int = 0
    registros_validos: int = 0
    registros_invalidos: int = 0
    registros_carregados: int = 0
    erro: Optional[str] = None
    inicio: str = field(default_factory=lambda: datetime.now().isoformat())
    fim: Optional[str] = None

    @property
    def sucesso(self) -> bool:
        return self.extracao_ok and self.transformacao_ok and self.carga_ok


@dataclass
class AlertaQualidade:
    """Alerta de qualidade de dados."""
    tipo: str  # "dados_ausentes", "queda_beneficiarios", "aumento_valores"
    programa: str
    referencia: str
    mensagem: str
    severidade: str = "media"  # "baixa", "media", "alta"


class OrquestradorETL:
    """Orquestra pipeline ETL completo.

    Coordena: Extracao -> Transformacao -> Carga
    Monitora qualidade e gera alertas.
    """

    def __init__(self, modo_mock: bool = True):
        self.extrator = ExtratorDadosAbertos(modo_mock=modo_mock)
        self.transformador = TransformadorDados()
        self.carregador = CarregadorDados(modo_mock=modo_mock)
        self.historico: List[ResultadoPipeline] = []
        self.alertas: List[AlertaQualidade] = []

    def executar_pipeline(
        self,
        programa: str,
        mes: int,
        ano: int,
        dry_run: bool = False,
    ) -> ResultadoPipeline:
        """Executa pipeline ETL completo para um programa.

        Args:
            programa: Codigo do programa (BOLSA_FAMILIA, BPC, etc)
            mes: Mes de referencia
            ano: Ano de referencia
            dry_run: Se True, nao carrega no destino

        Returns:
            ResultadoPipeline com estatisticas
        """
        referencia = f"{ano:04d}-{mes:02d}"
        resultado = ResultadoPipeline(programa=programa, referencia=referencia)

        logger.info(f"Iniciando pipeline ETL: {programa} ref {referencia}")

        # 1. Extracao
        try:
            extracao = self.extrator.extrair(programa, mes, ano)
            resultado.extracao_ok = extracao.sucesso
            resultado.registros_extraidos = extracao.total_registros

            if not extracao.sucesso:
                resultado.erro = f"Falha na extracao: {extracao.erro}"
                resultado.fim = datetime.now().isoformat()
                self.historico.append(resultado)
                return resultado
        except Exception as e:
            resultado.erro = f"Erro na extracao: {str(e)}"
            resultado.fim = datetime.now().isoformat()
            self.historico.append(resultado)
            return resultado

        # 2. Transformacao
        try:
            transformacao = self.transformador.transformar(extracao)
            resultado.transformacao_ok = transformacao.sucesso
            resultado.registros_validos = transformacao.total_validos
            resultado.registros_invalidos = transformacao.total_invalidos

            if not transformacao.sucesso:
                resultado.erro = "Falha na transformacao"
                resultado.fim = datetime.now().isoformat()
                self.historico.append(resultado)
                return resultado
        except Exception as e:
            resultado.erro = f"Erro na transformacao: {str(e)}"
            resultado.fim = datetime.now().isoformat()
            self.historico.append(resultado)
            return resultado

        # 3. Carga (skip se dry_run)
        if dry_run:
            resultado.carga_ok = True
            logger.info(f"Dry-run: pulando carga de {resultado.registros_validos} registros")
        else:
            try:
                carga = self.carregador.carregar(transformacao)
                resultado.carga_ok = carga.sucesso
                resultado.registros_carregados = carga.inseridos + carga.atualizados

                if not carga.sucesso:
                    resultado.erro = "Falha na carga"
            except Exception as e:
                resultado.erro = f"Erro na carga: {str(e)}"

        resultado.fim = datetime.now().isoformat()
        self.historico.append(resultado)

        # Verificar qualidade
        self._verificar_qualidade(resultado)

        logger.info(
            f"Pipeline concluido: {programa} ref {referencia} - "
            f"{'SUCESSO' if resultado.sucesso else 'FALHA'} "
            f"({resultado.registros_validos} registros)"
        )

        return resultado

    def executar_todos(
        self,
        mes: int,
        ano: int,
        dry_run: bool = False,
    ) -> List[ResultadoPipeline]:
        """Executa pipeline para todos os programas agendados.

        Args:
            mes: Mes de referencia
            ano: Ano de referencia
            dry_run: Se True, nao carrega no destino

        Returns:
            Lista de ResultadoPipeline
        """
        resultados = []
        for programa in AGENDA_PROGRAMAS:
            resultado = self.executar_pipeline(programa, mes, ano, dry_run)
            resultados.append(resultado)

        return resultados

    def consultar_status(self) -> Dict[str, Any]:
        """Consulta status dos pipelines executados."""
        total = len(self.historico)
        sucessos = sum(1 for r in self.historico if r.sucesso)
        falhas = total - sucessos

        ultimo = self.historico[-1] if self.historico else None

        return {
            "total_execucoes": total,
            "sucessos": sucessos,
            "falhas": falhas,
            "alertas_pendentes": len(self.alertas),
            "ultima_execucao": {
                "programa": ultimo.programa,
                "referencia": ultimo.referencia,
                "sucesso": ultimo.sucesso,
                "registros": ultimo.registros_validos,
                "fim": ultimo.fim,
            } if ultimo else None,
            "programas_disponiveis": list(PROGRAMA_FONTE.keys()),
        }

    def _verificar_qualidade(self, resultado: ResultadoPipeline):
        """Verifica qualidade dos dados e gera alertas."""
        # Alerta: nenhum registro extraido
        if resultado.registros_extraidos == 0:
            self.alertas.append(AlertaQualidade(
                tipo="dados_ausentes",
                programa=resultado.programa,
                referencia=resultado.referencia,
                mensagem=f"Nenhum registro extraido para {resultado.programa} ref {resultado.referencia}",
                severidade="alta",
            ))

        # Alerta: muitos registros invalidos (>10%)
        if resultado.registros_extraidos > 0:
            pct_invalidos = resultado.registros_invalidos / resultado.registros_extraidos
            if pct_invalidos > 0.1:
                self.alertas.append(AlertaQualidade(
                    tipo="qualidade_baixa",
                    programa=resultado.programa,
                    referencia=resultado.referencia,
                    mensagem=(
                        f"{resultado.registros_invalidos} de {resultado.registros_extraidos} "
                        f"registros invalidos ({pct_invalidos:.0%})"
                    ),
                    severidade="media",
                ))

        # Comparar com execucao anterior do mesmo programa
        anteriores = [
            r for r in self.historico
            if r.programa == resultado.programa
            and r.referencia != resultado.referencia
            and r.sucesso
        ]

        if anteriores:
            anterior = anteriores[-1]
            if anterior.registros_validos > 0:
                variacao = (
                    (resultado.registros_validos - anterior.registros_validos)
                    / anterior.registros_validos
                )
                if variacao < -0.3:
                    self.alertas.append(AlertaQualidade(
                        tipo="queda_beneficiarios",
                        programa=resultado.programa,
                        referencia=resultado.referencia,
                        mensagem=(
                            f"Queda de {abs(variacao):.0%} nos registros vs "
                            f"referencia anterior ({anterior.referencia})"
                        ),
                        severidade="alta",
                    ))


# =============================================================================
# Tool para o agente: consultar_dados_abertos
# =============================================================================

def consultar_dados_abertos(
    programa: Optional[str] = None,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
) -> Dict[str, Any]:
    """Consulta dados abertos sobre beneficios sociais.

    Retorna estatisticas agregadas de beneficiarios e valores por programa.

    Args:
        programa: Filtrar por programa (BOLSA_FAMILIA, BPC, TSEE, etc).
                  Se nao informado, retorna resumo de todos.
        mes: Mes de referencia (1-12). Padrao: mes atual.
        ano: Ano de referencia. Padrao: ano atual.

    Returns:
        dict com dados agregados do programa
    """
    now = datetime.now()
    mes = mes or now.month
    ano = ano or now.year

    orquestrador = OrquestradorETL(modo_mock=True)

    if programa:
        resultado = orquestrador.executar_pipeline(programa, mes, ano, dry_run=True)
        if resultado.sucesso:
            return {
                "programa": programa,
                "referencia": resultado.referencia,
                "registros": resultado.registros_validos,
                "status": "disponivel",
                "mensagem": f"Dados de {programa} ref {resultado.referencia}: {resultado.registros_validos} municipios.",
            }
        else:
            return {
                "programa": programa,
                "erro": resultado.erro,
                "status": "indisponivel",
            }

    # Listar todos
    programas = list(PROGRAMA_FONTE.keys())
    return {
        "programas_disponiveis": programas,
        "total_programas": len(programas),
        "fontes": [
            {"programa": p, "fonte": f.value}
            for p, f in PROGRAMA_FONTE.items()
        ],
        "mensagem": "Dados abertos de beneficios sociais. Escolha um programa para ver detalhes.",
    }
