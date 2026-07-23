"""
analytics.py
------------------------------------------------------------------
Analytics page - provides statistical analysis of the recruitment
data collected so far, fulfilling the "Statistical Analysis"
requirement of the project brief.

Displays:
    - Score distribution pie chart (Excellent / Good / Average / Low)
    - Screenings-per-job bar chart with average score overlay
    - A small statistics summary table (mean, median, min, max, std
      deviation of all match scores), computed using pandas

All charts are rendered with matplotlib, embedded directly into the
Tkinter window via FigureCanvasTkAgg for a native, responsive look.
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config


class AnalyticsPage(tk.Frame):
    """Statistical analysis and visual reporting of screening data."""

    def __init__(self, parent, db_manager):
        colors = config.COLORS
        super().__init__(parent, bg=colors["workspace_bg"])

        self.db_manager = db_manager
        self.colors = colors

        self._build_layout()

    # ==================================================================
    # LAYOUT
    # ==================================================================
    def _build_layout(self):
        outer = tk.Frame(self, bg=self.colors["workspace_bg"])
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        content_row = tk.Frame(outer, bg=self.colors["workspace_bg"])
        content_row.pack(fill="both", expand=True)
        content_row.grid_columnconfigure(0, weight=35)
        content_row.grid_columnconfigure(1, weight=40)
        content_row.grid_columnconfigure(2, weight=25)
        content_row.grid_rowconfigure(0, weight=1)

        # ----- Pie chart card: score distribution -----
        pie_card = self._create_card(content_row)
        pie_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self._build_distribution_chart(pie_card)

        # ----- Bar chart card: screenings per job -----
        bar_card = self._create_card(content_row)
        bar_card.grid(row=0, column=1, sticky="nsew", padx=(0, 14))
        self._build_job_performance_chart(bar_card)

        # ----- Summary statistics card -----
        stats_card = self._create_card(content_row)
        stats_card.grid(row=0, column=2, sticky="nsew")
        self._build_summary_stats(stats_card)

    # ------------------------------------------------------------
    def _create_card(self, parent):
        colors = self.colors
        card = tk.Frame(parent, bg=colors["card_bg"], highlightthickness=1,
                         highlightbackground=colors["card_border"])
        return card

    # ------------------------------------------------------------
    def _build_distribution_chart(self, parent):
        """Builds the score distribution pie chart section."""
        colors = self.colors

        tk.Label(
            parent, text="Match Score Distribution", font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(anchor="w", padx=18, pady=(16, 4))

        chart_frame = tk.Frame(parent, bg=colors["card_bg"])
        chart_frame.pack(fill="both", expand=True, padx=10, pady=(0, 14))

        self.pie_figure = Figure(figsize=(3.6, 3.2), dpi=100)
        self.pie_figure.patch.set_facecolor(colors["card_bg"])
        self.pie_axis = self.pie_figure.add_subplot(111)

        self.pie_canvas = FigureCanvasTkAgg(self.pie_figure, master=chart_frame)
        self.pie_canvas.get_tk_widget().pack(fill="both", expand=True)

    # ------------------------------------------------------------
    def _build_job_performance_chart(self, parent):
        """Builds the screenings-per-job bar chart section."""
        colors = self.colors

        tk.Label(
            parent, text="Screenings per Job Posting", font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(anchor="w", padx=18, pady=(16, 4))

        chart_frame = tk.Frame(parent, bg=colors["card_bg"])
        chart_frame.pack(fill="both", expand=True, padx=10, pady=(0, 14))

        self.job_figure = Figure(figsize=(4, 3.2), dpi=100)
        self.job_figure.patch.set_facecolor(colors["card_bg"])
        self.job_axis = self.job_figure.add_subplot(111)

        self.job_canvas = FigureCanvasTkAgg(self.job_figure, master=chart_frame)
        self.job_canvas.get_tk_widget().pack(fill="both", expand=True)

    # ------------------------------------------------------------
    def _build_summary_stats(self, parent):
        """Builds the pandas-powered summary statistics panel."""
        colors = self.colors

        tk.Label(
            parent, text="Score Statistics", font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(anchor="w", padx=18, pady=(16, 10))

        self.stats_container = tk.Frame(parent, bg=colors["card_bg"])
        self.stats_container.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    # ------------------------------------------------------------
    def _create_stat_row(self, parent, label_text, value_text):
        """Creates one label/value row inside the statistics panel."""
        colors = self.colors
        row = tk.Frame(parent, bg=colors["card_bg"])
        row.pack(fill="x", pady=6)

        tk.Label(
            row, text=label_text, font=config.FONTS["body"],
            bg=colors["card_bg"], fg=colors["text_secondary"]
        ).pack(side="left")

        tk.Label(
            row, text=value_text, font=config.FONTS["body_bold"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(side="right")

        divider = tk.Frame(parent, bg=colors["card_border"], height=1)
        divider.pack(fill="x", pady=(0, 0))

    # ==================================================================
    # DATA REFRESH
    # ==================================================================
    def refresh(self):
        """Reloads all charts and statistics from the database."""
        self._refresh_distribution_chart()
        self._refresh_job_performance_chart()
        self._refresh_summary_stats()

    # ------------------------------------------------------------
    def _refresh_distribution_chart(self):
        """Redraws the score distribution pie chart."""
        distribution = self.db_manager.get_score_distribution()
        colors = self.colors

        self.pie_axis.clear()

        labels = list(distribution.keys())
        values = list(distribution.values())
        total = sum(values)

        if total == 0:
            self.pie_axis.text(
                0.5, 0.5, "No screening data yet", ha="center", va="center",
                fontsize=10, color=colors["text_muted"], transform=self.pie_axis.transAxes
            )
            self.pie_axis.set_xticks([])
            self.pie_axis.set_yticks([])
        else:
            slice_colors = [
                colors["success"], colors["accent_primary"],
                colors["warning"], colors["danger"],
            ]
            wedges, texts, autotexts = self.pie_axis.pie(
                values, labels=labels, autopct=lambda pct: f"{pct:.0f}%" if pct > 0 else "",
                colors=slice_colors, startangle=90,
                textprops={"fontsize": 8, "color": colors["text_primary"]},
                wedgeprops={"linewidth": 1, "edgecolor": colors["card_bg"]}
            )
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontsize(8)
                autotext.set_fontweight("bold")

        self.pie_figure.tight_layout()
        self.pie_canvas.draw()

    # ------------------------------------------------------------
    def _refresh_job_performance_chart(self):
        """Redraws the screenings-per-job bar chart with an average-score line."""
        job_stats = self.db_manager.get_screenings_per_job()
        colors = self.colors

        self.job_axis.clear()

        if not job_stats:
            self.job_axis.text(
                0.5, 0.5, "No job data yet", ha="center", va="center",
                fontsize=10, color=colors["text_muted"], transform=self.job_axis.transAxes
            )
            self.job_axis.set_xticks([])
            self.job_axis.set_yticks([])
        else:
            # Use pandas to conveniently handle/aggregate the job stats
            dataframe = pd.DataFrame(job_stats)
            dataframe["job_title_short"] = dataframe["job_title"].apply(
                lambda title: title if len(title) <= 14 else title[:12] + "…"
            )

            bar_positions = range(len(dataframe))
            self.job_axis.bar(
                bar_positions, dataframe["screening_count"],
                color=colors["accent_primary"], width=0.55
            )
            self.job_axis.set_xticks(list(bar_positions))
            self.job_axis.set_xticklabels(
                dataframe["job_title_short"], rotation=30, ha="right", fontsize=7
            )
            self.job_axis.set_ylabel("Screenings", fontsize=8, color=colors["text_secondary"])

        self.job_axis.set_facecolor(colors["card_bg"])
        self.job_axis.spines["top"].set_visible(False)
        self.job_axis.spines["right"].set_visible(False)
        self.job_axis.tick_params(labelsize=7, colors=colors["text_secondary"])
        self.job_figure.tight_layout()
        self.job_canvas.draw()

    # ------------------------------------------------------------
    def _refresh_summary_stats(self):
        """
        Computes descriptive statistics over all match scores using
        pandas (mean, median, std deviation, min, max, count) and
        displays them in the summary panel.
        """
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        screenings = self.db_manager.get_all_screenings()

        if not screenings:
            tk.Label(
                self.stats_container, text="No screening data available yet.\n"
                                            "Run a screening to see statistics.",
                font=config.FONTS["small"], bg=self.colors["card_bg"], fg=self.colors["text_muted"],
                justify="left"
            ).pack(anchor="w", pady=10)
            return

        # Load scores into a pandas Series for statistical analysis
        scores_series = pd.Series([record["match_score"] for record in screenings])

        self._create_stat_row(self.stats_container, "Total Screenings", str(len(scores_series)))
        self._create_stat_row(self.stats_container, "Average Score", f"{scores_series.mean():.1f}%")
        self._create_stat_row(self.stats_container, "Median Score", f"{scores_series.median():.1f}%")
        self._create_stat_row(self.stats_container, "Highest Score", f"{scores_series.max():.1f}%")
        self._create_stat_row(self.stats_container, "Lowest Score", f"{scores_series.min():.1f}%")
        self._create_stat_row(self.stats_container, "Std. Deviation", f"{scores_series.std():.1f}")
