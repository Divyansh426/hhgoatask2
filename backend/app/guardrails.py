from app.schemas import RetrievedChunk

MIN_RETRIEVAL_SCORE = 0.45  # tune against your eval set


def check_off_topic(results: list[RetrievedChunk]) -> bool:
    """No result above threshold -> query is likely off-corpus."""
    if not results:
        return True
    return max(r.score for r in results) < MIN_RETRIEVAL_SCORE


def check_grounding(answer: str, results: list[RetrievedChunk]) -> bool:
    """Lexical overlap heuristic: does the answer reuse enough vocabulary
    from retrieved passages? Swap for an NLI model if time allows."""
    context_words = set(" ".join(r.text for r in results).split())
    answer_words = set(answer.split())
    if not answer_words:
        return False
    overlap = len(answer_words & context_words) / len(answer_words)
    return overlap > 0.25