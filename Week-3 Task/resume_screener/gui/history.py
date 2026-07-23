"""
history.py
------------------------------------------------------------------
Screening History page.

Displays every past screening record (candidate + job + match score
+ date) in a searchable, filterable table. Recruiters can:
    - Search by candidate name or job title
    - Filter by job posting
    - Filter by minimum match score
    - Delete individual screening records
    - View matched keywords for any screening at a glance

This page reads exclusively from the screening_history table via
DatabaseManager, joined with candidate and job names.
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

import config
from utils.helpers import format_date, format_score, truncate_text


class HistoryPage(tk.Frame):
    """Displays and manages the full screening history log."""

    def __init__(self, parent, db_manager):
        colors = config.COLORS
        super().__init__(parent, bg=colors["workspace_bg"])

        self.db_manager = db_manager
        self.colors = colors
        self.selected_screening_id = None
        self.job_filter_lookup = {}  # display string -> job_id (or None for "All Jobs")

        self._build_layout()
        self.refresh()

    # ==================================================================
    # LAYOUT
    # ==================================================================
    def _build_layout(self):
        outer = tk.Frame(self, bg=self.colors["workspace_bg"])
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        # ---------------- Filter toolbar ----------------
        toolbar = tk.Frame(outer, bg=self.colors["workspace_bg"])
        toolbar.pack(fill="x", pady=(0, 14))

        # Search box
        search_frame = tk.Frame(toolbar, bg="#FFFFFF", highlightthickness=1,
                                 highlightbackground=self.colors["card_border"])
        search_frame.pack(side="left", fill="x", expand=True, ipady=4)

        tk.Label(search_frame, text="🔎", bg="#FFFFFF", fg=self.colors["text_muted"]) \
            .pack(side="left", padx=(10, 4))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh())
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var, relief="flat",
            font=config.FONTS["body"], bg="#FFFFFF", fg=self.colors["text_primary"]
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Job filter dropdown
        tk.Label(
            toolbar, text="Job:", font=config.FONTS["body_bold"],
            bg=self.colors["workspace_bg"], fg=self.colors["text_primary"]
        ).pack(side="left", padx=(16, 6))

        self.job_filter_combobox = ttk.Combobox(
            toolbar, state="readonly", width=22,
            style="Modern.TCombobox", font=config.FONTS["body"]
        )
        self.job_filter_combobox.pack(side="left")
        self.job_filter_combobox.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Minimum score filter dropdown
        tk.Label(
            toolbar, text="Min Score:", font=config.FONTS["body_bold"],
            bg=self.colors["workspace_bg"], fg=self.colors["text_primary"]
        ).pack(side="left", padx=(16, 6))

        self.min_score_combobox = ttk.Combobox(
            toolbar, state="readonly", width=10,
            values=["All", "30%", "50%", "75%"],
            style="Modern.TCombobox", font=config.FONTS["body"]
        )
        self.min_score_combobox.current(0)
        self.min_score_combobox.pack(side="left")
        self.min_score_combobox.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # ---------------- Table card ----------------
        table_card = tk.Frame(outer, bg=self.colors["card_bg"], highlightthickness=1,
                               highlightbackground=self.colors["card_border"])
        table_card.pack(fill="both", expand=True)

        table_container = tk.Frame(table_card, bg=self.colors["card_bg"])
        table_container.pack(fill="both", expand=True, padx=16, pady=16)

        columns = ("candidate", "job", "score", "keywords", "rank", "date")
        column_headers = {
            "candidate": "Candidate", "job": "Job Title", "score": "Match Score",
            "keywords": "Matched Keywords", "rank": "Rank", "date": "Screening Date",
        }
        column_widths = {
            "candidate": 160, "job": 170, "score": 100,
            "keywords": 300, "rank": 60, "date": 150,
        }

        self.tree = ttk.Treeview(
            table_container, columns=columns, show="headings",
            style="Modern.Treeview", selectmode="browse"
        )
        for column in columns:
            self.tree.heading(column, text=column_headers[column])
            self.tree.column(column, width=column_widths[column], anchor="w")

        vertical_scrollbar = ttk.Scrollbar(
            table_container, orient="vertical", command=self.tree.yview,
            style="Modern.TScrollbar"
        )
        self.tree.configure(yscrollcommand=vertical_scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vertical_scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)

        self.tree.tag_configure("excellent", background=self.colors["accent_primary_light"])
        self.tree.tag_configure("good", background="#DBEAFE")
        self.tree.tag_configure("average", background="#FEF3C7")
        self.tree.tag_configure("low", background="#FEE2E2")

        # ---------------- Action bar ----------------
        action_bar = tk.Frame(outer, bg=self.colors["workspace_bg"])
        action_bar.pack(fill="x", pady=(12, 0))

        self.delete_button = ttk.Button(
            action_bar, text="Delete Record", style="Danger.TButton",
            command=self._delete_selected_record, state="disabled"
        )
        self.delete_button.pack(side="left")

        self.result_count_label = tk.Label(
            action_bar, text="", font=config.FONTS["small"],
            bg=self.colors["workspace_bg"], fg=self.colors["text_secondary"]
        )
        self.result_count_label.pack(side="right")

    # ==================================================================
    # DATA REFRESH
    # ==================================================================
    def refresh(self):
        """Reloads the job filter dropdown and the history table."""
        self._refresh_job_filter_options()
        self._refresh_table()

    # ------------------------------------------------------------
    def _refresh_job_filter_options(self):
        """Rebuilds the job filter dropdown, preserving the current selection if possible."""
        current_selection = self.job_filter_combobox.get()

        jobs = self.db_manager.get_all_jobs()
        self.job_filter_lookup = {"All Jobs": None}
        for job in jobs:
            self.job_filter_lookup[job["job_title"]] = job["id"]

        self.job_filter_combobox["values"] = list(self.job_filter_lookup.keys())

        if current_selection in self.job_filter_lookup:
            self.job_filter_combobox.set(current_selection)
        else:
            self.job_filter_combobox.current(0)

    # ------------------------------------------------------------
    def _refresh_table(self):
        """Reloads the screening history table applying all active filters."""
        search_term = self.search_var.get().strip() or None

        job_filter_label = self.job_filter_combobox.get()
        job_id = self.job_filter_lookup.get(job_filter_label)

        min_score_label = self.min_score_combobox.get()
        min_score = None if min_score_label == "All" else float(min_score_label.replace("%", ""))

        screenings = self.db_manager.get_all_screenings(
            job_id=job_id, min_score=min_score, search_term=search_term
        )

        self.tree.delete(*self.tree.get_children())

        for screening in screenings:
            score = screening["match_score"]
            if score >= config.SCORE_THRESHOLDS["excellent"]:
                tag = "excellent"
            elif score >= config.SCORE_THRESHOLDS["good"]:
                tag = "good"
            elif score >= config.SCORE_THRESHOLDS["average"]:
                tag = "average"
            else:
                tag = "low"

            self.tree.insert(
                "", "end", iid=str(screening["id"]),
                values=(
                    screening["candidate_name"],
                    screening["job_title"],
                    format_score(score),
                    truncate_text(screening["matched_keywords"] or "-", 45),
                    screening["rank_position"] or "-",
                    format_date(screening["screening_date"]),
                ),
                tags=(tag,)
            )

        self.result_count_label.config(text=f"{len(screenings)} screening record(s) found")
        self._on_row_selected()

    # ------------------------------------------------------------
    def _on_row_selected(self, event=None):
        selection = self.tree.selection()
        if selection:
            self.selected_screening_id = int(selection[0])
            self.delete_button.config(state="normal")
        else:
            self.selected_screening_id = None
            self.delete_button.config(state="disabled")

    # ==================================================================
    # DELETE
    # ==================================================================
    def _delete_selected_record(self):
        if self.selected_screening_id is None:
            return
        confirmed = messagebox.askyesno(
            "Delete Screening Record",
            "Are you sure you want to delete this screening record?\nThis action cannot be undone."
        )
        if confirmed:
            self.db_manager.delete_screening_record(self.selected_screening_id)
            self.refresh()
