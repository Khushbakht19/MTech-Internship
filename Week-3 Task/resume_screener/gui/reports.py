"""
reports.py
------------------------------------------------------------------
Reports page - lets recruiters export their data for offline use
or sharing with hiring managers, fulfilling the "Reports" module
and CSV/PDF export requirements of the project brief.

Supports exporting:
    - Candidates list
    - Job postings list
    - Screening history (with optional job filter)

Exports are written into the exports/ folder using utils/helpers.py,
supporting both CSV (always available) and PDF (rendered via
matplotlib, so no extra heavyweight PDF library is required).
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

import config
from utils.helpers import export_to_csv, export_to_pdf, generate_export_filename, format_date, format_score


class ReportsPage(tk.Frame):
    """Lets recruiters export candidates, jobs, or screening history."""

    def __init__(self, parent, db_manager):
        colors = config.COLORS
        super().__init__(parent, bg=colors["workspace_bg"])

        self.db_manager = db_manager
        self.colors = colors
        self.job_filter_lookup = {}

        self._build_layout()

    # ==================================================================
    # LAYOUT
    # ==================================================================
    def _build_layout(self):
        outer = tk.Frame(self, bg=self.colors["workspace_bg"])
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        # Intro card
        intro_card = tk.Frame(outer, bg=self.colors["card_bg"], highlightthickness=1,
                               highlightbackground=self.colors["card_border"])
        intro_card.pack(fill="x", pady=(0, 18))

        intro_inner = tk.Frame(intro_card, bg=self.colors["card_bg"])
        intro_inner.pack(fill="x", padx=20, pady=16)

        tk.Label(
            intro_inner, text="📁  Export Reports", font=config.FONTS["section_title"],
            bg=self.colors["card_bg"], fg=self.colors["text_primary"]
        ).pack(anchor="w")

        tk.Label(
            intro_inner,
            text="Generate CSV or PDF reports of your recruitment data. "
                 "Files are saved in the application's exports folder.",
            font=config.FONTS["small"], bg=self.colors["card_bg"], fg=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(4, 0))

        # Report options row
        options_row = tk.Frame(outer, bg=self.colors["workspace_bg"])
        options_row.pack(fill="both", expand=True)
        options_row.grid_columnconfigure(0, weight=1)
        options_row.grid_columnconfigure(1, weight=1)
        options_row.grid_columnconfigure(2, weight=1)
        options_row.grid_rowconfigure(0, weight=1)

        self._build_candidates_report_card(options_row, column=0)
        self._build_jobs_report_card(options_row, column=1)
        self._build_history_report_card(options_row, column=2)

    # ------------------------------------------------------------
    def _create_report_card(self, parent, column, icon, title, description):
        """Creates one export option card with a title, description, and export buttons area."""
        colors = self.colors

        card = tk.Frame(parent, bg=colors["card_bg"], highlightthickness=1,
                         highlightbackground=colors["card_border"])
        card.grid(row=0, column=column, sticky="nsew",
                  padx=(0 if column == 0 else 10, 0))

        inner = tk.Frame(card, bg=colors["card_bg"])
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            inner, text=icon, font=("Segoe UI Emoji", 26),
            bg=colors["card_bg"], fg=colors["accent_primary"]
        ).pack(anchor="w")

        tk.Label(
            inner, text=title, font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(anchor="w", pady=(10, 4))

        tk.Label(
            inner, text=description, font=config.FONTS["small"],
            bg=colors["card_bg"], fg=colors["text_secondary"],
            wraplength=220, justify="left"
        ).pack(anchor="w", pady=(0, 16))

        return inner

    # ------------------------------------------------------------
    def _build_candidates_report_card(self, parent, column):
        inner = self._create_report_card(
            parent, column, "👥", "Candidates Report",
            "Export the full candidate list including contact info, "
            "skills, experience, and education."
        )
        button_row = tk.Frame(inner, bg=self.colors["card_bg"])
        button_row.pack(fill="x")

        ttk.Button(
            button_row, text="Export CSV", style="Primary.TButton",
            command=self._export_candidates_csv
        ).pack(fill="x", pady=(0, 8))

        ttk.Button(
            button_row, text="Export PDF", style="Secondary.TButton",
            command=self._export_candidates_pdf
        ).pack(fill="x")

    # ------------------------------------------------------------
    def _build_jobs_report_card(self, parent, column):
        inner = self._create_report_card(
            parent, column, "💼", "Job Postings Report",
            "Export all job postings including required skills, "
            "department, and experience requirements."
        )
        button_row = tk.Frame(inner, bg=self.colors["card_bg"])
        button_row.pack(fill="x")

        ttk.Button(
            button_row, text="Export CSV", style="Primary.TButton",
            command=self._export_jobs_csv
        ).pack(fill="x", pady=(0, 8))

        ttk.Button(
            button_row, text="Export PDF", style="Secondary.TButton",
            command=self._export_jobs_pdf
        ).pack(fill="x")

    # ------------------------------------------------------------
    def _build_history_report_card(self, parent, column):
        inner = self._create_report_card(
            parent, column, "🕓", "Screening History Report",
            "Export ranked screening results with match scores and "
            "matched keywords, optionally filtered by job."
        )

        tk.Label(
            inner, text="Filter by Job (optional)", font=config.FONTS["small"],
            bg=self.colors["card_bg"], fg=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 4))

        self.history_job_combobox = ttk.Combobox(
            inner, state="readonly", style="Modern.TCombobox", font=config.FONTS["small"]
        )
        self.history_job_combobox.pack(fill="x", pady=(0, 12))
        self._populate_history_job_filter()

        button_row = tk.Frame(inner, bg=self.colors["card_bg"])
        button_row.pack(fill="x")

        ttk.Button(
            button_row, text="Export CSV", style="Primary.TButton",
            command=self._export_history_csv
        ).pack(fill="x", pady=(0, 8))

        ttk.Button(
            button_row, text="Export PDF", style="Secondary.TButton",
            command=self._export_history_pdf
        ).pack(fill="x")

    # ------------------------------------------------------------
    def _populate_history_job_filter(self):
        """Fills the job filter dropdown used by the history report card."""
        jobs = self.db_manager.get_all_jobs()
        self.job_filter_lookup = {"All Jobs": None}
        for job in jobs:
            self.job_filter_lookup[job["job_title"]] = job["id"]

        self.history_job_combobox["values"] = list(self.job_filter_lookup.keys())
        self.history_job_combobox.current(0)

    # ==================================================================
    # PAGE REFRESH
    # ==================================================================
    def refresh(self):
        """Refreshes the job filter dropdown in case new jobs were added."""
        current_selection = self.history_job_combobox.get()
        self._populate_history_job_filter()
        if current_selection in self.job_filter_lookup:
            self.history_job_combobox.set(current_selection)

    # ==================================================================
    # CANDIDATES EXPORT
    # ==================================================================
    def _get_candidates_export_rows(self):
        candidates = self.db_manager.get_all_candidates()
        headers = ["full_name", "email", "phone", "skills", "experience_years", "education", "date_added"]
        rows = []
        for candidate in candidates:
            rows.append({
                "full_name": candidate["full_name"],
                "email": candidate["email"] or "",
                "phone": candidate["phone"] or "",
                "skills": candidate["skills"] or "",
                "experience_years": candidate["experience_years"],
                "education": candidate["education"] or "",
                "date_added": format_date(candidate["date_added"]),
            })
        return headers, rows

    def _export_candidates_csv(self):
        headers, rows = self._get_candidates_export_rows()
        if not rows:
            messagebox.showinfo("No Data", "There are no candidates to export.")
            return
        filename = generate_export_filename("candidates_report", "csv")
        path = export_to_csv(rows, headers, filename)
        messagebox.showinfo("Export Successful", f"Candidates report exported to:\n{path}")

    def _export_candidates_pdf(self):
        headers, rows = self._get_candidates_export_rows()
        if not rows:
            messagebox.showinfo("No Data", "There are no candidates to export.")
            return
        filename = generate_export_filename("candidates_report", "pdf")
        path = export_to_pdf("Candidates Report", rows, headers, filename)
        messagebox.showinfo("Export Successful", f"Candidates report exported to:\n{path}")

    # ==================================================================
    # JOBS EXPORT
    # ==================================================================
    def _get_jobs_export_rows(self):
        jobs = self.db_manager.get_all_jobs()
        headers = ["job_title", "department", "required_skills", "experience_required", "date_posted"]
        rows = []
        for job in jobs:
            rows.append({
                "job_title": job["job_title"],
                "department": job["department"] or "",
                "required_skills": job["required_skills"] or "",
                "experience_required": job["experience_required"],
                "date_posted": format_date(job["date_posted"]),
            })
        return headers, rows

    def _export_jobs_csv(self):
        headers, rows = self._get_jobs_export_rows()
        if not rows:
            messagebox.showinfo("No Data", "There are no job postings to export.")
            return
        filename = generate_export_filename("jobs_report", "csv")
        path = export_to_csv(rows, headers, filename)
        messagebox.showinfo("Export Successful", f"Jobs report exported to:\n{path}")

    def _export_jobs_pdf(self):
        headers, rows = self._get_jobs_export_rows()
        if not rows:
            messagebox.showinfo("No Data", "There are no job postings to export.")
            return
        filename = generate_export_filename("jobs_report", "pdf")
        path = export_to_pdf("Job Postings Report", rows, headers, filename)
        messagebox.showinfo("Export Successful", f"Jobs report exported to:\n{path}")

    # ==================================================================
    # SCREENING HISTORY EXPORT
    # ==================================================================
    def _get_history_export_rows(self):
        job_filter_label = self.history_job_combobox.get()
        job_id = self.job_filter_lookup.get(job_filter_label)

        screenings = self.db_manager.get_all_screenings(job_id=job_id)
        headers = ["candidate_name", "job_title", "match_score", "matched_keywords", "rank_position", "screening_date"]
        rows = []
        for screening in screenings:
            rows.append({
                "candidate_name": screening["candidate_name"],
                "job_title": screening["job_title"],
                "match_score": format_score(screening["match_score"]),
                "matched_keywords": screening["matched_keywords"] or "",
                "rank_position": screening["rank_position"] or "",
                "screening_date": format_date(screening["screening_date"]),
            })
        return headers, rows

    def _export_history_csv(self):
        headers, rows = self._get_history_export_rows()
        if not rows:
            messagebox.showinfo("No Data", "There is no screening history to export for this selection.")
            return
        filename = generate_export_filename("screening_history_report", "csv")
        path = export_to_csv(rows, headers, filename)
        messagebox.showinfo("Export Successful", f"Screening history report exported to:\n{path}")

    def _export_history_pdf(self):
        headers, rows = self._get_history_export_rows()
        if not rows:
            messagebox.showinfo("No Data", "There is no screening history to export for this selection.")
            return
        filename = generate_export_filename("screening_history_report", "pdf")
        path = export_to_pdf("Screening History Report", rows, headers, filename)
        messagebox.showinfo("Export Successful", f"Screening history report exported to:\n{path}")
