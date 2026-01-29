"""
MCP (Model Context Protocol) wrappers para o Ta na Mao.

Este modulo fornece wrappers Python para interagir com MCPs externos,
permitindo integracao padronizada com servicos como Brasil API,
Google Maps, PDF/OCR e outros.
"""

from .base import (
    MCPClient,
    MCPManager,
    MCPError,
    MCPConnectionError,
    MCPToolError,
    MCPTimeoutError,
    mcp_manager,
    init_mcp,
)
from .brasil_api import BrasilAPIMCP
from .google_maps import GoogleMapsMCP
from .pdf_ocr import PDFOcrMCP

__all__ = [
    # Base
    "MCPClient",
    "MCPManager",
    "MCPError",
    "MCPConnectionError",
    "MCPToolError",
    "MCPTimeoutError",
    "mcp_manager",
    "init_mcp",
    # Wrappers
    "BrasilAPIMCP",
    "GoogleMapsMCP",
    "PDFOcrMCP",
]
