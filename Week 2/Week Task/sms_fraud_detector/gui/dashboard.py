"""
gui/dashboard.py
-----------------
The landing page of the application: a clean, modern single-screen overview.
"""

import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config


class DashboardPage(tk.Frame):
    """The Dashboard page (default landing page of the app)."""

    def __init__(self, master, database, classifier, app):
        super().__init__(master, bg=config.COLORS["main_bg"])
        self.database = database
        self.classifier = classifier
        self.app = app

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._configure_treeview_styles()
        self._build_page_title()
        self._build_stat_cards()
        self._build_main_content()

        self.refresh()

    def _configure_treeview_styles(self):
        """Custom Table Styling: White background, black text, header separator line."""
        style = ttk.Style()
        
        if "clam" in style.theme_names():
            style.theme_use("clam")
        
        # Header Styling: White BG, Black Text, Bottom Border line to separate from rows
        style.configure(
            "Custom.Treeview.Heading",
            background="#FFFFFF",
            foreground="#000000",
            font=(config.FONT_FAMILY, 9, "bold"),
            borderwidth=0,
            relief="flat",
            lightcolor = "#FFFFFF",
            darkcolor = "#FFFFFF"
        )
        
        # Table Body Styling: White BG, Dark Text, Full width alignment
        style.configure(
            "Custom.Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#000000",
            rowheight=26,
            font=(config.FONT_FAMILY, 9),
            borderwidth=0,
            relief="flat",
            lightcolor = "#FFFFFF",
            darkcolor = "#FFFFFF"
        )
        
        # Disable hover / selection highlights
        style.map(
            "Custom.Treeview",
            background=[('selected', '#FFFFFF'), ('active', '#FFFFFF')],
            foreground=[('selected', '#000000'), ('active', '#000000')]
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[('active', '#FFFFFF')],
            foreground=[('active', '#000000')]
        )

    # ------------------------------------------------------------------
    # PAGE TITLE
    # ------------------------------------------------------------------
    def _build_page_title(self):
        title_frame = tk.Frame(self, bg=config.COLORS["main_bg"])
        title_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))

        title_label = tk.Label(
            title_frame, text="Dashboard", font=config.FONTS["page_title"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_primary"],
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame, text="Overview of your SMS fraud detection activity",
            font=config.FONTS["body"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"],
        )
        subtitle_label.pack(anchor="w")

    # ------------------------------------------------------------------
    # STATISTIC CARDS
    # ------------------------------------------------------------------
    def _build_stat_cards(self):
        cards_frame = tk.Frame(self, bg=config.COLORS["main_bg"])
        cards_frame.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 16))

        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="stat_card")

        card_specs = [
            ("total", "📩", "Total SMS Scanned", config.COLORS["blue"]),
            ("spam", "🚫", "Spam Messages", config.COLORS["red"]),
            ("safe", "✅", "Safe Messages", config.COLORS["green"]),
            ("accuracy", "🎯", "Detection Accuracy", config.COLORS["purple"]),
        ]

        self.stat_value_labels = {}

        for index, (key, icon, label_text, card_bg_color) in enumerate(card_specs):
            card = tk.Frame(cards_frame, bg=card_bg_color, highlightthickness=0)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 10, 0))

            inner = tk.Frame(card, bg=card_bg_color)
            inner.pack(fill="both", expand=True, padx=18, pady=16)

            icon_box = tk.Label(
                inner, text=icon, font=(config.FONT_FAMILY, 16),
                bg=card_bg_color, fg="#FFFFFF", width=3, height=1,
            )
            icon_box.pack(anchor="w")

            value_label = tk.Label(
                inner, text="0", font=config.FONTS["card_value"],
                bg=card_bg_color, fg="#FFFFFF",
            )
            value_label.pack(anchor="w", pady=(8, 0))

            caption_label = tk.Label(
                inner, text=label_text, font=config.FONTS["card_label"],
                bg=card_bg_color, fg="#FFFFFF",
            )
            caption_label.pack(anchor="w")

            self.stat_value_labels[key] = value_label

    # ------------------------------------------------------------------
    # MAIN CONTENT
    # ------------------------------------------------------------------
    def _build_main_content(self):
        content_row = tk.Frame(self, bg=config.COLORS["main_bg"])
        content_row.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 20))
        content_row.grid_rowconfigure(0, weight=1)
        content_row.grid_columnconfigure(0, weight=3)
        content_row.grid_columnconfigure(1, weight=2)

        self._build_chart_card(content_row)

        right_column = tk.Frame(content_row, bg=config.COLORS["main_bg"])
        right_column.grid(row=0, column=1, sticky="nsew", padx=(16, 0))
        right_column.grid_rowconfigure(1, weight=1)
        right_column.grid_columnconfigure(0, weight=1)

        self._build_threat_card(right_column)
        self._build_recent_predictions_card(right_column)

    # ------------------------------------------------------------------
    # SPAM DISTRIBUTION CHART CARD
    # ------------------------------------------------------------------
    def _build_chart_card(self, parent):
        card = tk.Frame(parent, bg="#FFFFFF", highlightthickness=0)
        card.grid(row=0, column=0, sticky="nsew")

        header = tk.Label(
            card, text="Spam Distribution", font=config.FONTS["section_title"],
            bg="#FFFFFF", fg=config.COLORS["text_primary"], anchor="w",
        )
        header.pack(anchor="w", padx=20, pady=(18, 6))

        chart_container = tk.Frame(card, bg="#FFFFFF")
        chart_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.figure = Figure(figsize=(5, 4), dpi=90)
        self.figure.patch.set_facecolor("#FFFFFF")
        self.chart_axes = self.figure.add_subplot(111)

        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=chart_container)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _draw_chart(self, spam_count, safe_count):
        """Redraw the donut chart with dark-yet-bright vibrant colors and scaled text."""
        self.chart_axes.clear()

        if spam_count == 0 and safe_count == 0:
            self.chart_axes.text(
                0.5, 0.5, "No predictions yet",
                ha="center", va="center", fontsize=11,
                color=config.COLORS["text_muted"], transform=self.chart_axes.transAxes,
            )
            self.chart_axes.axis("off")
        else:
            values = [spam_count, safe_count]
            labels = ["Spam", "Safe"]
            # Dark yet bright vibrant shades for Red & Green
            colors = ["#D32F2F", "#2E7D32"]

            wedges, _texts, autotexts = self.chart_axes.pie(
                values, labels=None, colors=colors, autopct="%1.0f%%",
                startangle=90, pctdistance=0.75,
                wedgeprops={"width": 0.40, "edgecolor": "#FFFFFF", "linewidth": 3},
            )
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontsize(7.5)
                autotext.set_fontweight("bold")

            self.chart_axes.legend(
                wedges, labels, loc="lower center", ncol=2, frameon=False,
                bbox_to_anchor=(0.5, -0.08), fontsize=9,
            )
            self.chart_axes.set_aspect("equal")

        self.figure.tight_layout()
        self.chart_canvas.draw()

    # ------------------------------------------------------------------
    # TOP DETECTED THREAT CARD (#F0D031 Yellow)
    # ------------------------------------------------------------------
    def _build_threat_card(self, parent):
        yellow_bg = "#DBC865"

        card = tk.Frame(parent, bg=yellow_bg, highlightthickness=0)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        inner = tk.Frame(card, bg=yellow_bg)
        inner.pack(fill="x", padx=18, pady=16)

        header = tk.Label(
            inner, text="⚠️ Top Detected Threat", font=config.FONTS["body_bold"],
            bg=yellow_bg, fg="#FFFFFF", anchor="w",
        )
        header.pack(anchor="w")

        self.threat_value_label = tk.Label(
            inner, text="N/A", font=(config.FONT_FAMILY, 22, "bold"),
            bg=yellow_bg, fg="#FFFFFF", anchor="w",
        )
        self.threat_value_label.pack(anchor="w", pady=(4, 0))

        caption = tk.Label(
            inner, text="Most frequent keyword found in spam messages",
            font=config.FONTS["small"],
            bg=yellow_bg, fg="#FFFFFF", anchor="w",
        )
        caption.pack(anchor="w")

    # ------------------------------------------------------------------
    # RECENT PREDICTIONS CARD (#4CADF3 Blue Bar + White Table)
    # ------------------------------------------------------------------
    def _build_recent_predictions_card(self, parent):
        card_bg = "#FFFFFF"

        card = tk.Frame(parent, bg=card_bg, highlightthickness=0)
        card.grid(row=1, column=0, sticky="nsew")

        # Top Header Bar using #4CADF3
        header_frame = tk.Frame(card, bg="#4CADF3", padx=14, pady=8)
        header_frame.pack(fill="x")

        header = tk.Label(
            header_frame, text="📋 Recent Predictions", font=config.FONTS["section_title"],
            bg="#4CADF3", fg="#FFFFFF", anchor="w",
        )
        header.pack(anchor="w")

        # Table Container covering full width
        table_container = tk.Frame(card, bg=card_bg, highlightthickness=0, bd=0)
        table_container.pack(fill="both", expand=True)

        columns = ("message", "prediction", "confidence")
        self.recent_tree = ttk.Treeview(
            table_container, 
            columns=columns, 
            show="headings", 
            height=5,
            style="Custom.Treeview",
            selectmode = "none"
        )
        self.recent_tree.heading("message", text="Message")
        self.recent_tree.heading("prediction", text="Result")
        self.recent_tree.heading("confidence", text="Confidence")

        self.recent_tree.column("message", width=190, anchor="w")
        self.recent_tree.column("prediction", width=70, anchor="center")
        self.recent_tree.column("confidence", width=80, anchor="center")

        self.recent_tree.pack(fill="both", expand=True)

        self.recent_tree.tag_configure("spam_row", foreground=config.COLORS["red"])
        self.recent_tree.tag_configure("ham_row", foreground=config.COLORS["green"])

    # ------------------------------------------------------------------
    # REFRESH METHOD
    # ------------------------------------------------------------------
    def refresh(self):
        """Reload every statistic, chart, and table on this page from the database."""
        stats = self.database.get_dashboard_stats()

        self.stat_value_labels["total"].config(text=str(stats["total"]))
        self.stat_value_labels["spam"].config(text=str(stats["spam_count"]))
        self.stat_value_labels["safe"].config(text=str(stats["safe_count"]))
        self.stat_value_labels["accuracy"].config(text=f"{stats['accuracy']}%")

        self._draw_chart(stats["spam_count"], stats["safe_count"])

        top_keyword = self.database.get_top_threat_keyword()
        self.threat_value_label.config(text=top_keyword.upper() if top_keyword != "N/A" else "N/A")

        self._refresh_recent_predictions()

    def _refresh_recent_predictions(self):
        for row in self.recent_tree.get_children():
            self.recent_tree.delete(row)

        recent = self.database.get_recent_predictions(limit=6)
        for row in recent:
            message_preview = row["message_text"]
            if len(message_preview) > 38:
                message_preview = message_preview[:35] + "..."

            tag = "spam_row" if row["prediction"] == config.LABEL_SPAM else "ham_row"
            self.recent_tree.insert(
                "", "end",
                values=(message_preview, row["prediction"].upper(), f"{row['confidence']}%"),
                tags=(tag,),
            )