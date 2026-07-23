"""
main_window.py
------------------------------------------------------------------
The root layout controller of Resume Screener Pro.

Responsible for:
    - Applying the global ttk theme
    - Assembling the fixed layout: Sidebar (left) + Header (top) +
      dynamic Page container (main content area)
    - Handling navigation between pages, lazily creating each page
      the first time it is visited (and caching it afterward)
    - Refreshing a page's data every time the user navigates to it,
      so information like the Dashboard stats always stays current
------------------------------------------------------------------
"""

import tkinter as tk

import config
from gui.styles import apply_theme
from gui.sidebar import Sidebar
from gui.header import Header


# Maps page_key -> (Page Title, Page Subtitle) shown in the header
PAGE_INFO = {
    "dashboard": ("Dashboard", "Welcome back! Here's your recruitment overview."),
    "candidates": ("Candidate Management", "Add, edit, and manage candidate resumes."),
    "jobs": ("Job Management", "Create and manage open job postings."),
    "screening": ("Resume Screening", "Match and rank candidates against a job using NLP."),
    "history": ("Screening History", "Review all past screening sessions."),
    "analytics": ("Analytics", "Recruitment insights and statistical analysis."),
    "reports": ("Reports", "Export screening data to CSV or PDF."),
    "about": ("About", "Project information and technology overview."),
}


class MainWindow:
    """Builds and manages the entire application layout after startup."""

    def __init__(self, root, db_manager):
        """
        Args:
            root (tk.Tk): the application's root window.
            db_manager (DatabaseManager): shared database access object.
        """
        self.root = root
        self.db_manager = db_manager

        self.style = apply_theme(root)

        self.pages = {}          # page_key -> page instance (cached)
        self.current_page_key = None

        self._build_layout()
        self.navigate_to("dashboard")

    # ------------------------------------------------------------
    def _build_layout(self):
        """Builds the fixed sidebar + header + content-area skeleton."""
        colors = config.COLORS

        # Sidebar (always visible, fixed width, full height)
        self.sidebar = Sidebar(self.root, on_navigate=self.navigate_to)
        self.sidebar.pack(side="left", fill="y")

        # Right-hand container holds the header + page content stacked
        right_container = tk.Frame(self.root, bg=colors["workspace_bg"])
        right_container.pack(side="left", fill="both", expand=True)

        # Header (always visible, fixed height, spans workspace width)
        self.header = Header(right_container)
        self.header.pack(side="top", fill="x")

        # Content area where individual pages are drawn
        self.content_area = tk.Frame(right_container, bg=colors["workspace_bg"])
        self.content_area.pack(side="top", fill="both", expand=True)

    # ------------------------------------------------------------
    def _create_page(self, page_key):
        """
        Lazily imports and instantiates the requested page the first
        time it is navigated to. Subsequent visits reuse the cached
        instance (created once, refreshed on every visit).
        """
        if page_key == "dashboard":
            from gui.dashboard import DashboardPage
            return DashboardPage(self.content_area, self.db_manager, self.navigate_to)

        elif page_key == "candidates":
            from gui.candidates import CandidatesPage
            return CandidatesPage(self.content_area, self.db_manager)

        elif page_key == "jobs":
            from gui.jobs import JobsPage
            return JobsPage(self.content_area, self.db_manager)

        elif page_key == "screening":
            from gui.screening import ScreeningPage
            return ScreeningPage(self.content_area, self.db_manager)

        elif page_key == "history":
            from gui.history import HistoryPage
            return HistoryPage(self.content_area, self.db_manager)

        elif page_key == "analytics":
            from gui.analytics import AnalyticsPage
            return AnalyticsPage(self.content_area, self.db_manager)

        elif page_key == "reports":
            from gui.reports import ReportsPage
            return ReportsPage(self.content_area, self.db_manager)

        elif page_key == "about":
            from gui.about import AboutPage
            return AboutPage(self.content_area)

        raise ValueError(f"Unknown page key: {page_key}")

    # ------------------------------------------------------------
    def navigate_to(self, page_key):
        """
        Switches the visible page in the content area, updates the
        header's title/subtitle, and highlights the correct sidebar
        item. Called by the Sidebar on click and by pages themselves
        for cross-page navigation (e.g. Dashboard -> Screening).

        Args:
            page_key (str): one of the keys defined in PAGE_INFO.
        """
        if page_key not in PAGE_INFO:
            return

        # Hide the currently visible page (if any)
        if self.current_page_key is not None:
            self.pages[self.current_page_key].pack_forget()

        # Create the page on first visit; reuse it on later visits
        if page_key not in self.pages:
            self.pages[page_key] = self._create_page(page_key)

        page = self.pages[page_key]
        page.pack(fill="both", expand=True)

        # Refresh the page's data if it supports it, so information
        # like dashboard stats or table contents is always current.
        if hasattr(page, "refresh"):
            page.refresh()

        # Update header text and sidebar highlight
        title, subtitle = PAGE_INFO[page_key]
        self.header.set_page_info(title, subtitle)
        self.sidebar.set_active(page_key)

        self.current_page_key = page_key
