def trust_label(score: float) -> str:
    if score >= 90:
        return "Highly trustworthy"
    if score >= 75:
        return "Mostly grounded"
    if score >= 60:
        return "Needs review"
    if score >= 40:
        return "Risky"
    return "Not reliable"


def calculate_scores(claims: list[dict], source_topics: int, missing_topics: int, generated_text: str, output_type: str) -> dict:
    total = max(1, len(claims))
    supported = sum(c["status"] == "supported" for c in claims)
    weak = sum(c["status"] == "weakly_supported" for c in claims)
    unsupported = sum(c["status"] == "unsupported" for c in claims)
    contradicted = sum(c["status"] == "contradicted" for c in claims)
    grounding = (supported + 0.5 * weak) / total
    hallucination = min(1.0, (unsupported + contradicted * 1.5) / total)
    coverage = max(0.0, (source_topics - missing_topics) / max(1, source_topics))
    citation = sum(bool(c.get("supporting_chunk_id")) for c in claims) / total
    structured = generated_text.count("#") >= 2 or generated_text.count("\n-") >= 2
    long_sentences = sum(len(sentence.split()) > 32 for sentence in generated_text.split("."))
    readability = max(0.45, min(1.0, 0.72 + (0.18 if structured else 0) - long_sentences * 0.03))
    task_score = 0.8
    if output_type == "meeting_notes":
        task_score = 0.95 if "Action Items" in generated_text and "| Owner |" in generated_text else 0.55
    elif output_type == "quiz":
        task_score = 0.95 if "Answer:" in generated_text and "Source topic:" in generated_text else 0.55
    feedback_prior = 0.75
    trust = (
        0.35 * grounding
        + 0.25 * coverage
        + 0.15 * citation
        + 0.10 * readability
        + 0.10 * feedback_prior
        + 0.05 * task_score
    ) * 100
    return {
        "grounding_score": round(grounding, 4),
        "coverage_score": round(coverage, 4),
        "citation_score": round(citation, 4),
        "readability_score": round(readability, 4),
        "hallucination_risk": round(hallucination, 4),
        "action_item_score": round(task_score if output_type == "meeting_notes" else 0.8, 4),
        "quiz_relevance_score": round(task_score if output_type == "quiz" else 0.8, 4),
        "trust_score": round(trust, 1),
        "supported_claims": supported,
        "weakly_supported_claims": weak,
        "unsupported_claims": unsupported,
        "contradicted_claims": contradicted,
    }
