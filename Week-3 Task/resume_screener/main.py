"""
main.py
------------------------------------------------------------------
Entry point for Resume Screener Pro.

Startup flow:
    1. Show a splash screen while the app prepares itself.
    2. Initialize (and, on first run, seed) the SQLite database.
    3. Launch the main application window (sidebar + header + pages).

Run with:
    python main.py
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox

import config
from database import DatabaseManager


def start_main_application(root, db_manager):
    """
    Builds and displays the main dashboard window.
    Imported lazily so the splash screen appears instantly without
    waiting on the (larger) GUI package to fully load first.
    """
    from gui.main_window import MainWindow

    root.deiconify()
    root.title(f"{config.APP_NAME}  -  {config.APP_SUBTITLE}")
    root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
    root.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

    MainWindow(root, db_manager)


def initialize_application(root, db_manager):
    """
    Initializes the database (creating and seeding it if this is the
    first run) and then hands control over to the main window.
    """
    try:
        db_manager.initialize_database()
    except Exception as error:
        messagebox.showerror(
            "Database Error",
            f"Failed to initialize the database:\n\n{error}"
        )
        root.destroy()
        return

    start_main_application(root, db_manager)


def main():
    """Application entry point."""
    root = tk.Tk()
    root.withdraw()  # Keep the main window hidden until the splash screen finishes

    db_manager = DatabaseManager()

    try:
        from gui.splash_screen import SplashScreen
        SplashScreen(root, on_finished=lambda: initialize_application(root, db_manager))
    except ImportError:
        # Safety fallback in case the GUI package is not yet available
        initialize_application(root, db_manager)

    root.mainloop()


if __name__ == "__main__":
    main()
