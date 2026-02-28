import io
import pypdf


def extract_text(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Extrahuje text zo súboru. Podporuje PDF a plain text."""
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return _extract_pdf(file_bytes)
    return file_bytes.decode("utf-8", errors="replace")


def _extract_pdf(file_bytes: bytes) -> str:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)
