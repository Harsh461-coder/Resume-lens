"""
analyzer.py — Main Analyzer (Pipeline).

Orchestrates the full workflow: PDF Parser -> Text Cleaner -> Keyword
Matcher -> ATS Scorer -> Suggestions. This is the single entry point
app.py calls; it doesn't do any of the work itself, just wires the
five modules together in order.
"""

from .parser import extract_text_from_pdf
from .cleaner import clean_text
from .matcher import match_resume_to_job
from .scorer import calculate_ats_score, calculate_skill_match_score
from .suggestion import generate_suggestions


def analyze_resume(file_stream, job_description: str, resume_filename: str = "resume.pdf") -> dict:
    """
    Run the full analysis pipeline on an uploaded resume PDF against a
    job description, and return a single results dict ready to be sent
    to the frontend as JSON.
    """
    # Step 3: Parser
    raw_resume_text = extract_text_from_pdf(file_stream)

    # Step 4: Cleaner
    resume_text = clean_text(raw_resume_text)
    jd_text = clean_text(job_description)

    # Step 5: Matcher
    match_result = match_resume_to_job(resume_text, jd_text)

    # Step 6: Scorer
    ats_score = calculate_ats_score(resume_text, jd_text)
    skill_score = calculate_skill_match_score(
        match_result["matched_skills"], match_result["jd_skills"]
    )

    # Step 7: Suggestions
    suggestions = generate_suggestions(
        match_result["missing_skills"], ats_score, resume_text
    )

    return {
        "resume_filename": resume_filename,
        "match_score": ats_score,
        "skill_match_score": skill_score,
        "matched_skills": match_result["matched_skills"] or match_result["resume_skills"][:10],
        "missing_skills": match_result["missing_skills"],
        "suggestions": suggestions,
    }
