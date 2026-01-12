# codex/__init__.py
"""
Codex - Knowledge Base
======================
Knowledge storage and retrieval system.
"""

from .ingestion import CodexIngestion, ingest_documents, ingest_observation

__all__ = [
    'CodexIngestion',
    'ingest_documents',
    'ingest_observation',
]
