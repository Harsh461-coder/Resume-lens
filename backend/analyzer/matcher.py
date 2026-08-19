"""
matcher.py — Step 5 in the workflow: Keyword Matcher.

Loads the skills dataset and synonym map, then figures out which
skills appear in a given piece of text — and normalizes synonyms
("JS" -> "javascript") so matching isn't thrown off by wording.
"""

import csv
import os
import re

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset")


def _load_skills() -> list:
    path = os.path.join(DATASET_DIR, "skills.csv")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row["skill"].strip().lower() for row in reader if row["skill"].strip()]


def _load_synonyms() -> dict:
    path = os.path.join(DATASET_DIR, "synonyms.csv")
    mapping = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["synonym"].strip().lower()] = row["canonical_skill"].strip().lower()
    return mapping


SKILLS_DATASET = _load_skills()
SYNONYMS = _load_synonyms()


def normalize_synonyms(text: str) -> str:
    """Replace known synonyms/abbreviations with their canonical skill name."""
    for synonym, canonical in SYNONYMS.items():
        pattern = r"(?<![a-z0-9])" + re.escape(synonym) + r"(?![a-z0-9])"
        text = re.sub(pattern, canonical, text)
    return text


def find_skills_in_text(text: str, skills_dataset: list = None) -> list:
    """Return the list of dataset skills that appear in the given (already-cleaned) text."""
    if skills_dataset is None:
        skills_dataset = SKILLS_DATASET

    text = normalize_synonyms(text)

    found = []
    for skill in skills_dataset:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            found.append(skill)
    return found


def match_resume_to_job(resume_text: str, jd_text: str) -> dict:
    """
    Compare cleaned resume text against a cleaned job description.

    Returns a dict with matched_skills (present in both) and missing_skills
    (required by the JD but not found in the resume).
    """
    resume_skills = find_skills_in_text(resume_text)
    jd_skills = find_skills_in_text(jd_text)

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)

    # If the JD didn't mention any dataset skills at all, fall back to
    # showing what the resume has, so the user still gets a useful result.
    if not matched and not jd_set:
        matched = sorted(resume_set)[:10]

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills": sorted(resume_set),
        "jd_skills": sorted(jd_set),
    }
