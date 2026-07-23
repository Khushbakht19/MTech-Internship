"""
splash_screen.py
------------------------------------------------------------------
Displays a modern, branded splash screen while the application
prepares itself (database initialization etc.), giving Resume
Screener Pro a polished, professional first impression.

The splash screen is a borderless Toplevel window centered on the
screen, displaying the app name, subtitle, and a simple animated
progress bar. Once the animation completes, it calls the provided
on_finished callback and destroys itself.
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk

import config


class SplashScreen:
    """A simple animated splash/loading screen shown at app startup."""

    def __init__(self, root, on_finished):
        """
        Args:
            root (tk.Tk): the (currently hidden) root application window.
            on_finished (callable): called once the splash animation ends.
        """
        self.root = root
        self.on_finished = on_finished
        self.progress_value = 0

        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)  # borderless window
        self.window.configure(bg=config.COLORS["sidebar_bg"])
        self._center_window()

        self._build_layout()
        self._animate_progress()

    # ------------------------------------------------------------
    def _center_window(self):
        """Centers the splash window on the user's screen."""
        width = config.SPLASH_WIDTH
        height = config.SPLASH_HEIGHT
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = (screen_width // 2) - (width // 2)
        y_position = (screen_height // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x_position}+{y_position}")

    # ------------------------------------------------------------
    def _build_layout(self):
        """Builds the visual content of the splash screen."""
        colors = config.COLORS

        container = tk.Frame(self.window, bg=colors["sidebar_bg"])
        container.pack(expand=True, fill="both")

        # Decorative accent bar at the top
        accent_bar = tk.Frame(container, bg=colors["sidebar_accent"], height=6)
        accent_bar.pack(fill="x", side="top")

        spacer_top = tk.Frame(container, bg=colors["sidebar_bg"], height=40)
        spacer_top.pack(fill="x")

        # App icon (drawn using a simple emoji-style badge, no external assets needed)
        icon_label = tk.Label(
            container, text="📄", font=("Segoe UI Emoji", 42),
            bg=colors["sidebar_bg"], fg=colors["sidebar_accent"]
        )
        icon_label.pack(pady=(0, 12))

        title_label = tk.Label(
            container, text=config.APP_NAME,
            font=("Segoe UI", 24, "bold"),
            bg=colors["sidebar_bg"], fg=colors["text_on_dark"]
        )
        title_label.pack()

        subtitle_label = tk.Label(
            container, text=config.APP_SUBTITLE,
            font=("Segoe UI", 11),
            bg=colors["sidebar_bg"], fg=colors["sidebar_text_muted"]
        )
        subtitle_label.pack(pady=(4, 30))

        # Progress bar container
        progress_style = ttk.Style(self.window)
        progress_style.theme_use("clam")
        progress_style.configure(
            "Splash.Horizontal.TProgressbar",
            background=colors["sidebar_accent"],
            troughcolor=colors["sidebar_bg_hover"],
            borderwidth=0,
            thickness=6,
        )

        self.progress_bar = ttk.Progressbar(
            container, style="Splash.Horizontal.TProgressbar",
            orient="horizontal", length=320, mode="determinate", maximum=100
        )
        self.progress_bar.pack(pady=(0, 10))

        self.status_label = tk.Label(
            container, text="Initializing application...",
            font=("Segoe UI", 9),
            bg=colors["sidebar_bg"], fg=colors["sidebar_text_muted"]
        )
        self.status_label.pack()

        version_label = tk.Label(
            container, text=f"Version {config.APP_VERSION}",
            font=("Segoe UI", 8),
            bg=colors["sidebar_bg"], fg=colors["sidebar_text_muted"]
        )
        version_label.pack(side="bottom", pady=16)

    # ------------------------------------------------------------
    def _animate_progress(self):
        """Animates the progress bar smoothly, then triggers completion."""
        status_messages = [
            (0, "Initializing application..."),
            (25, "Loading database engine..."),
            (55, "Preparing NLP components..."),
            (80, "Loading dashboard..."),
            (100, "Ready!"),
        ]

        for threshold, message in status_messages:
            if self.progress_value >= threshold:
                self.status_label.config(text=message)

        self.progress_value += 4
        self.progress_bar["value"] = min(self.progress_value, 100)

        if self.progress_value < 100:
            step_delay = max(1, config.SPLASH_DURATION_MS // 25)
            self.window.after(step_delay, self._animate_progress)
        else:
            self.window.after(200, self._finish)

    # ------------------------------------------------------------
    def _finish(self):
        """Destroys the splash window and hands control to the main app."""
        self.window.destroy()
        self.on_finished()
