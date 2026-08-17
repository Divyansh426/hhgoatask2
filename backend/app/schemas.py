from pydantic import BaseModel, Field
from typing import Optional


class RetrievedChunk(BaseModel):
    text: str
    strategy: str
    query_id: Optional[int] = None  # was: Optional[str]
    passage_idx: Optional[int] = None
    is_selected: bool = False
    query_type: Optional[str] = None
    score: float


class PipelineTimings(BaseModel):
    stt_ms: float = 0.0
    retrieval_ms: float = 0.0
    generation_ms: float = 0.0
    total_ms: float = 0.0


class AskResponse(BaseModel):
    query: Optional[str] = None
    answer: Optional[str] = None
    refused: bool = False
    reason: Optional[str] = None
    sources: list[str] = Field(default_factory=list)
    timings: PipelineTimings = Field(default_factory=PipelineTimings)
    error: Optional[str] = None