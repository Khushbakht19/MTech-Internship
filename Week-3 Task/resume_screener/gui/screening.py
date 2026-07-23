"""
screening.py
------------------------------------------------------------------
Resume Screening page - the core NLP feature of the application.

Workflow:
    1. Recruiter selects a job posting from a dropdown.
    2. Recruiter selects which candidates to screen (all, or a
       chosen subset via checkboxes).
    3. Clicking "Run Screening" computes, for every selected
       candidate, a TF-IDF + Cosine Similarity match score against
       the job description (nlp/similarity.py), then ranks them.
    4. Results are displayed in a ranked table with match-score
       badges and matched keywords, and are saved into the
       screening_history table for later review/analytics.
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

import config
from nlp.similarity import rank_candidates, find_matched_keywords
from utils.helpers import format_score


class ScreeningPage(tk.Frame):
    """Lets recruiters run an NLP-based screening session for a job."""

    def __init__(self, parent, db_manager):
        colors = config.COLORS
        super().__init__(parent, bg=colors["workspace_bg"])

        self.db_manager = db_manager
        self.colors = colors

        self.job_lookup = {}          # display string -> job dict
        self.candidate_checkbox_vars = {}  # candidate_id -> tk.BooleanVar
        self.last_results = []        # cached ranked results for saving/export

        self._build_layout()
        self.refresh()

    # ==================================================================
    # LAYOUT
    # ==================================================================
    def _build_layout(self):
        outer = tk.Frame(self, bg=self.colors["workspace_bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        # ---------------- Top control card ----------------
        control_card = tk.Frame(outer, bg=self.colors["card_bg"], highlightthickness=1,
                                 highlightbackground=self.colors["card_border"])
        control_card.pack(fill="x", pady=(0, 14))

        control_inner = tk.Frame(control_card, bg=self.colors["card_bg"])
        control_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(
            control_inner, text="1. Select Job Posting", font=config.FONTS["body_bold"],
            bg=self.colors["card_bg"], fg=self.colors["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        self.job_combobox = ttk.Combobox(
            control_inner, state="readonly", width=38,
            style="Modern.TCombobox", font=config.FONTS["body"]
        )
        self.job_combobox.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.job_combobox.bind("<<ComboboxSelected>>", lambda e: self._update_candidate_list())

        tk.Label(
            control_inner, text="2. Select Candidates to Screen", font=config.FONTS["body_bold"],
            bg=self.colors["card_bg"], fg=self.colors["text_primary"]
        ).grid(row=0, column=1, sticky="w", padx=(30, 0))

        select_buttons_frame = tk.Frame(control_inner, bg=self.colors["card_bg"])
        select_buttons_frame.grid(row=1, column=1, sticky="w", padx=(30, 0), pady=(4, 0))

        ttk.Button(
            select_buttons_frame, text="Select All", style="Secondary.TButton",
            command=lambda: self._toggle_all_candidates(True)
        ).pack(side="left")
        ttk.Button(
            select_buttons_frame, text="Clear All", style="Secondary.TButton",
            command=lambda: self._toggle_all_candidates(False)
        ).pack(side="left", padx=(6, 0))

        run_button = ttk.Button(
            control_inner, text="🔍  Run Screening", style="Primary.TButton",
            command=self._run_screening
        )
        run_button.grid(row=0, column=2, rowspan=2, sticky="e", padx=(20, 0))
        control_inner.grid_columnconfigure(2, weight=1)

        # ---------------- Middle row: candidate checklist + results ----------------
        middle_row = tk.Frame(outer, bg=self.colors["workspace_bg"])
        middle_row.pack(fill="both", expand=True)
        middle_row.grid_columnconfigure(0, weight=30)
        middle_row.grid_columnconfigure(1, weight=70)
        middle_row.grid_rowconfigure(0, weight=1)

        # ----- Candidate checklist card -----
        checklist_card = tk.Frame(middle_row, bg=self.colors["card_bg"], highlightthickness=1,
                                   highlightbackground=self.colors["card_border"])
        checklist_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(
            checklist_card, text="Candidate Pool", font=config.FONTS["section_title"],
            bg=self.colors["card_bg"], fg=self.colors["text_primary"]
        ).pack(anchor="w", padx=14, pady=(12, 6))

        checklist_scroll_frame = tk.Frame(checklist_card, bg=self.colors["card_bg"])
        checklist_scroll_frame.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        canvas = tk.Canvas(checklist_scroll_frame, bg=self.colors["card_bg"],
                            highlightthickness=0)
        scrollbar = ttk.Scrollbar(checklist_scroll_frame, orient="vertical",
                                   command=canvas.yview, style="Vertical.TScrollbar")
        self.checklist_inner_frame = tk.Frame(canvas, bg=self.colors["card_bg"])

        self.checklist_inner_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.checklist_inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # ----- Results card -----
        results_card = tk.Frame(middle_row, bg=self.colors["card_bg"], highlightthickness=1,
                                 highlightbackground=self.colors["card_border"])
        results_card.grid(row=0, column=1, sticky="nsew")

        results_header = tk.Frame(results_card, bg=self.colors["card_bg"])
        results_header.pack(fill="x", padx=14, pady=(12, 6))

        tk.Label(
            results_header, text="Ranked Screening Results", font=config.FONTS["section_title"],
            bg=self.colors["card_bg"], fg=self.colors["text_primary"]
        ).pack(side="left")

        self.results_summary_label = tk.Label(
            results_header, text="", font=config.FONTS["small"],
            bg=self.colors["card_bg"], fg=self.colors["accent_primary"] # Highlighting status color
        )
        self.results_summary_label.pack(side="right")

        results_table_frame = tk.Frame(results_card, bg=self.colors["card_bg"])
        results_table_frame.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        columns = ("rank", "name", "score", "keywords", "experience")
        column_headers = {
            "rank": "#", "name": "Candidate", "score": "Match Score",
            "keywords": "Matched Keywords", "experience": "Experience",
        }
        column_widths = {
            "rank": 35, "name": 150, "score": 100, "keywords": 280, "experience": 85,
        }

        self.results_tree = ttk.Treeview(
            results_table_frame, columns=columns, show="headings",
            style="Modern.Treeview", selectmode="browse"
        )
        for column in columns:
            self.results_tree.heading(column, text=column_headers[column])
            self.results_tree.column(column, width=column_widths[column], anchor="w")

        results_scrollbar = ttk.Scrollbar(
            results_table_frame, orient="vertical", command=self.results_tree.yview,
            style="Vertical.TScrollbar"
        )
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        self.results_tree.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")

        # Tag configuration for score-based row coloring
        self.results_tree.tag_configure("excellent", background=self.colors["accent_primary_light"])
        self.results_tree.tag_configure("good", background="#DBEAFE")
        self.results_tree.tag_configure("average", background="#FEF3C7")
        self.results_tree.tag_configure("low", background="#FEE2E2")

    # ==================================================================
    # DATA REFRESH
    # ==================================================================
    def refresh(self):
        """Reloads the job dropdown list. Called on every page visit."""
        jobs = self.db_manager.get_all_jobs()
        self.job_lookup = {f"{job['job_title']}  ({job['department'] or 'N/A'})": job for job in jobs}

        self.job_combobox["values"] = list(self.job_lookup.keys())
        if self.job_lookup and not self.job_combobox.get():
            self.job_combobox.current(0)

        self._update_candidate_list()

    # ------------------------------------------------------------
    def _update_candidate_list(self):
        """Rebuilds the scrollable candidate checklist panel."""
        for widget in self.checklist_inner_frame.winfo_children():
            widget.destroy()
        self.candidate_checkbox_vars = {}

        candidates = self.db_manager.get_all_candidates()

        if not candidates:
            tk.Label(
                self.checklist_inner_frame, text="No candidates available.\nAdd candidates first.",
                font=config.FONTS["small"], bg=self.colors["card_bg"], fg=self.colors["text_muted"],
                justify="left"
            ).pack(anchor="w", padx=8, pady=8)
            return

        for candidate in candidates:
            var = tk.BooleanVar(value=True)
            self.candidate_checkbox_vars[candidate["id"]] = (var, candidate)

            row = tk.Frame(self.checklist_inner_frame, bg=self.colors["card_bg"])
            row.pack(fill="x", padx=4, pady=2)

            checkbox = tk.Checkbutton(
                row, text=candidate["full_name"], variable=var,
                font=config.FONTS["body"], bg=self.colors["card_bg"],
                fg=self.colors["text_primary"], activebackground=self.colors["card_bg"],
                selectcolor="#FFFFFF", anchor="w"
            )
            checkbox.pack(fill="x")

    # ------------------------------------------------------------
    def _toggle_all_candidates(self, select_state):
        """Checks or unchecks every candidate in the checklist at once."""
        for var, candidate in self.candidate_checkbox_vars.values():
            var.set(select_state)

    # ==================================================================
    # RUN SCREENING (CORE NLP ACTION)
    # ==================================================================
    def _run_screening(self):
        """
        Executes the core NLP workflow: gathers the selected job and
        candidates, runs TF-IDF + Cosine Similarity ranking, displays
        the results, and persists them into the screening_history table.
        """
        selected_job_label = self.job_combobox.get()
        if not selected_job_label or selected_job_label not in self.job_lookup:
            messagebox.showwarning("No Job Selected", "Please select a job posting to screen against.")
            return

        job = self.job_lookup[selected_job_label]

        selected_candidates = [
            candidate for var, candidate in self.candidate_checkbox_vars.values() if var.get()
        ]

        if not selected_candidates:
            messagebox.showwarning("No Candidates Selected", "Please select at least one candidate to screen.")
            return

        # --- Core NLP step: TF-IDF vectorization + cosine similarity ranking ---
        ranked_results = rank_candidates(selected_candidates, job["job_description"])
        self.last_results = ranked_results

        # Populate the results table
        self.results_tree.delete(*self.results_tree.get_children())

        for result in ranked_results:
            matched_keywords = find_matched_keywords(result["skills"], job["required_skills"])
            score = result["match_score"]

            if score >= config.SCORE_THRESHOLDS["excellent"]:
                tag = "excellent"
            elif score >= config.SCORE_THRESHOLDS["good"]:
                tag = "good"
            elif score >= config.SCORE_THRESHOLDS["average"]:
                tag = "average"
            else:
                tag = "low"

            self.results_tree.insert(
                "", "end",
                values=(
                    result["rank_position"],
                    result["full_name"],
                    format_score(score),
                    matched_keywords,
                    f"{result['experience_years']} yrs",
                ),
                tags=(tag,)
            )

            # Persist this screening result into the database
            self.db_manager.add_screening_record(
                candidate_id=result["id"],
                job_id=job["id"],
                match_score=score,
                matched_keywords=matched_keywords,
                rank_position=result["rank_position"],
            )

        # Subtle live status update right on the table header (No annoying popup!)
        self.results_summary_label.config(
            text=f"✓ Screened {len(ranked_results)} candidate(s) for '{job['job_title']}'"
        )