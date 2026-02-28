import io
import pypdf
import docx


DOCX_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


def extract_text(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Extrahuje text zo súboru. Podporuje PDF, DOCX a plain text."""
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        text = _extract_pdf(file_bytes)
    elif content_type in DOCX_CONTENT_TYPES or filename.lower().endswith(".docx"):
        text = _extract_docx(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="replace")
    return text.replace("\x00", "")


def _extract_pdf(file_bytes: bytes) -> str:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _extract_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text)
