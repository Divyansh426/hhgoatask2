from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer
import duckdb
import faiss
import numpy as np
import json
import os

MODEL = SentenceTransformer("intfloat/multilingual-e5-small")
N_SAMPLES = 5000  # test small first, bump to 30000 once this works end-to-end
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def get_rows(n_samples: int):
    path = hf_hub_download(
        repo_id="ai4bharat/MSMARCO-XI",
        filename="train/hintrain.parquet",
        repo_type="dataset",
    )
    con = duckdb.connect()
    con.execute("PRAGMA threads=8")
    print("Querying parquet file...")
    table = con.execute(
        f"""SELECT query, Answer, query_id, query_type, passages
            FROM read_parquet('{path}') LIMIT {n_samples}"""
    ).fetch_arrow_table()
    print("Query done, converting to rows...")
    df = table.to_pandas()
    for row in df.to_dict("records"):
        yield row


def strategy_passage_native(row, qid):
    chunks = []
    passages = row["passages"]["Translated_passages"]
    selected = row["passages"]["is_selected"]
    for i, (p, sel) in enumerate(zip(passages, selected)):
        if len(p.split()) <= 200:
            chunks.append({
                "text": p, "strategy": "passage_native",
                "query_id": qid, "passage_idx": i,
                "is_selected": bool(sel), "query_type": row["query_type"],
            })
    return chunks


def strategy_sliding_window(row, qid, window=150, overlap=30):
    chunks = []
    for i, p in enumerate(row["passages"]["Translated_passages"]):
        words = p.split()
        if len(words) <= 200:
            continue
        for start in range(0, len(words), window - overlap):
            piece = " ".join(words[start:start + window])
            chunks.append({
                "text": piece, "strategy": "sliding_window",
                "query_id": qid, "passage_idx": i, "window_start": start,
                "is_selected": bool(row["passages"]["is_selected"][i]),
                "query_type": row["query_type"],
            })
    return chunks


def build():
    all_chunks = []
    for row in get_rows(N_SAMPLES):
        all_chunks.extend(strategy_passage_native(row, row["query_id"]))
        all_chunks.extend(strategy_sliding_window(row, row["query_id"]))

    print(f"Built {len(all_chunks)} chunks, embedding now...")
    texts = [c["text"] for c in all_chunks]
    embeddings = MODEL.encode(texts, batch_size=64, show_progress_bar=True,
                               normalize_embeddings=True)

    dim = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dim, 32)
    index.hnsw.efConstruction = 100
    index.add(np.array(embeddings, dtype="float32"))

    os.makedirs(OUT_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(OUT_DIR, "faiss.index"))
    with open(os.path.join(OUT_DIR, "metadata.jsonl"), "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"Indexed {len(all_chunks)} chunks from {N_SAMPLES} queries")


if __name__ == "__main__":
    build()