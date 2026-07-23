"""
preprocessing.py
------------------------------------------------------------------
Text cleaning and preprocessing utilities used before any NLP
similarity calculations take place.

Pipeline implemented here:
    1. Lowercasing
    2. Removing punctuation, numbers, and special characters
    3. Removing extra whitespace
    4. Tokenization
    5. Stopword removal (using a built-in stopword list, so the
       project does not require downloading NLTK corpora)

This keeps the NLP pipeline simple, dependency-light, and fully
understandable at a second-semester AI student level, while still
demonstrating real text preprocessing concepts taught in NLP courses.
------------------------------------------------------------------
"""

import re


# ==================================================================
# BUILT-IN ENGLISH STOPWORD LIST
# ------------------------------------------------------------------
# A small, self-contained stopword list is used instead of NLTK to
# avoid an extra download step (nltk.download(...)) that could fail
# on a machine without internet access during grading/demo.
# ==================================================================
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "in", "on",
    "at", "to", "for", "with", "as", "by", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its", "i", "you",
    "he", "she", "we", "they", "them", "his", "her", "their", "our", "your",
    "my", "me", "us", "him", "which", "who", "whom", "will", "would", "shall",
    "should", "can", "could", "may", "might", "must", "have", "has", "had",
    "do", "does", "did", "not", "no", "nor", "too", "very", "just", "also",
    "about", "into", "over", "under", "again", "further", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "only", "own", "same",
    "than", "s", "t", "don", "now", "up", "down", "out", "off", "from",
}


def clean_text(raw_text):
    """
    Cleans raw resume/job text by lowercasing, removing punctuation,
    numbers, and collapsing extra whitespace.

    Args:
        raw_text (str): unprocessed text.

    Returns:
        str: cleaned text (still contains normal words separated by
             single spaces).
    """
    if not raw_text:
        return ""

    text = raw_text.lower()

    # Remove anything that is not a letter or whitespace
    text = re.sub(r"[^a-z\s]", " ", text)

    # Collapse multiple spaces/newlines/tabs into a single space
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(cleaned_text):
    """
    Splits cleaned text into a list of individual word tokens.

    Args:
        cleaned_text (str): text already processed by clean_text().

    Returns:
        list[str]: list of word tokens.
    """
    if not cleaned_text:
        return []
    return cleaned_text.split(" ")


def remove_stopwords(tokens):
    """
    Filters out common English stopwords and very short tokens
    (length < 2) that carry little semantic meaning.

    Args:
        tokens (list[str]): list of word tokens.

    Returns:
        list[str]: filtered list of meaningful tokens.
    """
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def preprocess_text(raw_text):
    """
    Full preprocessing pipeline: clean -> tokenize -> remove stopwords
    -> rejoin into a single space-separated string.

    This final string is what gets passed into the TF-IDF vectorizer,
    since scikit-learn's TfidfVectorizer expects plain text strings.

    Args:
        raw_text (str): unprocessed resume or job description text.

    Returns:
        str: fully preprocessed text, ready for vectorization.
    """
    cleaned = clean_text(raw_text)
    tokens = tokenize(cleaned)
    filtered_tokens = remove_stopwords(tokens)
    return " ".join(filtered_tokens)


def extract_keywords(raw_text, top_n=15):
    """
    Extracts the most frequent meaningful keywords from a piece of
    text. Used to give recruiters a quick "at a glance" summary of
    a resume or job description's core topics.

    Args:
        raw_text (str): unprocessed text.
        top_n (int): number of top keywords to return.

    Returns:
        list[str]: the top_n most frequent keywords, ordered by
                    frequency (highest first).
    """
    cleaned = clean_text(raw_text)
    tokens = tokenize(cleaned)
    filtered_tokens = remove_stopwords(tokens)

    frequency = {}
    for token in filtered_tokens:
        frequency[token] = frequency.get(token, 0) + 1

    sorted_tokens = sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    return [word for word, count in sorted_tokens[:top_n]]
