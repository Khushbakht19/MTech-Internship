"""
gui/reports.py
----------------
The Reports page: lets the user export the prediction history to a
CSV file (for spreadsheets) or a PDF file (for printing / sharing),
optionally scoped to only Spam or only Safe messages.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import config
from utils.helpers import (
    export_predictions_to_csv,
    export_predictions_to_pdf,
    timestamped_filename,
    open_file,
)


class ReportsPage(tk.Frame):
    """The Reports page."""

    def __init__(self, master, database, classifier, app):
        super().__init__(master, bg=config.COLORS["main_bg"])
        self.database = database
        self.classifier = classifier
        self.app = app

        self.last_exported_path = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_page_title()
        self._build_main_content()

    # ------------------------------------------------------------------
    def _build_page_title(self):
        title_frame = tk.Frame(self, bg=config.COLORS["main_bg"])
        title_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))

        title_label = tk.Label(
            title_frame, text="Reports", font=config.FONTS["page_title"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_primary"],
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame, text="Export your prediction history as a CSV spreadsheet or a PDF report",
            font=config.FONTS["body"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"],
        )
        subtitle_label.pack(anchor="w")

    # ------------------------------------------------------------------
    def _build_main_content(self):
        card = tk.Frame(self, bg=config.COLORS["card_bg"], highlightthickness=1,
                         highlightbackground=config.COLORS["border"])
        card.grid(row=1, column=0, sticky="new", padx=28, pady=(0, 24))

        header = tk.Label(
            card, text="Generate Report", font=config.FONTS["section_title"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        header.pack(anchor="w", padx=24, pady=(22, 4))

        description = tk.Label(
            card, text="Choose which predictions to include, then export in your preferred format.",
            font=config.FONTS["body"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_secondary"],
        )
        description.pack(anchor="w", padx=24, pady=(0, 18))

        # --- Scope selector ---
        scope_row = tk.Frame(card, bg=config.COLORS["card_bg"])
        scope_row.pack(fill="x", padx=24, pady=(0, 6))

        scope_label = tk.Label(
            scope_row, text="Include:", font=config.FONTS["body_bold"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"],
        )
        scope_label.pack(side="left", padx=(0, 12))

        self.scope_var = tk.StringVar(value="All")
        scope_combo = ttk.Combobox(
            scope_row, textvariable=self.scope_var, state="readonly",
            values=["All", "Spam Only", "Safe Only"], width=16, font=config.FONTS["body"],
        )
        scope_combo.pack(side="left")
        scope_combo.bind("<<ComboboxSelected>>", lambda e: self._update_preview())

        # --- Live preview of how many rows will be exported ---
        self.preview_label = tk.Label(
            card, text="0 messages will be included in this report.",
            font=config.FONTS["small"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_muted"],
        )
        self.preview_label.pack(anchor="w", padx=24, pady=(10, 20))

        # --- Export buttons ---
        button_row = tk.Frame(card, bg=config.COLORS["card_bg"])
        button_row.pack(fill="x", padx=24, pady=(0, 12))

        csv_button = tk.Button(
            button_row, text="⬇  Export as CSV", font=config.FONTS["button"],
            bg=config.COLORS["blue"], fg=config.COLORS["white"], relief="flat",
            cursor="hand2", padx=18, pady=10, command=self._handle_export_csv,
        )
        csv_button.pack(side="left")

        pdf_button = tk.Button(
            button_row, text="⬇  Export as PDF", font=config.FONTS["button"],
            bg=config.COLORS["purple"], fg=config.COLORS["white"], relief="flat",
            cursor="hand2", padx=18, pady=10, command=self._handle_export_pdf,
        )
        pdf_button.pack(side="left", padx=(10, 0))

        # --- Status / last export info ---
        self.status_frame = tk.Frame(card, bg=config.COLORS["green_light"])
        self.status_label = tk.Label(
            self.status_frame, text="", font=config.FONTS["small"], justify="left",
            bg=config.COLORS["green_light"], fg=config.COLORS["text_primary"], anchor="w",
        )
        self.status_label.pack(side="left", padx=14, pady=10, fill="x", expand=True)

        self.open_button = tk.Button(
            self.status_frame, text="Open File", font=config.FONTS["small"],
            bg=config.COLORS["green_light"], fg=config.COLORS["green"],
            relief="flat", cursor="hand2", command=self._handle_open_last_export,
        )
        self.open_button.pack(side="right", padx=14)

        self._update_preview()

    # ------------------------------------------------------------------
    # DATA SCOPE HELPERS
    # ------------------------------------------------------------------
    def _get_scoped_predictions(self):
        scope = self.scope_var.get()
        if scope == "Spam Only":
            return self.database.filter_predictions(config.LABEL_SPAM)
        if scope == "Safe Only":
            return self.database.filter_predictions(config.LABEL_HAM)
        return self.database.get_all_predictions()

    def _update_preview(self):
        rows = self._get_scoped_predictions()
        word = "message" if len(rows) == 1 else "messages"
        self.preview_label.config(text=f"{len(rows)} {word} will be included in this report.")

    # ------------------------------------------------------------------
    # EXPORT HANDLERS
    # ------------------------------------------------------------------
    def _handle_export_csv(self):
        rows = self._get_scoped_predictions()
        default_name = timestamped_filename("sms_report", "csv")

        filepath = filedialog.asksaveasfilename(
            initialdir=str(config.REPORTS_DIR),
            initialfile=default_name,
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            title="Save CSV Report",
        )
        if not filepath:
            return  # User cancelled the dialog.

        try:
            export_predictions_to_csv(rows, filepath)
            self._show_export_success(filepath, "CSV")
        except Exception as error:
            messagebox.showerror("Export Failed", f"Could not export the CSV report:\n{error}")

    def _handle_export_pdf(self):
        rows = self._get_scoped_predictions()
        stats = self._compute_scoped_stats(rows)
        default_name = timestamped_filename("sms_report", "pdf")

        filepath = filedialog.asksaveasfilename(
            initialdir=str(config.REPORTS_DIR),
            initialfile=default_name,
            defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")],
            title="Save PDF Report",
        )
        if not filepath:
            return

        try:
            export_predictions_to_pdf(rows, stats, filepath)
            self._show_export_success(filepath, "PDF")
        except Exception as error:
            messagebox.showerror("Export Failed", f"Could not export the PDF report:\n{error}")

    def _compute_scoped_stats(self, rows):
        """Build a small stats dict (matching Database.get_dashboard_stats' shape) for the PDF summary."""
        spam_count = sum(1 for r in rows if r["prediction"] == config.LABEL_SPAM)
        safe_count = sum(1 for r in rows if r["prediction"] == config.LABEL_HAM)
        overall_stats = self.database.get_dashboard_stats()
        return {
            "total": len(rows),
            "spam_count": spam_count,
            "safe_count": safe_count,
            "accuracy": overall_stats["accuracy"],
        }

    def _show_export_success(self, filepath, file_type):
        self.last_exported_path = filepath
        self.status_frame.pack(fill="x", padx=24, pady=(6, 20))
        self.status_label.config(
            text=f"✔ {file_type} report exported successfully:\n{filepath}"
        )

    def _handle_open_last_export(self):
        if not self.last_exported_path:
            return
        opened = open_file(self.last_exported_path)
        if not opened:
            messagebox.showinfo(
                "File Saved", f"The report was saved to:\n{self.last_exported_path}"
            )

    # ------------------------------------------------------------------
    def refresh(self):
        """Refresh the live preview count whenever this page becomes visible."""
        self._update_preview()
