"""
main.py
-------
Entry point for the SMS Fraud Detector desktop application.

Startup sequence:
    1. Show a splash screen while the app prepares itself.
    2. Initialize the SQLite database (creating + seeding it the very
       first time the app is run).
    3. Train the Naive Bayes spam classifier on the seeded corpus.
    4. Build the main window: a fixed sidebar for navigation, a top
       header, and a content area that swaps between pages
       (Dashboard, SMS Scanner, Prediction History, Analytics,
       Reports, About).

Run with:
    python main.py

NOTE: The GUI page modules referenced below (gui.sidebar, gui.header,
gui.dashboard, gui.scanner, gui.history, gui.analytics, gui.reports,
gui.about) and the ML module (ml.classifier) are delivered in the
following parts of this build. This file defines the final structure
they plug into.
"""

import tkinter as tk
from tkinter import ttk

import config
from database import Database
from seed_data import seed_database


class SplashScreen(tk.Toplevel):
    """
    A short-lived borderless window shown while the application loads
    its database and trains the ML model, so the user never sees a
    blank/frozen window on first launch.
    """

    def __init__(self, master, on_finished):
        super().__init__(master)
        self.on_finished = on_finished

        self.overrideredirect(True)  # Remove title bar / borders.
        self.configure(bg=config.COLORS["sidebar_bg"])
        self._center_window(config.SPLASH_WIDTH, config.SPLASH_HEIGHT)

        self._build_widgets()

        # Kick off the (fast) startup work shortly after the splash
        # screen is drawn, so the window paints before we do any work.
        self.after(150, self._run_startup_tasks)

    def _center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_widgets(self):
        container = tk.Frame(self, bg=config.COLORS["sidebar_bg"])
        container.place(relx=0.5, rely=0.5, anchor="center")

        icon_label = tk.Label(
            container, text="     🛡️", font=(config.FONT_FAMILY, 48),
            bg=config.COLORS["sidebar_bg"], fg=config.COLORS["white"],
        )
        icon_label.pack(pady=(0, 10))

        title_label = tk.Label(
            container, text=config.APP_NAME,
            font=config.FONTS["splash_title"],
            bg=config.COLORS["sidebar_bg"], fg=config.COLORS["white"],
        )
        title_label.pack()

        subtitle_label = tk.Label(
            container, text="AI-Powered SMS Spam & Fraud Detection",
            font=config.FONTS["splash_subtitle"],
            bg=config.COLORS["sidebar_bg"], fg=config.COLORS["sidebar_text"],
        )
        subtitle_label.pack(pady=(4, 20))

        self.status_label = tk.Label(
            container, text="Starting up...",
            font=config.FONTS["small"],
            bg=config.COLORS["sidebar_bg"], fg=config.COLORS["sidebar_text"],
        )
        self.status_label.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(
            container, mode="determinate", length=320, maximum=100
        )
        self.progress.pack()

    def _set_status(self, text, progress_value):
        self.status_label.config(text=text)
        self.progress["value"] = progress_value
        self.update_idletasks()

    def _run_startup_tasks(self):
        """
        Perform the real initialization work (database + ML training)
        while updating the progress bar, then hand control back to the
        main application via the on_finished callback.
        """
        self._set_status("Preparing database...", 20)
        database = Database()

        self._set_status("Loading sample data...", 45)
        seed_database(database)

        self._set_status("Training detection model...", 75)
        classifier = self._train_model(database)

        self._set_status("Almost ready...", 100)
        self.after(400, lambda: self._finish(database, classifier))

    def _train_model(self, database):
        """
        Train the ML classifier on the seeded corpus.
        The actual SpamClassifier class is implemented in ml/classifier.py
        (delivered in the next part of this build). Imported here, inside
        the method, so this file can still be read top-to-bottom even
        before that module exists.
        """
        from ml.classifier import SpamClassifier

        classifier = SpamClassifier()
        classifier.train(database)
        return classifier

    def _finish(self, database, classifier):
        self.destroy()
        self.on_finished(database, classifier)


class MainApplication(tk.Tk):
    """
    The main application window: sidebar (navigation) + header (search /
    profile) + a content area that swaps between the different pages of
    the app.
    """

    def __init__(self, database, classifier):
        super().__init__()
        self.database = database
        self.classifier = classifier

        self.title(config.APP_NAME)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        self.configure(bg=config.COLORS["main_bg"])
        self._center_window(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self._configure_ttk_style()

        # Holds every page frame, keyed by the NAV_ITEMS "key" (e.g. "dashboard").
        self.pages = {}
        self.active_page_key = None

        self._build_layout()
        self.show_page("dashboard")

    # ------------------------------------------------------------------
    def _center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _configure_ttk_style(self):
        """
        Set up a consistent ttk theme so every widget (buttons, progress
        bars, scrollbars, treeviews used later in History/Reports) shares
        the same premium look instead of the default Tkinter appearance.
        """
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "TProgressbar",
            troughcolor=config.COLORS["sidebar_bg_light"],
            background=config.COLORS["blue"],
            bordercolor=config.COLORS["sidebar_bg_light"],
            lightcolor=config.COLORS["blue"],
            darkcolor=config.COLORS["blue"],
        )

        style.configure(
            "Treeview",
            background=config.COLORS["card_bg"],
            fieldbackground=config.COLORS["card_bg"],
            foreground=config.COLORS["text_primary"],
            rowheight=32,
            borderwidth=0,
            font=config.FONTS["body"],
        )
        style.configure(
            "Treeview.Heading",
            background=config.COLORS["main_bg"],
            foreground=config.COLORS["text_secondary"],
            font=config.FONTS["body_bold"],
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", config.COLORS["blue_light"])],
            foreground=[("selected", config.COLORS["text_primary"])],
        )

    # ------------------------------------------------------------------
    def _build_layout(self):
        """
        Lay out the three structural regions of the app using grid:
        a fixed-width sidebar on the left, a header across the top of
        the remaining space, and a content frame beneath the header
        where individual pages are shown/hidden.
        """
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar (left column, full height) ---
        from gui.sidebar import Sidebar  # Implemented in a later part of this build.

        self.sidebar = Sidebar(self, on_navigate=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # --- Right side container: header (row 0) + content (row 1) ---
        right_container = tk.Frame(self, bg=config.COLORS["main_bg"])
        right_container.grid(row=0, column=1, sticky="nsew")
        right_container.grid_rowconfigure(1, weight=1)
        right_container.grid_columnconfigure(0, weight=1)

        from gui.header import Header  # Implemented in a later part of this build.

        self.header = Header(right_container, on_search=self._handle_global_search)
        self.header.grid(row=0, column=0, sticky="ew")

        self.content_frame = tk.Frame(right_container, bg=config.COLORS["main_bg"])
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _handle_global_search(self, search_term):
        """
        Sent from the header's search box. Jumps to the History page and
        filters it by the given search term.
        """
        self.show_page("history")
        history_page = self.pages.get("history")
        if history_page and hasattr(history_page, "apply_search"):
            history_page.apply_search(search_term)

    # ------------------------------------------------------------------
    def _get_page_class(self, page_key):
        """
        Lazily import and return the page class for a given navigation
        key. Imported here (rather than at the top of the file) so this
        file remains fully readable/importable even before every page
        module in gui/ has been created.
        """
        page_classes = {
            "dashboard": ("gui.dashboard", "DashboardPage"),
            "scanner": ("gui.scanner", "ScannerPage"),
            "history": ("gui.history", "HistoryPage"),
            "analytics": ("gui.analytics", "AnalyticsPage"),
            "reports": ("gui.reports", "ReportsPage"),
            "about": ("gui.about", "AboutPage"),
        }
        module_name, class_name = page_classes[page_key]
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)

    def show_page(self, page_key):
        """
        Display the requested page, creating it the first time it is
        visited and simply raising it on subsequent visits so switching
        pages feels instant.
        """
        if page_key not in self.pages:
            page_class = self._get_page_class(page_key)
            page_instance = page_class(
                self.content_frame,
                database=self.database,
                classifier=self.classifier,
                app=self,
            )
            self.pages[page_key] = page_instance
            page_instance.grid(row=0, column=0, sticky="nsew")

        self.pages[page_key].tkraise()

        # Let the freshly-shown page refresh its own data (e.g. Dashboard
        # stats after a new scan was made on another page).
        if hasattr(self.pages[page_key], "refresh"):
            self.pages[page_key].refresh()

        self.active_page_key = page_key
        self.sidebar.set_active(page_key)


def main():
    """
    Application bootstrap.

    A temporary hidden root window hosts the splash screen. Once startup
    (database + model training) is done, that root is fully torn down
    and a single MainApplication window takes over -- this avoids ever
    having two Tk() instances alive at the same time.
    """
    startup_result = {}

    root = tk.Tk()
    root.withdraw()  # Hide the empty root window while the splash screen is shown.

    def on_splash_finished(database, classifier):
        startup_result["database"] = database
        startup_result["classifier"] = classifier
        root.quit()  # Stop the temporary mainloop; widgets are cleaned up below.

    SplashScreen(root, on_finished=on_splash_finished)
    root.mainloop()
    root.destroy()

    app_window = MainApplication(
        startup_result["database"], startup_result["classifier"]
    )
    app_window.mainloop()


if __name__ == "__main__":
    main()
