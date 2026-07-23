"""
gui/header.py
--------------
The top header bar shown above the content area on every page.

Contains:
    - A search box (searches the Prediction History by message text).
    - A notification bell icon (decorative, gives the dashboard a
      polished "admin panel" feel).
    - A user avatar + name, so the app feels like a real multi-purpose
      product rather than a bare script.
"""

import tkinter as tk

import config


class Header(tk.Frame):
    """Top bar: search box on the left, profile/notifications on the right."""

    def __init__(self, master, on_search):
        super().__init__(
            master,
            bg=config.COLORS["header_bg"],
            height=config.HEADER_HEIGHT,
        )
        self.on_search = on_search
        self.pack_propagate(False)
        self.grid_propagate(False)

        self._build_bottom_border()
        self._build_search_box()
        self._build_profile_section()

    # ------------------------------------------------------------------
    def _build_bottom_border(self):
        border = tk.Frame(self, bg=config.COLORS["border"], height=1)
        border.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

    # ------------------------------------------------------------------
    def _build_search_box(self):
        search_container = tk.Frame(
            self, bg=config.COLORS["main_bg"], highlightthickness=1,
            highlightbackground=config.COLORS["border"],
        )
        search_container.place(x=28, rely=0.5, anchor="w", width=340, height=38)

        icon_label = tk.Label(
            search_container, text="🔎", font=(config.FONT_FAMILY, 10),
            bg=config.COLORS["main_bg"], fg=config.COLORS["text_muted"],
        )
        icon_label.pack(side="left", padx=(12, 6))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_container, textvariable=self.search_var,
            font=config.FONTS["body"], bg=config.COLORS["main_bg"],
            fg=config.COLORS["text_primary"], relief="flat",
            insertbackground=config.COLORS["text_primary"],
        )
        search_entry.pack(side="left", fill="both", expand=True, padx=(0, 12))
        search_entry.insert(0, "")
        search_entry.bind("<Return>", self._handle_search_submit)

        # Simple placeholder-text behaviour since tk.Entry has none built in.
        placeholder = "Search books, messages, predictions..."
        search_entry.insert(0, placeholder)
        search_entry.configure(fg=config.COLORS["text_muted"])

        def clear_placeholder(event):
            if search_entry.get() == placeholder:
                search_entry.delete(0, "end")
                search_entry.configure(fg=config.COLORS["text_primary"])

        def restore_placeholder(event):
            if not search_entry.get():
                search_entry.insert(0, placeholder)
                search_entry.configure(fg=config.COLORS["text_muted"])

        search_entry.bind("<FocusIn>", clear_placeholder)
        search_entry.bind("<FocusOut>", restore_placeholder)
        self.search_entry = search_entry
        self._placeholder_text = placeholder

    def _handle_search_submit(self, event):
        term = self.search_var.get().strip()
        if term and term != self._placeholder_text and self.on_search:
            self.on_search(term)

    # ------------------------------------------------------------------
    def _build_profile_section(self):
        profile_frame = tk.Frame(self, bg=config.COLORS["header_bg"])
        profile_frame.place(relx=1.0, rely=0.5, anchor="e", x=-28)

        bell_label = tk.Label(
            profile_frame, text="🔔", font=(config.FONT_FAMILY, 14),
            bg=config.COLORS["header_bg"], fg=config.COLORS["text_secondary"],
        )
        bell_label.pack(side="left", padx=(0, 20))

        divider = tk.Frame(profile_frame, bg=config.COLORS["border"], width=1, height=32)
        divider.pack(side="left", padx=(0, 20))

        avatar = tk.Label(
            profile_frame, text="      🛡️", font=(config.FONT_FAMILY, 12, "bold"),
            bg=config.COLORS["blue"], fg=config.COLORS["white"],
            width=3, height=1,
        )
        avatar.pack(side="left", padx=(0, 10))

        text_frame = tk.Frame(profile_frame, bg=config.COLORS["header_bg"])
        text_frame.pack(side="left")

        name_label = tk.Label(
            text_frame, text="Welcome Back", font=config.FONTS["body_bold"],
            bg=config.COLORS["header_bg"], fg=config.COLORS["header_text"], anchor="w",
        )
        name_label.pack(anchor="w")

        role_label = tk.Label(
            text_frame, text="Your SMS Security Centre", font=config.FONTS["small"],
            bg=config.COLORS["header_bg"], fg=config.COLORS["text_muted"], anchor="w",
        )
        role_label.pack(anchor="w")
