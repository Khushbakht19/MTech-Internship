"""
gui/about.py
-------------
A static informational page describing the application, how the ML
model works, the technology stack used, and academic project details.
"""

import tkinter as tk

import config


class AboutPage(tk.Frame):
    """The About page."""

    def __init__(self, master, database, classifier, app):
        super().__init__(master, bg=config.COLORS["main_bg"])
        self.database = database
        self.classifier = classifier
        self.app = app

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_page_title()
        self._build_main_content()

    # ------------------------------------------------------------------
    def _build_page_title(self):
        title_frame = tk.Frame(self, bg=config.COLORS["main_bg"])
        title_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))

        title_label = tk.Label(
            title_frame, text="About", font=config.FONTS["page_title"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_primary"],
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame, text="How this application works, and the technology behind it",
            font=config.FONTS["body"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"],
        )
        subtitle_label.pack(anchor="w")

    # ------------------------------------------------------------------
    def _build_main_content(self):
        content_row = tk.Frame(self, bg=config.COLORS["main_bg"])
        content_row.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        content_row.grid_columnconfigure(0, weight=3)
        content_row.grid_columnconfigure(1, weight=2)
        content_row.grid_rowconfigure(0, weight=1)

        self._build_overview_card(content_row)
        self._build_side_column(content_row)

    # ------------------------------------------------------------------
    def _build_overview_card(self, parent):
        card = tk.Frame(parent, bg=config.COLORS["card_bg"], highlightthickness=1,
                         highlightbackground=config.COLORS["border"])
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        inner = tk.Frame(card, bg=config.COLORS["card_bg"])
        inner.pack(fill="both", expand=True, padx=26, pady=24)

        icon_row = tk.Frame(inner, bg=config.COLORS["card_bg"])
        icon_row.pack(anchor="w", pady=(0, 10))

        icon_label = tk.Label(
            icon_row, text="🛡️", font=(config.FONT_FAMILY, 30),
            bg=config.COLORS["card_bg"],
        )
        icon_label.pack(side="left", padx=(0, 12))

        name_box = tk.Frame(icon_row, bg=config.COLORS["card_bg"])
        name_box.pack(side="left")
        tk.Label(
            name_box, text=config.APP_NAME, font=(config.FONT_FAMILY, 18, "bold"),
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        ).pack(anchor="w")
        tk.Label(
            name_box, text=f"Version {config.APP_VERSION}", font=config.FONTS["small"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_muted"],
        ).pack(anchor="w")

        description = (
            "SMS Fraud Detector uses Machine Learning to protect users from phishing "
            "links, fake banking alerts, lottery scams, OTP theft, and other malicious "
            "SMS messages. Every message you scan is analyzed by a trained Naive Bayes "
            "classifier and checked against a list of common fraud-related keywords, "
            "then logged so you can track patterns over time."
        )
        tk.Label(
            inner, text=description, font=config.FONTS["body"], wraplength=560,
            justify="left", bg=config.COLORS["card_bg"], fg=config.COLORS["text_secondary"],
        ).pack(anchor="w", pady=(0, 18))

        self._build_section_heading(inner, "How Detection Works")
        steps = [
            "1.  The message text is cleaned (lowercased, links & punctuation removed, "
            "common stopwords filtered out).",
            "2.  The cleaned text is converted into numeric features using TF-IDF "
            "(Term Frequency - Inverse Document Frequency) vectorization.",
            "3.  A Multinomial Naive Bayes classifier, trained on a labeled dataset of "
            "spam and legitimate messages, predicts the most likely category.",
            "4.  The original message is also scanned for known fraud-related keywords "
            "(e.g. \"verify\", \"otp\", \"click here\", \"prize\") to support the verdict.",
        ]
        for step in steps:
            tk.Label(
                inner, text=step, font=config.FONTS["body"], wraplength=560,
                justify="left", bg=config.COLORS["card_bg"], fg=config.COLORS["text_secondary"],
            ).pack(anchor="w", pady=(0, 6))

        self._build_section_heading(inner, "Features")
        features = (
            "Real-time SMS scanning  \u2022  Confidence scoring  \u2022  Keyword detection  \u2022  "
            "Searchable prediction history  \u2022  Statistical analytics  \u2022  CSV & PDF reports"
        )
        tk.Label(
            inner, text=features, font=config.FONTS["body"], wraplength=560,
            justify="left", bg=config.COLORS["card_bg"], fg=config.COLORS["text_secondary"],
        ).pack(anchor="w")

    def _build_section_heading(self, parent, text):
        heading = tk.Label(
            parent, text=text, font=config.FONTS["body_bold"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        heading.pack(anchor="w", pady=(4, 8))

    # ------------------------------------------------------------------
    def _build_side_column(self, parent):
        column = tk.Frame(parent, bg=config.COLORS["main_bg"])
        column.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self._build_tech_stack_card(column)
        self._build_project_info_card(column)

    def _build_tech_stack_card(self, parent):
        card = tk.Frame(parent, bg=config.COLORS["card_bg"], highlightthickness=1,
                         highlightbackground=config.COLORS["border"])
        card.pack(fill="x", pady=(0, 16))

        header = tk.Label(
            card, text="Technology Stack", font=config.FONTS["section_title"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        header.pack(anchor="w", padx=20, pady=(18, 10))

        tech_items = [
            ("\U0001F40D", "Python 3", "Core application language"),
            ("\U0001F5BC", "Tkinter", "Desktop GUI framework"),
            ("\U0001F5C4", "SQLite", "Local database storage"),
            ("\U0001F916", "Scikit-learn", "TF-IDF + Naive Bayes ML"),
            ("\U0001F43C", "Pandas", "Data handling & CSV export"),
            ("\U0001F4CA", "Matplotlib", "Charts & PDF reports"),
        ]
        for icon, name, caption in tech_items:
            row = tk.Frame(card, bg=config.COLORS["card_bg"])
            row.pack(fill="x", padx=20, pady=4)

            tk.Label(
                row, text=icon, font=(config.FONT_FAMILY, 13),
                bg=config.COLORS["card_bg"], width=3,
            ).pack(side="left")

            text_box = tk.Frame(row, bg=config.COLORS["card_bg"])
            text_box.pack(side="left", fill="x", expand=True)
            tk.Label(
                text_box, text=name, font=config.FONTS["body_bold"],
                bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"], anchor="w",
            ).pack(anchor="w")
            tk.Label(
                text_box, text=caption, font=config.FONTS["small"],
                bg=config.COLORS["card_bg"], fg=config.COLORS["text_muted"], anchor="w",
            ).pack(anchor="w")

        tk.Frame(card, bg=config.COLORS["card_bg"], height=10).pack()

    def _build_project_info_card(self, parent):
        card = tk.Frame(parent, bg=config.COLORS["blue_light"])
        card.pack(fill="x")

        inner = tk.Frame(card, bg=config.COLORS["blue_light"])
        inner.pack(fill="x", padx=20, pady=18)

        tk.Label(
            inner, text="Academic Project", font=config.FONTS["body_bold"],
            bg=config.COLORS["blue_light"], fg=config.COLORS["text_primary"], anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        details = (
            "Developed as a semester project for the\n"
            "BS Artificial Intelligence program.\n\n"
            "Course focus: practical Machine Learning\n"
            "applied to a real-world problem - SMS\n"
            "spam and fraud detection."
        )
        tk.Label(
            inner, text=details, font=config.FONTS["small"], justify="left",
            bg=config.COLORS["blue_light"], fg=config.COLORS["text_secondary"], anchor="w",
        ).pack(anchor="w")
