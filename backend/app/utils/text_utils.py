import re
from collections import Counter


STOP_WORDS = {
    "about", "after", "again", "also", "and", "are", "because", "been", "before",
    "being", "between", "both", "but", "can", "could", "does", "each", "for",
    "from", "good", "have", "into", "its", "many", "more", "must", "need", "not",
    "only", "other", "our", "over", "should", "some", "such", "than", "that", "the",
    "their", "them", "then", "there", "these", "they", "this", "through", "today",
    "use", "users", "using", "very", "was", "well", "were", "what", "when", "where",
    "which", "while", "who", "will", "with", "would", "you", "your", "section",
    "title", "host", "main", "idea", "key", "points",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    return [
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", text)
        if token.lower() not in STOP_WORDS
    ]


def sentences(text: str) -> list[str]:
    cleaned = re.sub(r"^#+\s*.*$", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"^\|?[-:\s|]+\|?$", "", cleaned, flags=re.MULTILINE)
    parts = re.split(r"(?<=[.!?])\s+|\n+", cleaned)
    return [normalize(part.strip(" -*#|")) for part in parts if len(normalize(part)) > 20]


def top_terms(text: str, limit: int = 12) -> list[tuple[str, int]]:
    counts = Counter(words(text))
    return counts.most_common(limit)


def slug_title(text: str) -> str:
    line = next((line for line in text.splitlines() if line.strip()), "Untitled document")
    return re.sub(r"^(title|#)\s*:?\s*", "", line.strip(), flags=re.IGNORECASE)[:90]

