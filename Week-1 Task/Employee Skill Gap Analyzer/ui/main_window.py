"""
main_window.py
---------------
The application's main window. Provides a sidebar navigation menu and a
stacked widget that swaps between all the feature pages (Dashboard,
Employee Management, Skill Management, Gap Analysis, Training
Recommendations, Department Analytics, Reports, About).
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QButtonGroup, QFrame
)
from PyQt5.QtCore import Qt

from ui.dashboard import DashboardPage
from ui.employee_management import EmployeeManagementPage
from ui.skill_management import SkillManagementPage
from ui.gap_analysis import GapAnalysisPage
from ui.training_recommendations import TrainingRecommendationsPage
from ui.department_analytics import DepartmentAnalyticsPage
from ui.reports import ReportsPage
from ui.about import AboutPage


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    # Each entry: (icon, label, page_key)
    NAV_ITEMS = [
        ("🏠", "Dashboard", "dashboard"),
        ("👥", "Employees", "employees"),
        ("🧩", "Skills", "skills"),
        ("📉", "Gap Analysis", "gap_analysis"),
        ("🎓", "Training", "training"),
        ("🏢", "Departments", "departments"),
        ("📄", "Reports", "reports"),
        ("ℹ️", "About", "about"),
    ]

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setWindowTitle("Employee Skills Gap Analyzer")
        self.resize(1400, 860)
        self.setMinimumSize(1100, 700)

        self._pages = {}
        self._nav_buttons = {}

        self._build_ui()
        self._navigate_to("dashboard")

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_sidebar())

        right_column = QVBoxLayout()
        right_column.setContentsMargins(0, 0, 0, 0)
        right_column.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        self._register_pages()
        right_column.addWidget(self.stacked_widget)

        right_container = QWidget()
        right_container.setLayout(right_column)
        root_layout.addWidget(right_container, stretch=1)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(2)

        title = QLabel("SkillGap")
        title.setObjectName("SidebarTitle")
        layout.addWidget(title)

        subtitle = QLabel("Analyzer")
        subtitle.setObjectName("SidebarSubtitle")
        layout.addWidget(subtitle)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        for icon, label, page_key in self.NAV_ITEMS:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, key=page_key: self._navigate_to(key))
            layout.addWidget(btn)
            self.button_group.addButton(btn)
            self._nav_buttons[page_key] = btn

        layout.addStretch()

        footer = QLabel("v1.0  •  BS AI Semester Project")
        footer.setObjectName("MutedLabel")
        footer.setContentsMargins(20, 0, 20, 8)
        layout.addWidget(footer)

        return sidebar

    def _register_pages(self):
        """Creates every page once and adds it to the stacked widget."""
        self._pages["dashboard"] = DashboardPage(self.db)
        self._pages["employees"] = EmployeeManagementPage(self.db)
        self._pages["skills"] = SkillManagementPage(self.db)
        self._pages["gap_analysis"] = GapAnalysisPage(self.db)
        self._pages["training"] = TrainingRecommendationsPage(self.db)
        self._pages["departments"] = DepartmentAnalyticsPage(self.db)
        self._pages["reports"] = ReportsPage(self.db)
        self._pages["about"] = AboutPage()

        for key in self._pages:
            self.stacked_widget.addWidget(self._pages[key])

    def _navigate_to(self, page_key):
        """
        Switches the visible page. Refreshes the page's data first (for
        pages that support it) so information is always current -
        this matters because data can change on other pages (e.g. adding
        an employee should be reflected immediately on the Dashboard).
        """
        page = self._pages.get(page_key)
        if page is None:
            return

        if hasattr(page, "refresh_data"):
            page.refresh_data()

        self.stacked_widget.setCurrentWidget(page)

        btn = self._nav_buttons.get(page_key)
        if btn:
            btn.setChecked(True)
