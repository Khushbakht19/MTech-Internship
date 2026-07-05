"""
training_recommendations.py
-----------------------------
Training Recommendations page - lets HR select an employee and instantly
see a rule-based, prioritized list of training courses that would close
their skill gaps.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt

from algorithms.analyzer import SkillGapAnalyzer
from ui.widgets import make_colored_badge


PRIORITY_COLORS = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#3b82f6"}


class TrainingRecommendationsPage(QWidget):
    """Displays rule-based training recommendations for a selected employee."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        header = QLabel("Training Recommendations")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        subtitle = QLabel(
            "Select an employee to generate a prioritized, rule-based training plan "
            "that closes their skill gaps."
        )
        subtitle.setObjectName("MutedLabel")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Employee:"))
        self.employee_combo = QComboBox()
        self.employee_combo.currentIndexChanged.connect(self._on_employee_changed)
        toolbar.addWidget(self.employee_combo, stretch=1)
        layout.addLayout(toolbar)

        # Summary banner card
        self.summary_card = QFrame()
        self.summary_card.setObjectName("ContentCard")
        summary_layout = QHBoxLayout(self.summary_card)
        summary_layout.setContentsMargins(18, 14, 18, 14)
        self.summary_label = QLabel("No employee selected.")
        self.summary_label.setObjectName("MutedLabel")
        summary_layout.addWidget(self.summary_label)
        layout.addWidget(self.summary_card)

        # Recommendations table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Skill", "Current", "Required", "Gap", "Priority",
            "Recommended Course", "Provider / Duration"
        ])
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh_data(self):
        matrix = self.db.get_all_employee_skill_matrix()
        self.analyzer = SkillGapAnalyzer(matrix)
        self.training_courses = self.db.get_training_courses()

        self.employee_combo.blockSignals(True)
        self.employee_combo.clear()
        employees = self.db.get_employees()
        for emp in employees:
            self.employee_combo.addItem(
                f"{emp['full_name']} ({emp['position']})", emp["employee_id"]
            )
        self.employee_combo.blockSignals(False)

        if employees:
            self._on_employee_changed(0)

    def _on_employee_changed(self, index):
        employee_id = self.employee_combo.currentData()
        if employee_id is None:
            return

        recommendations = self.analyzer.recommend_training(employee_id, self.training_courses)

        if not recommendations:
            self.summary_label.setText(
                "✅ This employee meets or exceeds all required skill levels for their role. No training needed."
            )
        else:
            high_count = sum(1 for r in recommendations if r["priority"] == "High")
            self.summary_label.setText(
                f"⚠️ {len(recommendations)} skill gap(s) found — {high_count} high priority. "
                "Recommended courses are listed below, ordered by urgency."
            )

        self.table.setRowCount(len(recommendations))
        for row_idx, rec in enumerate(recommendations):
            self.table.setItem(row_idx, 0, QTableWidgetItem(rec["skill_name"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(rec["current_level"])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(rec["required_level"])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(rec["gap"])))

            badge = make_colored_badge(rec["priority"], PRIORITY_COLORS.get(rec["priority"], "#9ca3b5"))
            self.table.setCellWidget(row_idx, 4, badge)

            self.table.setItem(row_idx, 5, QTableWidgetItem(rec["recommended_course"]))
            provider_text = f"{rec['provider']} • {rec['duration_hours']}h" if rec["provider"] != "-" else "-"
            self.table.setItem(row_idx, 6, QTableWidgetItem(provider_text))

        self.table.resizeRowsToContents()
