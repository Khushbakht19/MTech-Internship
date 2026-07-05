"""
db_manager.py
--------------
This module is responsible for ALL communication between the application
and the SQLite database. Keeping every SQL statement inside one class
(DatabaseManager) makes the rest of the application clean, because the
GUI code never has to write raw SQL directly.

Design pattern used: Repository Pattern (a single class that "repositories"
all data access for the whole app).
"""

import sqlite3
import os


class DatabaseManager:
    """
    Handles connection creation, table creation and every CRUD
    (Create, Read, Update, Delete) operation needed by the application.
    """

    def __init__(self, db_path="data/skillgap.db"):
        """
        Initializes the database manager and makes sure the folder that
        will hold the .db file actually exists on disk.
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self):
        """
        Creates and returns a new SQLite connection.
        `check_same_thread=False` allows the connection to be safely used
        from PyQt's event loop.
        Foreign keys are turned ON because SQLite disables them by default.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # lets us access columns by name
        return conn

    def database_exists(self):
        """Returns True if the database file already exists on disk."""
        return os.path.exists(self.db_path)

    # ------------------------------------------------------------------
    # TABLE CREATION
    # ------------------------------------------------------------------
    def create_tables(self):
        """
        Creates every table required by the application if it does not
        already exist. This method is idempotent (safe to run many times).
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Departments table - top-level organizational units
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        """)

        # Employees table - each employee belongs to one department
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT,
                position TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                hire_date TEXT,
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
                    ON DELETE CASCADE
            )
        """)

        # Skills catalog - master list of every skill the company tracks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT
            )
        """)

        # Required skills - what proficiency level a position/department
        # expects for a given skill. This is the "target" employees are
        # measured against.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS required_skills (
                requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_id INTEGER NOT NULL,
                position TEXT NOT NULL,
                skill_id INTEGER NOT NULL,
                required_level INTEGER NOT NULL CHECK (required_level BETWEEN 1 AND 5),
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
                    ON DELETE CASCADE
            )
        """)

        # Employee skills - the actual proficiency level an employee has
        # for a particular skill (this is compared against required_skills).
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_skills (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                proficiency_level INTEGER NOT NULL CHECK (proficiency_level BETWEEN 0 AND 5),
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
                    ON DELETE CASCADE,
                UNIQUE (employee_id, skill_id)
            )
        """)

        # Training courses - one or more recommended courses per skill
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id INTEGER NOT NULL,
                course_name TEXT NOT NULL,
                provider TEXT,
                duration_hours INTEGER,
                course_level INTEGER CHECK (course_level BETWEEN 1 AND 5),
                FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # DEPARTMENTS
    # ------------------------------------------------------------------
    def get_departments(self):
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM departments ORDER BY name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_department(self, name, description=""):
        conn = self.get_connection()
        conn.execute(
            "INSERT INTO departments (name, description) VALUES (?, ?)",
            (name, description),
        )
        conn.commit()
        conn.close()

    def update_department(self, department_id, name, description):
        conn = self.get_connection()
        conn.execute(
            "UPDATE departments SET name=?, description=? WHERE department_id=?",
            (name, description, department_id),
        )
        conn.commit()
        conn.close()

    def delete_department(self, department_id):
        conn = self.get_connection()
        conn.execute("DELETE FROM departments WHERE department_id=?", (department_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # EMPLOYEES
    # ------------------------------------------------------------------
    def get_employees(self):
        """Returns all employees joined with their department name."""
        conn = self.get_connection()
        rows = conn.execute("""
            SELECT e.employee_id, e.full_name, e.email, e.position,
                   e.hire_date, e.department_id, d.name AS department_name
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            ORDER BY e.full_name
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_employee_by_id(self, employee_id):
        conn = self.get_connection()
        row = conn.execute("""
            SELECT e.*, d.name AS department_name
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            WHERE e.employee_id = ?
        """, (employee_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def add_employee(self, full_name, email, position, department_id, hire_date):
        conn = self.get_connection()
        cur = conn.execute(
            """INSERT INTO employees (full_name, email, position, department_id, hire_date)
               VALUES (?, ?, ?, ?, ?)""",
            (full_name, email, position, department_id, hire_date),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id

    def update_employee(self, employee_id, full_name, email, position, department_id, hire_date):
        conn = self.get_connection()
        conn.execute(
            """UPDATE employees
               SET full_name=?, email=?, position=?, department_id=?, hire_date=?
               WHERE employee_id=?""",
            (full_name, email, position, department_id, hire_date, employee_id),
        )
        conn.commit()
        conn.close()

    def delete_employee(self, employee_id):
        conn = self.get_connection()
        conn.execute("DELETE FROM employees WHERE employee_id=?", (employee_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # SKILLS
    # ------------------------------------------------------------------
    def get_skills(self):
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM skills ORDER BY category, name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_skill(self, name, category):
        conn = self.get_connection()
        cur = conn.execute(
            "INSERT INTO skills (name, category) VALUES (?, ?)", (name, category)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id

    def update_skill(self, skill_id, name, category):
        conn = self.get_connection()
        conn.execute(
            "UPDATE skills SET name=?, category=? WHERE skill_id=?",
            (name, category, skill_id),
        )
        conn.commit()
        conn.close()

    def delete_skill(self, skill_id):
        conn = self.get_connection()
        conn.execute("DELETE FROM skills WHERE skill_id=?", (skill_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # REQUIRED SKILLS
    # ------------------------------------------------------------------
    def get_required_skills(self, department_id=None, position=None):
        """
        Returns the list of skills required for a given department/position.
        If no filters are given, returns every requirement in the system.
        """
        conn = self.get_connection()
        query = """
            SELECT rs.requirement_id, rs.department_id, rs.position,
                   rs.skill_id, rs.required_level, s.name AS skill_name,
                   s.category, d.name AS department_name
            FROM required_skills rs
            JOIN skills s ON rs.skill_id = s.skill_id
            JOIN departments d ON rs.department_id = d.department_id
            WHERE 1=1
        """
        params = []
        if department_id is not None:
            query += " AND rs.department_id = ?"
            params.append(department_id)
        if position is not None:
            query += " AND rs.position = ?"
            params.append(position)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_required_skill(self, department_id, position, skill_id, required_level):
        conn = self.get_connection()
        conn.execute(
            """INSERT INTO required_skills (department_id, position, skill_id, required_level)
               VALUES (?, ?, ?, ?)""",
            (department_id, position, skill_id, required_level),
        )
        conn.commit()
        conn.close()

    def delete_required_skill(self, requirement_id):
        conn = self.get_connection()
        conn.execute("DELETE FROM required_skills WHERE requirement_id=?", (requirement_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # EMPLOYEE SKILLS
    # ------------------------------------------------------------------
    def get_employee_skills(self, employee_id):
        conn = self.get_connection()
        rows = conn.execute("""
            SELECT es.record_id, es.employee_id, es.skill_id,
                   es.proficiency_level, s.name AS skill_name, s.category
            FROM employee_skills es
            JOIN skills s ON es.skill_id = s.skill_id
            WHERE es.employee_id = ?
        """, (employee_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def set_employee_skill(self, employee_id, skill_id, proficiency_level):
        """
        Inserts a new employee-skill record, or updates the proficiency
        level if that employee/skill pair already exists (UPSERT).
        """
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO employee_skills (employee_id, skill_id, proficiency_level)
            VALUES (?, ?, ?)
            ON CONFLICT(employee_id, skill_id)
            DO UPDATE SET proficiency_level = excluded.proficiency_level
        """, (employee_id, skill_id, proficiency_level))
        conn.commit()
        conn.close()

    def delete_employee_skill(self, record_id):
        conn = self.get_connection()
        conn.execute("DELETE FROM employee_skills WHERE record_id=?", (record_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # TRAINING COURSES
    # ------------------------------------------------------------------
    def get_training_courses(self, skill_id=None):
        conn = self.get_connection()
        query = """
            SELECT tc.*, s.name AS skill_name
            FROM training_courses tc
            JOIN skills s ON tc.skill_id = s.skill_id
        """
        params = []
        if skill_id is not None:
            query += " WHERE tc.skill_id = ?"
            params.append(skill_id)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_training_course(self, skill_id, course_name, provider, duration_hours, course_level):
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO training_courses (skill_id, course_name, provider, duration_hours, course_level)
            VALUES (?, ?, ?, ?, ?)
        """, (skill_id, course_name, provider, duration_hours, course_level))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # AGGREGATE / HELPER QUERIES
    # ------------------------------------------------------------------
    def get_all_employee_skill_matrix(self):
        """
        Returns a flat list of dictionaries containing every employee,
        their department, position, and their full skill set with both
        required and actual proficiency levels. This is the primary data
        source used by the Gap Analysis algorithms.
        """
        conn = self.get_connection()
        rows = conn.execute("""
            SELECT
                e.employee_id, e.full_name, e.position, e.department_id,
                d.name AS department_name,
                s.skill_id, s.name AS skill_name, s.category,
                COALESCE(es.proficiency_level, 0) AS actual_level,
                rs.required_level AS required_level,
                rs.requirement_id
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            JOIN required_skills rs
                ON rs.department_id = e.department_id AND rs.position = e.position
            JOIN skills s ON rs.skill_id = s.skill_id
            LEFT JOIN employee_skills es
                ON es.employee_id = e.employee_id AND es.skill_id = s.skill_id
            ORDER BY e.full_name, s.name
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]
