import math
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_PATH = BASE_DIR / "data" / "rag_corpus.md"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z]{2,}", text.lower())


def _chunk_corpus(raw: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    for line in raw.splitlines():
        if line.startswith("## ") and current:
            chunks.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current).strip())
    return [c for c in chunks if c and not c.startswith("# ")]


def _tf(tokens: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    if not tokens:
        return out
    for token in tokens:
        out[token] = out.get(token, 0) + 1
    total = float(len(tokens))
    return {k: v / total for k, v in out.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a.keys()) | set(b.keys())
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def retrieve_context(query: str, top_k: int = 3) -> tuple[str, list[str]]:
    raw = CORPUS_PATH.read_text(encoding="utf-8") if CORPUS_PATH.exists() else ""
    chunks = _chunk_corpus(raw)
    if not chunks:
        return ("", [])

    q_vec = _tf(_tokenize(query))
    scored: list[tuple[float, str]] = []
    for chunk in chunks:
        score = _cosine(q_vec, _tf(_tokenize(chunk)))
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [chunk for score, chunk in scored[:top_k] if score > 0]
    if not selected:
        selected = chunks[:1]
    sources = [f"KB Chunk {i + 1}" for i in range(len(selected))]
    context = "\n\n---\n\n".join(selected)
    return (context, sources)
