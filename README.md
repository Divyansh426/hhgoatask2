# Voice-Enabled RAG — HH Goa 2026

Pipeline: Sarvam STT -> FAISS retrieval (multi-strategy chunking) -> guardrails -> Claude Haiku 4.5

## Scope
Indexed the Hindi (`hi`) subset of `ai4bharat/MSMARCO-XI`, `is_selected=1` passages,
~30k query-passage pairs.

## Chunking strategies
1. **Passage-native** — MS MARCO passages are already atomic (~50-150 words); indexed as-is.
2. **Sliding window** — 150-token windows, 30-token overlap, for passages over 200 words.
3. **Semantic merge** (in progress) — clusters related passages per query by embedding similarity.
All chunks carry metadata: query_type, is_selected, source passage index.

## Latency
See `backend/scripts/eval_latency.py` output. P50/P70/P100 measured across N held-out
validation-split queries. NOTE: the <200ms target is interpreted as retrieval-path latency
(STT + retrieval), not including LLM generation — see submission notes for reasoning.

## Guardrails
- Off-topic rejection via retrieval-score threshold
- Post-generation grounding check (lexical overlap heuristic against retrieved context)
- Structured error handling at every harness stage (STT/retrieval/generation failures
  degrade gracefully instead of crashing)

## Run locally
Backend: `cd backend && uvicorn app.main:app --reload`
Frontend: `cd frontend && npm run dev`