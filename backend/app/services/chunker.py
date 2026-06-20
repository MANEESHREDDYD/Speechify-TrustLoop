import re


HEADING_RE = re.compile(r"^(?:#{1,4}\s+|section\s+\d+\s*:|title\s*:|attendees\s*:|transcript\s*:)(.+)$", re.I)


def chunk_document(text: str, max_chars: int = 900, overlap: int = 120) -> list[dict]:
    lines = text.splitlines()
    sections: list[tuple[str, str]] = []
    title = "Document"
    buffer: list[str] = []

    def flush():
        nonlocal buffer
        body = "\n".join(buffer).strip()
        if body:
            sections.append((title, body))
        buffer = []

    for line in lines:
        match = HEADING_RE.match(line.strip())
        if match:
            flush()
            title = line.strip().replace("#", "").strip()
        else:
            buffer.append(line)
    flush()

    if not sections:
        sections = [("Document", text)]

    chunks: list[dict] = []
    for section_title, body in sections:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        current = ""
        for paragraph in paragraphs or [body]:
            if len(current) + len(paragraph) + 2 <= max_chars:
                current = f"{current}\n\n{paragraph}".strip()
                continue
            if current:
                chunks.append(_chunk(len(chunks), section_title, current))
            if len(paragraph) <= max_chars:
                current = paragraph
            else:
                start = 0
                while start < len(paragraph):
                    part = paragraph[start:start + max_chars]
                    chunks.append(_chunk(len(chunks), section_title, part))
                    start += max_chars - overlap
                current = ""
        if current:
            chunks.append(_chunk(len(chunks), section_title, current))
    return chunks


def _chunk(index: int, title: str, text: str) -> dict:
    return {
        "chunk_index": index,
        "section_title": title[:120],
        "page_number": max(1, index // 3 + 1),
        "text": text.strip(),
        "token_estimate": max(1, len(text.split()) * 4 // 3),
    }

