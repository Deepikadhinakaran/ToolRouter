"""Document search (RAG) tool.

Uses Chroma + OpenAI embeddings when OPENAI_API_KEY is set. Otherwise falls
back to a dependency-free keyword-overlap retriever so the project runs
end-to-end without any API key.
"""
import os
import re
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "documents"

TOOL_META = {
    "name": "document_search",
    "description": "Search internal policy/project documents for an answer (RAG).",
    "capabilities": [
        "document", "policy", "rag", "knowledge-base",
        "leave", "sick", "vacation", "hours", "working", "hr",
        "benefits", "company", "remote", "expense", "training",
    ],
    "min_role": "employee",
    "risk": "low",
    "cost": 0.0005,
    "avg_latency_ms": 120,
}

_STOPWORDS = {
    "what", "is", "the", "a", "an", "of", "for", "to", "on", "in", "and",
    "are", "how", "do", "does", "can", "i", "my", "please", "tell", "me",
}


def _load_documents() -> list[tuple[str, str]]:
    docs = []
    if DOCS_DIR.exists():
        for path in sorted(DOCS_DIR.glob("*.txt")):
            docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs


def _keyword_retrieve(query: str, k: int = 1) -> list[dict]:
    tokens = {t for t in re.findall(r"[a-z]+", query.lower()) if t not in _STOPWORDS}
    scored = []
    for name, text in _load_documents():
        text_tokens = set(re.findall(r"[a-z]+", text.lower()))
        overlap = len(tokens & text_tokens)
        if overlap:
            scored.append((overlap, name, text))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"source": name, "chunk": text[:600]} for _, name, text in scored[:k]]


def _embedding_retrieve(query: str, k: int = 1) -> list[dict]:
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document

    docs = [Document(page_content=text, metadata={"source": name}) for name, text in _load_documents()]
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    vectordb = Chroma.from_documents(chunks, OpenAIEmbeddings())
    results = vectordb.similarity_search(query, k=k)
    return [{"source": r.metadata.get("source", "unknown"), "chunk": r.page_content} for r in results]


def run(query: str) -> dict:
    if not _load_documents():
        return {"status": "error", "result": "No documents indexed yet."}

    try:
        if os.getenv("OPENAI_API_KEY"):
            hits = _embedding_retrieve(query)
        else:
            hits = _keyword_retrieve(query)
    except Exception:  # noqa: BLE001 — embeddings unavailable, fall back
        hits = _keyword_retrieve(query)

    if not hits:
        return {"status": "success", "result": "No relevant document content found."}
    return {"status": "success", "result": hits}
