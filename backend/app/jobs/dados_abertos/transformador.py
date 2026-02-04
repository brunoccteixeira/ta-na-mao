"""
Transformador de dados abertos.

Agrega dados brutos por municipio, normaliza campos e valida schemas.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .extrator import ResultadoExtracao

logger = logging.getLogger(__name__)


@dataclass
class RegistroTransformado:
    """Registro normalizado e pronto para carga."""
    municipio_ibge: str
    municipio_nome: str
    uf: str
    programa: str
    referencia: str
    beneficiarios: int
    valor_total: float
    transformado_em: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ResultadoTransformacao:
    """Resultado da transformacao."""
    programa: str
    referencia: str
    registros: List[RegistroTransformado] = field(default_factory=list)
    total_validos: int = 0
    total_invalidos: int = 0
    erros_validacao: List[Dict[str, Any]] = field(default_factory=list)
    sucesso: bool = True


# Schemas esperados por programa
_CAMPOS_OBRIGATORIOS = [
    "municipio_ibge", "municipio_nome", "uf",
    "programa", "referencia", "beneficiarios", "valor_total",
]


class TransformadorDados:
    """Transforma e valida dados extraidos."""

    def transformar(self, extracao: ResultadoExtracao) -> ResultadoTransformacao:
        """Transforma dados brutos em formato normalizado.

        Args:
            extracao: Resultado da extracao com registros brutos

        Returns:
            ResultadoTransformacao com registros validados
        """
        if not extracao.sucesso:
            return ResultadoTransformacao(
                programa=extracao.programa,
                referencia=extracao.referencia,
                sucesso=False,
            )

        logger.info(
            f"Transformando {extracao.total_registros} registros "
            f"de {extracao.programa} ref {extracao.referencia}"
        )

        resultado = ResultadoTransformacao(
            programa=extracao.programa,
            referencia=extracao.referencia,
        )

        # Agregar por municipio (caso haja duplicatas)
        agregados = self._agregar_por_municipio(extracao.registros)

        # Validar e normalizar cada registro
        for registro in agregados:
            erros = self._validar_registro(registro)
            if erros:
                resultado.total_invalidos += 1
                resultado.erros_validacao.append({
                    "municipio_ibge": registro.get("municipio_ibge", "?"),
                    "erros": erros,
                })
                continue

            resultado.registros.append(RegistroTransformado(
                municipio_ibge=str(registro["municipio_ibge"]).strip(),
                municipio_nome=str(registro["municipio_nome"]).strip(),
                uf=str(registro["uf"]).strip().upper(),
                programa=str(registro["programa"]).strip().upper(),
                referencia=str(registro["referencia"]).strip(),
                beneficiarios=int(registro["beneficiarios"]),
                valor_total=float(registro["valor_total"]),
            ))
            resultado.total_validos += 1

        logger.info(
            f"Transformacao concluida: {resultado.total_validos} validos, "
            f"{resultado.total_invalidos} invalidos"
        )

        return resultado

    def _agregar_por_municipio(
        self, registros: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Agrega registros por municipio (soma beneficiarios e valores)."""
        agrupados: Dict[str, Dict[str, Any]] = {}

        for reg in registros:
            chave = f"{reg.get('municipio_ibge')}_{reg.get('programa')}_{reg.get('referencia')}"

            if chave not in agrupados:
                agrupados[chave] = dict(reg)
            else:
                agrupados[chave]["beneficiarios"] = (
                    agrupados[chave].get("beneficiarios", 0)
                    + reg.get("beneficiarios", 0)
                )
                agrupados[chave]["valor_total"] = (
                    agrupados[chave].get("valor_total", 0)
                    + reg.get("valor_total", 0)
                )

        return list(agrupados.values())

    def _validar_registro(self, registro: Dict[str, Any]) -> List[str]:
        """Valida um registro contra o schema esperado."""
        erros = []

        # Campos obrigatorios
        for campo in _CAMPOS_OBRIGATORIOS:
            if campo not in registro or registro[campo] is None:
                erros.append(f"Campo obrigatorio ausente: {campo}")

        # Validacoes de tipo/valor
        if "municipio_ibge" in registro:
            ibge = str(registro["municipio_ibge"])
            if not ibge.isdigit() or len(ibge) != 7:
                erros.append(f"municipio_ibge invalido: {ibge} (esperado 7 digitos)")

        if "uf" in registro:
            uf = str(registro["uf"]).upper()
            if len(uf) != 2:
                erros.append(f"UF invalida: {uf}")

        if "beneficiarios" in registro:
            try:
                ben = int(registro["beneficiarios"])
                if ben < 0:
                    erros.append(f"beneficiarios negativo: {ben}")
            except (ValueError, TypeError):
                erros.append(f"beneficiarios nao numerico: {registro['beneficiarios']}")

        if "valor_total" in registro:
            try:
                val = float(registro["valor_total"])
                if val < 0:
                    erros.append(f"valor_total negativo: {val}")
            except (ValueError, TypeError):
                erros.append(f"valor_total nao numerico: {registro['valor_total']}")

        if "referencia" in registro:
            ref = str(registro["referencia"])
            if len(ref) != 7 or ref[4] != "-":
                erros.append(f"referencia formato invalido: {ref} (esperado YYYY-MM)")

        return erros
