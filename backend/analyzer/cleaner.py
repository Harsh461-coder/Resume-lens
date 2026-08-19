"""
cleaner.py — Step 4 in the workflow: Text Cleaner.

Takes raw extracted text and normalizes it so the matcher and scorer
get consistent, comparable input. Doesn't know about skills or scoring
— just text hygiene.
"""

import re


def clean_text(text: str) -> str:
    """
    Lowercase, strip extra whitespace, and remove punctuation that isn't
    useful for matching — while keeping characters that matter for tech
    terms like 'c++', 'c#', and 'node.js'.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+\#\.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_extra_whitespace(text: str) -> str:
    """Collapse repeated blank lines/spaces left over from PDF extraction."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()
