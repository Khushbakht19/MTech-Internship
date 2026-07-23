"""
validators.py
------------------------------------------------------------------
Simple input validation helpers used by the Candidate and Job
forms in the GUI. Keeping validation logic here (instead of inline
inside the GUI code) keeps forms.py files short and readable.
------------------------------------------------------------------
"""

import re


def is_valid_name(name):
    """A valid name must be non-empty and contain at least one letter."""
    return bool(name and name.strip() and any(char.isalpha() for char in name))


def is_valid_email(email):
    """
    Validates a basic email format (not exhaustive RFC validation,
    but sufficient for a student project form check).
    Empty email is allowed since it's an optional field.
    """
    if not email or not email.strip():
        return True
    pattern = r"^[\w\.\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def is_valid_phone(phone):
    """
    Validates that a phone number contains only digits, spaces,
    dashes, and an optional leading '+'. Empty phone is allowed.
    """
    if not phone or not phone.strip():
        return True
    pattern = r"^\+?[\d\s\-]{7,15}$"
    return bool(re.match(pattern, phone.strip()))


def is_valid_experience(experience_value):
    """Validates that experience (years) is a non-negative number."""
    try:
        return float(experience_value) >= 0
    except (TypeError, ValueError):
        return False


def is_non_empty(text_value):
    """Validates that a required text field is not empty/whitespace-only."""
    return bool(text_value and text_value.strip())


def validate_candidate_form(full_name, email, phone, experience_years, resume_text):
    """
    Runs all relevant validations for the Candidate form in one call.

    Returns:
        tuple(bool, str): (is_valid, error_message). error_message is
                           an empty string when is_valid is True.
    """
    if not is_non_empty(full_name):
        return False, "Full name is required."
    if not is_valid_name(full_name):
        return False, "Full name must contain valid letters."
    if not is_valid_email(email):
        return False, "Please enter a valid email address (e.g. name@example.com)."
    if not is_valid_phone(phone):
        return False, "Please enter a valid phone number."
    if not is_valid_experience(experience_years):
        return False, "Experience (years) must be a valid non-negative number."
    if not is_non_empty(resume_text):
        return False, "Resume text cannot be empty. Please upload a file or paste the resume content."
    return True, ""


def validate_job_form(job_title, required_skills, experience_required, job_description):
    """
    Runs all relevant validations for the Job Posting form in one call.

    Returns:
        tuple(bool, str): (is_valid, error_message).
    """
    if not is_non_empty(job_title):
        return False, "Job title is required."
    if not is_non_empty(required_skills):
        return False, "Please list at least one required skill."
    if not is_valid_experience(experience_required):
        return False, "Experience required must be a valid non-negative number."
    if not is_non_empty(job_description):
        return False, "Job description cannot be empty."
    return True, ""
