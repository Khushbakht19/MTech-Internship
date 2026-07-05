"""
seed_data.py
------------
This script populates a brand-new (empty) database with realistic,
hand-designed sample data so the application is immediately usable and
demonstrable without requiring the user to manually type in data first.

It is only ever called once - the very first time the application is
launched and no database file exists yet (see main.py).
"""

import random
from database.db_manager import DatabaseManager


def seed_database(db: DatabaseManager):
    """
    Populates every table with realistic sample records.
    `db` is an already-initialized DatabaseManager whose tables have
    already been created.
    """
    conn = db.get_connection()
    cur = conn.cursor()

    # ------------------------------------------------------------------
    # 1. DEPARTMENTS
    # ------------------------------------------------------------------
    departments = [
        ("Software Engineering", "Builds and maintains company software products"),
        ("Data Science", "Extracts insights and builds ML models from company data"),
        ("Human Resources", "Manages recruitment, training and employee relations"),
        ("Marketing", "Handles branding, campaigns and market research"),
        ("Finance", "Manages budgeting, accounting and financial reporting"),
    ]
    cur.executemany(
        "INSERT INTO departments (name, description) VALUES (?, ?)", departments
    )

    dept_ids = {}
    for row in cur.execute("SELECT department_id, name FROM departments"):
        dept_ids[row["name"]] = row["department_id"]

    # ------------------------------------------------------------------
    # 2. SKILLS
    # ------------------------------------------------------------------
    skills = [
        ("Python Programming", "Technical"),
        ("SQL & Databases", "Technical"),
        ("Machine Learning", "Technical"),
        ("Data Visualization", "Technical"),
        ("Cloud Computing (AWS/Azure)", "Technical"),
        ("Software Testing", "Technical"),
        ("Web Development", "Technical"),
        ("Statistical Analysis", "Technical"),
        ("Project Management", "Management"),
        ("Communication Skills", "Soft Skill"),
        ("Leadership", "Management"),
        ("Recruitment & Onboarding", "HR"),
        ("Performance Management", "HR"),
        ("Digital Marketing", "Marketing"),
        ("Content Strategy", "Marketing"),
        ("SEO & Analytics", "Marketing"),
        ("Financial Modeling", "Finance"),
        ("Budgeting & Forecasting", "Finance"),
        ("Risk Management", "Finance"),
        ("Excel & Reporting", "Technical"),
    ]
    cur.executemany("INSERT INTO skills (name, category) VALUES (?, ?)", skills)

    skill_ids = {}
    for row in cur.execute("SELECT skill_id, name FROM skills"):
        skill_ids[row["name"]] = row["skill_id"]

    # ------------------------------------------------------------------
    # 3. REQUIRED SKILLS (per department + position)
    # ------------------------------------------------------------------
    # Format: (department, position, {skill_name: required_level})
    requirements = [
        ("Software Engineering", "Software Engineer", {
            "Python Programming": 4, "SQL & Databases": 3, "Web Development": 3,
            "Software Testing": 3, "Cloud Computing (AWS/Azure)": 3,
            "Communication Skills": 3,
        }),
        ("Software Engineering", "Senior Software Engineer", {
            "Python Programming": 5, "SQL & Databases": 4, "Web Development": 4,
            "Software Testing": 4, "Cloud Computing (AWS/Azure)": 4,
            "Leadership": 3, "Project Management": 3,
        }),
        ("Data Science", "Data Scientist", {
            "Python Programming": 4, "Machine Learning": 4, "Statistical Analysis": 4,
            "Data Visualization": 3, "SQL & Databases": 3, "Communication Skills": 3,
        }),
        ("Data Science", "ML Engineer", {
            "Python Programming": 5, "Machine Learning": 5, "Cloud Computing (AWS/Azure)": 4,
            "SQL & Databases": 3, "Software Testing": 3,
        }),
        ("Human Resources", "HR Executive", {
            "Recruitment & Onboarding": 4, "Performance Management": 3,
            "Communication Skills": 4, "Excel & Reporting": 3,
        }),
        ("Human Resources", "HR Manager", {
            "Recruitment & Onboarding": 4, "Performance Management": 5,
            "Leadership": 4, "Communication Skills": 5, "Project Management": 3,
        }),
        ("Marketing", "Marketing Executive", {
            "Digital Marketing": 4, "Content Strategy": 3, "SEO & Analytics": 3,
            "Communication Skills": 4,
        }),
        ("Marketing", "Marketing Manager", {
            "Digital Marketing": 5, "Content Strategy": 4, "SEO & Analytics": 4,
            "Leadership": 4, "Project Management": 3,
        }),
        ("Finance", "Financial Analyst", {
            "Financial Modeling": 4, "Budgeting & Forecasting": 4,
            "Excel & Reporting": 4, "Risk Management": 3,
        }),
        ("Finance", "Finance Manager", {
            "Financial Modeling": 5, "Budgeting & Forecasting": 5,
            "Risk Management": 4, "Leadership": 4, "Communication Skills": 3,
        }),
    ]

    for dept_name, position, skill_map in requirements:
        for skill_name, level in skill_map.items():
            cur.execute("""
                INSERT INTO required_skills (department_id, position, skill_id, required_level)
                VALUES (?, ?, ?, ?)
            """, (dept_ids[dept_name], position, skill_ids[skill_name], level))

    # ------------------------------------------------------------------
    # 4. EMPLOYEES
    # ------------------------------------------------------------------
    employees = [
        # (full_name, email, position, department, hire_date)
        ("Ahmed Raza", "ahmed.raza@company.com", "Software Engineer", "Software Engineering", "2022-03-14"),
        ("Sara Khan", "sara.khan@company.com", "Senior Software Engineer", "Software Engineering", "2019-07-01"),
        ("Bilal Ahmed", "bilal.ahmed@company.com", "Software Engineer", "Software Engineering", "2023-01-10"),
        ("Hina Malik", "hina.malik@company.com", "Senior Software Engineer", "Software Engineering", "2018-11-20"),
        ("Usman Tariq", "usman.tariq@company.com", "Software Engineer", "Software Engineering", "2021-06-05"),
        ("Ayesha Noor", "ayesha.noor@company.com", "Data Scientist", "Data Science", "2020-09-15"),
        ("Fahad Siddiqui", "fahad.siddiqui@company.com", "ML Engineer", "Data Science", "2021-02-18"),
        ("Mahnoor Iqbal", "mahnoor.iqbal@company.com", "Data Scientist", "Data Science", "2022-08-22"),
        ("Zainab Hussain", "zainab.hussain@company.com", "ML Engineer", "Data Science", "2019-12-01"),
        ("Omar Farooq", "omar.farooq@company.com", "HR Executive", "Human Resources", "2022-05-09"),
        ("Nadia Sheikh", "nadia.sheikh@company.com", "HR Manager", "Human Resources", "2017-04-11"),
        ("Hassan Raza", "hassan.raza@company.com", "HR Executive", "Human Resources", "2023-02-20"),
        ("Mariam Yousaf", "mariam.yousaf@company.com", "Marketing Executive", "Marketing", "2021-10-03"),
        ("Ali Hamza", "ali.hamza@company.com", "Marketing Manager", "Marketing", "2018-06-17"),
        ("Sana Aslam", "sana.aslam@company.com", "Marketing Executive", "Marketing", "2022-11-29"),
        ("Talha Javed", "talha.javed@company.com", "Financial Analyst", "Finance", "2020-01-25"),
        ("Rabia Anwar", "rabia.anwar@company.com", "Finance Manager", "Finance", "2016-09-08"),
        ("Kamran Shahid", "kamran.shahid@company.com", "Financial Analyst", "Finance", "2023-04-16"),
        ("Iqra Bashir", "iqra.bashir@company.com", "Software Engineer", "Software Engineering", "2023-07-01"),
        ("Waqas Ali", "waqas.ali@company.com", "Data Scientist", "Data Science", "2021-03-30"),
    ]

    employee_ids = []
    for name, email, position, dept_name, hire_date in employees:
        cur.execute("""
            INSERT INTO employees (full_name, email, position, department_id, hire_date)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, position, dept_ids[dept_name], hire_date))
        employee_ids.append((cur.lastrowid, position, dept_name))

    # ------------------------------------------------------------------
    # 5. EMPLOYEE SKILLS (randomized but realistic proficiency levels)
    # ------------------------------------------------------------------
    # We build proficiency levels so that most employees are reasonably
    # close to their requirement, but a few clearly show gaps - this makes
    # the Gap Analysis / Dashboard results look realistic and meaningful.
    #
    # Real HR data is never "everyone is fine" - newer hires and a couple
    # of underperforming employees are what make the Dashboard's
    # "Employees Needing Training" card and the Training Recommendations
    # page actually show something. So we give a handful of employees
    # (mostly the recently hired ones) a weaker skill profile on purpose.
    random.seed(42)  # fixed seed -> same "random" sample data every run

    req_lookup = {}
    for dept_name, position, skill_map in requirements:
        req_lookup[(dept_name, position)] = skill_map

    # Performance tier per employee (by name). "normal" employees are not
    # listed here and use the default balanced distribution below.
    performance_tier = {
        "Iqra Bashir": "critical",        # newest hire (2023-07) -> still learning the role
        "Kamran Shahid": "critical",      # newest hire in Finance
        "Bilal Ahmed": "needs_training",  # hired 2023, still ramping up
        "Hassan Raza": "needs_training",  # hired 2023, still ramping up
        "Sana Aslam": "developing",       # hired late 2022, getting there
    }

    # Offset ranges per tier - subtracted from the required level to get
    # the employee's actual level (then clipped to the valid 0-5 range).
    tier_offsets = {
        "critical": [-4, -3, -3, -2],
        "needs_training": [-2, -2, -1, -1],
        "developing": [-2, -1, -1],
        "normal": [-2, -1, -1, 0, 0, 0, 1, 1],
    }

    # Map employee_id -> full_name using the original `employees` list,
    # which was inserted in the same order as `employee_ids` above.
    name_by_id = {emp_id: name for (name, _, _, _, _), (emp_id, _, _) in zip(employees, employee_ids)}

    for emp_id, position, dept_name in employee_ids:
        full_name = name_by_id.get(emp_id, "")
        tier = performance_tier.get(full_name, "normal")
        offsets = tier_offsets[tier]

        skill_map = req_lookup.get((dept_name, position), {})
        for skill_name, required_level in skill_map.items():
            # Simulate realistic variance: employee's actual level is the
            # required level plus/minus a random offset, clipped to 0-5.
            offset = random.choice(offsets)
            actual_level = max(0, min(5, required_level + offset))
            cur.execute("""
                INSERT INTO employee_skills (employee_id, skill_id, proficiency_level)
                VALUES (?, ?, ?)
            """, (emp_id, skill_ids[skill_name], actual_level))

    # ------------------------------------------------------------------
    # 6. TRAINING COURSES (one or two per skill)
    # ------------------------------------------------------------------
    training_courses = [
        ("Python Programming", "Python for Professionals", "Coursera", 30, 4),
        ("Python Programming", "Advanced Python Bootcamp", "Udemy", 40, 5),
        ("SQL & Databases", "SQL Mastery for Data Roles", "Udemy", 20, 4),
        ("Machine Learning", "Machine Learning Specialization", "Coursera", 60, 5),
        ("Machine Learning", "Applied ML with Python", "edX", 45, 4),
        ("Data Visualization", "Data Visualization with Matplotlib & Power BI", "Udemy", 15, 3),
        ("Cloud Computing (AWS/Azure)", "AWS Certified Solutions Architect", "AWS Training", 50, 5),
        ("Software Testing", "Software Testing Fundamentals", "Udemy", 20, 3),
        ("Web Development", "Full-Stack Web Development", "Coursera", 60, 4),
        ("Statistical Analysis", "Statistics for Data Science", "edX", 30, 4),
        ("Project Management", "PMP Certification Prep", "PMI", 45, 5),
        ("Communication Skills", "Business Communication Skills", "LinkedIn Learning", 10, 3),
        ("Leadership", "Leadership & Management Essentials", "LinkedIn Learning", 20, 4),
        ("Recruitment & Onboarding", "Modern Recruitment Strategies", "HR Academy", 15, 3),
        ("Performance Management", "Employee Performance Management", "HR Academy", 15, 4),
        ("Digital Marketing", "Digital Marketing Professional Certificate", "Google", 40, 4),
        ("Content Strategy", "Content Strategy for Professionals", "Coursera", 20, 3),
        ("SEO & Analytics", "SEO & Google Analytics Mastery", "Udemy", 25, 4),
        ("Financial Modeling", "Financial Modeling & Valuation", "CFI", 35, 5),
        ("Budgeting & Forecasting", "Corporate Budgeting & Forecasting", "CFI", 25, 4),
        ("Risk Management", "Risk Management Fundamentals", "CFI", 20, 3),
        ("Excel & Reporting", "Excel for Business Reporting", "Udemy", 15, 3),
    ]

    for skill_name, course_name, provider, duration, level in training_courses:
        cur.execute("""
            INSERT INTO training_courses (skill_id, course_name, provider, duration_hours, course_level)
            VALUES (?, ?, ?, ?, ?)
        """, (skill_ids[skill_name], course_name, provider, duration, level))

    conn.commit()
    conn.close()
    print("Database seeded successfully with sample data.")


def initialize_database_if_needed(db_path="data/skillgap.db"):
    """
    Convenience function used by main.py. Creates the DatabaseManager,
    creates tables if missing, and seeds sample data ONLY if the database
    file did not already exist before this call.
    """
    db = DatabaseManager(db_path)
    is_new_database = not db.database_exists()
    db.create_tables()
    if is_new_database:
        seed_database(db)
    return db
