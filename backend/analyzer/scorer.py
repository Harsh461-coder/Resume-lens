"""
scorer.py — Step 6 in the workflow: ATS Scorer.

Calculates the overall ATS match score (0-100) between resume text and
job description text using TF-IDF + cosine similarity. Pure scoring —
doesn't know about skills lists or suggestions.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_ats_score(resume_text: str, jd_text: str) -> float:
    """
    Calculate an overall match score (0-100) between two pieces of
    (already-cleaned) text using TF-IDF vectors and cosine similarity.
    """
    documents = [resume_text, jd_text]

    if not documents[0] or not documents[1]:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError:
        # happens if both texts are empty after removing stopwords
        return 0.0

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity) * 100, 2)


def calculate_skill_match_score(matched_skills: list, jd_skills: list) -> float:
    """
    A secondary score: what fraction of the JD's required skills the
    resume actually has. Useful alongside the TF-IDF score since it's
    easier to explain to the user ("6 of 8 required skills found").
    """
    if not jd_skills:
        return 0.0
    return round((len(matched_skills) / len(jd_skills)) * 100, 2)
