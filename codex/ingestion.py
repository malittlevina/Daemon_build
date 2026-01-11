import os
import json
from typing import Any, Optional

from codex.vector_store import SimpleVectorStore

vector_store = SimpleVectorStore()

class CodexIngestion:
    def __init__(self):
        self.knowledge_base = {}

    def ingest_file(self, path):
        if path.endswith(".json"):
            with open(path, "r") as f:
                data = json.load(f)
                self.knowledge_base[path] = data
                print(f"[Codex] Loaded JSON file: {path}")
                try:
                    vector_store.add_texts([json.dumps(data)], metadatas=[{"source": path, "type": "json"}])
                except Exception:
                    pass
        elif path.endswith(".txt"):
            with open(path, "r") as f:
                text = f.read()
                self.knowledge_base[path] = text
                print(f"[Codex] Loaded text file: {path}")
                try:
                    vector_store.add_texts([text], metadatas=[{"source": path, "type": "txt"}])
                except Exception:
                    pass
        else:
            print(f"[Codex] Unsupported file type: {path}")

    def summarize(self, path):
        if path in self.knowledge_base:
            content = self.knowledge_base[path]
            if isinstance(content, dict):
                return {k: str(v)[:50] for k, v in content.items()}
            return content[:250]
        else:
            return "[Codex] No data available for that path."

def ingest_documents(folder_path):
    ingestor = CodexIngestion()
    for file in os.listdir(folder_path):
        ingestor.ingest_file(os.path.join(folder_path, file))

def ingest_observation(content):
    """
    Simulates ingestion of external content into the Codex system.
    Logs or processes content for knowledge storage or symbolic study.
    """
    print(f"[Codex] Ingested content: {content}")
    try:
        vector_store.add_texts([json.dumps(content) if not isinstance(content, str) else content], metadatas=[{"source": "observation"}])
    except Exception:
        pass
    return f"Codex acknowledged: {content}"


def ingest_web_or_pdf(source: str) -> str:
    """
    Best-effort ingestion helper for ScrollEngine.
    - If source looks like a URL: fetch and return cleaned text
    - If it's a local PDF path: extract text
    """
    src = (source or "").strip()
    if not src:
        return "[Codex] No source provided."

    if src.lower().startswith(("http://", "https://")):
        try:
            from codex.web_loader import fetch_and_clean_webpage
            text = fetch_and_clean_webpage(src)
            ingest_observation({"type": "web", "source": src, "text": text[:2000]})
            return f"[Codex] Ingested webpage: {src}"
        except Exception as e:
            return f"[Codex] Web ingest failed: {e}"

    if src.lower().endswith(".pdf"):
        try:
            from codex.pdf_loader import extract_text_from_pdf
            text = extract_text_from_pdf(src)
            ingest_observation({"type": "pdf", "source": src, "text": text[:2000]})
            return f"[Codex] Ingested pdf: {src}"
        except Exception as e:
            return f"[Codex] PDF ingest failed: {e}"

    return f"[Codex] Unsupported source for ingest: {src}"
