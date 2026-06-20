import re

from app.services.retrieval import lexical_similarity
from app.utils.text_utils import sentences, words


NAMES = {"maya", "leo", "priya", "sam", "jordan", "nora", "alex", "mei"}


def split_into_claims(generated_text: str) -> list[str]:
    claims: list[str] = []
    for line in generated_text.splitlines():
        cleaned = line.strip().strip("|").strip()
        if not cleaned or cleaned.startswith("#") or re.fullmatch(r"[-:| ]+", cleaned):
            continue
        if "|" in cleaned:
            cells = [cell.strip() for cell in cleaned.split("|") if cell.strip()]
            if cells and not any(cell.lower() in {"owner", "task", "due date", "product", "focus"} for cell in cells):
                cleaned = "; ".join(cells)
        cleaned = re.sub(r"^(?:\d+\.|[-*]|Host [12]:)\s*", "", cleaned)
        if re.match(r"^[A-D]\.\s", cleaned) or cleaned.lower().startswith(("answer:", "source topic:")):
            continue
        for sentence in sentences(cleaned):
            if len(words(sentence)) >= 4:
                claims.append(sentence)
    return list(dict.fromkeys(claims))[:40]


def contradiction_reason(claim: str, source_text: str) -> str | None:
    claim_lower, source_lower = claim.lower(), source_text.lower()
    claim_dates = set(re.findall(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b", claim_lower))
    source_dates = set(re.findall(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b", source_lower))
    overlap = set(words(claim)) & set(words(source_text))
    if claim_dates and source_dates and not (claim_dates & source_dates) and len(overlap) >= 2:
        return "The date conflicts with the matching source context."
    if re.search(r"\b(no|not|never)\b", claim_lower) and re.search(r"\b(required|must|need|needs)\b", source_lower) and len(overlap) >= 2:
        return "The claim negates a requirement stated in the source."
    claim_names = NAMES & set(words(claim))
    if claim_names:
        for sentence in sentences(source_text):
            source_names = NAMES & set(words(sentence))
            task_overlap = (set(words(claim)) - NAMES) & (set(words(sentence)) - NAMES)
            if source_names and claim_names != source_names and len(task_overlap) >= 2:
                return "The task appears to be assigned to a different owner in the source."
    return None


def classify_claim(claim: str, retrieved: list[dict]) -> dict:
    best = retrieved[0] if retrieved else {"similarity": 0.0, "text": "", "id": None}
    contradiction = None
    for item in retrieved:
        reason = contradiction_reason(claim, item["text"])
        if reason:
            contradiction = (item, reason)
            break
    if contradiction and best["similarity"] < 0.78:
        item, reason = contradiction
        return {
            "status": "contradicted",
            "confidence": round(max(0.75, 1 - item["similarity"] / 2), 3),
            "supporting_chunk_id": item["id"],
            "supporting_text": f"{reason} Source: {item['text']}",
        }
    score = best["similarity"]
    status = "supported" if score >= 0.78 else "weakly_supported" if score >= 0.62 else "unsupported"
    return {
        "status": status,
        "confidence": round(score if status != "unsupported" else 1 - score, 3),
        "supporting_chunk_id": best.get("id") if score >= 0.35 else None,
        "supporting_text": best.get("text", "") if score >= 0.35 else "",
    }

