"""
gap_analysis.py
----------------
Gap Analysis page - the heart of the application. Shows every employee's
readiness score and classification, and lets HR drill down into a
specific employee to see a color-coded, skill-by-skill gap breakdown.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter
)
from PyQt5.QtCore import Qt

from algorithms.analyzer import SkillGapAnalyzer
from ui.widgets import make_colored_badge, make_readiness_progress_bar, classification_color


class GapAnalysisPage(QWidget):
    """Company-wide gap analysis with a drill-down detail panel."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.selected_employee_id = None
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        header = QLabel("Skills Gap Analysis")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search employee...")
        self.search_input.textChanged.connect(self._refresh_summary_table)
        toolbar.addWidget(self.search_input, stretch=1)

        self.classification_filter = QComboBox()
        self.classification_filter.addItems([
            "All Classifications", "Expert / Fully Ready", "Proficient",
            "Developing", "Needs Training", "Critical Gap",
        ])
        self.classification_filter.currentTextChanged.connect(self._refresh_summary_table)
        toolbar.addWidget(self.classification_filter, stretch=1)
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, stretch=1)

        # ---- Left: summary table (readiness + classification) ----
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(4)
        self.summary_table.setHorizontalHeaderLabels(
            ["Employee", "Department", "Readiness", "Classification"]
        )
        self.summary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.summary_table.verticalHeader().setVisible(False)
        self.summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.summary_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.itemSelectionChanged.connect(self._on_row_selected)
        splitter.addWidget(self.summary_table)

        # ---- Right: skill-by-skill detail table for selected employee ----
        detail_container = QWidget()
        detail_layout = QVBoxLayout(detail_container)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(8)

        self.detail_title = QLabel("Select an employee to view skill gap details")
        self.detail_title.setObjectName("SectionHeader")
        detail_layout.addWidget(self.detail_title)

        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels(
            ["Skill", "Required", "Actual", "Gap"]
        )
        self.detail_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.detail_table.verticalHeader().setVisible(False)
        self.detail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.detail_table.setAlternatingRowColors(True)
        detail_layout.addWidget(self.detail_table)

        splitter.addWidget(detail_container)
        splitter.setSizes([480, 480])

    def refresh_data(self):
        matrix = self.db.get_all_employee_skill_matrix()
        self.analyzer = SkillGapAnalyzer(matrix)
        self._refresh_summary_table()

    def _refresh_summary_table(self):
        classified = self.analyzer.classify_all_employees()

        keyword = self.search_input.text().strip().lower()
        selected_class = self.classification_filter.currentText()

        if not classified.empty:
            if keyword:
                classified = classified[
                    classified["full_name"].str.lower().str.contains(keyword)
                    | classified["department_name"].str.lower().str.contains(keyword)
                ]
            if selected_class != "All Classifications":
                classified = classified[classified["classification"] == selected_class]

        self.summary_table.setRowCount(len(classified))
        for row_idx, (_, row) in enumerate(classified.iterrows()):
            self.summary_table.setItem(row_idx, 0, QTableWidgetItem(row["full_name"]))
            self.summary_table.setItem(row_idx, 1, QTableWidgetItem(row["department_name"]))

            self.summary_table.setCellWidget(
                row_idx, 2, make_readiness_progress_bar(row["readiness_score"])
            )

            badge = make_colored_badge(
                row["classification"], classification_color(row["classification"])
            )
            self.summary_table.setCellWidget(row_idx, 3, badge)

            # store employee_id in the first column's item for later retrieval
            self.summary_table.item(row_idx, 0).setData(Qt.UserRole, int(row["employee_id"]))

        self.summary_table.resizeRowsToContents()

    def _on_row_selected(self):
        selected_items = self.summary_table.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        name_item = self.summary_table.item(row, 0)
        if name_item is None:
            return
        employee_id = name_item.data(Qt.UserRole)
        employee_name = name_item.text()
        self.selected_employee_id = employee_id
        self._populate_detail_table(employee_id, employee_name)

    def _populate_detail_table(self, employee_id, employee_name):
        self.detail_title.setText(f"Skill Gap Breakdown - {employee_name}")
        details = self.analyzer.get_employee_gap_details(employee_id)

        self.detail_table.setRowCount(len(details))
        for row_idx, (_, row) in enumerate(details.iterrows()):
            self.detail_table.setItem(row_idx, 0, QTableWidgetItem(row["skill_name"]))
            self.detail_table.setItem(row_idx, 1, QTableWidgetItem(str(int(row["required_level"]))))
            self.detail_table.setItem(row_idx, 2, QTableWidgetItem(str(int(row["actual_level"]))))

            gap_value = int(row["gap"])
            gap_item = QTableWidgetItem(str(gap_value))
            # Color-code the gap cell: green = no gap, orange = moderate, red = severe
            if gap_value == 0:
                gap_item.setForeground(Qt.green)
            elif gap_value <= 1:
                from PyQt5.QtGui import QColor
                gap_item.setForeground(QColor("#f59e0b"))
            else:
                from PyQt5.QtGui import QColor
                gap_item.setForeground(QColor("#ef4444"))
            self.detail_table.setItem(row_idx, 3, gap_item)

        self.detail_table.resizeRowsToContents()
