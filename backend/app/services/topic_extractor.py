import re

from app.utils.text_utils import top_terms, words


def extract_topics(text: str, limit: int = 10) -> list[dict]:
    candidates: list[tuple[str, float]] = []
    for line in text.splitlines():
        match = re.match(r"(?:#{1,4}\s+|Section\s+\d+\s*:\s*)(.+)", line.strip(), re.I)
        if match:
            topic = match.group(1).strip().lower()
            if topic not in {"summary", "key points", "main idea", "why it matters"}:
                candidates.append((topic, 1.0))
    for term, count in top_terms(text, limit * 2):
        candidates.append((term, min(0.9, 0.45 + count * 0.08)))
    result = []
    seen = set()
    for topic, score in candidates:
        normalized = re.sub(r"[^a-z0-9 ]", "", topic)
        if normalized and normalized not in seen and len(normalized) > 2:
            seen.add(normalized)
            result.append({"topic": normalized, "importance_score": round(score, 2)})
    return result[:limit]


def detect_missing_topics(source_text: str, generated_text: str) -> list[dict]:
    output_tokens = set(words(generated_text))
    output_lower = generated_text.lower()
    missing = []
    for item in extract_topics(source_text, 12):
        topic = item["topic"]
        topic_tokens = set(words(topic))
        present = topic in output_lower or (topic_tokens and len(topic_tokens & output_tokens) / len(topic_tokens) >= 0.6)
        if not present:
            missing.append(
                {
                    "topic": topic,
                    "importance_score": item["importance_score"],
                    "reason": "Important in the source but not represented in the output.",
                }
            )
    return missing[:8]

