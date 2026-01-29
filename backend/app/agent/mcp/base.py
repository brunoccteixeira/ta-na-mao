"""
MCP Client Base - Interface base para comunicacao com servidores MCP.

O Model Context Protocol (MCP) permite que agentes de IA se conectem
a ferramentas externas de forma padronizada via JSON-RPC sobre stdio.
"""

import asyncio
import json
import os
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type

import structlog

logger = structlog.get_logger(__name__)


class MCPError(Exception):
    """Erro base para operacoes MCP."""

    pass


class MCPConnectionError(MCPError):
    """Erro de conexao com servidor MCP."""

    pass


class MCPToolError(MCPError):
    """Erro ao executar tool MCP."""

    pass


class MCPTimeoutError(MCPError):
    """Timeout na comunicacao com MCP."""

    pass


class MCPServerType(str, Enum):
    """Tipos de servidor MCP suportados."""

    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


@dataclass
class MCPServerConfig:
    """Configuracao de um servidor MCP."""

    name: str
    server_type: MCPServerType
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    timeout: int = 30000  # ms
    enabled: bool = True

    @classmethod
    def from_dict(cls, name: str, config: Dict[str, Any]) -> "MCPServerConfig":
        """Cria configuracao a partir de dicionario."""
        return cls(
            name=name,
            server_type=MCPServerType(config.get("type", "stdio")),
            command=config.get("command", ""),
            args=config.get("args", []),
            env=config.get("env", {}),
            description=config.get("description", ""),
            timeout=config.get("timeout", 30000),
            enabled=config.get("enabled", True),
        )


@dataclass
class MCPToolResult:
    """Resultado de uma chamada de tool MCP."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    tool_name: str = ""
    server_name: str = ""
    execution_time_ms: float = 0

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "tool_name": self.tool_name,
            "server_name": self.server_name,
            "execution_time_ms": self.execution_time_ms,
        }


class MCPClient:
    """
    Cliente MCP para comunicacao com servidores via stdio.

    Implementa o protocolo JSON-RPC 2.0 sobre stdio para
    comunicacao com processos MCP externos.
    """

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self._process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._lock = asyncio.Lock()
        self._started = False

    @property
    def is_running(self) -> bool:
        """Verifica se o processo esta em execucao."""
        return self._process is not None and self._process.poll() is None

    async def start(self) -> bool:
        """
        Inicia o servidor MCP.

        Returns:
            bool: True se iniciou com sucesso
        """
        if self.is_running:
            return True

        try:
            # Resolve variaveis de ambiente
            env = os.environ.copy()
            for key, value in self.config.env.items():
                if value.startswith("${") and value.endswith("}"):
                    env_key = value[2:-1]
                    env[key] = os.environ.get(env_key, "")
                else:
                    env[key] = value

            # Monta comando
            cmd = [self.config.command] + self.config.args

            logger.info(
                "starting_mcp_server",
                server=self.config.name,
                command=cmd,
            )

            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
            )

            # Aguarda inicializacao
            await asyncio.sleep(0.5)

            if not self.is_running:
                stderr = self._process.stderr.read() if self._process.stderr else ""
                raise MCPConnectionError(
                    f"MCP server {self.config.name} failed to start: {stderr}"
                )

            self._started = True
            logger.info("mcp_server_started", server=self.config.name)
            return True

        except Exception as e:
            logger.error(
                "mcp_server_start_failed",
                server=self.config.name,
                error=str(e),
            )
            raise MCPConnectionError(f"Failed to start MCP {self.config.name}: {e}")

    async def stop(self) -> None:
        """Para o servidor MCP."""
        if self._process:
            logger.info("stopping_mcp_server", server=self.config.name)
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
            self._started = False

    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict:
        """
        Envia request JSON-RPC para o servidor.

        Args:
            method: Metodo a chamar
            params: Parametros do metodo

        Returns:
            Dict: Resposta do servidor
        """
        if not self.is_running:
            await self.start()

        async with self._lock:
            self._request_id += 1
            request = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": self._request_id,
            }

            try:
                # Envia request
                request_line = json.dumps(request) + "\n"
                self._process.stdin.write(request_line)
                self._process.stdin.flush()

                # Aguarda resposta com timeout
                response_line = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, self._process.stdout.readline
                    ),
                    timeout=self.config.timeout / 1000,
                )

                if not response_line:
                    raise MCPConnectionError("Empty response from MCP server")

                return json.loads(response_line)

            except asyncio.TimeoutError:
                raise MCPTimeoutError(
                    f"Timeout waiting for MCP response ({self.config.timeout}ms)"
                )
            except json.JSONDecodeError as e:
                raise MCPError(f"Invalid JSON response: {e}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista tools disponiveis no servidor.

        Returns:
            List[Dict]: Lista de tools com nome e descricao
        """
        response = await self._send_request("tools/list", {})

        if "error" in response:
            raise MCPToolError(response["error"].get("message", "Unknown error"))

        return response.get("result", {}).get("tools", [])

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> MCPToolResult:
        """
        Chama uma tool do servidor MCP.

        Args:
            tool_name: Nome da tool
            arguments: Argumentos para a tool

        Returns:
            MCPToolResult: Resultado da execucao
        """
        import time

        start_time = time.time()

        try:
            response = await self._send_request(
                "tools/call",
                {"name": tool_name, "arguments": arguments},
            )

            execution_time = (time.time() - start_time) * 1000

            if "error" in response:
                return MCPToolResult(
                    success=False,
                    error=response["error"].get("message", "Unknown error"),
                    tool_name=tool_name,
                    server_name=self.config.name,
                    execution_time_ms=execution_time,
                )

            result = response.get("result", {})

            return MCPToolResult(
                success=True,
                data=result.get("content", result),
                tool_name=tool_name,
                server_name=self.config.name,
                execution_time_ms=execution_time,
            )

        except MCPError as e:
            execution_time = (time.time() - start_time) * 1000
            return MCPToolResult(
                success=False,
                error=str(e),
                tool_name=tool_name,
                server_name=self.config.name,
                execution_time_ms=execution_time,
            )


class MCPWrapper(ABC):
    """
    Classe base para wrappers de MCP especificos.

    Cada MCP (Brasil API, Google Maps, etc.) deve implementar
    um wrapper que estende esta classe.
    """

    def __init__(self, client: MCPClient):
        self.client = client

    @property
    @abstractmethod
    def server_name(self) -> str:
        """Nome do servidor MCP."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifica se o MCP esta funcionando."""
        pass

    async def ensure_started(self) -> bool:
        """Garante que o cliente esta iniciado."""
        return await self.client.start()

    async def call(self, tool_name: str, **kwargs) -> MCPToolResult:
        """
        Wrapper para chamar tools.

        Args:
            tool_name: Nome da tool
            **kwargs: Argumentos da tool

        Returns:
            MCPToolResult: Resultado
        """
        await self.ensure_started()
        return await self.client.call_tool(tool_name, kwargs)


class MCPManager:
    """
    Gerenciador de conexoes MCP.

    Mantém pool de clientes MCP e gerencia ciclo de vida.
    """

    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}
        self._wrappers: Dict[str, MCPWrapper] = {}
        self._config: Dict[str, MCPServerConfig] = {}
        self._initialized = False

    def load_config(self, config_path: str = ".mcp.json") -> None:
        """
        Carrega configuracao de arquivo JSON.

        Args:
            config_path: Caminho para .mcp.json
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            servers = config.get("mcpServers", {})
            for name, server_config in servers.items():
                self._config[name] = MCPServerConfig.from_dict(name, server_config)

            logger.info(
                "mcp_config_loaded",
                config_path=config_path,
                servers=list(self._config.keys()),
            )
            self._initialized = True

        except FileNotFoundError:
            logger.warning("mcp_config_not_found", path=config_path)
        except json.JSONDecodeError as e:
            logger.error("mcp_config_invalid_json", path=config_path, error=str(e))

    def get_client(self, server_name: str) -> Optional[MCPClient]:
        """
        Obtem ou cria cliente para um servidor.

        Args:
            server_name: Nome do servidor

        Returns:
            MCPClient ou None se nao configurado
        """
        if server_name not in self._config:
            logger.warning("mcp_server_not_configured", server=server_name)
            return None

        if server_name not in self._clients:
            config = self._config[server_name]
            if config.enabled:
                self._clients[server_name] = MCPClient(config)

        return self._clients.get(server_name)

    def register_wrapper(
        self, server_name: str, wrapper_class: Type[MCPWrapper]
    ) -> Optional[MCPWrapper]:
        """
        Registra wrapper para um servidor.

        Args:
            server_name: Nome do servidor
            wrapper_class: Classe do wrapper

        Returns:
            Instancia do wrapper ou None
        """
        client = self.get_client(server_name)
        if client:
            wrapper = wrapper_class(client)
            self._wrappers[server_name] = wrapper
            return wrapper
        return None

    def get_wrapper(self, server_name: str) -> Optional[MCPWrapper]:
        """Obtem wrapper registrado."""
        return self._wrappers.get(server_name)

    async def start_all(self) -> Dict[str, bool]:
        """
        Inicia todos os servidores configurados.

        Returns:
            Dict mapeando servidor -> sucesso
        """
        results = {}
        for name, client in self._clients.items():
            try:
                results[name] = await client.start()
            except MCPError as e:
                logger.error("mcp_start_failed", server=name, error=str(e))
                results[name] = False
        return results

    async def stop_all(self) -> None:
        """Para todos os servidores."""
        for client in self._clients.values():
            await client.stop()

    async def health_check(self) -> Dict[str, bool]:
        """
        Verifica saude de todos os servidores.

        Returns:
            Dict mapeando servidor -> status
        """
        results = {}
        for name, wrapper in self._wrappers.items():
            try:
                results[name] = await wrapper.health_check()
            except Exception:
                results[name] = False
        return results


# Singleton global
mcp_manager = MCPManager()


def init_mcp(config_path: str = ".mcp.json") -> MCPManager:
    """
    Inicializa o gerenciador MCP global.

    Args:
        config_path: Caminho para arquivo de configuracao

    Returns:
        MCPManager: Instancia do gerenciador
    """
    mcp_manager.load_config(config_path)
    return mcp_manager
