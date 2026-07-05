"""
department_analytics.py
-------------------------
Department Analytics page - department-wide readiness comparisons,
company-wide employee ranking (leaderboard), and descriptive statistics
computed with pandas/numpy.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt

from algorithms.analyzer import SkillGapAnalyzer
from ui.widgets import ChartCard, StatCard, make_readiness_progress_bar, ACCENT_PALETTE


class DepartmentAnalyticsPage(QWidget):
    """Department comparison charts + company-wide employee ranking table."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._build_ui()
        self.refresh_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        header = QLabel("Department Analytics & Employee Ranking")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        # ---- Statistical summary cards ----
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(16)
        self.card_mean = StatCard("μ", "Mean Readiness", "0%", "#3b82f6")
        self.card_median = StatCard("◇", "Median Readiness", "0%", "#22c55e")
        self.card_std = StatCard("σ", "Std. Deviation", "0", "#f59e0b")
        self.card_range = StatCard("↕", "Min / Max", "0 / 0", "#a855f7")
        self.stats_grid.addWidget(self.card_mean, 0, 0)
        self.stats_grid.addWidget(self.card_median, 0, 1)
        self.stats_grid.addWidget(self.card_std, 0, 2)
        self.stats_grid.addWidget(self.card_range, 0, 3)
        layout.addLayout(self.stats_grid)

        # ---- Charts row ----
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)
        self.chart_department_comparison = ChartCard("Department Readiness Comparison")
        self.chart_distribution = ChartCard("Readiness Score Distribution")
        charts_row.addWidget(self.chart_department_comparison, stretch=1)
        charts_row.addWidget(self.chart_distribution, stretch=1)
        layout.addLayout(charts_row)

        # ---- Ranking table ----
        ranking_header_row = QHBoxLayout()
        ranking_label = QLabel("Employee Ranking")
        ranking_label.setObjectName("SectionHeader")
        ranking_header_row.addWidget(ranking_label)
        ranking_header_row.addStretch()

        ranking_header_row.addWidget(QLabel("Filter by Department:"))
        self.department_filter = QComboBox()
        self.department_filter.addItem("All Departments")
        self.department_filter.currentTextChanged.connect(self._refresh_ranking_table)
        ranking_header_row.addWidget(self.department_filter)
        layout.addLayout(ranking_header_row)

        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(5)
        self.ranking_table.setHorizontalHeaderLabels(
            ["Rank", "Employee", "Department", "Position", "Readiness"]
        )
        self.ranking_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ranking_table.verticalHeader().setVisible(False)
        self.ranking_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ranking_table.setAlternatingRowColors(True)
        layout.addWidget(self.ranking_table)

    def refresh_data(self):
        matrix = self.db.get_all_employee_skill_matrix()
        self.analyzer = SkillGapAnalyzer(matrix)

        if self.department_filter.count() == 1:
            for dept in self.db.get_departments():
                self.department_filter.addItem(dept["name"])

        # ---- Statistics cards ----
        stats = self.analyzer.readiness_statistics()
        self.card_mean.set_value(f"{stats['mean']}%")
        self.card_median.set_value(f"{stats['median']}%")
        self.card_std.set_value(stats["std_dev"])
        self.card_range.set_value(f"{stats['minimum']} / {stats['maximum']}")

        # ---- Department comparison chart ----
        dept_summary = self.analyzer.department_readiness()
        ax = self.chart_department_comparison.get_axes()
        if not dept_summary.empty:
            bars = ax.bar(
                dept_summary["department_name"], dept_summary["avg_readiness"],
                color=ACCENT_PALETTE[: len(dept_summary)],
            )
            ax.set_ylabel("Avg Readiness (%)")
            ax.set_ylim(0, 100)
            ax.tick_params(axis="x", rotation=25)
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.0f}%", (bar.get_x() + bar.get_width() / 2, height),
                            textcoords="offset points", xytext=(0, 4), ha="center",
                            color="#e8eaf0", fontsize=8)
        else:
            ax.text(0.5, 0.5, "No data available", ha="center", color="#9ca3b5")
        self.chart_department_comparison.refresh()

        # ---- Distribution histogram ----
        ax = self.chart_distribution.get_axes()
        distribution = stats["distribution"]
        if distribution:
            labels = list(distribution.keys())
            values = list(distribution.values())
            ax.bar(range(len(labels)), values, color=ACCENT_PALETTE[2])
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels([l.split(" ")[0] for l in labels], rotation=0, fontsize=7)
            ax.set_ylabel("Number of Employees")
        else:
            ax.text(0.5, 0.5, "No data available", ha="center", color="#9ca3b5")
        self.chart_distribution.refresh()

        self._refresh_ranking_table()

    def _refresh_ranking_table(self):
        selected_dept_name = self.department_filter.currentText()
        department_id = None
        if selected_dept_name != "All Departments":
            for dept in self.db.get_departments():
                if dept["name"] == selected_dept_name:
                    department_id = dept["department_id"]
                    break

        ranked = self.analyzer.rank_employees(department_id=department_id)

        self.ranking_table.setRowCount(len(ranked))
        for row_idx, (_, row) in enumerate(ranked.iterrows()):
            rank_item = QTableWidgetItem(f"#{int(row['rank'])}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.ranking_table.setItem(row_idx, 0, rank_item)
            self.ranking_table.setItem(row_idx, 1, QTableWidgetItem(row["full_name"]))
            self.ranking_table.setItem(row_idx, 2, QTableWidgetItem(row["department_name"]))
            self.ranking_table.setItem(row_idx, 3, QTableWidgetItem(row["position"]))
            self.ranking_table.setCellWidget(
                row_idx, 4, make_readiness_progress_bar(row["readiness_score"])
            )

        self.ranking_table.resizeRowsToContents()
