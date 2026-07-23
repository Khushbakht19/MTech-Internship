"""
similarity.py
------------------------------------------------------------------
Core NLP matching engine of Resume Screener Pro.

Implements:
    - TF-IDF Vectorization       (scikit-learn TfidfVectorizer)
    - Cosine Similarity          (scikit-learn cosine_similarity)
    - Match Score calculation    (0-100 scale)
    - Resume Ranking             (sorting candidates by score)
    - Keyword Matching           (skills overlap between resume & job)

This module is intentionally kept separate from the database and
GUI layers so the matching logic can be tested and understood on
its own, independent of the rest of the application.
------------------------------------------------------------------
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp.preprocessing import preprocess_text


def calculate_match_score(resume_text, job_description):
    """
    Calculates a similarity score between a single resume and a
    single job description using TF-IDF + Cosine Similarity.

    Steps:
        1. Preprocess both texts (clean, tokenize, remove stopwords).
        2. Fit a TF-IDF vectorizer on both documents together, so
           they share the same vocabulary/feature space.
        3. Compute the cosine similarity between the two TF-IDF
           vectors (a value between 0 and 1).
        4. Scale the result to a 0-100 "match score" for easier
           interpretation by recruiters.

    Args:
        resume_text (str): raw resume text.
        job_description (str): raw job description text.

    Returns:
        float: match score between 0.0 and 100.0
    """
    processed_resume = preprocess_text(resume_text)
    processed_job = preprocess_text(job_description)

    # Guard against completely empty documents (would break TF-IDF)
    if not processed_resume.strip() or not processed_job.strip():
        return 0.0

    documents = [processed_resume, processed_job]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Cosine similarity between the resume vector (row 0) and the
    # job description vector (row 1). Result is a 1x1 matrix.
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    similarity_score = similarity_matrix[0][0]

    match_score = round(float(similarity_score) * 100, 2)
    return match_score


def rank_candidates(candidates, job_description):
    """
    Ranks a list of candidates against a single job description
    using TF-IDF cosine similarity, from best match to worst match.

    Args:
        candidates (list[dict]): each dict must contain at least
                                  'id', 'full_name', and 'resume_text'.
        job_description (str): raw job description text.

    Returns:
        list[dict]: the same candidate dicts, each with an added
                    'match_score' key, sorted descending by score.
    """
    ranked_results = []

    for candidate in candidates:
        score = calculate_match_score(candidate["resume_text"], job_description)
        candidate_with_score = dict(candidate)
        candidate_with_score["match_score"] = score
        ranked_results.append(candidate_with_score)

    # Sort candidates from highest to lowest match score
    ranked_results.sort(key=lambda item: item["match_score"], reverse=True)

    # Assign a rank position (1 = best match) after sorting
    for position, candidate in enumerate(ranked_results, start=1):
        candidate["rank_position"] = position

    return ranked_results


def find_matched_keywords(candidate_skills, required_skills):
    """
    Compares a candidate's listed skills against a job's required
    skills and returns the ones that overlap (case-insensitive).

    Args:
        candidate_skills (str): comma-separated skill string.
        required_skills (str): comma-separated skill string.

    Returns:
        str: comma-separated string of matched skills, or a
             friendly message if no skills matched.
    """
    if not candidate_skills or not required_skills:
        return "No skill data available"

    candidate_set = {
        skill.strip().lower() for skill in candidate_skills.split(",") if skill.strip()
    }
    required_set = {
        skill.strip().lower() for skill in required_skills.split(",") if skill.strip()
    }

    matched_skills = candidate_set.intersection(required_set)

    if not matched_skills:
        return "No direct keyword matches"

    return ", ".join(sorted(matched_skills))


def calculate_keyword_overlap_percentage(candidate_skills, required_skills):
    """
    Calculates what percentage of the job's REQUIRED skills are
    actually present in the candidate's skill list. This is a
    simple, explainable complement to the TF-IDF match score.

    Args:
        candidate_skills (str): comma-separated skill string.
        required_skills (str): comma-separated skill string.

    Returns:
        float: percentage (0-100) of required skills matched.
    """
    if not required_skills:
        return 0.0

    candidate_set = {
        skill.strip().lower() for skill in candidate_skills.split(",") if skill.strip()
    }
    required_set = {
        skill.strip().lower() for skill in required_skills.split(",") if skill.strip()
    }

    if not required_set:
        return 0.0

    matched_count = len(candidate_set.intersection(required_set))
    percentage = (matched_count / len(required_set)) * 100
    return round(percentage, 1)


def get_top_matching_keywords(resume_text, job_description, top_n=10):
    """
    Returns the top overlapping keywords between a resume and a job
    description based on shared vocabulary after preprocessing.
    Useful for showing recruiters *why* a resume scored the way it did.

    Args:
        resume_text (str): raw resume text.
        job_description (str): raw job description text.
        top_n (int): maximum number of shared keywords to return.

    Returns:
        list[str]: shared keywords between the two documents.
    """
    from nlp.preprocessing import clean_text, tokenize, remove_stopwords

    resume_tokens = set(remove_stopwords(tokenize(clean_text(resume_text))))
    job_tokens = set(remove_stopwords(tokenize(clean_text(job_description))))

    shared_tokens = resume_tokens.intersection(job_tokens)
    return sorted(list(shared_tokens))[:top_n]
