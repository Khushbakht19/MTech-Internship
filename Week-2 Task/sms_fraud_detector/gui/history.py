"""
gui/history.py
----------------
The Prediction History page: a searchable, filterable table of every
SMS message that has ever been scanned by the app.

Features (per project brief):
    - Search       -> free-text search over the message content.
    - Filter        -> show only Spam, only Safe, or All.
    - Scrolling     -> this is a content-heavy page, so smooth
                       mouse-wheel scrolling is enabled on the table.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import config


class HistoryPage(tk.Frame):
    """The Prediction History page."""

    def __init__(self, master, database, classifier, app):
        super().__init__(master, bg=config.COLORS["main_bg"])
        self.database = database
        self.classifier = classifier
        self.app = app

        self.current_filter = "all"     # "all" | "spam" | "ham"
        self.current_search = ""

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_page_title()
        self._build_toolbar()
        self._build_table_card()

    # ------------------------------------------------------------------
    def _build_page_title(self):
        title_frame = tk.Frame(self, bg=config.COLORS["main_bg"])
        title_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))

        title_label = tk.Label(
            title_frame, text="Prediction History", font=config.FONTS["page_title"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_primary"],
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame, text="Every SMS message scanned by the detector, searchable and filterable",
            font=config.FONTS["body"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"],
        )
        subtitle_label.pack(anchor="w")

    # ------------------------------------------------------------------
    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=config.COLORS["main_bg"])
        toolbar.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 14))

        # --- Search box ---
        search_box = tk.Frame(toolbar, bg=config.COLORS["card_bg"], highlightthickness=1,
                               highlightbackground=config.COLORS["border"])
        search_box.pack(side="left", fill="y")

        search_icon = tk.Label(
            search_box, text="🔎", bg=config.COLORS["card_bg"], fg=config.COLORS["text_muted"],
        )
        search_icon.pack(side="left", padx=(12, 4), pady=8)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_box, textvariable=self.search_var, font=config.FONTS["body"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_primary"], relief="flat", width=32,
            insertbackground=config.COLORS["text_primary"],
        )
        search_entry.pack(side="left", padx=(0, 12), pady=8)
        search_entry.bind("<Return>", lambda event: self._handle_search())
        self.search_entry = search_entry

        search_button = tk.Button(
            toolbar, text="Search", font=config.FONTS["button"],
            bg=config.COLORS["blue"], fg=config.COLORS["white"], relief="flat",
            cursor="hand2", padx=14, pady=6, command=self._handle_search,
        )
        search_button.pack(side="left", padx=(10, 0))

        reset_button = tk.Button(
            toolbar, text="Reset", font=config.FONTS["button"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"], relief="flat",
            cursor="hand2", padx=14, pady=6, command=self._handle_reset,
        )
        reset_button.pack(side="left", padx=(6, 0))

        # --- Filter dropdown ---
        filter_label = tk.Label(
            toolbar, text="Filter:", font=config.FONTS["body"],
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_secondary"],
        )
        filter_label.pack(side="left", padx=(24, 6))

        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            toolbar, textvariable=self.filter_var, state="readonly",
            values=["All", "Spam", "Safe"], width=10, font=config.FONTS["body"],
        )
        filter_combo.pack(side="left")
        filter_combo.bind("<<ComboboxSelected>>", self._handle_filter_change)

        # --- Clear history (right-aligned) ---
        clear_button = tk.Button(
            toolbar, text="🗑  Clear History", font=config.FONTS["button"],
            bg=config.COLORS["red_light"], fg=config.COLORS["red"], relief="flat",
            cursor="hand2", padx=14, pady=6, command=self._handle_clear_history,
        )
        clear_button.pack(side="right")

    # ------------------------------------------------------------------
    def _build_table_card(self):
        card = tk.Frame(self, bg=config.COLORS["card_bg"], highlightthickness=1,
                         highlightbackground=config.COLORS["border"])
        card.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 24))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        self.result_count_label = tk.Label(
            card, text="0 results", font=config.FONTS["small"],
            bg=config.COLORS["card_bg"], fg=config.COLORS["text_muted"],
        )
        self.result_count_label.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 6))

        table_frame = tk.Frame(card, bg=config.COLORS["card_bg"])
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "message", "prediction", "confidence", "keywords", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        headings = {
            "id": ("#", 40),
            "message": ("Message", 340),
            "prediction": ("Result", 80),
            "confidence": ("Confidence", 90),
            "keywords": ("Detected Keywords", 220),
            "date": ("Date Scanned", 150),
        }
        for key, (text, width) in headings.items():
            self.tree.heading(key, text=text)
            anchor = "center" if key in ("id", "prediction", "confidence") else "w"
            self.tree.column(key, width=width, anchor=anchor)

        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.tag_configure("spam_row", foreground=config.COLORS["red"])
        self.tree.tag_configure("ham_row", foreground=config.COLORS["green"])

        # Smooth mouse-wheel scrolling (content-heavy page).
        self.tree.bind("<MouseWheel>", self._on_mousewheel)   # Windows / macOS
        self.tree.bind("<Button-4>", self._on_mousewheel)      # Linux scroll up
        self.tree.bind("<Button-5>", self._on_mousewheel)      # Linux scroll down

    def _on_mousewheel(self, event):
        if getattr(event, "num", None) == 4:
            self.tree.yview_scroll(-2, "units")
        elif getattr(event, "num", None) == 5:
            self.tree.yview_scroll(2, "units")
        else:
            self.tree.yview_scroll(int(-1 * (event.delta / 120) * 2), "units")

    # ------------------------------------------------------------------
    # SEARCH / FILTER HANDLERS
    # ------------------------------------------------------------------
    def _handle_search(self):
        self.current_search = self.search_var.get().strip()
        self._load_rows()

    def _handle_reset(self):
        self.search_var.set("")
        self.filter_var.set("All")
        self.current_search = ""
        self.current_filter = "all"
        self._load_rows()

    def _handle_filter_change(self, event=None):
        label_to_key = {"All": "all", "Spam": "spam", "Safe": "ham"}
        self.current_filter = label_to_key.get(self.filter_var.get(), "all")
        self._load_rows()

    def _handle_clear_history(self):
        confirmed = messagebox.askyesno(
            "Clear Prediction History",
            "This will permanently delete every saved prediction. Continue?",
        )
        if confirmed:
            self.database.clear_prediction_history()
            self._load_rows()

    def apply_search(self, search_term):
        """
        Called by the global header search box (see gui/header.py and
        MainApplication._handle_global_search in main.py) so typing in
        the header jumps here and filters immediately.
        """
        self.search_var.set(search_term)
        self.filter_var.set("All")
        self.current_filter = "all"
        self.current_search = search_term
        self._load_rows()

    # ------------------------------------------------------------------
    # DATA LOADING
    # ------------------------------------------------------------------
    def refresh(self):
        """Called every time this page is shown; reloads with current filters intact."""
        self._load_rows()

    def _load_rows(self):
        if self.current_search:
            rows = self.database.search_predictions(self.current_search)
            # A search combined with a non-"all" filter narrows results further.
            if self.current_filter != "all":
                rows = [r for r in rows if r["prediction"] == self.current_filter]
        elif self.current_filter != "all":
            rows = self.database.filter_predictions(self.current_filter)
        else:
            rows = self.database.get_all_predictions()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for display_number, row in enumerate(rows, start=1):
            tag = "spam_row" if row["prediction"] == config.LABEL_SPAM else "ham_row"
            self.tree.insert(
                "", "end",
                values=(
                    display_number,
                    row["message_text"],
                    row["prediction"].upper(),
                    f"{row['confidence']}%",
                    row["detected_keywords"] or "-",
                    row["date_predicted"],
                ),
                tags=(tag,),
            )

        self.result_count_label.config(text=f"{len(rows)} result(s)")
