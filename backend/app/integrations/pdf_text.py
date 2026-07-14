from typing import BinaryIO, Protocol

from pypdf import PdfReader


class PdfTextExtractionError(Exception):
    """Raised when a PDF cannot be parsed safely for text extraction."""


class PdfTextExtractorPort(Protocol):
    def extract(self, body: BinaryIO) -> str: ...


class PyPdfTextExtractor:
    def extract(self, body: BinaryIO) -> str:
        try:
            body.seek(0)
            pages = (page.extract_text() or "" for page in PdfReader(body).pages)
            return "\n\n".join(text.strip() for text in pages if text.strip()).strip()
        except Exception as exc:
            raise PdfTextExtractionError("PDF text extraction failed") from exc
        finally:
            body.seek(0)
