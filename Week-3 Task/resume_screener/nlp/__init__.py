"""
nlp package
------------------------------------------------------------------
Contains all Natural Language Processing logic used by Resume
Screener Pro:

    - text_extraction.py  : reading resume text from uploaded files
    - preprocessing.py    : cleaning & tokenizing raw text
    - similarity.py       : TF-IDF vectorization, cosine similarity,
                             ranking, and keyword matching

Keeping NLP logic completely separate from the GUI and database
layers makes the project modular and easy to test/extend.
------------------------------------------------------------------
"""
