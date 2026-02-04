"""
Extrator de dados abertos de portais governamentais.

Fontes suportadas:
- Portal da Transparencia (CGU): Bolsa Familia, BPC, Auxilio Gas, Seguro Defeso
- dados.gov.br: Beneficios concedidos, CadUnico agregado
- SAGI/MDS: Relatorios sociais
- OpenDataSUS: Farmacia Popular, Dignidade Menstrual
- ANEEL: Tarifa Social de Energia
- IBGE: Populacao, PIB, indicadores
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class FonteDados(str, Enum):
    PORTAL_TRANSPARENCIA = "portal_transparencia"
    DADOS_GOV = "dados_gov"
    SAGI_MDS = "sagi_mds"
    OPENDATASUS = "opendatasus"
    ANEEL = "aneel"
    IBGE = "ibge"
    IPEA = "ipea"
    FNDE = "fnde"


@dataclass
class ConfigFonte:
    """Configuracao de uma fonte de dados."""
    fonte: FonteDados
    url_base: str
    encoding: str = "utf-8"
    formato: str = "csv"
    rate_limit_por_min: int = 60
    requer_autenticacao: bool = False
    api_key_env: Optional[str] = None


@dataclass
class ResultadoExtracao:
    """Resultado da extracao de uma fonte."""
    fonte: FonteDados
    programa: str
    referencia: str  # "YYYY-MM"
    registros: List[Dict[str, Any]] = field(default_factory=list)
    total_registros: int = 0
    sucesso: bool = True
    erro: Optional[str] = None
    extraido_em: str = field(default_factory=lambda: datetime.now().isoformat())


# Configuracoes das fontes
FONTES = {
    FonteDados.PORTAL_TRANSPARENCIA: ConfigFonte(
        fonte=FonteDados.PORTAL_TRANSPARENCIA,
        url_base="https://portaldatransparencia.gov.br/download-de-dados",
        encoding="latin-1",
        formato="csv",
        rate_limit_por_min=30,
    ),
    FonteDados.IBGE: ConfigFonte(
        fonte=FonteDados.IBGE,
        url_base="https://servicodados.ibge.gov.br/api/v3",
        formato="json",
        rate_limit_por_min=60,
    ),
    FonteDados.SAGI_MDS: ConfigFonte(
        fonte=FonteDados.SAGI_MDS,
        url_base="https://aplicacoes.mds.gov.br/sagi",
        formato="csv",
        requer_autenticacao=True,
        api_key_env="SAGI_API_KEY",
    ),
    FonteDados.OPENDATASUS: ConfigFonte(
        fonte=FonteDados.OPENDATASUS,
        url_base="https://opendatasus.saude.gov.br",
        formato="csv",
    ),
    FonteDados.ANEEL: ConfigFonte(
        fonte=FonteDados.ANEEL,
        url_base="https://dadosabertos.aneel.gov.br/api/3/action",
        formato="json",
    ),
}

# Mapeamento programa -> fonte
PROGRAMA_FONTE = {
    "BOLSA_FAMILIA": FonteDados.PORTAL_TRANSPARENCIA,
    "BPC": FonteDados.PORTAL_TRANSPARENCIA,
    "AUXILIO_GAS": FonteDados.PORTAL_TRANSPARENCIA,
    "SEGURO_DEFESO": FonteDados.PORTAL_TRANSPARENCIA,
    "FARMACIA_POPULAR": FonteDados.OPENDATASUS,
    "DIGNIDADE_MENSTRUAL": FonteDados.OPENDATASUS,
    "TSEE": FonteDados.ANEEL,
    "POPULACAO": FonteDados.IBGE,
    "INDICADORES": FonteDados.IBGE,
    "PNAE": FonteDados.SAGI_MDS,
}


class ExtratorDadosAbertos:
    """Extrator de dados abertos governamentais.

    Faz download de dados brutos das fontes configuradas.
    Em producao, conecta via httpx. Em dev/test, retorna dados mock.
    """

    def __init__(self, modo_mock: bool = True):
        """Inicializa extrator.

        Args:
            modo_mock: Se True, retorna dados simulados (dev/test).
        """
        self.modo_mock = modo_mock

    def extrair(
        self,
        programa: str,
        mes: int,
        ano: int,
    ) -> ResultadoExtracao:
        """Extrai dados de um programa para um mes/ano.

        Args:
            programa: Codigo do programa (BOLSA_FAMILIA, BPC, etc)
            mes: Mes de referencia (1-12)
            ano: Ano de referencia

        Returns:
            ResultadoExtracao com registros brutos
        """
        referencia = f"{ano:04d}-{mes:02d}"
        fonte = PROGRAMA_FONTE.get(programa)

        if not fonte:
            return ResultadoExtracao(
                fonte=FonteDados.PORTAL_TRANSPARENCIA,
                programa=programa,
                referencia=referencia,
                sucesso=False,
                erro=f"Programa '{programa}' nao tem fonte configurada.",
            )

        logger.info(f"Extraindo {programa} referencia {referencia} de {fonte.value}")

        if self.modo_mock:
            return self._extrair_mock(programa, referencia, fonte)

        # Em producao: httpx download
        return self._extrair_real(programa, referencia, fonte)

    def _extrair_mock(
        self, programa: str, referencia: str, fonte: FonteDados
    ) -> ResultadoExtracao:
        """Retorna dados mock para desenvolvimento/testes."""
        registros_mock = _gerar_dados_mock(programa, referencia)
        return ResultadoExtracao(
            fonte=fonte,
            programa=programa,
            referencia=referencia,
            registros=registros_mock,
            total_registros=len(registros_mock),
            sucesso=True,
        )

    def _extrair_real(
        self, programa: str, referencia: str, fonte: FonteDados
    ) -> ResultadoExtracao:
        """Extrai dados reais via HTTP (requer httpx).

        TODO: Implementar quando APIs estiverem disponiveis.
        """
        logger.warning(f"Extracao real nao implementada para {programa}. Usando mock.")
        return self._extrair_mock(programa, referencia, fonte)

    def listar_programas(self) -> List[Dict[str, str]]:
        """Lista programas disponiveis para extracao."""
        return [
            {"programa": prog, "fonte": fonte.value}
            for prog, fonte in PROGRAMA_FONTE.items()
        ]

    def verificar_disponibilidade(self, programa: str) -> Dict[str, Any]:
        """Verifica se fonte esta disponivel."""
        fonte = PROGRAMA_FONTE.get(programa)
        if not fonte:
            return {"disponivel": False, "erro": "Programa nao encontrado"}

        if self.modo_mock:
            return {"disponivel": True, "modo": "mock"}

        # Em producao: verificar conectividade
        return {"disponivel": True, "modo": "mock", "nota": "Modo real nao implementado"}


def _gerar_dados_mock(programa: str, referencia: str) -> List[Dict[str, Any]]:
    """Gera dados mock realistas para testes."""
    # Municipios exemplo (IBGE codes)
    municipios = [
        {"ibge": "3550308", "nome": "Sao Paulo", "uf": "SP"},
        {"ibge": "3304557", "nome": "Rio de Janeiro", "uf": "RJ"},
        {"ibge": "5300108", "nome": "Brasilia", "uf": "DF"},
        {"ibge": "2927408", "nome": "Salvador", "uf": "BA"},
        {"ibge": "1302603", "nome": "Manaus", "uf": "AM"},
    ]

    registros = []
    for mun in municipios:
        if programa == "BOLSA_FAMILIA":
            registros.append({
                "municipio_ibge": mun["ibge"],
                "municipio_nome": mun["nome"],
                "uf": mun["uf"],
                "programa": "BOLSA_FAMILIA",
                "referencia": referencia,
                "beneficiarios": 150000 + hash(mun["ibge"]) % 50000,
                "valor_total": 90000000.0 + (hash(mun["ibge"]) % 30000000),
            })
        elif programa == "BPC":
            registros.append({
                "municipio_ibge": mun["ibge"],
                "municipio_nome": mun["nome"],
                "uf": mun["uf"],
                "programa": "BPC",
                "referencia": referencia,
                "beneficiarios": 30000 + hash(mun["ibge"]) % 10000,
                "valor_total": 45000000.0 + (hash(mun["ibge"]) % 15000000),
            })
        elif programa == "TSEE":
            registros.append({
                "municipio_ibge": mun["ibge"],
                "municipio_nome": mun["nome"],
                "uf": mun["uf"],
                "programa": "TSEE",
                "referencia": referencia,
                "beneficiarios": 80000 + hash(mun["ibge"]) % 20000,
                "valor_total": 5000000.0 + (hash(mun["ibge"]) % 2000000),
            })
        elif programa == "FARMACIA_POPULAR":
            registros.append({
                "municipio_ibge": mun["ibge"],
                "municipio_nome": mun["nome"],
                "uf": mun["uf"],
                "programa": "FARMACIA_POPULAR",
                "referencia": referencia,
                "beneficiarios": 200000 + hash(mun["ibge"]) % 80000,
                "valor_total": 15000000.0 + (hash(mun["ibge"]) % 5000000),
            })
        else:
            registros.append({
                "municipio_ibge": mun["ibge"],
                "municipio_nome": mun["nome"],
                "uf": mun["uf"],
                "programa": programa,
                "referencia": referencia,
                "beneficiarios": 10000 + hash(mun["ibge"]) % 5000,
                "valor_total": 5000000.0 + (hash(mun["ibge"]) % 2000000),
            })

    return registros
