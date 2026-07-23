"""
header.py
------------------------------------------------------------------
Implements the always-visible top header bar, shown above every
page in the workspace area. Displays the current page title/
subtitle on the left and a simple user/profile badge on the right,
giving the application a professional enterprise-software feel.
------------------------------------------------------------------
"""

import tkinter as tk
from datetime import datetime

import config


class Header(tk.Frame):
    """The top header bar shown above the active page content."""

    def __init__(self, parent):
        colors = config.COLORS
        super().__init__(parent, bg=colors["header_bg"], height=config.HEADER_HEIGHT)
        self.pack_propagate(False)
        self.colors = colors

        # Bottom border for visual separation from the workspace
        border = tk.Frame(self, bg=colors["header_border"], height=1)
        border.pack(side="bottom", fill="x")

        content = tk.Frame(self, bg=colors["header_bg"])
        content.pack(fill="both", expand=True, padx=28)

 # ---------------- Left side: page title & subtitle ----------------
        title_container = tk.Frame(content, bg=colors["header_bg"])
        title_container.pack(side="left", fill="both", expand=True)

        # Center alignment using grid/pack vertical layout
        title_inner = tk.Frame(title_container, bg=colors["header_bg"])
        title_inner.pack(side="left", anchor="w", expand=True)

        # Title: Prominent, wide Bahnschrift
        self.title_label = tk.Label(
            title_inner, text="Dashboard",
            font=("Segoe UI Bold", 24, "bold"),
            bg=colors["header_bg"], fg=colors["text_primary"],
            anchor="w"
        )
        self.title_label.pack(anchor="w", pady= 0)

        # Subtitle: Matching Bahnschrift Light for clean visual harmony
        self.subtitle_label = tk.Label(
            title_inner, text="Welcome back! Here's your recruitment overview.",
            font=("Segoe UI ", 10),
            bg=colors["header_bg"], fg=colors["text_secondary"],
            anchor="w"
        )
        self.subtitle_label.pack(anchor="w", pady= 0)

        # ---------------- Right side: date + user badge ----------------
        right_container = tk.Frame(content, bg=colors["header_bg"])
        right_container.pack(side="right", fill="y")

        user_badge = tk.Frame(right_container, bg=colors["header_bg"])
        user_badge.pack(side="right", anchor="e", expand=True)

        avatar_circle = tk.Label(
            user_badge, text="HR", font=(config.FONT_FAMILY, 10, "bold"),
            bg=colors["accent_primary"], fg="white",
            width=3, height=1,
        )
        avatar_circle.pack(side="right", padx=(10, 0))

        user_text_frame = tk.Frame(user_badge, bg=colors["header_bg"])
        user_text_frame.pack(side="right")

        user_name_label = tk.Label(
            user_text_frame, text="Recruiter Admin",
            font=config.FONTS["body_bold"],
            bg=colors["header_bg"], fg=colors["text_primary"]
        )
        user_name_label.pack(anchor="e")

        self.date_label = tk.Label(
            user_text_frame, text=datetime.now().strftime("%A, %B %d, %Y"),
            font=config.FONTS["small"],
            bg=colors["header_bg"], fg=colors["text_muted"]
        )
        self.date_label.pack(anchor="e")

    # ------------------------------------------------------------
    def set_page_info(self, title, subtitle):
        """
        Updates the header's title and subtitle text. Called by
        main_window.py every time the user navigates to a new page.

        Args:
            title (str): the new page title (e.g. "Candidates").
            subtitle (str): a short descriptive subtitle line.
        """
        self.title_label.config(text=title)
        self.subtitle_label.config(text=subtitle)