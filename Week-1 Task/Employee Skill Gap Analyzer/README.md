# Employee Skills Gap Analyzer

A desktop application built with **Python, PyQt5, SQLite, Pandas and Matplotlib**
that helps HR departments identify employee skill gaps, calculate readiness
scores, classify employees, recommend training courses and analyze
department-wide performance.

## Project Info

- **Course Project:** BS Artificial Intelligence – Semester 2
- **Type:** Desktop GUI Application
- **Domain:** Human Resource Analytics / Applied AI Concepts (rule-based
  reasoning, scoring algorithms, statistical analysis)

## Problem Statement

Companies often struggle to identify employee skill gaps manually. HR
departments need a tool that automatically compares employee skills against
the skills required for their job, highlights missing competencies,
calculates a readiness score, recommends relevant training courses, and
gives management a clear, visual, department-wide picture of workforce
readiness.

## Features

- Splash screen with loading animation
- Modern dark-themed dashboard with statistic cards and charts
- Full Employee Management (add / edit / delete / search / filter / sort)
- Full Skill Management (skills catalog + required skills per department)
- Skills Gap Analysis engine with color-coded gap indicators
- Readiness Score calculation and Employee Classification
- Rule-Based Training Recommendation engine
- Employee Ranking (leaderboard style)
- Department-wide Readiness Analytics with multiple chart types
- Statistical Analysis (mean, median, std. deviation, distribution)
- Report export to Excel (.xlsx) and PDF
- Clean, modular, well-commented, object-oriented code base

## Technology Stack

| Layer            | Technology     |
|------------------|----------------|
| GUI              | PyQt5          |
| Database         | SQLite3        |
| Data Processing  | Pandas / NumPy |
| Charts           | Matplotlib     |
| Reports          | openpyxl, reportlab |

## Project Structure

```
skillgap/
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── algorithms/
│   ├── __init__.py
│   └── analyzer.py                 # All core algorithms (gap, readiness, etc.)
├── assets/
│   └── .gitkeep                    # UI assets directory
├── data/
│   └── .gitkeep                    # Database directory (skillgap.db generates here)
├── database/
│   ├── __init__.py
│   ├── db_manager.py               # All SQL/database access logic
│   └── seed_data.py                # Auto-creates & seeds the SQLite DB
└── ui/
    ├── __init__.py
    ├── styles.py                   # Central QSS stylesheet (dark + blue theme)
    ├── splash_screen.py            # Splash / loading screen
    ├── main_window.py              # Main window + sidebar navigation
    ├── dashboard.py                # Dashboard page with KPI cards + charts
    ├── employee_management.py      # Employee CRUD page
    ├── skill_management.py         # Skill & required-skill CRUD page
    ├── gap_analysis.py             # Skill gap analysis page
    ├── training_recommendations.py # Training recommendation page
    ├── department_analytics.py     # Department analytics + charts
    ├── reports.py                  # Report export page (Excel / PDF)
    ├── widgets.py                  # Custom reusable UI widgets
    └── about.py                    # About page
```

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

The database (`data/skillgap.db`) is created and populated automatically
with realistic sample data the first time the application is launched.

## Core Algorithms Implemented

1. **Skills Gap Analysis** – compares each employee's proficiency against the
   required proficiency for their department/position.
2. **Readiness Score Calculation** – weighted percentage showing how ready an
   employee is for their current role.
3. **Employee Classification** – rule-based classification into
   Expert / Proficient / Developing / Needs Training / Critical Gap.
4. **Rule-Based Training Recommendation** – recommends the most relevant
   training course for every skill gap, prioritized by gap severity.
5. **Employee Ranking** – ranks employees company-wide and per department.
6. **Department Readiness Analysis** – aggregates employee readiness scores
   per department.
7. **Search / Filter / Sort** – across employees, skills and gap tables.
8. **Statistical Analysis** – mean, median, standard deviation, and
   distribution of readiness scores using pandas/numpy.

## Author

Student Project – BS Artificial Intelligence, Semester 2.
