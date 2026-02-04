"""
Carregador de dados transformados.

Faz upsert no banco de dados (ou salva em arquivo para dev/test).
"""

import logging
import json
from typing import Dict, Any, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

from .transformador import ResultadoTransformacao, RegistroTransformado

logger = logging.getLogger(__name__)


@dataclass
class ResultadoCarga:
    """Resultado da carga de dados."""
    programa: str
    referencia: str
    inseridos: int = 0
    atualizados: int = 0
    erros: int = 0
    sucesso: bool = True
    modo: str = "arquivo"  # "arquivo" ou "banco"
    carregado_em: str = field(default_factory=lambda: datetime.now().isoformat())


class CarregadorDados:
    """Carrega dados transformados no destino.

    Em modo mock/dev: salva em arquivo JSON.
    Em producao: faz upsert na tabela BeneficiaryData via SQLAlchemy.
    """

    def __init__(self, modo_mock: bool = True, diretorio_saida: str = "/tmp/dados_abertos"):
        """Inicializa carregador.

        Args:
            modo_mock: Se True, salva em arquivo. Se False, usa banco.
            diretorio_saida: Diretorio para salvar arquivos (modo mock).
        """
        self.modo_mock = modo_mock
        self.diretorio_saida = Path(diretorio_saida)

    def carregar(self, transformacao: ResultadoTransformacao) -> ResultadoCarga:
        """Carrega dados transformados no destino.

        Args:
            transformacao: Resultado da transformacao com registros validados

        Returns:
            ResultadoCarga com estatisticas da operacao
        """
        if not transformacao.sucesso:
            return ResultadoCarga(
                programa=transformacao.programa,
                referencia=transformacao.referencia,
                sucesso=False,
            )

        if not transformacao.registros:
            logger.warning(f"Nenhum registro para carregar: {transformacao.programa}")
            return ResultadoCarga(
                programa=transformacao.programa,
                referencia=transformacao.referencia,
                sucesso=True,
            )

        logger.info(
            f"Carregando {transformacao.total_validos} registros "
            f"de {transformacao.programa} ref {transformacao.referencia}"
        )

        if self.modo_mock:
            return self._carregar_arquivo(transformacao)

        return self._carregar_banco(transformacao)

    def _carregar_arquivo(self, transformacao: ResultadoTransformacao) -> ResultadoCarga:
        """Salva dados em arquivo JSON (modo dev/test)."""
        self.diretorio_saida.mkdir(parents=True, exist_ok=True)

        nome_arquivo = (
            f"{transformacao.programa}_{transformacao.referencia}.json"
        )
        caminho = self.diretorio_saida / nome_arquivo

        dados = [asdict(r) for r in transformacao.registros]

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)

            logger.info(f"Dados salvos em {caminho}")
            return ResultadoCarga(
                programa=transformacao.programa,
                referencia=transformacao.referencia,
                inseridos=len(dados),
                sucesso=True,
                modo="arquivo",
            )
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {e}")
            return ResultadoCarga(
                programa=transformacao.programa,
                referencia=transformacao.referencia,
                erros=1,
                sucesso=False,
                modo="arquivo",
            )

    def _carregar_banco(self, transformacao: ResultadoTransformacao) -> ResultadoCarga:
        """Faz upsert no banco de dados.

        TODO: Implementar quando modelo BeneficiaryData estiver pronto.
        Usa INSERT ON CONFLICT UPDATE por (municipio_ibge, programa, referencia).
        """
        logger.warning("Carga em banco nao implementada. Usando modo arquivo.")
        return self._carregar_arquivo(transformacao)
