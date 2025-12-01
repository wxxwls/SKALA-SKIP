"""File loading utilities."""
from pathlib import Path
from typing import List, Optional

import pdfplumber
from docx import Document as DocxDocument


def load_pdf(file_path: str) -> str:
    """Load text content from PDF file."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    return "\n\n".join(text_parts)


def load_docx(file_path: str) -> str:
    """Load text content from DOCX file."""
    doc = DocxDocument(file_path)
    return "\n\n".join([para.text for para in doc.paragraphs if para.text])


def load_text(file_path: str) -> str:
    """Load text content from text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_document(file_path: str) -> str:
    """Load document content based on file extension."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return load_pdf(file_path)
    elif suffix in [".docx", ".doc"]:
        return load_docx(file_path)
    elif suffix in [".txt", ".md"]:
        return load_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def load_documents_from_directory(
    directory: str,
    extensions: Optional[List[str]] = None,
) -> List[dict]:
    """Load all documents from a directory."""
    extensions = extensions or [".pdf", ".docx", ".txt", ".md"]
    path = Path(directory)
    documents = []

    for ext in extensions:
        for file_path in path.glob(f"*{ext}"):
            try:
                content = load_document(str(file_path))
                documents.append({
                    "id": file_path.stem,
                    "path": str(file_path),
                    "content": content,
                })
            except Exception:
                continue

    return documents
