import httpx
import os

SARVAM_API_KEY = os.environ["SARVAM_API_KEY"]


async def transcribe(audio_bytes: bytes) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            "https://api.sarvam.ai/speech-to-text",
            headers={"api-subscription-key": SARVAM_API_KEY},
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={
                "language_code": "hi-IN",
                "model": "saaras:v3",
                "mode": "transcribe",
            },
        )
        resp.raise_for_status()
        return resp.json()["transcript"]