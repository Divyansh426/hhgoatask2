import time
from app.stt import transcribe
from app.retrieval import retrieve
from app.guardrails import check_off_topic, check_grounding
from app.generation import generate_answer
from app.schemas import AskResponse, PipelineTimings


async def run_pipeline(audio_bytes: bytes) -> AskResponse:
    t0 = time.perf_counter()
    timings = PipelineTimings()

    try:
        query = await transcribe(audio_bytes)
    except Exception as e:
        return AskResponse(error=f"stt_failed: {e}")
    timings.stt_ms = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    try:
        results = retrieve(query)
    except Exception as e:
        return AskResponse(query=query, error=f"retrieval_failed: {e}")
    timings.retrieval_ms = (time.perf_counter() - t1) * 1000

    if check_off_topic(results):
        timings.total_ms = (time.perf_counter() - t0) * 1000
        return AskResponse(
            query=query, refused=True, reason="off_topic_or_no_match",
            timings=timings,
        )

    t2 = time.perf_counter()
    try:
        answer = generate_answer(query, results)
    except Exception as e:
        return AskResponse(query=query, error=f"generation_failed: {e}")
    timings.generation_ms = (time.perf_counter() - t2) * 1000

    if not check_grounding(answer, results):
        timings.total_ms = (time.perf_counter() - t0) * 1000
        return AskResponse(
            query=query, refused=True, reason="ungrounded_answer",
            timings=timings,
        )

    timings.total_ms = (time.perf_counter() - t0) * 1000
    return AskResponse(
        query=query, answer=answer, refused=False,
        sources=[r.text[:150] for r in results[:3]],
        timings=timings,
    )