"""
candidates.py
------------------------------------------------------------------
Candidate Management page.

Provides full CRUD functionality for candidates:
    - View all candidates in a modern table (Treeview)
    - Live search by name / skills / education
    - Add a new candidate (with optional resume file upload:
      .txt / .pdf / .docx, or manual resume text paste)
    - Edit an existing candidate
    - Delete a candidate (with confirmation)
    - View a candidate's full resume text in a read-only dialog

This page uses the shared DatabaseManager for all data operations
and nlp.text_extraction for reading uploaded resume files.
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import config
from utils.helpers import format_date, truncate_text
from utils.validators import validate_candidate_form
from nlp.text_extraction import extract_text_from_file, TextExtractionError


class CandidatesPage(tk.Frame):
    """Full candidate management interface (list, add, edit, delete)."""

    def __init__(self, parent, db_manager):
        colors = config.COLORS
        super().__init__(parent, bg=colors["workspace_bg"])

        self.db_manager = db_manager
        self.colors = colors
        self.selected_candidate_id = None

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
            toolbar, text="+ Add Candidate", style="Primary.TButton",
            command=self._open_add_dialog
        )
        add_button.pack(side="right", padx=(10, 0))

        # ---------------- Table card ----------------
        table_card = tk.Frame(outer, bg=self.colors["card_bg"], highlightthickness=1,
                               highlightbackground=self.colors["card_border"])
        table_card.pack(fill="both", expand=True)

        table_container = tk.Frame(table_card, bg=self.colors["card_bg"])
        table_container.pack(fill="both", expand=True, padx=16, pady=16)

        columns = ("name", "email", "phone", "skills", "experience", "education", "date_added")
        column_headers = {
            "name": "Full Name", "email": "Email", "phone": "Phone",
            "skills": "Skills", "experience": "Experience", "education": "Education",
            "date_added": "Date Added",
        }
        column_widths = {
            "name": 150, "email": 170, "phone": 110, "skills": 260,
            "experience": 90, "education": 150, "date_added": 110,
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
            action_bar, text="View Resume", style="Secondary.TButton",
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
            command=self._delete_selected_candidate, state="disabled"
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
        """Reloads the candidate table from the database using the current search term."""
        search_term = self.search_var.get().strip()
        candidates = self.db_manager.get_all_candidates(search_term=search_term or None)

        self.tree.delete(*self.tree.get_children())
        for candidate in candidates:
            self.tree.insert(
                "", "end", iid=str(candidate["id"]),
                values=(
                    candidate["full_name"],
                    candidate["email"] or "-",
                    candidate["phone"] or "-",
                    truncate_text(candidate["skills"] or "-", 45),
                    f"{candidate['experience_years']} yrs",
                    candidate["education"] or "-",
                    format_date(candidate["date_added"]),
                )
            )

        self.result_count_label.config(text=f"{len(candidates)} candidate(s) found")
        self._on_row_selected()  # reset action buttons since selection is now cleared

    # ------------------------------------------------------------
    def _on_row_selected(self, event=None):
        """Enables/disables action buttons based on current table selection."""
        selection = self.tree.selection()
        if selection:
            self.selected_candidate_id = int(selection[0])
            self.view_button.config(state="normal")
            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")
        else:
            self.selected_candidate_id = None
            self.view_button.config(state="disabled")
            self.edit_button.config(state="disabled")
            self.delete_button.config(state="disabled")

    # ==================================================================
    # DELETE
    # ==================================================================
    def _delete_selected_candidate(self):
        if self.selected_candidate_id is None:
            return
        candidate = self.db_manager.get_candidate_by_id(self.selected_candidate_id)
        confirmed = messagebox.askyesno(
            "Delete Candidate",
            f"Are you sure you want to delete '{candidate['full_name']}'?\n"
            "This will also remove their screening history."
        )
        if confirmed:
            self.db_manager.delete_candidate(self.selected_candidate_id)
            self.refresh()

    # ==================================================================
    # VIEW RESUME DIALOG
    # ==================================================================
    def _open_view_dialog(self):
        if self.selected_candidate_id is None:
            return
        candidate = self.db_manager.get_candidate_by_id(self.selected_candidate_id)
        if not candidate:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Resume - {candidate['full_name']}")
        dialog.geometry("560x480")
        dialog.configure(bg=self.colors["card_bg"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        header = tk.Label(
            dialog, text=candidate["full_name"], font=config.FONTS["section_title"],
            bg=self.colors["card_bg"], fg=self.colors["text_primary"]
        )
        header.pack(anchor="w", padx=20, pady=(18, 2))

        subtitle = tk.Label(
            dialog, text=f"{candidate['email'] or 'No email'}  ·  {candidate['education'] or 'N/A'}",
            font=config.FONTS["small"], bg=self.colors["card_bg"], fg=self.colors["text_secondary"]
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 12))

        text_frame = tk.Frame(dialog, bg=self.colors["card_bg"])
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        text_widget = tk.Text(
            text_frame, wrap="word", font=config.FONTS["body"],
            bg="#FAFBFA", fg=self.colors["text_primary"], relief="flat",
            padx=12, pady=12
        )
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.insert("1.0", candidate["resume_text"])
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
        self._open_candidate_form(candidate=None)

    def _open_edit_dialog(self):
        if self.selected_candidate_id is None:
            return
        candidate = self.db_manager.get_candidate_by_id(self.selected_candidate_id)
        self._open_candidate_form(candidate=candidate)

    def _open_candidate_form(self, candidate):
        """
        Builds the shared Add/Edit candidate dialog. If `candidate` is
        None, the form is in "Add" mode; otherwise it's pre-filled for
        editing the given candidate record.
        """
        is_edit_mode = candidate is not None
        colors = self.colors

        dialog = tk.Toplevel(self)
        dialog.title("Edit Candidate" if is_edit_mode else "Add New Candidate")
        dialog.geometry("560x640")
        dialog.configure(bg=colors["card_bg"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.resizable(False, False)

        form_container = tk.Frame(dialog, bg=colors["card_bg"])
        form_container.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(
            form_container, text="Candidate Details", font=config.FONTS["section_title"],
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

        name_entry = add_field("Full Name *")
        email_entry = add_field("Email")
        phone_entry = add_field("Phone")
        skills_entry = add_field("Skills (comma separated) *")
        experience_entry = add_field("Experience (years) *")
        education_entry = add_field("Education")

        if is_edit_mode:
            name_entry.insert(0, candidate["full_name"])
            email_entry.insert(0, candidate["email"] or "")
            phone_entry.insert(0, candidate["phone"] or "")
            skills_entry.insert(0, candidate["skills"] or "")
            experience_entry.insert(0, str(candidate["experience_years"]))
            education_entry.insert(0, candidate["education"] or "")

        # ---------------- Resume text section ----------------
        resume_header_row = tk.Frame(form_container, bg=colors["card_bg"])
        resume_header_row.pack(fill="x", pady=(10, 3))

        tk.Label(
            resume_header_row, text="Resume Text *", font=config.FONTS["body_bold"],
            bg=colors["card_bg"], fg=colors["text_primary"]
        ).pack(side="left")

        upload_button = ttk.Button(
            resume_header_row, text="📁 Upload File (.txt/.pdf/.docx)",
            style="Secondary.TButton",
            command=lambda: self._handle_resume_upload(resume_text_widget)
        )
        upload_button.pack(side="right")

        resume_text_widget = tk.Text(
            form_container, height=8, font=config.FONTS["body"],
            relief="solid", bd=1, wrap="word"
        )
        resume_text_widget.pack(fill="both", expand=True, pady=(0, 6))

        if is_edit_mode:
            resume_text_widget.insert("1.0", candidate["resume_text"])

        # ---------------- Action buttons ----------------
        button_row = tk.Frame(form_container, bg=colors["card_bg"])
        button_row.pack(fill="x", pady=(14, 0))

        def handle_save():
            self._save_candidate_form(
                dialog=dialog,
                candidate_id=candidate["id"] if is_edit_mode else None,
                name_entry=name_entry, email_entry=email_entry, phone_entry=phone_entry,
                skills_entry=skills_entry, experience_entry=experience_entry,
                education_entry=education_entry, resume_text_widget=resume_text_widget,
            )

        ttk.Button(
            button_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy
        ).pack(side="right", padx=(8, 0))

        ttk.Button(
            button_row, text="Save Candidate", style="Primary.TButton", command=handle_save
        ).pack(side="right")

    # ------------------------------------------------------------
    def _handle_resume_upload(self, resume_text_widget):
        """Opens a file dialog, extracts resume text, and fills the text widget."""
        file_path = filedialog.askopenfilename(
            title="Select Resume File",
            filetypes=[("Resume Files", "*.txt *.pdf *.docx"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            extracted_text = extract_text_from_file(file_path)
            resume_text_widget.delete("1.0", "end")
            resume_text_widget.insert("1.0", extracted_text)
        except TextExtractionError as error:
            messagebox.showwarning("Could Not Read File", str(error))

    # ------------------------------------------------------------
    def _save_candidate_form(self, dialog, candidate_id, name_entry, email_entry,
                              phone_entry, skills_entry, experience_entry,
                              education_entry, resume_text_widget):
        """Validates form input and inserts/updates the candidate record."""
        full_name = name_entry.get().strip()
        email = email_entry.get().strip()
        phone = phone_entry.get().strip()
        skills = skills_entry.get().strip()
        experience_raw = experience_entry.get().strip()
        education = education_entry.get().strip()
        resume_text = resume_text_widget.get("1.0", "end").strip()

        is_valid, error_message = validate_candidate_form(
            full_name, email, phone, experience_raw or "0", resume_text
        )
        if not is_valid:
            messagebox.showerror("Invalid Input", error_message)
            return

        experience_years = float(experience_raw) if experience_raw else 0.0

        if candidate_id is None:
            self.db_manager.add_candidate(
                full_name, email, phone, skills, experience_years,
                education, resume_text
            )
            messagebox.showinfo("Success", f"Candidate '{full_name}' added successfully.")
        else:
            self.db_manager.update_candidate(
                candidate_id, full_name, email, phone, skills,
                experience_years, education, resume_text
            )
            messagebox.showinfo("Success", f"Candidate '{full_name}' updated successfully.")

        dialog.destroy()
        self.refresh()
