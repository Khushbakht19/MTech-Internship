"""
ml/preprocessor.py
-------------------
Text preprocessing utilities used before any message is fed into the
TF-IDF vectorizer / Naive Bayes classifier.

Cleaning an SMS message before vectorizing it is important because raw
text is full of "noise" (punctuation, links, numbers, capitalization
differences) that would otherwise confuse the model into thinking
"FREE!!!" and "free" are unrelated words.

This module intentionally avoids external NLP libraries like NLTK to
keep the dependency list small (the project brief only allows Python,
Tkinter, SQLite, Scikit-learn, Pandas, and Matplotlib) -- a small
built-in stopword list is used instead.
"""

import re
import string

import config


# A small, common English stopword list. These are words that appear in
# almost every sentence and carry very little meaning for spam detection
# (e.g. "the", "is", "and"). Removing them lets the model focus on the
# words that actually distinguish spam from legitimate messages.
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
    "us", "them", "my", "your", "his", "its", "our", "their",
    "this", "that", "these", "those", "am", "and", "or", "but", "if",
    "then", "so", "to", "of", "in", "on", "at", "by", "for", "with",
    "about", "as", "into", "than", "too", "very", "can", "will",
    "just", "do", "does", "did", "not", "no", "nor", "up", "down",
    "out", "off", "over", "under", "again", "further", "here", "there",
    "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "only", "own",
    "same", "s", "t", "d", "ll", "m", "o", "re", "ve", "y",
}

URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+|\b\S+\.(com|net|org|biz|co)\S*\b)")


def clean_text(message_text):
    """
    Clean a raw SMS message so it is ready for TF-IDF vectorization.

    Steps:
        1. Lowercase everything.
        2. Replace URLs with a single placeholder token "urlplaceholder"
           (spam messages very often contain links, so keeping a signal
           that *a* link existed is actually useful for the model).
        3. Strip punctuation.
        4. Strip standalone digits.
        5. Remove common stopwords.
        6. Collapse extra whitespace.

    Returns a single cleaned string (not a list of tokens), since that
    is the input format scikit-learn's TfidfVectorizer expects.
    """
    if not message_text:
        return ""

    text = message_text.lower()
    text = URL_PATTERN.sub(" urlplaceholder ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\b\d+\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = [word for word in text.split(" ") if word and word not in STOPWORDS]
    return " ".join(tokens)


def tokenize(message_text):
    """Return the cleaned message as a list of individual word tokens."""
    cleaned = clean_text(message_text)
    return cleaned.split() if cleaned else []


def extract_keywords(message_text):
    """
    Scan the ORIGINAL (uncleaned) message for suspicious keywords defined
    in config.SUSPICIOUS_KEYWORDS. Using the original text (rather than
    the cleaned version) lets multi-word phrases like "click here" or
    "act now" still be matched correctly.

    Returns a list of the distinct keywords found, in the order they
    appear in config.SUSPICIOUS_KEYWORDS.
    """
    lowered = message_text.lower()
    found = [keyword for keyword in config.SUSPICIOUS_KEYWORDS if keyword in lowered]
    return found


def extract_keywords_string(message_text):
    """Convenience wrapper returning the detected keywords as 'kw1, kw2, kw3'."""
    return ", ".join(extract_keywords(message_text))
