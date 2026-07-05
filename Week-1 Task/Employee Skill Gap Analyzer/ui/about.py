"""
about.py
--------
Simple About page describing the project, its purpose, the technology
stack used, and the algorithms implemented.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea
from PyQt5.QtCore import Qt


class AboutPage(QWidget):
    """Static informational page about the application."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(18)

        title = QLabel("📊 Employee Skills Gap Analyzer")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #ffffff;")
        layout.addWidget(title)

        subtitle = QLabel("HR Analytics & Workforce Readiness Platform")
        subtitle.setObjectName("MutedLabel")
        layout.addWidget(subtitle)

        layout.addWidget(self._section(
            "Problem Statement",
            "Companies often struggle to identify employee skill gaps manually. "
            "This application automatically compares employee skills against the "
            "skills required for their job, identifies missing competencies, "
            "calculates readiness scores, recommends relevant training, and "
            "provides department-wide analytics — solving a real HR workforce "
            "management problem."
        ))

        layout.addWidget(self._section(
            "Technology Stack",
            "•  Python 3 — application logic\n"
            "•  PyQt5 — desktop graphical user interface\n"
            "•  SQLite3 — relational database storage\n"
            "•  Pandas & NumPy — data processing and statistical analysis\n"
            "•  Matplotlib — data visualization / charts\n"
            "•  ReportLab & OpenPyXL — PDF and Excel report generation"
        ))

        layout.addWidget(self._section(
            "Algorithms Implemented",
            "1. Skills Gap Analysis — compares required vs. actual proficiency\n"
            "2. Readiness Score Calculation — weighted percentage readiness metric\n"
            "3. Employee Classification — rule-based labeling (Expert → Critical Gap)\n"
            "4. Rule-Based Training Recommendation — suggests best-fit courses\n"
            "5. Employee Ranking — company-wide and department-wide leaderboards\n"
            "6. Department Readiness Analysis — aggregated department metrics\n"
            "7. Search, Filter & Sort — across employees, skills, and gaps\n"
            "8. Statistical Analysis — mean, median, standard deviation, distribution"
        ))

        layout.addWidget(self._section(
            "Academic Context",
            "This project was developed as a semester project for a BS Artificial "
            "Intelligence program, applying foundational programming, database, and "
            "applied data-analysis concepts to a realistic business problem."
        ))

        layout.addStretch()

    def _section(self, title_text, body_text):
        card = QFrame()
        card.setObjectName("ContentCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 18, 22, 18)
        card_layout.setSpacing(8)

        title_label = QLabel(title_text)
        title_label.setObjectName("SectionHeader")
        card_layout.addWidget(title_label)

        body_label = QLabel(body_text)
        body_label.setWordWrap(True)
        body_label.setStyleSheet("color: #c3c8d6; font-size: 13px; line-height: 150%;")
        card_layout.addWidget(body_label)

        return card
