import faiss
import json
import os
from sentence_transformers import SentenceTransformer
from app.schemas import RetrievedChunk

_HERE = os.path.dirname(os.path.dirname(__file__))  # backend/
MODEL = SentenceTransformer("intfloat/multilingual-e5-small")
INDEX = faiss.read_index(os.path.join(_HERE, "data", "faiss.index"))

with open(os.path.join(_HERE, "data", "metadata.jsonl"), encoding="utf-8") as f:
    METADATA = [json.loads(line) for line in f]


def retrieve(query: str, k: int = 8, query_type_filter: str | None = None) -> list[RetrievedChunk]:
    q_emb = MODEL.encode([query], normalize_embeddings=True).astype("float32")
    scores, idxs = INDEX.search(q_emb, k * 3)  # over-fetch then filter

    results: list[RetrievedChunk] = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx == -1:
            continue
        meta = METADATA[idx]
        if query_type_filter and meta.get("query_type") != query_type_filter:
            continue
        results.append(RetrievedChunk(**meta, score=float(score)))
        if len(results) >= k:
            break
    return results