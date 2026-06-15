"""
tools/policy_search.py

Lightweight TF-IDF search over HR policy chunks.
No external vector DB needed — works out of the box for the prototype.
"""

import math, re
from typing import List, Tuple
from tools.chunker import PolicyChunk, load_and_chunk

DOCX_PATH = "data/HR_Header_Chunking_Policies.docx"

_chunks: List[PolicyChunk] = []
_tfidf: List[dict] = []


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z]+", text.lower())


def _build_index(chunks: List[PolicyChunk]):
    global _tfidf
    N = len(chunks)
    df = {}
    docs = []
    for c in chunks:
        tokens = _tokenize(f"{c.section} {c.subsection or ''} {c.content}")
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        docs.append(tf)
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1

    _tfidf = []
    for tf in docs:
        vec = {t: (1 + math.log(v)) * math.log(N / df[t])
               for t, v in tf.items()}
        _tfidf.append(vec)


def _cosine(a: dict, b: dict) -> float:
    inter = set(a) & set(b)
    if not inter:
        return 0.0
    dot = sum(a[t] * b[t] for t in inter)
    na  = math.sqrt(sum(v*v for v in a.values()))
    nb  = math.sqrt(sum(v*v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _ensure_loaded():
    global _chunks
    if not _chunks:
        _chunks = load_and_chunk(DOCX_PATH)
        _build_index(_chunks)


def search_policy(query: str, top_k: int = 3) -> List[Tuple[PolicyChunk, float]]:
    """Return top-k chunks most relevant to the query."""
    _ensure_loaded()
    q_tf = {}
    for t in _tokenize(query):
        q_tf[t] = q_tf.get(t, 0) + 1
    scores = [(_chunks[i], _cosine(q_tf, vec)) for i, vec in enumerate(_tfidf)]
    scores.sort(key=lambda x: x[1], reverse=True)
    return [(c, s) for c, s in scores[:top_k] if s > 0]
