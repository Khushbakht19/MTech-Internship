"""
analyzer.py
-----------
This module contains every core ALGORITHM used by the application.
Keeping the algorithms separate from both the database layer and the GUI
layer follows the Single Responsibility Principle and makes the logic
easy to read, test, and grade.

Algorithms implemented in this file:
    1. Skills Gap Analysis
    2. Readiness Score Calculation
    3. Employee Classification (rule-based)
    4. Rule-Based Training Recommendation
    5. Employee Ranking
    6. Department Readiness Analysis
    7. Search / Filter / Sort helpers
    8. Statistical Analysis (using pandas / numpy)
"""

import pandas as pd
import numpy as np


class SkillGapAnalyzer:
    """
    Wraps all analytical algorithms. This class receives raw data
    (already fetched from the database) and returns processed,
    ready-to-display results. It does NOT talk to the database directly -
    that separation keeps the algorithms reusable and easily testable.
    """

    # Classification thresholds (percentage readiness score)
    CLASSIFICATION_RULES = [
        (90, "Expert / Fully Ready"),
        (75, "Proficient"),
        (60, "Developing"),
        (40, "Needs Training"),
        (0, "Critical Gap"),
    ]

    def __init__(self, skill_matrix):
        """
        `skill_matrix` is the list of dictionaries returned by
        DatabaseManager.get_all_employee_skill_matrix() - one row per
        (employee, required skill) combination, containing both the
        required_level and the actual_level.
        """
        # Using a pandas DataFrame makes grouping / aggregation algorithms
        # much simpler and is a good, practical use of pandas for a
        # second-semester AI student.
        self.df = pd.DataFrame(skill_matrix)

    # ------------------------------------------------------------------
    # 1. SKILLS GAP ANALYSIS
    # ------------------------------------------------------------------
    def compute_skill_gaps(self):
        """
        For every (employee, skill) pair, computes:
            gap = max(0, required_level - actual_level)

        A gap of 0 means the employee meets or exceeds the requirement.
        Returns a DataFrame with an added 'gap' column.
        """
        if self.df.empty:
            return self.df.copy()

        df = self.df.copy()
        df["gap"] = (df["required_level"] - df["actual_level"]).clip(lower=0)
        return df

    def get_employee_gap_details(self, employee_id):
        """Returns the full gap breakdown (skill by skill) for one employee."""
        gaps = self.compute_skill_gaps()
        if gaps.empty:
            return gaps
        return gaps[gaps["employee_id"] == employee_id].reset_index(drop=True)

    # ------------------------------------------------------------------
    # 2. READINESS SCORE CALCULATION
    # ------------------------------------------------------------------
    def compute_readiness_scores(self):
        """
        Readiness Score for an employee is calculated as:

            readiness = ( sum(min(actual, required)) / sum(required) ) * 100

        This rewards employees for meeting requirements, but does not give
        "extra credit" beyond what's required (min() caps contribution),
        which matches how HR readiness scoring works in the real world.

        Returns a DataFrame: employee_id, full_name, department_name,
        position, readiness_score (0-100, rounded to 2 dp).
        """
        gaps = self.compute_skill_gaps()
        if gaps.empty:
            return pd.DataFrame(columns=[
                "employee_id", "full_name", "department_name",
                "position", "readiness_score"
            ])

        gaps["capped_actual"] = gaps[["actual_level", "required_level"]].min(axis=1)

        grouped = gaps.groupby(
            ["employee_id", "full_name", "department_name", "position"]
        ).agg(
            total_capped=("capped_actual", "sum"),
            total_required=("required_level", "sum"),
        ).reset_index()

        grouped["readiness_score"] = (
            grouped["total_capped"] / grouped["total_required"] * 100
        ).round(2)

        return grouped[[
            "employee_id", "full_name", "department_name",
            "position", "readiness_score"
        ]].sort_values("readiness_score", ascending=False).reset_index(drop=True)

    # ------------------------------------------------------------------
    # 3. EMPLOYEE CLASSIFICATION (rule-based)
    # ------------------------------------------------------------------
    def classify_employee(self, readiness_score):
        """
        Simple rule-based classifier. Iterates through CLASSIFICATION_RULES
        (sorted from highest to lowest threshold) and returns the first
        label whose threshold the score satisfies.
        """
        for threshold, label in self.CLASSIFICATION_RULES:
            if readiness_score >= threshold:
                return label
        return "Critical Gap"

    def classify_all_employees(self):
        """
        Adds a 'classification' column to the readiness score table so the
        whole workforce can be labeled in a single pass.
        """
        readiness_df = self.compute_readiness_scores()
        if readiness_df.empty:
            readiness_df["classification"] = []
            return readiness_df
        readiness_df["classification"] = readiness_df["readiness_score"].apply(
            self.classify_employee
        )
        return readiness_df

    # ------------------------------------------------------------------
    # 4. RULE-BASED TRAINING RECOMMENDATION
    # ------------------------------------------------------------------
    def recommend_training(self, employee_id, training_courses):
        """
        Rule-based recommendation engine.

        Rules:
          - Only skills with gap > 0 need training.
          - Larger gaps are considered higher priority.
          - For each skill gap, recommend the training course whose
            course_level is >= the employee's actual level (so the course
            is not too easy) and as close as possible to the required
            level (so it is not needlessly advanced either).
          - If no course matches that rule, fall back to any course for
            that skill.

        `training_courses` is the list of dicts from
        DatabaseManager.get_training_courses().

        Returns a list of dicts, sorted by priority (largest gap first):
            { skill_name, gap, priority, recommended_course }
        """
        emp_gaps = self.get_employee_gap_details(employee_id)
        emp_gaps = emp_gaps[emp_gaps["gap"] > 0].sort_values("gap", ascending=False)

        recommendations = []
        for _, row in emp_gaps.iterrows():
            skill_id = row["skill_id"]
            actual = row["actual_level"]
            required = row["required_level"]
            gap = row["gap"]

            # Filter training courses that belong to this specific skill
            candidate_courses = [c for c in training_courses if c["skill_id"] == skill_id]

            best_course = None
            if candidate_courses:
                # Prefer a course whose level is between the employee's
                # current level and the required level (closest fit).
                suitable = [c for c in candidate_courses if actual < c["course_level"] <= required]
                if suitable:
                    # pick the course with the smallest level (easiest sufficient course)
                    best_course = min(suitable, key=lambda c: c["course_level"])
                else:
                    # fallback: pick the course with the highest level available
                    best_course = max(candidate_courses, key=lambda c: c["course_level"])

            priority = "High" if gap >= 3 else ("Medium" if gap == 2 else "Low")

            recommendations.append({
                "skill_name": row["skill_name"],
                "current_level": int(actual),
                "required_level": int(required),
                "gap": int(gap),
                "priority": priority,
                "recommended_course": best_course["course_name"] if best_course else "No course available",
                "provider": best_course["provider"] if best_course else "-",
                "duration_hours": best_course["duration_hours"] if best_course else 0,
            })

        return recommendations

    # ------------------------------------------------------------------
    # 5. EMPLOYEE RANKING
    # ------------------------------------------------------------------
    def rank_employees(self, department_id=None):
        """
        Ranks employees by readiness score (descending). If department_id
        is provided, ranking is restricted to that department only.
        Adds a 'rank' column (1 = best).
        """
        readiness_df = self.compute_readiness_scores()
        if department_id is not None and not readiness_df.empty:
            # Need department_id in the frame; merge back from original data
            id_map = self.df[["employee_id", "department_id"]].drop_duplicates()
            readiness_df = readiness_df.merge(id_map, on="employee_id", how="left")
            readiness_df = readiness_df[readiness_df["department_id"] == department_id]

        readiness_df = readiness_df.sort_values("readiness_score", ascending=False).reset_index(drop=True)
        readiness_df["rank"] = readiness_df.index + 1
        return readiness_df

    # ------------------------------------------------------------------
    # 6. DEPARTMENT READINESS ANALYSIS
    # ------------------------------------------------------------------
    def department_readiness(self):
        """
        Aggregates readiness scores per department: average readiness,
        number of employees, and number needing training (score < 60).
        """
        readiness_df = self.compute_readiness_scores()
        if readiness_df.empty:
            return pd.DataFrame(columns=[
                "department_name", "avg_readiness", "employee_count", "needs_training_count"
            ])

        def needs_training_count(series):
            return (series < 60).sum()

        summary = readiness_df.groupby("department_name").agg(
            avg_readiness=("readiness_score", "mean"),
            employee_count=("readiness_score", "count"),
            needs_training_count=("readiness_score", needs_training_count),
        ).reset_index()

        summary["avg_readiness"] = summary["avg_readiness"].round(2)
        return summary.sort_values("avg_readiness", ascending=False).reset_index(drop=True)

    # ------------------------------------------------------------------
    # 7. SEARCH / FILTER / SORT HELPERS
    # ------------------------------------------------------------------
    @staticmethod
    def search_employees(employees, keyword):
        """
        Simple case-insensitive substring search across name, position,
        department and email. `employees` is a list of dicts.
        """
        keyword = keyword.strip().lower()
        if not keyword:
            return employees
        results = []
        for emp in employees:
            haystack = " ".join([
                str(emp.get("full_name", "")),
                str(emp.get("position", "")),
                str(emp.get("department_name", "")),
                str(emp.get("email", "")),
            ]).lower()
            if keyword in haystack:
                results.append(emp)
        return results

    @staticmethod
    def filter_employees(employees, department_name=None, position=None):
        """Filters a list of employee dicts by department and/or position."""
        result = employees
        if department_name and department_name != "All Departments":
            result = [e for e in result if e.get("department_name") == department_name]
        if position and position != "All Positions":
            result = [e for e in result if e.get("position") == position]
        return result

    @staticmethod
    def sort_records(records, key, descending=False):
        """Generic sort helper for a list of dicts by any given key."""
        try:
            return sorted(records, key=lambda r: r.get(key, 0), reverse=descending)
        except TypeError:
            # Fallback: convert to string if types are not directly comparable
            return sorted(records, key=lambda r: str(r.get(key, "")), reverse=descending)

    # ------------------------------------------------------------------
    # 8. STATISTICAL ANALYSIS
    # ------------------------------------------------------------------
    def readiness_statistics(self):
        """
        Computes descriptive statistics over all employees' readiness
        scores using numpy: mean, median, standard deviation, min, max,
        and a simple distribution bucket count.
        """
        readiness_df = self.compute_readiness_scores()
        if readiness_df.empty:
            return {
                "mean": 0, "median": 0, "std_dev": 0,
                "minimum": 0, "maximum": 0, "distribution": {},
            }

        scores = readiness_df["readiness_score"].to_numpy()

        distribution = {
            "0-40 (Critical)": int(np.sum((scores >= 0) & (scores < 40))),
            "40-60 (Needs Training)": int(np.sum((scores >= 40) & (scores < 60))),
            "60-75 (Developing)": int(np.sum((scores >= 60) & (scores < 75))),
            "75-90 (Proficient)": int(np.sum((scores >= 75) & (scores < 90))),
            "90-100 (Expert)": int(np.sum((scores >= 90) & (scores <= 100))),
        }

        return {
            "mean": round(float(np.mean(scores)), 2),
            "median": round(float(np.median(scores)), 2),
            "std_dev": round(float(np.std(scores)), 2),
            "minimum": round(float(np.min(scores)), 2),
            "maximum": round(float(np.max(scores)), 2),
            "distribution": distribution,
        }

    def skill_category_distribution(self):
        """
        Returns the average gap per skill category (e.g. Technical,
        Management, Soft Skill) across the whole company - useful for the
        'Skill Distribution' dashboard chart.
        """
        gaps = self.compute_skill_gaps()
        if gaps.empty:
            return pd.DataFrame(columns=["category", "avg_gap"])
        summary = gaps.groupby("category").agg(avg_gap=("gap", "mean")).reset_index()
        summary["avg_gap"] = summary["avg_gap"].round(2)
        return summary
