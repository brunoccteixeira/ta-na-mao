"""
Brasil API MCP Wrapper.

Wrapper para o MCP da Brasil API que fornece acesso a dados
brasileiros como CEP, CNPJ, DDD, bancos e feriados.

Referencia: https://github.com/mauricio-cantu/brasil-api-mcp
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog

from .base import MCPClient, MCPWrapper

logger = structlog.get_logger(__name__)


@dataclass
class EnderecoResult:
    """Resultado de busca de endereco por CEP."""

    cep: str
    logradouro: str
    complemento: str
    bairro: str
    cidade: str
    estado: str
    ibge: Optional[str] = None
    ddd: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnderecoResult":
        """Cria a partir de dicionario."""
        return cls(
            cep=data.get("cep", ""),
            logradouro=data.get("street", data.get("logradouro", "")),
            complemento=data.get("complemento", ""),
            bairro=data.get("neighborhood", data.get("bairro", "")),
            cidade=data.get("city", data.get("localidade", "")),
            estado=data.get("state", data.get("uf", "")),
            ibge=data.get("ibge"),
            ddd=data.get("ddd"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "cep": self.cep,
            "logradouro": self.logradouro,
            "complemento": self.complemento,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado,
            "ibge": self.ibge,
            "ddd": self.ddd,
        }

    def formato_completo(self) -> str:
        """Retorna endereco formatado."""
        partes = [self.logradouro]
        if self.bairro:
            partes.append(self.bairro)
        partes.append(f"{self.cidade}/{self.estado}")
        partes.append(f"CEP: {self.cep}")
        return ", ".join(partes)


@dataclass
class BancoResult:
    """Informacoes de um banco brasileiro."""

    ispb: str
    nome: str
    codigo: Optional[int] = None
    nome_completo: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BancoResult":
        """Cria a partir de dicionario."""
        return cls(
            ispb=data.get("ispb", ""),
            nome=data.get("name", data.get("nome", "")),
            codigo=data.get("code", data.get("codigo")),
            nome_completo=data.get("fullName", data.get("nome_completo")),
        )


@dataclass
class FeriadoResult:
    """Informacoes de um feriado."""

    data: str
    nome: str
    tipo: str  # national, state, municipal

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeriadoResult":
        """Cria a partir de dicionario."""
        return cls(
            data=data.get("date", ""),
            nome=data.get("name", ""),
            tipo=data.get("type", "national"),
        )


@dataclass
class DDDResult:
    """Informacoes de um DDD."""

    ddd: str
    estado: str
    cidades: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DDDResult":
        """Cria a partir de dicionario."""
        return cls(
            ddd=str(data.get("ddd", "")),
            estado=data.get("state", ""),
            cidades=data.get("cities", []),
        )


class BrasilAPIMCP(MCPWrapper):
    """
    Wrapper para Brasil API MCP.

    Fornece metodos tipados para acessar:
    - CEP (enderecamento)
    - CNPJ (empresas)
    - DDD (telefonia)
    - Bancos
    - Feriados

    Exemplo:
        ```python
        brasil_api = BrasilAPIMCP(client)
        endereco = await brasil_api.buscar_cep("01310100")
        print(endereco.cidade)  # "Sao Paulo"
        ```
    """

    SERVER_NAME = "brasil-api"

    @property
    def server_name(self) -> str:
        return self.SERVER_NAME

    async def health_check(self) -> bool:
        """Verifica se o MCP esta funcionando."""
        try:
            # Tenta buscar um CEP conhecido
            result = await self.buscar_cep("01310100")
            return result is not None
        except Exception:
            return False

    # =========================================================================
    # CEP
    # =========================================================================

    async def buscar_cep(self, cep: str) -> Optional[EnderecoResult]:
        """
        Busca endereco por CEP.

        Args:
            cep: CEP (com ou sem formatacao)

        Returns:
            EnderecoResult ou None se nao encontrado

        Exemplo:
            >>> await brasil_api.buscar_cep("01310-100")
            EnderecoResult(cidade="Sao Paulo", ...)
        """
        # Normaliza CEP (remove caracteres nao numericos)
        cep_limpo = re.sub(r"\D", "", cep)

        if len(cep_limpo) != 8:
            logger.warning("cep_invalido", cep=cep)
            return None

        result = await self.call("cep-lookup", cep=cep_limpo)

        if not result.success:
            logger.warning("cep_nao_encontrado", cep=cep, error=result.error)
            return None

        return EnderecoResult.from_dict(result.data)

    async def validar_cep(self, cep: str) -> bool:
        """
        Valida se um CEP existe.

        Args:
            cep: CEP a validar

        Returns:
            bool: True se CEP valido
        """
        endereco = await self.buscar_cep(cep)
        return endereco is not None

    # =========================================================================
    # CNPJ
    # =========================================================================

    async def buscar_cnpj(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados publicos de empresa por CNPJ.

        Args:
            cnpj: CNPJ (com ou sem formatacao)

        Returns:
            Dict com dados da empresa ou None

        Exemplo:
            >>> await brasil_api.buscar_cnpj("00.000.000/0001-91")
            {"razao_social": "...", "situacao": "ATIVA", ...}
        """
        # Normaliza CNPJ
        cnpj_limpo = re.sub(r"\D", "", cnpj)

        if len(cnpj_limpo) != 14:
            logger.warning("cnpj_invalido", cnpj=cnpj)
            return None

        result = await self.call("cnpj-lookup", cnpj=cnpj_limpo)

        if not result.success:
            logger.warning("cnpj_nao_encontrado", cnpj=cnpj, error=result.error)
            return None

        return result.data

    async def verificar_farmacia_credenciada(self, cnpj: str) -> bool:
        """
        Verifica se farmacia esta ativa (base para verificar credenciamento).

        Args:
            cnpj: CNPJ da farmacia

        Returns:
            bool: True se empresa ativa

        Nota:
            Esta funcao verifica apenas se a empresa esta ativa.
            A verificacao de credenciamento no Farmacia Popular
            requer consulta adicional ao sistema do MS.
        """
        dados = await self.buscar_cnpj(cnpj)
        if not dados:
            return False

        situacao = dados.get("descricao_situacao_cadastral", "").upper()
        return situacao == "ATIVA"

    # =========================================================================
    # DDD
    # =========================================================================

    async def buscar_ddd(self, ddd: str) -> Optional[DDDResult]:
        """
        Busca informacoes por DDD.

        Args:
            ddd: Codigo DDD (ex: "11", "21")

        Returns:
            DDDResult com estado e cidades

        Exemplo:
            >>> await brasil_api.buscar_ddd("11")
            DDDResult(estado="SP", cidades=["Sao Paulo", ...])
        """
        ddd_limpo = re.sub(r"\D", "", ddd)

        if len(ddd_limpo) != 2:
            logger.warning("ddd_invalido", ddd=ddd)
            return None

        result = await self.call("ddd-lookup", ddd=ddd_limpo)

        if not result.success:
            return None

        return DDDResult.from_dict(result.data)

    async def identificar_regiao_por_telefone(self, telefone: str) -> Optional[str]:
        """
        Identifica regiao pelo numero de telefone.

        Args:
            telefone: Numero de telefone com DDD

        Returns:
            UF ou None

        Exemplo:
            >>> await brasil_api.identificar_regiao_por_telefone("11999999999")
            "SP"
        """
        telefone_limpo = re.sub(r"\D", "", telefone)

        # Remove codigo do pais se presente
        if telefone_limpo.startswith("55"):
            telefone_limpo = telefone_limpo[2:]

        if len(telefone_limpo) < 10:
            return None

        ddd = telefone_limpo[:2]
        info_ddd = await self.buscar_ddd(ddd)

        return info_ddd.estado if info_ddd else None

    # =========================================================================
    # Bancos
    # =========================================================================

    async def listar_bancos(self) -> List[BancoResult]:
        """
        Lista todos os bancos brasileiros.

        Returns:
            Lista de BancoResult

        Exemplo:
            >>> bancos = await brasil_api.listar_bancos()
            >>> for b in bancos[:3]:
            ...     print(f"{b.codigo}: {b.nome}")
            1: Banco do Brasil
            33: Santander
            104: Caixa Economica
        """
        result = await self.call("get-banks")

        if not result.success:
            return []

        bancos = result.data if isinstance(result.data, list) else []
        return [BancoResult.from_dict(b) for b in bancos]

    async def buscar_banco(self, codigo: int) -> Optional[BancoResult]:
        """
        Busca banco por codigo.

        Args:
            codigo: Codigo do banco (ex: 104 para Caixa)

        Returns:
            BancoResult ou None
        """
        bancos = await self.listar_bancos()
        for banco in bancos:
            if banco.codigo == codigo:
                return banco
        return None

    # =========================================================================
    # Feriados
    # =========================================================================

    async def listar_feriados(self, ano: int) -> List[FeriadoResult]:
        """
        Lista feriados nacionais de um ano.

        Args:
            ano: Ano (ex: 2026)

        Returns:
            Lista de FeriadoResult

        Exemplo:
            >>> feriados = await brasil_api.listar_feriados(2026)
            >>> for f in feriados[:3]:
            ...     print(f"{f.data}: {f.nome}")
            2026-01-01: Confraternizacao Universal
            2026-02-16: Carnaval
            2026-02-17: Carnaval
        """
        result = await self.call("get-holidays", year=ano)

        if not result.success:
            return []

        feriados = result.data if isinstance(result.data, list) else []
        return [FeriadoResult.from_dict(f) for f in feriados]

    async def verificar_feriado(self, data: str) -> Optional[FeriadoResult]:
        """
        Verifica se uma data e feriado.

        Args:
            data: Data no formato YYYY-MM-DD

        Returns:
            FeriadoResult se for feriado, None caso contrario
        """
        ano = int(data[:4])
        feriados = await self.listar_feriados(ano)

        for feriado in feriados:
            if feriado.data == data:
                return feriado

        return None

    async def proximo_dia_util(self, data: str) -> str:
        """
        Retorna proximo dia util a partir de uma data.

        Args:
            data: Data no formato YYYY-MM-DD

        Returns:
            Proxima data util

        Nota:
            Considera apenas feriados nacionais.
            Nao considera feriados estaduais/municipais.
        """
        from datetime import datetime, timedelta

        dt = datetime.strptime(data, "%Y-%m-%d")
        ano = dt.year
        feriados = await self.listar_feriados(ano)
        datas_feriados = {f.data for f in feriados}

        while True:
            # Verifica se e fim de semana (5=sab, 6=dom)
            if dt.weekday() >= 5:
                dt += timedelta(days=1)
                continue

            # Verifica se e feriado
            data_str = dt.strftime("%Y-%m-%d")
            if data_str in datas_feriados:
                dt += timedelta(days=1)
                continue

            return data_str


# Factory function
def create_brasil_api_wrapper(client: MCPClient) -> BrasilAPIMCP:
    """
    Cria wrapper Brasil API.

    Args:
        client: Cliente MCP configurado

    Returns:
        BrasilAPIMCP: Wrapper configurado
    """
    return BrasilAPIMCP(client)
