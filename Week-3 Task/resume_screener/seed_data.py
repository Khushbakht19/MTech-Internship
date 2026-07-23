"""
seed_data.py
------------------------------------------------------------------
Populates the Resume Screener Pro database with realistic sample
data the very first time the application is launched.

Generates:
    - 18 sample candidates (with realistic resume text)
    - 6 sample job postings
    - Screening history records, with match scores computed using
      real TF-IDF + Cosine Similarity (the same technique used by
      the live application in nlp/similarity.py), so the seeded
      analytics look authentic rather than random.
------------------------------------------------------------------
"""

import sqlite3
import random
from datetime import datetime, timedelta

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==================================================================
# SAMPLE CANDIDATES
# ==================================================================
CANDIDATES = [
    {
        "full_name": "Ayesha Khan", "email": "ayesha.khan@example.com", "phone": "0301-1234567",
        "skills": "Python, Machine Learning, Pandas, Scikit-learn, Data Visualization",
        "experience_years": 2.5, "education": "BS Artificial Intelligence",
        "resume_text": "Data scientist with 2.5 years of experience building machine learning models "
                        "using python pandas and scikit-learn. Skilled in data cleaning, exploratory "
                        "data analysis, feature engineering, and building classification and regression "
                        "models. Experienced with data visualization using matplotlib and seaborn. "
                        "Completed projects on customer churn prediction and sales forecasting."
    },
    {
        "full_name": "Bilal Ahmed", "email": "bilal.ahmed@example.com", "phone": "0302-2345678",
        "skills": "Python, Django, REST API, PostgreSQL, Docker",
        "experience_years": 3, "education": "BS Computer Science",
        "resume_text": "Backend python developer with 3 years of experience building rest apis using "
                        "django and flask. Strong knowledge of postgresql database design, docker "
                        "containerization, and deploying scalable web services. Worked on e-commerce "
                        "backend systems handling thousands of daily transactions."
    },
    {
        "full_name": "Sara Malik", "email": "sara.malik@example.com", "phone": "0303-3456789",
        "skills": "Machine Learning, Deep Learning, TensorFlow, NLP, Python",
        "experience_years": 4, "education": "MS Data Science",
        "resume_text": "Machine learning engineer with 4 years of experience in deep learning and "
                        "natural language processing. Built text classification and sentiment analysis "
                        "systems using tensorflow and scikit-learn. Experience with tf-idf vectorization, "
                        "word embeddings, and deploying ml models into production pipelines."
    },
    {
        "full_name": "Hamza Tariq", "email": "hamza.tariq@example.com", "phone": "0304-4567890",
        "skills": "React, JavaScript, HTML, CSS, UI/UX Design",
        "experience_years": 2, "education": "BS Software Engineering",
        "resume_text": "Frontend developer with 2 years of experience creating responsive web "
                        "applications using react javascript html and css. Passionate about ui ux design "
                        "and building clean modern user interfaces. Experience with redux state "
                        "management and integrating rest apis into frontend applications."
    },
    {
        "full_name": "Zainab Hussain", "email": "zainab.hussain@example.com", "phone": "0305-5678901",
        "skills": "AWS, Docker, Kubernetes, CI/CD, Linux",
        "experience_years": 3.5, "education": "BS Computer Science",
        "resume_text": "Devops engineer with 3.5 years of experience managing cloud infrastructure on "
                        "aws. Skilled in docker kubernetes container orchestration and building ci cd "
                        "pipelines using jenkins and github actions. Strong linux administration "
                        "background and experience automating deployment workflows."
    },
    {
        "full_name": "Usman Riaz", "email": "usman.riaz@example.com", "phone": "0306-6789012",
        "skills": "Python, SQL, Data Analysis, Excel, Power BI",
        "experience_years": 1.5, "education": "BBA Business Analytics",
        "resume_text": "Business analyst with 1.5 years of experience performing data analysis using "
                        "python sql and excel. Built interactive dashboards in power bi for tracking "
                        "sales and operational kpis. Strong communication skills and experience "
                        "presenting insights to stakeholders."
    },
    {
        "full_name": "Fatima Noor", "email": "fatima.noor@example.com", "phone": "0307-7890123",
        "skills": "Python, Machine Learning, NLP, TF-IDF, Cosine Similarity",
        "experience_years": 1, "education": "BS Artificial Intelligence",
        "resume_text": "Recent artificial intelligence graduate skilled in python and machine learning. "
                        "Academic projects include a resume screening system using tf-idf vectorization "
                        "and cosine similarity, and a spam email classifier using natural language "
                        "processing techniques. Familiar with scikit-learn pandas and numpy."
    },
    {
        "full_name": "Ali Raza", "email": "ali.raza@example.com", "phone": "0308-8901234",
        "skills": "Java, Spring Boot, MySQL, Microservices",
        "experience_years": 3, "education": "BS Software Engineering",
        "resume_text": "Java backend developer with 3 years of experience building microservices "
                        "using spring boot. Strong knowledge of mysql database design and restful api "
                        "development. Experience working in agile teams and using git for version "
                        "control on enterprise applications."
    },
    {
        "full_name": "Mahnoor Iqbal", "email": "mahnoor.iqbal@example.com", "phone": "0309-9012345",
        "skills": "Python, Deep Learning, Computer Vision, OpenCV, PyTorch",
        "experience_years": 2.5, "education": "MS Artificial Intelligence",
        "resume_text": "Computer vision engineer with 2.5 years of experience in deep learning using "
                        "pytorch and opencv. Built object detection and image classification models for "
                        "real time applications. Strong foundation in convolutional neural networks and "
                        "model optimization for deployment."
    },
    {
        "full_name": "Danish Aslam", "email": "danish.aslam@example.com", "phone": "0310-0123456",
        "skills": "Python, Flask, MongoDB, REST API",
        "experience_years": 1.5, "education": "BS Computer Science",
        "resume_text": "Junior python developer with 1.5 years of experience building rest apis using "
                        "flask and mongodb. Comfortable working with json data structures and "
                        "integrating third party apis. Eager to learn new backend technologies and "
                        "improve application performance."
    },
    {
        "full_name": "Komal Yousaf", "email": "komal.yousaf@example.com", "phone": "0311-1234098",
        "skills": "Data Analysis, Python, Pandas, NumPy, Statistics",
        "experience_years": 2, "education": "BS Statistics",
        "resume_text": "Data analyst with 2 years of experience using python pandas and numpy for "
                        "statistical analysis. Skilled in hypothesis testing regression analysis and "
                        "data cleaning. Experience creating clear reports and visualizations to support "
                        "business decision making."
    },
    {
        "full_name": "Talha Farooq", "email": "talha.farooq@example.com", "phone": "0312-2345109",
        "skills": "React, Node.js, Express, MongoDB, JavaScript",
        "experience_years": 3, "education": "BS Computer Science",
        "resume_text": "Full stack javascript developer with 3 years of experience using react on the "
                        "frontend and node.js express and mongodb on the backend. Built several full "
                        "stack web applications from scratch including authentication and payment "
                        "integration. Comfortable with agile development practices."
    },
    {
        "full_name": "Iqra Shahid", "email": "iqra.shahid@example.com", "phone": "0313-3456210",
        "skills": "Machine Learning, Python, Scikit-learn, Data Preprocessing",
        "experience_years": 1, "education": "BS Artificial Intelligence",
        "resume_text": "Aspiring machine learning engineer with academic experience in python and "
                        "scikit-learn. Completed coursework projects on text preprocessing tf-idf "
                        "feature extraction and building classification models. Strong understanding of "
                        "data cleaning and preprocessing pipelines for nlp applications."
    },
    {
        "full_name": "Omar Sheikh", "email": "omar.sheikh@example.com", "phone": "0314-4567321",
        "skills": "AWS, Terraform, Docker, Linux, Networking",
        "experience_years": 4, "education": "BS Information Technology",
        "resume_text": "Cloud infrastructure engineer with 4 years of experience deploying and "
                        "managing infrastructure on aws using terraform. Skilled in docker containers "
                        "linux system administration and network security. Experience automating "
                        "infrastructure provisioning and reducing deployment time."
    },
    {
        "full_name": "Rabia Saeed", "email": "rabia.saeed@example.com", "phone": "0315-5678432",
        "skills": "SQL, Data Analysis, Power BI, Excel, Business Intelligence",
        "experience_years": 2.5, "education": "BBA Business Analytics",
        "resume_text": "Business intelligence analyst with 2.5 years of experience writing complex sql "
                        "queries and building power bi dashboards. Strong analytical skills with "
                        "experience translating business requirements into data driven insights for "
                        "management reporting."
    },
    {
        "full_name": "Faizan Qureshi", "email": "faizan.qureshi@example.com", "phone": "0316-6789543",
        "skills": "Python, Machine Learning, NLP, spaCy, Text Classification",
        "experience_years": 2, "education": "BS Artificial Intelligence",
        "resume_text": "Nlp engineer with 2 years of experience building text classification and named "
                        "entity recognition systems using python and spacy. Experience with text "
                        "preprocessing tokenization stopword removal and tf-idf feature extraction for "
                        "downstream machine learning models."
    },
    {
        "full_name": "Nimra Aziz", "email": "nimra.aziz@example.com", "phone": "0317-7890654",
        "skills": "HTML, CSS, JavaScript, React, Figma",
        "experience_years": 1.5, "education": "BS Software Engineering",
        "resume_text": "Junior frontend developer with 1.5 years of experience building responsive "
                        "websites with html css and javascript. Familiar with react components and "
                        "figma for ui design handoff. Strong eye for clean layout spacing and modern "
                        "typography in web interfaces."
    },
    {
        "full_name": "Adeel Nasir", "email": "adeel.nasir@example.com", "phone": "0318-8901765",
        "skills": "Python, Machine Learning, Data Science, Pandas, Model Deployment",
        "experience_years": 3, "education": "MS Data Science",
        "resume_text": "Data scientist with 3 years of experience developing end to end machine "
                        "learning pipelines using python and pandas. Experience with model training "
                        "evaluation and deployment using flask apis. Worked on recommendation systems "
                        "and resume ranking models using cosine similarity."
    },
]

# ==================================================================
# SAMPLE JOB POSTINGS
# ==================================================================
JOBS = [
    {
        "job_title": "Data Scientist", "department": "Data & Analytics",
        "required_skills": "Python, Machine Learning, Pandas, Scikit-learn, Statistics",
        "experience_required": 2,
        "job_description": "We are looking for a data scientist skilled in python and machine "
                            "learning to build predictive models. Responsibilities include data "
                            "cleaning, feature engineering, model training with scikit-learn, and "
                            "presenting insights using data visualization. Experience with pandas, "
                            "statistics, and data preprocessing is required."
    },
    {
        "job_title": "Machine Learning Engineer", "department": "AI & Research",
        "required_skills": "Python, Deep Learning, TensorFlow, NLP, Model Deployment",
        "experience_required": 3,
        "job_description": "Seeking a machine learning engineer with strong python skills to design "
                            "and deploy deep learning models. Must have experience with tensorflow, "
                            "natural language processing, text classification, and deploying models "
                            "into production. Knowledge of tf-idf and cosine similarity is a plus."
    },
    {
        "job_title": "Python Backend Developer", "department": "Engineering",
        "required_skills": "Python, Django, Flask, REST API, PostgreSQL",
        "experience_required": 2,
        "job_description": "We need a backend developer with solid python experience to build and "
                            "maintain rest apis using django or flask. Must be comfortable with "
                            "postgresql database design, docker containers, and writing clean "
                            "maintainable code following best practices."
    },
    {
        "job_title": "Frontend Developer", "department": "Engineering",
        "required_skills": "React, JavaScript, HTML, CSS, UI/UX",
        "experience_required": 1.5,
        "job_description": "Looking for a frontend developer experienced with react javascript html "
                            "and css to build responsive modern web interfaces. Should have an eye for "
                            "ui ux design, clean layout, and be comfortable integrating rest apis into "
                            "frontend applications."
    },
    {
        "job_title": "DevOps Engineer", "department": "Infrastructure",
        "required_skills": "AWS, Docker, Kubernetes, CI/CD, Linux",
        "experience_required": 3,
        "job_description": "We are hiring a devops engineer to manage cloud infrastructure on aws, "
                            "build ci cd pipelines, and maintain docker and kubernetes based "
                            "deployments. Strong linux administration and automation skills are "
                            "required for this role."
    },
    {
        "job_title": "Business Data Analyst", "department": "Business Intelligence",
        "required_skills": "SQL, Python, Excel, Power BI, Data Analysis",
        "experience_required": 1.5,
        "job_description": "Seeking a business data analyst to analyze company data using sql and "
                            "python, and build reporting dashboards in power bi and excel. Strong "
                            "analytical thinking and the ability to communicate insights to non "
                            "technical stakeholders is essential."
    },
]


# ==================================================================
# LIGHTWEIGHT TEXT HELPERS (used only for seeding realistic scores)
# ==================================================================
def _clean_text_basic(text):
    """
    Minimal cleaning used only for seed-time similarity computation.
    The full cleaning/preprocessing pipeline used by the live app
    lives in nlp/preprocessing.py.
    """
    text = text.lower()
    text = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text)
    return " ".join(text.split())


def _compute_match_score(resume_text, job_description):
    """
    Computes a match score (0-100) between a resume and a job
    description using TF-IDF vectorization and cosine similarity -
    the same core NLP technique used throughout the application.
    """
    documents = [_clean_text_basic(resume_text), _clean_text_basic(job_description)]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 2)


def _extract_matched_keywords(candidate_skills, required_skills):
    """
    Returns a comma separated string of skills that appear in both
    the candidate's skill list and the job's required skill list.
    """
    candidate_set = {skill.strip().lower() for skill in candidate_skills.split(",")}
    required_set = {skill.strip().lower() for skill in required_skills.split(",")}
    matched = candidate_set.intersection(required_set)
    return ", ".join(sorted(matched)) if matched else "No direct keyword matches"


# ==================================================================
# MAIN SEED FUNCTION
# ==================================================================
def seed_database(db_path):
    """
    Populates an empty database with sample candidates, jobs, and a
    realistic screening history. Called automatically by
    DatabaseManager.initialize_database() the first time the app runs.
    """
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    now = datetime.now()

    # --------------------------------------------------------------
    # Insert candidates
    # --------------------------------------------------------------
    candidate_ids = []
    for candidate in CANDIDATES:
        cursor.execute(
            """
            INSERT INTO candidates
                (full_name, email, phone, skills, experience_years,
                 education, resume_text, file_name, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate["full_name"], candidate["email"], candidate["phone"],
                candidate["skills"], candidate["experience_years"],
                candidate["education"], candidate["resume_text"],
                f"{candidate['full_name'].replace(' ', '_').lower()}_resume.txt",
                (now - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        candidate_ids.append(cursor.lastrowid)

    # --------------------------------------------------------------
    # Insert jobs
    # --------------------------------------------------------------
    job_ids = []
    for job in JOBS:
        cursor.execute(
            """
            INSERT INTO jobs
                (job_title, department, required_skills,
                 experience_required, job_description, date_posted)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                job["job_title"], job["department"], job["required_skills"],
                job["experience_required"], job["job_description"],
                (now - timedelta(days=random.randint(5, 45))).strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        job_ids.append(cursor.lastrowid)

    connection.commit()

    # --------------------------------------------------------------
    # Generate realistic screening history
    # For each job, screen a random subset of candidates and rank
    # them by their computed TF-IDF cosine similarity match score.
    # --------------------------------------------------------------
    for job_index, job_id in enumerate(job_ids):
        job_data = JOBS[job_index]

        # Screen between 8 and 14 random candidates per job
        sample_size = random.randint(8, min(14, len(CANDIDATES)))
        sampled_indices = random.sample(range(len(CANDIDATES)), sample_size)

        job_results = []
        for candidate_index in sampled_indices:
            candidate_data = CANDIDATES[candidate_index]
            candidate_id = candidate_ids[candidate_index]

            score = _compute_match_score(
                candidate_data["resume_text"], job_data["job_description"]
            )
            keywords = _extract_matched_keywords(
                candidate_data["skills"], job_data["required_skills"]
            )
            job_results.append((candidate_id, score, keywords))

        # Rank candidates for this job from highest to lowest score
        job_results.sort(key=lambda item: item[1], reverse=True)

        for rank, (candidate_id, score, keywords) in enumerate(job_results, start=1):
            screening_date = (now - timedelta(days=random.randint(0, 30),
                                               hours=random.randint(0, 23))).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """
                INSERT INTO screening_history
                    (candidate_id, job_id, match_score, matched_keywords,
                     rank_position, screening_date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (candidate_id, job_id, score, keywords, rank, screening_date)
            )

    connection.commit()
    connection.close()

    print("[seed_data] Sample database created successfully:")
    print(f"  - {len(CANDIDATES)} candidates inserted")
    print(f"  - {len(JOBS)} jobs inserted")
    print("  - Screening history generated using TF-IDF + Cosine Similarity")
