from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.harness import run_pipeline
from app.schemas import AskResponse

app = FastAPI(title="Voice RAG - HH Goa 2026")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    result = await run_pipeline(audio_bytes)
    return result