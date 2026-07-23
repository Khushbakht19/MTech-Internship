"""
dashboard.py
------------------------------------------------------------------
The Dashboard page with a clean layout and modern custom scrollbar.
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import config
from utils.helpers import format_date, format_score


class ModernScrollbar(tk.Canvas):
    """Custom thin & modern scrollbar replacing the clunky default OS scrollbar."""
    
    def __init__(self, parent, target_canvas, width=6, bg_color="#F3F4F6", thumb_color="#CBD5E1", thumb_hover="#94A3B8"):
        super().__init__(parent, width=width, bg=bg_color, highlightthickness=0, bd=0)
        self.target_canvas = target_canvas
        self.thumb_color = thumb_color
        self.thumb_hover = thumb_hover
        self.bg_color = bg_color
        self.width_px = width
        
        self.thumb_id = None
        self._dragging = False
        self._start_y = 0
        
        # Bind events
        self.bind("<Configure>", self._update_thumb)
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Enter>", lambda e: self.itemconfig(self.thumb_id, fill=self.thumb_hover))
        self.bind("<Leave>", lambda e: self.itemconfig(self.thumb_id, fill=self.thumb_color))
        
        # Listen to canvas scrolling
        self.target_canvas.configure(yscrollcommand=self._on_canvas_scroll)

    def _on_canvas_scroll(self, first, last):
        self.first = float(first)
        self.last = float(last)
        self._update_thumb()

    def _update_thumb(self, event=None):
        self.delete("all")
        if not hasattr(self, 'first') or not hasattr(self, 'last'):
            return
            
        height = self.winfo_height()
        if self.last - self.first >= 1.0:
            return  # No scrollbar needed if content fits
            
        y1 = self.first * height
        y2 = self.last * height
        
        # Ensure minimum visible thumb height
        if (y2 - y1) < 20:
            y2 = y1 + 20

        # Draw sleek rounded rectangle thumb
        self.thumb_id = self.create_rectangle(
            1, y1, self.width_px - 1, y2,
            fill=self.thumb_color, outline="", width=0
        )

    def _on_click(self, event):
        self._dragging = True
        self._start_y = event.y

    def _on_drag(self, event):
        if not self._dragging:
            return
        height = self.winfo_height()
        if height == 0:
            return
        delta = (event.y - self._start_y) / height
        self._start_y = event.y
        self.target_canvas.yview_scroll(int(delta * 30), "units")


class DashboardPage(tk.Frame):
    """Main landing page showing key recruitment metrics at a glance."""

    def __init__(self, parent, db_manager, navigate_callback):
        colors = config.COLORS
        super().__init__(parent, bg=colors["workspace_bg"])

        self.db_manager = db_manager
        self.navigate_callback = navigate_callback
        self.colors = colors

        self.stat_value_labels = {}
        self.recent_screenings_container = None
        self.top_candidate_container = None

        self._build_layout()

    # ==================================================================
    # LAYOUT CONSTRUCTION
    # ==================================================================
    def _build_layout(self):
        """Builds the static structure of the dashboard."""
        outer = tk.Frame(self, bg=self.colors["workspace_bg"])
        # Tightened top padding to move elements up gracefully
        outer.pack(fill="both", expand=True, padx=20, pady=(6, 12))

        # ---------------- Row 1: Statistic Cards ----------------
        stats_row = tk.Frame(outer, bg=self.colors["workspace_bg"])
        stats_row.pack(fill="x", pady=(0, 10))

        stat_definitions = [
            ("total_candidates", "👥", "Total Candidates", self.colors["accent_primary"]),
            ("total_jobs", "💼", "Active Job Postings", self.colors["info"]),
            ("total_screenings", "🔍", "Screening Sessions", "#8B5CF6"),
            ("average_match_score", "⭐", "Average Match Score", self.colors["warning"]),
        ]

        for index, (stat_key, icon, label, accent_color) in enumerate(stat_definitions):
            card = self._create_stat_card(stats_row, icon, label, accent_color)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 10, 0))
            stats_row.grid_columnconfigure(index, weight=1)
            self.stat_value_labels[stat_key] = card.value_label

        # ---------------- Row 2: Charts + Side panel ----------------
        content_row = tk.Frame(outer, bg=self.colors["workspace_bg"])
        content_row.pack(fill="both", expand=True)
        content_row.grid_columnconfigure(0, weight=65)
        content_row.grid_columnconfigure(1, weight=35)
        content_row.grid_rowconfigure(0, weight=1)

        # ----- Left column: ranking chart + recent screenings -----
        left_column = tk.Frame(content_row, bg=self.colors["workspace_bg"])
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_column.grid_rowconfigure(0, weight=52)
        left_column.grid_rowconfigure(1, weight=48)
        left_column.grid_columnconfigure(0, weight=1)

        chart_card = self._create_card(left_column)
        chart_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self._build_ranking_chart(chart_card)

        recent_card = self._create_card(left_column)
        recent_card.grid(row=1, column=0, sticky="nsew")
        self._build_recent_screenings(recent_card)

        # ----- Right column: top candidate + quick action -----
        right_column = tk.Frame(content_row, bg=self.colors["workspace_bg"])
        right_column.grid(row=0, column=1, sticky="nsew")
        right_column.grid_rowconfigure(0, weight=58)
        right_column.grid_rowconfigure(1, weight=42)
        right_column.grid_columnconfigure(0, weight=1)

        top_candidate_card = self._create_card(right_column)
        top_candidate_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self._build_top_candidate_card(top_candidate_card)

        quick_action_card = self._create_card(right_column)
        quick_action_card.grid(row=1, column=0, sticky="nsew")
        self._build_quick_actions(quick_action_card)

    # ------------------------------------------------------------
    def _create_stat_card(self, parent, icon, label_text, accent_color):
        """Creates one headline statistic card with compact vertical padding."""
        colors = self.colors

        card = tk.Frame(parent, bg=colors["card_bg"], highlightthickness=1,
                        highlightbackground=colors["card_border"])

        accent_strip = tk.Frame(card, bg=accent_color, height=3)
        accent_strip.pack(fill="x", side="top")

        # Reduced inner padding (pady=6) to bring text slightly up
        inner = tk.Frame(card, bg=colors["card_bg"])
        inner.pack(fill="both", expand=True, padx=12, pady=6)

        top_row = tk.Frame(inner, bg=colors["card_bg"])
        top_row.pack(fill="x")

        icon_badge = tk.Label(
            top_row, text=icon, font=("Segoe UI Emoji", 12),
            bg=colors["workspace_bg"], fg=accent_color, width=2, height=1
        )
        icon_badge.pack(side="left")

        value_label = tk.Label(
            inner, text="0", font=config.FONTS["stat_value"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        )
        value_label.pack(anchor="w", pady=(2, 0))

        caption_label = tk.Label(
            inner, text=label_text, font=config.FONTS["stat_label"],
            bg=colors["card_bg"], fg=colors["text_secondary"],
            wraplength=130, justify="left"
        )
        caption_label.pack(anchor="w")

        card.value_label = value_label
        return card

    # ------------------------------------------------------------
    def _create_card(self, parent):
        colors = self.colors
        return tk.Frame(parent, bg=colors["card_bg"], highlightthickness=1,
                        highlightbackground=colors["card_border"])

    # ------------------------------------------------------------
    def _build_ranking_chart(self, parent):
        """Builds the ranking chart with optimized title spacing."""
        colors = self.colors

        # Header padding adjusted to (6, 0)
        header = tk.Frame(parent, bg=colors["card_bg"])
        header.pack(fill="x", padx=12, pady=(6, 0))
        
        tk.Label(
            header, text="Top Candidates by Match Score", font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(side="left")

        chart_frame = tk.Frame(parent, bg=colors["card_bg"])
        chart_frame.pack(fill="both", expand=True, padx=6, pady=(2, 4))

        self.ranking_figure = Figure(figsize=(5, 2.2), dpi=100)
        self.ranking_figure.patch.set_facecolor(colors["card_bg"])
        self.ranking_axis = self.ranking_figure.add_subplot(111)

        self.ranking_canvas = FigureCanvasTkAgg(self.ranking_figure, master=chart_frame)
        self.ranking_canvas.get_tk_widget().pack(fill="both", expand=True)

    # ------------------------------------------------------------
    def _build_recent_screenings(self, parent):
        """Builds 'Recent Screenings' with a modern 6px thin custom scrollbar."""
        colors = self.colors

        # Adjusted title spacing (6, 2) to move header up cleanly without touching top border
        header = tk.Frame(parent, bg=colors["card_bg"])
        header.pack(fill="x", padx=12, pady=(6, 2))
        
        tk.Label(
            header, text="Recent Screenings", font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(side="left")

        wrapper = tk.Frame(parent, bg=colors["card_bg"])
        wrapper.pack(fill="both", expand=True, padx=(12, 6), pady=(0, 6))

        canvas = tk.Canvas(wrapper, bg=colors["card_bg"], highlightthickness=0, bd=0)
        
        # Attach custom sleek scrollbar (6px width, modern colors)
        custom_scrollbar = ModernScrollbar(
            wrapper, target_canvas=canvas, width=6,
            bg_color=colors["card_bg"],
            thumb_color="#CBD5E1", thumb_hover="#94A3B8"
        )

        self.recent_screenings_container = tk.Frame(canvas, bg=colors["card_bg"])

        self.recent_screenings_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=self.recent_screenings_container, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", _on_canvas_configure)

        # Smooth mousewheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        custom_scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    # ------------------------------------------------------------
    def _build_top_candidate_card(self, parent):
        colors = self.colors

        header = tk.Frame(parent, bg=colors["card_bg"])
        header.pack(fill="x", padx=12, pady=(6, 2))
        
        tk.Label(
            header, text="🏆 Top Candidate", font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(side="left")

        self.top_candidate_container = tk.Frame(parent, bg=colors["card_bg"])
        self.top_candidate_container.pack(fill="both", expand=True, padx=12, pady=(0, 6))

    # ------------------------------------------------------------
    def _build_quick_actions(self, parent):
        colors = self.colors

        inner = tk.Frame(parent, bg=colors["card_bg"])
        inner.pack(fill="both", expand=True, padx=12, pady=8)

        tk.Label(
            inner, text="Ready to screen candidates?", font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(anchor="w")

        tk.Label(
            inner, text="Match resumes against a job description\nusing TF-IDF & Cosine Similarity.",
            font=config.FONTS["small"], bg=colors["card_bg"], fg=colors["text_secondary"],
            justify="left", wraplength=210
        ).pack(anchor="w", pady=(2, 8))

        start_button = ttk.Button(
            inner, text="Start New Screening →", style="Primary.TButton",
            command=lambda: self.navigate_callback("screening")
        )
        start_button.pack(anchor="w")

    # ==================================================================
    # DATA REFRESH
    # ==================================================================
    def refresh(self):
        self._refresh_stat_cards()
        self._refresh_ranking_chart()
        self._refresh_recent_screenings()
        self._refresh_top_candidate()

    def _refresh_stat_cards(self):
        stats = self.db_manager.get_dashboard_stats()
        self.stat_value_labels["total_candidates"].config(text=str(stats["total_candidates"]))
        self.stat_value_labels["total_jobs"].config(text=str(stats["total_jobs"]))
        self.stat_value_labels["total_screenings"].config(text=str(stats["total_screenings"]))
        self.stat_value_labels["average_match_score"].config(text=f"{stats['average_match_score']}%")

    def _refresh_ranking_chart(self):
        top_candidates = self.db_manager.get_top_candidates_overall(limit=6)
        self.ranking_axis.clear()

        if top_candidates:
            names = [row["full_name"] for row in reversed(top_candidates)]
            scores = [row["best_score"] for row in reversed(top_candidates)]
            bar_colors = [config.get_score_color(score) for score in scores]

            self.ranking_axis.barh(names, scores, color=bar_colors, height=0.55)
            self.ranking_axis.set_xlim(0, 100)
            self.ranking_axis.set_xlabel("Match Score (%)", fontsize=8, color=self.colors["text_secondary"])
        else:
            self.ranking_axis.text(
                0.5, 0.5, "No screening data yet", ha="center", va="center",
                fontsize=10, color=self.colors["text_muted"], transform=self.ranking_axis.transAxes
            )
            self.ranking_axis.set_xticks([])
            self.ranking_axis.set_yticks([])

        self.ranking_axis.set_facecolor(self.colors["card_bg"])
        self.ranking_axis.spines["top"].set_visible(False)
        self.ranking_axis.spines["right"].set_visible(False)
        self.ranking_axis.tick_params(labelsize=8, colors=self.colors["text_secondary"])
        self.ranking_figure.tight_layout()
        self.ranking_canvas.draw()

    def _refresh_recent_screenings(self):
        for widget in self.recent_screenings_container.winfo_children():
            widget.destroy()

        recent_screenings = self.db_manager.get_recent_screenings(limit=10)

        if not recent_screenings:
            tk.Label(
                self.recent_screenings_container, text="No screenings have been run yet.",
                font=config.FONTS["small"], bg=self.colors["card_bg"], fg=self.colors["text_muted"]
            ).pack(anchor="w", pady=6)
            return

        for screening in recent_screenings:
            self._create_screening_row(self.recent_screenings_container, screening)

    def _create_screening_row(self, parent, screening):
        colors = self.colors
        score = screening["match_score"]

        row = tk.Frame(parent, bg=colors["card_bg"])
        row.pack(fill="x", pady=3, padx=2)

        text_frame = tk.Frame(row, bg=colors["card_bg"])
        text_frame.pack(side="left", fill="x", expand=True)

        tk.Label(
            text_frame, text=screening["candidate_name"], font=config.FONTS["body_bold"],
            bg=colors["card_bg"], fg=colors["text_primary"], wraplength=190, justify="left"
        ).pack(anchor="w")

        tk.Label(
            text_frame, text=f"{screening['job_title']} · {format_date(screening['screening_date'])}",
            font=config.FONTS["small"], bg=colors["card_bg"], fg=colors["text_secondary"],
            wraplength=190, justify="left"
        ).pack(anchor="w")

        badge_bg = config.get_score_color(score)
        badge = tk.Label(
            row, text=format_score(score), font=config.FONTS["small"],
            bg=badge_bg, fg="white", padx=6, pady=1
        )
        badge.pack(side="right")

        sep = tk.Frame(parent, bg=colors["card_border"], height=1)
        sep.pack(fill="x", pady=(2, 0))

    def _refresh_top_candidate(self):
        for widget in self.top_candidate_container.winfo_children():
            widget.destroy()

        top_candidate = self.db_manager.get_top_candidate()
        colors = self.colors

        if not top_candidate:
            tk.Label(
                self.top_candidate_container,
                text="Run a screening to discover\nyour top-matching candidate.",
                font=config.FONTS["small"], bg=colors["card_bg"], fg=colors["text_muted"],
                justify="left"
            ).pack(anchor="w", pady=6)
            return

        initials = "".join([part[0].upper() for part in top_candidate["full_name"].split()[:2]])
        avatar = tk.Label(
            self.top_candidate_container, text=initials, font=(config.FONT_FAMILY, 13, "bold"),
            bg=colors["accent_primary"], fg="white", width=3, height=1
        )
        avatar.pack(anchor="w", pady=(2, 4))

        tk.Label(
            self.top_candidate_container, text=top_candidate["full_name"],
            font=config.FONTS["section_title"], bg=colors["card_bg"], fg=colors["text_primary"],
            wraplength=210, justify="left"
        ).pack(anchor="w")

        tk.Label(
            self.top_candidate_container, text=top_candidate["email"] or "No email on file",
            font=config.FONTS["small"], bg=colors["card_bg"], fg=colors["text_secondary"],
            wraplength=210, justify="left"
        ).pack(anchor="w", pady=(0, 4))

        score = top_candidate["match_score"]
        score_badge = tk.Label(
            self.top_candidate_container,
            text=f"{format_score(score)} match for {top_candidate['job_title']}",
            font=config.FONTS["body_bold"], bg=config.get_score_color(score), fg="white",
            padx=6, pady=3, wraplength=210, justify="left"
        )
        score_badge.pack(anchor="w", pady=(0, 4))

        skills_text = top_candidate["skills"] or "No skills listed"
        tk.Label(
            self.top_candidate_container, text=f"Skills: {skills_text}",
            font=config.FONTS["small"], bg=colors["card_bg"], fg=colors["text_secondary"],
            wraplength=210, justify="left"
        ).pack(anchor="w")