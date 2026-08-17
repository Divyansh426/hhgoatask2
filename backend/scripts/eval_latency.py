import asyncio
import glob
import numpy as np
from app.harness import run_pipeline


async def eval_all(audio_dir: str = "eval_audio"):
    audio_files = glob.glob(f"{audio_dir}/*.wav")
    if not audio_files:
        print(f"No .wav files found in {audio_dir}/ — add >=50 held-out samples first")
        return

    all_timings = []
    for path in audio_files:
        with open(path, "rb") as f:
            audio_bytes = f.read()
        result = await run_pipeline(audio_bytes)
        if result.error:
            print(f"SKIPPED {path}: {result.error}")
            continue
        all_timings.append(result.timings)

    print(f"\nEvaluated {len(all_timings)} queries\n")
    for stage in ["stt_ms", "retrieval_ms", "generation_ms", "total_ms"]:
        vals = sorted(getattr(t, stage) for t in all_timings)
        if not vals:
            continue
        p50 = np.percentile(vals, 50)
        p70 = np.percentile(vals, 70)
        p100 = max(vals)
        print(f"{stage:15s} P50={p50:7.1f}ms  P70={p70:7.1f}ms  P100={p100:7.1f}ms")


if __name__ == "__main__":
    asyncio.run(eval_all())