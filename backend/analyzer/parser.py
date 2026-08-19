"""
parser.py — Step 3 in the workflow: PDF Parser.

Responsible only for getting raw text out of an uploaded resume PDF.
Knows nothing about scoring, matching, or skills — just extraction.
"""

import pdfplumber


def extract_text_from_pdf(file_stream) -> str:
    """
    Extract raw text from a resume PDF file stream.

    Args:
        file_stream: a file-like object (e.g. from Flask's request.files["resume"].stream)

    Returns:
        The extracted text as a single string, with pages joined by newlines.
        Returns an empty string if no text could be extracted (e.g. a scanned
        image-only PDF with no selectable text).
    """
    text_parts = []
    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)
