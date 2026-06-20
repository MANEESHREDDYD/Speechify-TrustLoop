from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentChunk
from app.utils.text_utils import words


def lexical_similarity(query: str, candidate: str) -> float:
    q = words(query)
    c = words(candidate)
    if not q or not c:
        return 0.0
    q_counts, c_counts = Counter(q), Counter(c)
    common = sum(min(q_counts[token], c_counts[token]) for token in q_counts)
    recall = common / len(q)
    precision = common / min(len(c), max(len(q) * 2, 1))
    q_set, c_set = set(q), set(c)
    jaccard = len(q_set & c_set) / max(1, len(q_set | c_set))
    phrase_bonus = 0.12 if " ".join(q[:5]) in " ".join(c) else 0.0
    entity_tokens = [w for w in q if any(ch.isdigit() for ch in w)]
    entity_match = 1.0 if not entity_tokens else sum(t in c for t in entity_tokens) / len(entity_tokens)
    score = 0.58 * recall + 0.18 * precision + 0.14 * jaccard + 0.10 * entity_match + phrase_bonus
    return round(min(1.0, score), 4)


def retrieve_top_k(session: Session, query: str, document_id: str, k: int = 3) -> list[dict]:
    chunks = session.scalars(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    ).all()
    ranked = sorted(
        (
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "section_title": chunk.section_title,
                "page_number": chunk.page_number,
                "text": chunk.text,
                "similarity": lexical_similarity(query, chunk.text),
            }
            for chunk in chunks
        ),
        key=lambda item: item["similarity"],
        reverse=True,
    )
    return ranked[:k]
