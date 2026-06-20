from app.utils.text_utils import words


def embed_text(text: str) -> list[float]:
    """A tiny deterministic hashed embedding with no model download."""
    vector = [0.0] * 128
    tokens = words(text)
    for token in tokens:
        vector[hash(token) % len(vector)] += 1.0
    norm = sum(value * value for value in vector) ** 0.5 or 1.0
    return [value / norm for value in vector]


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return [embed_text(chunk) for chunk in chunks]

