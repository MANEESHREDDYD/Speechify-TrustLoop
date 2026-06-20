import re
from pathlib import Path


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_txt(path: str) -> str:
    return clean_text(Path(path).read_text(encoding="utf-8"))


def parse_md(path: str) -> str:
    return parse_txt(path)


def parse_pdf(path: str) -> tuple[str, int]:
    import fitz

    doc = fitz.open(path)
    return clean_text("\n\n".join(page.get_text() for page in doc)), len(doc)


def parse_docx(path: str) -> str:
    from docx import Document

    doc = Document(path)
    return clean_text("\n".join(paragraph.text for paragraph in doc.paragraphs))

