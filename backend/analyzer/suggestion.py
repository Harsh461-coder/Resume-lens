"""
suggestions.py — Step 7 in the workflow: Suggestions.

Generates simple, rule-based suggestions for the applicant based on
missing skills, the overall score, and whether the resume uses strong
action verbs / has the sections a resume usually needs.
"""

import csv
import os
import re

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset")


def _load_keywords(keyword_type: str) -> list:
    path = os.path.join(DATASET_DIR, "keywords.csv")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row["keyword"].strip().lower() for row in reader if row["type"] == keyword_type]


ACTION_VERBS = _load_keywords("action_verb")
RESUME_SECTIONS = _load_keywords("section")


def check_action_verbs(resume_text: str) -> bool:
    """Does the resume use at least a couple of strong action verbs?"""
    found = [verb for verb in ACTION_VERBS if re.search(r"\b" + re.escape(verb) + r"\b", resume_text)]
    return len(found) >= 2


def check_sections(resume_text: str) -> list:
    """Which common resume sections seem to be missing?"""
    missing = [s for s in RESUME_SECTIONS if s not in resume_text]
    return missing


def generate_suggestions(missing_skills: list, match_score: float, resume_text: str) -> list:
    """Build a short, prioritized list of suggestions for the applicant."""
    suggestions = []

    if missing_skills:
        top_missing = missing_skills[:5]
        suggestions.append(
            "Consider adding these skills to your resume if you genuinely have them: "
            + ", ".join(top_missing)
        )

    if match_score < 50:
        suggestions.append(
            "Your overall match score is quite low. Try rewriting your resume summary "
            "and experience sections using more of the same wording as the job description."
        )
    elif match_score < 80:
        suggestions.append(
            "You're on the right track. Adding a couple more relevant keywords from the "
            "job description could push your match score higher."
        )
    else:
        suggestions.append(
            "Your resume already matches this job description well. Just double-check "
            "formatting so an ATS can read it properly (avoid tables/images for key info)."
        )

    if not check_action_verbs(resume_text):
        suggestions.append(
            "Try using stronger action verbs (e.g. built, led, improved, launched) to "
            "describe your experience — it reads more confidently to both ATS and recruiters."
        )

    missing_sections = check_sections(resume_text)
    if missing_sections:
        suggestions.append(
            "Your resume may be missing a clearly labeled section for: "
            + ", ".join(missing_sections[:3])
        )

    if not missing_skills:
        suggestions.append("No obvious skill gaps found based on our skill list — nice work.")

    return suggestions
