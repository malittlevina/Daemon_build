# interop/__init__.py
"""
Interop Layer - External integrations and API interfaces

Provides:
- LLM provider abstraction
- Tool use framework
- REST API server
- Webhook handlers
"""

from interop.llm_providers import LLMProvider, get_provider
from interop.tool_framework import ToolRegistry, Tool
from interop.api_server import APIServer

__all__ = ["LLMProvider", "get_provider", "ToolRegistry", "Tool", "APIServer"]
