"""
gui/analytics.py
------------------
The Analytics page: deeper statistical analysis of everything the
detector has scanned so far.

Layout (redesigned to fit a single 1366x768 screen, no scrolling):
    - A row of 3 compact statistic cards (Total Scanned, Spam Ratio,
      Model Accuracy) matching the Dashboard's visual style.
    - Two compact charts side by side:
        1. Spam vs. Safe messages scanned per day (bar chart, last 7
           days that have data).
        2. Top 5 most frequently detected suspicious keywords
           (horizontal bar chart).
"""

import tkinter as tk
from collections import Counter, defaultdict
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config


class AnalyticsPage(tk.Frame):
    """The Analytics page."""

    def __init__(self, master, database, classifier, app):
        super().__init__(master, bg=config.COLORS["main_bg"])
        self.database = database
        self.classifier = classifier
        self.app = app

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_page_title()
        self._build_stat_cards()
        self._build_charts_row()

        self.refresh()

    # ------------------------------------------------------------------
    # PAGE TITLE
    # ------------------------------------------------------------------
    def _build_page_title(self):
        title_frame = tk.Frame(self, bg=config.COLORS["main_bg"])
        title_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))

        title_label = tk.Label(
            title_frame, text="Analytics", font=config.FONTS["page_title"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_primary"],
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame, text="Statistical insights drawn from every scanned message",
            font=config.FONTS["body"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"],
        )
        subtitle_label.pack(anchor="w")

    # ------------------------------------------------------------------
    # STATISTIC CARDS (Soft Light Tones)
    # ------------------------------------------------------------------
    def _build_stat_cards(self):
        cards_frame = tk.Frame(self, bg=config.COLORS["main_bg"])
        cards_frame.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 16))

        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="analytics_stat_card")

        # Soft Light Shades for clean and soothing aesthetic
        card_specs = [
            ("total", "📩", "Total Messages Scanned", "#D4E7F9", "#3E66EA"),      # Soft Light Blue
            ("spam_ratio", "📈", "Spam Ratio", "#FEE2E2", "#991B1B"),            # Soft Light Red
            ("model_accuracy", "🎯", "Model Accuracy", "#F3E8FF", "#6B21A8"),    # Soft Light Purple
        ]

        self.summary_labels = {}

        for index, (key, icon, label_text, soft_bg, text_fg) in enumerate(card_specs):
            card = tk.Frame(cards_frame, bg=soft_bg, highlightthickness=0, bd=0)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 10, 0))

            inner = tk.Frame(card, bg=soft_bg)
            inner.pack(fill="both", expand=True, padx=18, pady=14)

            icon_box = tk.Label(
                inner, text=icon, font=(config.FONT_FAMILY, 15),
                bg=soft_bg, fg=text_fg, width=3, height=1,
            )
            icon_box.pack(anchor="w")

            value_label = tk.Label(
                inner, text="--", font=(config.FONT_FAMILY, 21, "bold"),
                bg=soft_bg, fg=text_fg,
            )
            value_label.pack(anchor="w", pady=(8, 0))

            caption_label = tk.Label(
                inner, text=label_text, font=config.FONTS["card_label"],
                bg=soft_bg, fg=text_fg,
            )
            caption_label.pack(anchor="w")

            self.summary_labels[key] = value_label

    # ------------------------------------------------------------------
    # CHARTS ROW (side by side, compact, fits without scrolling)
    # ------------------------------------------------------------------
    def _build_charts_row(self):
        charts_row = tk.Frame(self, bg=config.COLORS["main_bg"])
        charts_row.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 20))
        charts_row.grid_rowconfigure(0, weight=1)
        charts_row.grid_columnconfigure(0, weight=1, uniform="chart_col")
        charts_row.grid_columnconfigure(1, weight=1, uniform="chart_col")

        self._build_daily_trend_card(charts_row)
        self._build_top_keywords_card(charts_row)

    # ------------------------------------------------------------------
    # DAILY TREND CARD
    # ------------------------------------------------------------------
    def _build_daily_trend_card(self, parent):
        card = tk.Frame(parent, bg=config.COLORS["card_bg"], highlightthickness=1,
                         highlightbackground=config.COLORS["border"])
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        header = tk.Label(
            card, text="Messages Per Day (Spam vs Safe)",
            font=config.FONTS["section_title"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        header.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 4))

        chart_container = tk.Frame(card, bg=config.COLORS["card_bg"])
        chart_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 14))

        self.trend_figure = Figure(figsize=(5.0, 3.1), dpi=88)
        self.trend_figure.patch.set_facecolor(config.COLORS["card_bg"])
        self.trend_axes = self.trend_figure.add_subplot(111)

        self.trend_canvas = FigureCanvasTkAgg(self.trend_figure, master=chart_container)
        self.trend_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _draw_daily_trend(self, predictions):
        self.trend_axes.clear()

        if not predictions:
            self.trend_axes.text(
                0.5, 0.5, "No predictions yet", ha="center", va="center",
                fontsize=10, color=config.COLORS["text_muted"],
                transform=self.trend_axes.transAxes,
            )
            self.trend_axes.axis("off")
            self.trend_figure.tight_layout()
            self.trend_canvas.draw()
            return

        # Aggregate: {date_string: {"spam": n, "ham": n}}
        daily_counts = defaultdict(lambda: {"spam": 0, "ham": 0})
        for row in predictions:
            date_part = row["date_predicted"].split(" ")[0]
            daily_counts[date_part][row["prediction"]] += 1

        # Keep only the most recent 5 days that actually have data
        sorted_dates = sorted(daily_counts.keys())[-5:]
        spam_values = [daily_counts[d]["spam"] for d in sorted_dates]
        ham_values = [daily_counts[d]["ham"] for d in sorted_dates]

        # Shorten labels like "2026-07-21" -> "Jul 21"
        display_labels = []
        for d in sorted_dates:
            try:
                display_labels.append(datetime.strptime(d, "%Y-%m-%d").strftime("%b %d"))
            except ValueError:
                display_labels.append(d)

        # Fixed Spacing & Offset for side-by-side non-overlapping bars
        x_positions = range(len(sorted_dates))
        bar_width = 0.35
        
        x_spam = [x - (bar_width / 2) - 0.02 for x in x_positions]
        x_safe = [x + (bar_width / 2) + 0.02 for x in x_positions]

        self.trend_axes.bar(
            x_spam, spam_values, width=bar_width,
            color=config.COLORS["red"], label="Spam", align="center"
        )
        self.trend_axes.bar(
            x_safe, ham_values, width=bar_width,
            color=config.COLORS["green"], label="Safe", align="center"
        )

        self.trend_axes.set_xticks(list(x_positions))
        self.trend_axes.set_xticklabels(display_labels, fontsize=8)
        self.trend_axes.tick_params(axis="y", labelsize=8)
        
        # Add padding at the top of Y-axis
        max_val = max(max(spam_values, default=0), max(ham_values, default=0))
        self.trend_axes.set_ylim(0, max_val + (max_val * 0.25 if max_val > 0 else 5))

        self.trend_axes.legend(frameon=False, fontsize=8, loc="upper right")
        self.trend_axes.spines["top"].set_visible(False)
        self.trend_axes.spines["right"].set_visible(False)

        self.trend_figure.tight_layout()
        self.trend_canvas.draw()

    # ------------------------------------------------------------------
    # TOP KEYWORDS CARD (Border Completely Removed: bd=0, highlightthickness=0)
    # ------------------------------------------------------------------
    def _build_top_keywords_card(self, parent):
        card = tk.Frame(parent, bg=config.COLORS["card_bg"], highlightthickness=0, bd=0)
        card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        header = tk.Label(
            card, text="Top 5 Detected Keywords", font=config.FONTS["section_title"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        header.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 4))

        chart_container = tk.Frame(card, bg=config.COLORS["card_bg"], highlightthickness=0, bd=0)
        chart_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 14))

        self.keywords_figure = Figure(figsize=(5.0, 3.1), dpi=88)
        self.keywords_figure.patch.set_facecolor(config.COLORS["card_bg"])
        self.keywords_axes = self.keywords_figure.add_subplot(111)

        self.keywords_canvas = FigureCanvasTkAgg(self.keywords_figure, master=chart_container)
        self.keywords_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _draw_top_keywords(self, predictions):
        self.keywords_axes.clear()

        keyword_counter = Counter()
        for row in predictions:
            if row["prediction"] != config.LABEL_SPAM:
                continue
            for keyword in (row["detected_keywords"] or "").split(","):
                keyword = keyword.strip()
                if keyword:
                    keyword_counter[keyword] += 1

        top_items = keyword_counter.most_common(5)

        if not top_items:
            self.keywords_axes.text(
                0.5, 0.5, "No keywords detected yet", ha="center", va="center",
                fontsize=10, color=config.COLORS["text_muted"],
                transform=self.keywords_axes.transAxes,
            )
            self.keywords_axes.axis("off")
        else:
            labels = [item[0] for item in top_items][::-1]
            values = [item[1] for item in top_items][::-1]

            self.keywords_axes.barh(labels, values, color=config.COLORS["purple"])
            self.keywords_axes.tick_params(axis="both", labelsize=8)
            self.keywords_axes.spines["top"].set_visible(False)
            self.keywords_axes.spines["right"].set_visible(False)

        self.keywords_figure.tight_layout()
        self.keywords_canvas.draw()

    # ------------------------------------------------------------------
    # REFRESH
    # ------------------------------------------------------------------
    def refresh(self):
        """Reload every chart and statistic on this page from the database."""
        stats = self.database.get_dashboard_stats()
        predictions = self.database.get_all_predictions()

        self.summary_labels["total"].config(text=str(stats["total"]))

        if stats["total"] > 0:
            spam_ratio = round((stats["spam_count"] / stats["total"]) * 100, 1)
        else:
            spam_ratio = 0.0
        self.summary_labels["spam_ratio"].config(text=f"{spam_ratio}%")
        self.summary_labels["model_accuracy"].config(text=f"{stats['accuracy']}%")

        self._draw_daily_trend(predictions)
        self._draw_top_keywords(predictions)