from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from app.integrations.pdf_text import PdfTextExtractionError, PyPdfTextExtractor


def test_pdf_extractor_normalizes_nonempty_pages_and_rewinds() -> None:
    body = BytesIO(b"pdf")
    pages = [MagicMock(), MagicMock(), MagicMock()]
    pages[0].extract_text.return_value = " First page \n"
    pages[1].extract_text.return_value = None
    pages[2].extract_text.return_value = " Second page "

    with patch("app.integrations.pdf_text.PdfReader", return_value=MagicMock(pages=pages)):
        assert PyPdfTextExtractor().extract(body) == "First page\n\nSecond page"
    assert body.tell() == 0


def test_pdf_extractor_wraps_parser_errors_and_rewinds() -> None:
    body = BytesIO(b"pdf")
    with (
        patch("app.integrations.pdf_text.PdfReader", side_effect=ValueError("parser detail")),
        pytest.raises(PdfTextExtractionError, match="extraction failed"),
    ):
        PyPdfTextExtractor().extract(body)
    assert body.tell() == 0
