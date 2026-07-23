"""
utils/helpers.py
------------------
Small, reusable utility functions shared across the application.

Keeping formatting helpers and file-export logic here (instead of
scattered inside GUI page files) follows the project's requirement to
separate GUI code, database code, ML code, and general utilities.
"""

import os
import platform
import subprocess
from datetime import datetime

import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

import config


# --------------------------------------------------------------------------
# TEXT / FORMATTING HELPERS
# --------------------------------------------------------------------------
def truncate_text(text, max_length=50):
    """Shorten a string to max_length characters, adding '...' if cut off."""
    if text is None:
        return ""
    text = str(text)
    return text if len(text) <= max_length else text[: max_length - 3] + "..."


def format_display_date(date_string, output_format="%b %d, %Y  %I:%M %p"):
    """
    Convert a 'YYYY-MM-DD HH:MM:SS' string (as stored in SQLite) into a
    friendlier display format, e.g. 'Jul 22, 2026  09:41 AM'.
    Falls back to the raw string if parsing fails for any reason.
    """
    try:
        parsed = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return parsed.strftime(output_format)
    except (ValueError, TypeError):
        return date_string or ""


def format_percentage(value, decimals=1):
    """Format a number as a percentage string, e.g. 92.456 -> '92.5%'."""
    try:
        return f"{round(float(value), decimals)}%"
    except (ValueError, TypeError):
        return "0%"


def safe_divide(numerator, denominator, default=0.0):
    """Divide two numbers, returning `default` instead of raising on division by zero."""
    try:
        return numerator / denominator if denominator else default
    except (TypeError, ZeroDivisionError):
        return default


def timestamped_filename(prefix, extension):
    """Build a unique, sortable filename like 'prefix_20260722_094512.ext'."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = extension.lstrip(".")
    return f"{prefix}_{stamp}.{extension}"


# --------------------------------------------------------------------------
# FILE-SYSTEM HELPERS
# --------------------------------------------------------------------------
def open_file(filepath):
    """
    Open a file with the operating system's default application
    (e.g. opens a CSV in Excel, a PDF in the default PDF viewer).
    Returns True on success, False if the file could not be opened.
    """
    try:
        system_name = platform.system()
        if system_name == "Windows":
            os.startfile(filepath)  # noqa: only exists on Windows
        elif system_name == "Darwin":
            subprocess.Popen(["open", filepath])
        else:
            subprocess.Popen(["xdg-open", filepath])
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------
# REPORT EXPORT HELPERS (used by gui/reports.py)
# --------------------------------------------------------------------------
def export_predictions_to_csv(predictions, filepath):
    """
    Export a list of prediction dictionaries (as returned by
    Database.get_all_predictions / filter_predictions / search_predictions)
    to a CSV file using pandas.
    """
    columns = ["id", "message_text", "prediction", "confidence", "detected_keywords", "date_predicted"]

    if predictions:
        dataframe = pd.DataFrame(predictions)[columns]
    else:
        dataframe = pd.DataFrame(columns=columns)

    dataframe.to_csv(filepath, index=False)
    return filepath


def export_predictions_to_pdf(predictions, stats, filepath):
    """
    Build a simple, readable PDF report using Matplotlib's PdfPages
    backend. This deliberately avoids adding a dedicated PDF library
    (like reportlab) so the project stays within its approved tech
    stack of Python / Tkinter / SQLite / Scikit-learn / Pandas / Matplotlib.

    The PDF has two pages:
        1. A text summary (headline stats + a list of predictions).
        2. A small spam-vs-safe distribution chart.
    """
    with PdfPages(filepath) as pdf:
        _add_summary_page(pdf, predictions, stats)
        _add_chart_page(pdf, stats)

    return filepath


def _add_summary_page(pdf, predictions, stats):
    figure = Figure(figsize=(8.27, 11.69))  # A4 portrait, in inches
    axes = figure.add_subplot(111)
    axes.axis("off")

    lines = [
        f"{config.APP_NAME} - Prediction Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "-" * 78,
        f"Total Messages Scanned : {stats['total']}",
        f"Spam Messages          : {stats['spam_count']}",
        f"Safe Messages           : {stats['safe_count']}",
        f"Detection Accuracy      : {stats['accuracy']}%",
        "-" * 78,
        "",
        "Predictions:",
        "",
    ]

    y_position = 0.97
    for line in lines:
        weight = "bold" if line.startswith(config.APP_NAME) else "normal"
        axes.text(0.02, y_position, line, fontsize=11, family="monospace",
                   fontweight=weight, transform=axes.transAxes)
        y_position -= 0.022

    for row in predictions[:28]:
        message_preview = truncate_text(row["message_text"], 58)
        line = f"[{row['prediction'].upper():>4}] {row['confidence']:>5}%   {message_preview}"
        axes.text(0.02, y_position, line, fontsize=8, family="monospace",
                   transform=axes.transAxes)
        y_position -= 0.021
        if y_position < 0.03:
            axes.text(0.02, y_position, "...(truncated, export CSV for the full list)",
                       fontsize=8, family="monospace", style="italic",
                       transform=axes.transAxes)
            break

    pdf.savefig(figure)


def _add_chart_page(pdf, stats):
    figure = Figure(figsize=(8.27, 11.69))
    axes = figure.add_subplot(111)

    spam_count = stats["spam_count"]
    safe_count = stats["safe_count"]

    if spam_count == 0 and safe_count == 0:
        axes.text(0.5, 0.5, "No predictions to chart yet", ha="center", va="center")
        axes.axis("off")
    else:
        axes.pie(
            [spam_count, safe_count], labels=["Spam", "Safe"],
            colors=[config.COLORS["red"], config.COLORS["green"]],
            autopct="%1.0f%%", startangle=90,
        )
        axes.set_title("Spam Distribution")

    pdf.savefig(figure)
