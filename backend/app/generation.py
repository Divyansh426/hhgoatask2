import httpx
import os

SARVAM_API_KEY = os.environ["SARVAM_API_KEY"]


async def generate_answer(query: str, results: list) -> str:
    context = "\n\n".join(f"[{i+1}] {r.text}" for i, r in enumerate(results))
    prompt = f"""Answer the question using ONLY the context below.
If the context doesn't contain the answer, say so explicitly.

Context:
{context}

Question: {query}

Answer (in Hindi):"""

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            "https://api.sarvam.ai/v1/chat/completions",
            headers={"api-subscription-key": SARVAM_API_KEY},
            json={
                "model": "sarvam-105b-conversations",  # tuned for real-time/voice workloads
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "reasoning_effort": None,  # disable thinking mode — cuts latency for a speed-sensitive path
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]