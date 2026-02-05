"""Tá na Mão Agent - Assistente para benefícios sociais.

Este módulo implementa um agente conversacional usando Google ADK + Gemini Flash
para ajudar cidadãos brasileiros a acessar benefícios sociais.

Note: root_agent is imported lazily to allow tools to be imported without
requiring google.generativeai to be installed (useful for testing).
"""


def __getattr__(name: str):
    """Lazy import of root_agent to avoid dependency on google.generativeai at import time."""
    if name == "root_agent":
        from app.agent.agent import root_agent
        return root_agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["root_agent"]
