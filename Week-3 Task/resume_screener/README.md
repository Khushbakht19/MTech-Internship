# Resume Screener Pro (v2)

An AI-powered desktop application that helps recruiters screen, rank,
and analyze candidate resumes against job descriptions using NLP.

## Problem Statement

Recruiters receive hundreds of resumes per job opening and cannot
manually review every CV. Resume Screener Pro automates this process
using TF-IDF vectorization and Cosine Similarity to score how well
each resume matches a job description, then ranks candidates
accordingly.

## Technology Used

- Python 3
- Tkinter / ttk (GUI)
- SQLite (database)
- Scikit-learn (TF-IDF, Cosine Similarity)
- Pandas (statistical analysis)
- Matplotlib (charts & PDF reports)

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

The database is created and seeded with realistic sample data
automatically on first run (`seed_data.py`) - no manual setup needed.

## Project Structure

```
resume_screener/
├── main.py             Entry point (splash screen -> main window)
├── config.py            Theme, fonts, paths, constants
├── database.py          SQLite schema + DatabaseManager (all CRUD/queries)
├── seed_data.py         Sample data generator (first-run only)
├── gui/                 All Tkinter pages and UI components
├── nlp/                 Text extraction, preprocessing, TF-IDF/similarity
└── utils/               Formatting, CSV/PDF export, form validation
```

## Modules

Splash Screen · Dashboard · Candidate Management · Job Management ·
Resume Screening · Screening History · Analytics · Reports · About

## Core NLP Pipeline

1. **Text Extraction** - reads resume content from `.txt` files (and
   `.pdf` / `.docx` if the optional `PyPDF2` / `python-docx` libraries
   are installed), or accepts pasted resume text directly.
2. **Text Cleaning & Preprocessing** - lowercasing, punctuation/number
   removal, tokenization, and stopword removal (`nlp/preprocessing.py`).
3. **TF-IDF Vectorization** - converts resume and job description text
   into weighted term-frequency vectors using scikit-learn's
   `TfidfVectorizer`.
4. **Cosine Similarity** - measures the similarity between the resume
   vector and job description vector, scaled to a 0-100 match score.
5. **Ranking** - candidates are sorted by match score, highest first.
6. **Keyword Matching** - candidate skills are compared against a
   job's required skills to surface overlapping keywords.

## Database Schema

- **candidates** - full name, contact info, skills, experience,
  education, resume text.
- **jobs** - job title, department, required skills, experience
  required, job description.
- **screening_history** - candidate/job pair, match score, matched
  keywords, rank position, screening date.

## Notes

- Optional PDF/DOCX resume upload requires `PyPDF2` / `python-docx`
  (not included in requirements.txt to keep the stack minimal per the
  assignment brief). Without them, `.txt` upload and manual paste
  always work.
- PDF report export uses Matplotlib's PDF backend, so no extra PDF
  library is required for that feature.
- The database and sample data are generated automatically on first
  launch - there is no manual setup step required before grading.

## Author

BS Artificial Intelligence Student (Semester 2) - 2026
