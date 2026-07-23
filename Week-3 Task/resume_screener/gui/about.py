"""
about.py
------------------------------------------------------------------
About page - displays project information, technology overview,
and author details. Fulfills the "About" module of the project
brief and gives graders a clear, at-a-glance summary of the system.
------------------------------------------------------------------
"""

import tkinter as tk

import config


class AboutPage(tk.Frame):
    """A static informational page describing the project."""

    def __init__(self, parent):
        colors = config.COLORS
        super().__init__(parent, bg=colors["workspace_bg"])
        self.colors = colors

        self._build_layout()

    # ==================================================================
    def _build_layout(self):
        colors = self.colors

        outer = tk.Frame(self, bg=colors["workspace_bg"])
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        card = tk.Frame(outer, bg=colors["card_bg"], highlightthickness=1,
                         highlightbackground=colors["card_border"])
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=colors["card_bg"])
        inner.pack(fill="both", expand=True, padx=40, pady=32)

        # ---------------- Header ----------------
        header_row = tk.Frame(inner, bg=colors["card_bg"])
        header_row.pack(fill="x", anchor="w")

        tk.Label(
            header_row, text="📄", font=("Segoe UI Emoji", 32),
            bg=colors["card_bg"], fg=colors["accent_primary"]
        ).pack(side="left", padx=(0, 14))

        title_frame = tk.Frame(header_row, bg=colors["card_bg"])
        title_frame.pack(side="left")

        tk.Label(
            title_frame, text=config.APP_NAME, font=("Segoe UI", 22, "bold"),
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(anchor="w")

        tk.Label(
            title_frame, text=f"Version {config.APP_VERSION}  ·  {config.APP_SUBTITLE}",
            font=config.FONTS["subtitle"], bg=colors["card_bg"], fg=colors["text_secondary"]
        ).pack(anchor="w")

        divider = tk.Frame(inner, bg=colors["card_border"], height=1)
        divider.pack(fill="x", pady=20)

        # ---------------- Two-column content ----------------
        content_row = tk.Frame(inner, bg=colors["card_bg"])
        content_row.pack(fill="both", expand=True)
        content_row.grid_columnconfigure(0, weight=1)
        content_row.grid_columnconfigure(1, weight=1)

        # ----- Left column: problem statement + features -----
        left_column = tk.Frame(content_row, bg=colors["card_bg"])
        left_column.grid(row=0, column=0, sticky="nw", padx=(0, 30))

        self._add_section(
            left_column, "🎯 Problem Statement",
            "Recruiters receive hundreds of resumes for every job opening and "
            "cannot manually review each one. Resume Screener Pro uses Natural "
            "Language Processing to automatically compare resumes against job "
            "descriptions, rank candidates by relevance, and surface the best "
            "matches - saving recruiters hours of manual screening work."
        )

        self._add_section(
            left_column, "✨ Key Features",
            "• Resume text extraction (.txt / .pdf / .docx)\n"
            "• Text cleaning & preprocessing pipeline\n"
            "• TF-IDF vectorization & cosine similarity matching\n"
            "• Automated candidate ranking & keyword matching\n"
            "• Screening history tracking & search/filter tools\n"
            "• Recruitment analytics with statistical analysis\n"
            "• CSV & PDF report exporting"
        )

        # ----- Right column: tech stack + academic info -----
        right_column = tk.Frame(content_row, bg=colors["card_bg"])
        right_column.grid(row=0, column=1, sticky="nw")

        self._add_section(
            right_column, "🛠️ Technology Stack",
            "• Python 3  -  core application logic\n"
            "• Tkinter / ttk  -  desktop graphical interface\n"
            "• SQLite  -  local relational database\n"
            "• Scikit-learn  -  TF-IDF & cosine similarity (NLP/ML)\n"
            "• Pandas  -  data analysis & statistics\n"
            "• Matplotlib  -  charts and PDF report rendering"
        )

        self._add_section(
            right_column, "🎓 Academic Information",
            f"Developed by: {config.APP_AUTHOR}\n"
            "Program: BS Artificial Intelligence (Semester 2)\n"
            f"Project Year: {config.APP_YEAR}\n\n"
            "This project was built as a practical demonstration of "
            "applying core NLP and Machine Learning concepts - text "
            "preprocessing, vectorization, and similarity scoring - to "
            "a real-world recruitment problem."
        )

    # ------------------------------------------------------------
    def _add_section(self, parent, heading, body_text):
        """Adds one titled text section to the About page."""
        colors = self.colors

        section = tk.Frame(parent, bg=colors["card_bg"])
        section.pack(fill="x", pady=(0, 22), anchor="w")

        tk.Label(
            section, text=heading, font=config.FONTS["body_bold"],
            bg=colors["card_bg"], fg=colors["accent_primary"]
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            section, text=body_text, font=config.FONTS["body"],
            bg=colors["card_bg"], fg=colors["text_secondary"],
            justify="left", wraplength=420
        ).pack(anchor="w")
