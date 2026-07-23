"""
jobs.py
------------------------------------------------------------------
Job Management page.

Provides full CRUD functionality for job postings:
    - View all jobs in a modern table (Treeview)
    - Live search by title / department / required skills
    - Add a new job posting
    - Edit an existing job posting
    - Delete a job posting (with confirmation)
    - View full job description in a read-only dialog

Mirrors the structure of candidates.py for consistency across the
application's codebase.
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox

import config
from utils.helpers import format_date, truncate_text
from utils.validators import validate_job_form


class JobsPage(tk.Frame):
    """Full job posting management interface (list, add, edit, delete)."""

    def __init__(self, parent, db_manager):
        colors = config.COLORS
        super().__init__(parent, bg=colors["workspace_bg"])

        self.db_manager = db_manager
        self.colors = colors
        self.selected_job_id = None

        self._build_layout()
        self.refresh()

    # ==================================================================
    # LAYOUT
    # ==================================================================
    def _build_layout(self):
        outer = tk.Frame(self, bg=self.colors["workspace_bg"])
        outer.pack(fill="both", expand=True, padx=28, pady=18)

        # ---------------- Toolbar: search + action buttons ----------------
        toolbar = tk.Frame(outer, bg=self.colors["workspace_bg"])
        toolbar.pack(fill="x", pady=(0, 14))

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

        add_button = ttk.Button(
            toolbar, text="+ Add Job Posting", style="Primary.TButton",
            command=self._open_add_dialog
        )
        add_button.pack(side="right", padx=(10, 0))

        # ---------------- Table card ----------------
        table_card = tk.Frame(outer, bg=self.colors["card_bg"], highlightthickness=1,
                               highlightbackground=self.colors["card_border"])
        table_card.pack(fill="both", expand=True)

        table_container = tk.Frame(table_card, bg=self.colors["card_bg"])
        table_container.pack(fill="both", expand=True, padx=16, pady=16)

        columns = ("title", "department", "skills", "experience", "date_posted")
        column_headers = {
            "title": "Job Title", "department": "Department",
            "skills": "Required Skills", "experience": "Experience Req.",
            "date_posted": "Date Posted",
        }
        column_widths = {
            "title": 200, "department": 170, "skills": 340,
            "experience": 120, "date_posted": 130,
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
        self.tree.bind("<Double-1>", lambda event: self._open_view_dialog())

        # ---------------- Action bar (below table) ----------------
        action_bar = tk.Frame(outer, bg=self.colors["workspace_bg"])
        action_bar.pack(fill="x", pady=(12, 0))

        self.view_button = ttk.Button(
            action_bar, text="View Description", style="Secondary.TButton",
            command=self._open_view_dialog, state="disabled"
        )
        self.view_button.pack(side="left")

        self.edit_button = ttk.Button(
            action_bar, text="Edit", style="Secondary.TButton",
            command=self._open_edit_dialog, state="disabled"
        )
        self.edit_button.pack(side="left", padx=8)

        self.delete_button = ttk.Button(
            action_bar, text="Delete", style="Danger.TButton",
            command=self._delete_selected_job, state="disabled"
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
        """Reloads the job table from the database using the current search term."""
        search_term = self.search_var.get().strip()
        jobs = self.db_manager.get_all_jobs(search_term=search_term or None)

        self.tree.delete(*self.tree.get_children())
        for job in jobs:
            self.tree.insert(
                "", "end", iid=str(job["id"]),
                values=(
                    job["job_title"],
                    job["department"] or "-",
                    truncate_text(job["required_skills"] or "-", 55),
                    f"{job['experience_required']} yrs",
                    format_date(job["date_posted"]),
                )
            )

        self.result_count_label.config(text=f"{len(jobs)} job posting(s) found")
        self._on_row_selected()

    # ------------------------------------------------------------
    def _on_row_selected(self, event=None):
        """Enables/disables action buttons based on current table selection."""
        selection = self.tree.selection()
        if selection:
            self.selected_job_id = int(selection[0])
            self.view_button.config(state="normal")
            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")
        else:
            self.selected_job_id = None
            self.view_button.config(state="disabled")
            self.edit_button.config(state="disabled")
            self.delete_button.config(state="disabled")

    # ==================================================================
    # DELETE
    # ==================================================================
    def _delete_selected_job(self):
        if self.selected_job_id is None:
            return
        job = self.db_manager.get_job_by_id(self.selected_job_id)
        confirmed = messagebox.askyesno(
            "Delete Job Posting",
            f"Are you sure you want to delete '{job['job_title']}'?\n"
            "This will also remove its screening history."
        )
        if confirmed:
            self.db_manager.delete_job(self.selected_job_id)
            self.refresh()

    # ==================================================================
    # VIEW DESCRIPTION DIALOG
    # ==================================================================
    def _open_view_dialog(self):
        if self.selected_job_id is None:
            return
        job = self.db_manager.get_job_by_id(self.selected_job_id)
        if not job:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Job Description - {job['job_title']}")
        dialog.geometry("560x480")
        dialog.configure(bg=self.colors["card_bg"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        header = tk.Label(
            dialog, text=job["job_title"], font=config.FONTS["section_title"],
            bg=self.colors["card_bg"], fg=self.colors["text_primary"]
        )
        header.pack(anchor="w", padx=20, pady=(18, 2))

        subtitle = tk.Label(
            dialog, text=f"{job['department'] or 'N/A'}  ·  Requires {job['experience_required']} yrs experience",
            font=config.FONTS["small"], bg=self.colors["card_bg"], fg=self.colors["text_secondary"]
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 6))

        skills_label = tk.Label(
            dialog, text=f"Required Skills: {job['required_skills']}",
            font=config.FONTS["body_bold"], bg=self.colors["card_bg"], fg=self.colors["accent_primary"],
            wraplength=520, justify="left"
        )
        skills_label.pack(anchor="w", padx=20, pady=(0, 12))

        text_frame = tk.Frame(dialog, bg=self.colors["card_bg"])
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        text_widget = tk.Text(
            text_frame, wrap="word", font=config.FONTS["body"],
            bg="#FAFBFA", fg=self.colors["text_primary"], relief="flat",
            padx=12, pady=12
        )
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.insert("1.0", job["job_description"])
        text_widget.configure(state="disabled")

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(
            dialog, text="Close", style="Secondary.TButton", command=dialog.destroy
        ).pack(pady=(0, 16))

    # ==================================================================
    # ADD / EDIT DIALOG
    # ==================================================================
    def _open_add_dialog(self):
        self._open_job_form(job=None)

    def _open_edit_dialog(self):
        if self.selected_job_id is None:
            return
        job = self.db_manager.get_job_by_id(self.selected_job_id)
        self._open_job_form(job=job)

    def _open_job_form(self, job):
        """
        Builds the shared Add/Edit job dialog. If `job` is None, the
        form is in "Add" mode; otherwise it's pre-filled for editing.
        """
        is_edit_mode = job is not None
        colors = self.colors

        dialog = tk.Toplevel(self)
        dialog.title("Edit Job Posting" if is_edit_mode else "Add New Job Posting")
        dialog.geometry("560x620")
        dialog.configure(bg=colors["card_bg"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.resizable(False, False)

        form_container = tk.Frame(dialog, bg=colors["card_bg"])
        form_container.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(
            form_container, text="Job Posting Details", font=config.FONTS["section_title"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(anchor="w", pady=(0, 14))

        def add_field(label_text):
            tk.Label(
                form_container, text=label_text, font=config.FONTS["body_bold"],
                bg=colors["card_bg"], fg=colors["text_primary"]
            ).pack(anchor="w", pady=(6, 3))
            entry = tk.Entry(
                form_container, font=config.FONTS["body"], relief="solid",
                highlightthickness=1, bd=1
            )
            entry.pack(fill="x", ipady=5)
            return entry

        title_entry = add_field("Job Title *")
        department_entry = add_field("Department")
        skills_entry = add_field("Required Skills (comma separated) *")
        experience_entry = add_field("Experience Required (years) *")

        if is_edit_mode:
            title_entry.insert(0, job["job_title"])
            department_entry.insert(0, job["department"] or "")
            skills_entry.insert(0, job["required_skills"] or "")
            experience_entry.insert(0, str(job["experience_required"]))

        tk.Label(
            form_container, text="Job Description *", font=config.FONTS["body_bold"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(anchor="w", pady=(10, 3))

        description_text_widget = tk.Text(
            form_container, height=9, font=config.FONTS["body"],
            relief="solid", bd=1, wrap="word"
        )
        description_text_widget.pack(fill="both", expand=True, pady=(0, 6))

        if is_edit_mode:
            description_text_widget.insert("1.0", job["job_description"])

        # ---------------- Action buttons ----------------
        button_row = tk.Frame(form_container, bg=colors["card_bg"])
        button_row.pack(fill="x", pady=(14, 0))

        def handle_save():
            self._save_job_form(
                dialog=dialog,
                job_id=job["id"] if is_edit_mode else None,
                title_entry=title_entry, department_entry=department_entry,
                skills_entry=skills_entry, experience_entry=experience_entry,
                description_text_widget=description_text_widget,
            )

        ttk.Button(
            button_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy
        ).pack(side="right", padx=(8, 0))

        ttk.Button(
            button_row, text="Save Job Posting", style="Primary.TButton", command=handle_save
        ).pack(side="right")

    # ------------------------------------------------------------
    def _save_job_form(self, dialog, job_id, title_entry, department_entry,
                        skills_entry, experience_entry, description_text_widget):
        """Validates form input and inserts/updates the job record."""
        job_title = title_entry.get().strip()
        department = department_entry.get().strip()
        required_skills = skills_entry.get().strip()
        experience_raw = experience_entry.get().strip()
        job_description = description_text_widget.get("1.0", "end").strip()

        is_valid, error_message = validate_job_form(
            job_title, required_skills, experience_raw or "0", job_description
        )
        if not is_valid:
            messagebox.showerror("Invalid Input", error_message)
            return

        experience_required = float(experience_raw) if experience_raw else 0.0

        if job_id is None:
            self.db_manager.add_job(
                job_title, department, required_skills,
                experience_required, job_description
            )
            messagebox.showinfo("Success", f"Job posting '{job_title}' added successfully.")
        else:
            self.db_manager.update_job(
                job_id, job_title, department, required_skills,
                experience_required, job_description
            )
            messagebox.showinfo("Success", f"Job posting '{job_title}' updated successfully.")

        dialog.destroy()
        self.refresh()
