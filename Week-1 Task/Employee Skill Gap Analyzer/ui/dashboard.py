"""
dashboard.py
------------
The Dashboard page - the first thing the user sees after the sidebar
loads. Shows company-wide KPI statistic cards plus several charts giving
an at-a-glance picture of workforce readiness.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt

from ui.widgets import StatCard, ChartCard, ACCENT_PALETTE
from algorithms.analyzer import SkillGapAnalyzer


class DashboardPage(QWidget):
    """Main landing dashboard page."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._build_ui()
        self.refresh_data()

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
        layout.setSpacing(20)

        header = QLabel("Company-Wide Workforce Overview")
        header.setObjectName("SectionHeader")
        layout.addWidget(header)

        # ---- Row 1: statistic cards ----
        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)

        self.card_total_employees = StatCard("👥", "Total Employees", "0", "#3b82f6")
        self.card_total_departments = StatCard("🏢", "Total Departments", "0", "#22c55e")
        self.card_avg_readiness = StatCard("📈", "Average Readiness", "0%", "#f59e0b")
        self.card_needs_training = StatCard("🎯", "Need Training", "0", "#ef4444")
        self.card_best_dept = StatCard("🏆", "Best Department", "-", "#a855f7")
        self.card_weak_dept = StatCard("⚠️", "Weakest Department", "-", "#f97316")

        stats_grid.addWidget(self.card_total_employees, 0, 0)
        stats_grid.addWidget(self.card_total_departments, 0, 1)
        stats_grid.addWidget(self.card_avg_readiness, 0, 2)
        stats_grid.addWidget(self.card_needs_training, 1, 0)
        stats_grid.addWidget(self.card_best_dept, 1, 1)
        stats_grid.addWidget(self.card_weak_dept, 1, 2)

        layout.addLayout(stats_grid)

        # ---- Row 2: charts ----
        charts_row1 = QHBoxLayout()
        charts_row1.setSpacing(16)
        self.chart_classification = ChartCard("Employee Classification Breakdown")
        self.chart_department_bar = ChartCard("Department Readiness Comparison")
        charts_row1.addWidget(self.chart_classification, stretch=1)
        charts_row1.addWidget(self.chart_department_bar, stretch=1)
        layout.addLayout(charts_row1)

        charts_row2 = QHBoxLayout()
        charts_row2.setSpacing(16)
        self.chart_top_employees = ChartCard("Top 8 Employees by Readiness")
        self.chart_skill_distribution = ChartCard("Average Skill Gap by Category")
        charts_row2.addWidget(self.chart_top_employees, stretch=1)
        charts_row2.addWidget(self.chart_skill_distribution, stretch=1)
        layout.addLayout(charts_row2)

        layout.addStretch()

    def refresh_data(self):
        """
        Pulls fresh data from the database, runs the analysis algorithms,
        and updates every card + chart on the page. Called on startup and
        whenever the user navigates back to the Dashboard.
        """
        employees = self.db.get_employees()
        departments = self.db.get_departments()
        matrix = self.db.get_all_employee_skill_matrix()
        analyzer = SkillGapAnalyzer(matrix)

        classified = analyzer.classify_all_employees()
        dept_summary = analyzer.department_readiness()
        stats = analyzer.readiness_statistics()

        # ---- Update KPI cards ----
        self.card_total_employees.set_value(len(employees))
        self.card_total_departments.set_value(len(departments))
        self.card_avg_readiness.set_value(f"{stats['mean']}%")

        needs_training_count = 0
        if not classified.empty:
            needs_training_count = int(
                (classified["classification"].isin(["Needs Training", "Critical Gap"])).sum()
            )
        self.card_needs_training.set_value(needs_training_count)

        if not dept_summary.empty:
            self.card_best_dept.set_value(dept_summary.iloc[0]["department_name"])
            self.card_weak_dept.set_value(dept_summary.iloc[-1]["department_name"])
        else:
            self.card_best_dept.set_value("-")
            self.card_weak_dept.set_value("-")

        # ---- Chart 1: Classification pie chart ----
        ax = self.chart_classification.get_axes()
        if not classified.empty:
            counts = classified["classification"].value_counts()
            colors_map = {
                "Expert / Fully Ready": "#22c55e",
                "Proficient": "#3b82f6",
                "Developing": "#f59e0b",
                "Needs Training": "#f97316",
                "Critical Gap": "#ef4444",
            }
            pie_colors = [colors_map.get(label, "#9ca3b5") for label in counts.index]
            ax.pie(
                counts.values, labels=counts.index, autopct="%1.0f%%",
                colors=pie_colors, textprops={"color": "#e8eaf0", "fontsize": 8},
                wedgeprops={"edgecolor": "#232838", "linewidth": 1.5},
            )
        else:
            ax.text(0.5, 0.5, "No data available", ha="center", color="#9ca3b5")
        self.chart_classification.refresh()

        # ---- Chart 2: Department readiness bar chart ----
        ax = self.chart_department_bar.get_axes()
        if not dept_summary.empty:
            ax.bar(
                dept_summary["department_name"], dept_summary["avg_readiness"],
                color=ACCENT_PALETTE[0], edgecolor="none",
            )
            ax.set_ylabel("Avg Readiness (%)")
            ax.set_ylim(0, 100)
            ax.tick_params(axis="x", rotation=25)
        else:
            ax.text(0.5, 0.5, "No data available", ha="center", color="#9ca3b5")
        self.chart_department_bar.refresh()

        # ---- Chart 3: Top employees bar chart ----
        ax = self.chart_top_employees.get_axes()
        if not classified.empty:
            top = classified.head(8).sort_values("readiness_score")
            ax.barh(top["full_name"], top["readiness_score"], color=ACCENT_PALETTE[1])
            ax.set_xlabel("Readiness (%)")
            ax.set_xlim(0, 100)
        else:
            ax.text(0.5, 0.5, "No data available", ha="center", color="#9ca3b5")
        self.chart_top_employees.refresh()

        # ---- Chart 4: Skill category distribution ----
        ax = self.chart_skill_distribution.get_axes()
        category_dist = analyzer.skill_category_distribution()
        if not category_dist.empty:
            ax.bar(
                category_dist["category"], category_dist["avg_gap"],
                color=ACCENT_PALETTE[3],
            )
            ax.set_ylabel("Average Gap")
            ax.tick_params(axis="x", rotation=25)
        else:
            ax.text(0.5, 0.5, "No data available", ha="center", color="#9ca3b5")
        self.chart_skill_distribution.refresh()
