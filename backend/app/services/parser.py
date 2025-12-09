import re
from pathlib import Path
from docx import Document
from PyPDF2 import PdfReader

def read_txt(path: str) -> str:
    """
    Read a plain text file and return its contents as a string.
    """
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def read_docx(path: str) -> str:
    """
    Read a Word (.docx) file and return all paragraph text joined by newlines.
    """
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def read_pdf(path: str) -> str:
    """
    Read a PDF file and return extracted text from all pages.
    """
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def load_draft(path: str) -> str:
    """
    Detect file type by extension and load its text content.
    Supports .txt, .docx, and .pdf.
    """
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".txt":
        return read_txt(path)
    if suffix == ".docx":
        return read_docx(path)
    if suffix == ".pdf":
        return read_pdf(path)
    raise ValueError(f"Unsupported file type: {suffix}")

def structure_text(raw: str) -> dict:
    """
    Split raw text into question chunks based on numbering patterns (Q1., 1), etc.
    Returns a dict with the raw text and a list of chunks.
    """
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    chunks, buffer = [], []

    for line in lines:
        # Detect start of a new question (Q1., 1., 2), etc.)
        if re.match(r"^(Q?\d+)[\.\)]\s", line):
            if buffer:
                chunks.append("\n".join(buffer))
                buffer = []
        buffer.append(line)

    if buffer:
        chunks.append("\n".join(buffer))

    return {"raw": raw, "chunks": chunks}