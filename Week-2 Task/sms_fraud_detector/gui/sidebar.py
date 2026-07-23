"""
gui/sidebar.py
---------------
The fixed, dark-blue navigation sidebar shown on every page of the
application, similar to a professional admin dashboard.

Responsibilities:
    - Display the app brand/logo at the top.
    - Render one clickable row per entry in config.NAV_ITEMS.
    - Highlight whichever page is currently active.
    - Call back into MainApplication.show_page() when an item is clicked.
"""

import tkinter as tk

import config


class Sidebar(tk.Frame):
    """The left-hand navigation panel."""

    def __init__(self, master, on_navigate):
        super().__init__(
            master,
            bg=config.COLORS["sidebar_bg"],
            width=config.SIDEBAR_WIDTH,
        )
        self.on_navigate = on_navigate
        self.grid_propagate(False)  # Keep the fixed width even as children are added.

        # Keeps a reference to each nav row's widgets so we can restyle
        # them later when the active page changes.
        self.nav_rows = {}
        self.active_key = None

        self._build_brand()
        self._build_nav_items()
        self._build_footer()

    # ------------------------------------------------------------------
    def _build_brand(self):
        brand_frame = tk.Frame(self, bg=config.COLORS["sidebar_bg"], height=88)
        brand_frame.pack(fill="x", side="top")
        brand_frame.pack_propagate(False)

        # A plain left-aligned pack layout (not place()-centering) so the
        # icon and title always sit fully inside the sidebar's fixed
        # width, regardless of font rendering differences across systems.
        inner = tk.Frame(brand_frame, bg=config.COLORS["sidebar_bg"])
        inner.pack(
    fill="x",
    padx=(12,12),
    pady=(22,12)
)

        text_frame = tk.Frame(inner, bg=config.COLORS["sidebar_bg"])
        text_frame.pack(
    side="left",
    fill="both",
    expand=True
)

        title_label = tk.Label(
    text_frame,
    text="FRAUD DETECTOR",
    font=("Bahnschrift Bold", 15),
    bg=config.COLORS["sidebar_bg"],
    fg="white",
    anchor="w",
    justify="left",
)
        title_label.pack(
    anchor="w"
)

        subtitle_label = tk.Label(
    text_frame,
    text="Monitor 💠 Detect 💠 Analyze",
    font=("Bahnschrift", 8),
    bg=config.COLORS["sidebar_bg"],
    fg=config.COLORS["sidebar_text"],
    anchor="w",
)
        subtitle_label.pack(
    anchor="w",
    pady=(1,0)
)

        divider = tk.Frame(self, bg=config.COLORS["sidebar_bg_light"], height=1)
        divider.pack(fill="x", side="top")

    # ------------------------------------------------------------------
    def _build_nav_items(self):
        nav_container = tk.Frame(self, bg=config.COLORS["sidebar_bg"])
        nav_container.pack(fill="x", side="top", pady=(16, 0))

        for item in config.NAV_ITEMS:
            row = self._create_nav_row(nav_container, item)
            row.pack(fill="x", padx=12, pady=3)
            self.nav_rows[item["key"]] = row

    def _create_nav_row(self, parent, item):
        """
        Build a single clickable navigation row. Every child widget
        (the row frame, icon label, and text label) is bound to the
        same click handler so the whole row is clickable, not just the
        text.
        """
        row = tk.Frame(parent, bg=config.COLORS["sidebar_bg"], cursor="hand2")

        icon_label = tk.Label(
            row, text=item["icon"], font=(config.FONT_FAMILY, 13),
            bg=config.COLORS["sidebar_bg"], fg=config.COLORS["sidebar_text"],
            width=3, anchor="w",
        )
        icon_label.pack(side="left", padx=(10, 4), pady=10)

        text_label = tk.Label(
            row, text=item["label"], font=config.FONTS["sidebar_item"],
            bg=config.COLORS["sidebar_bg"], fg=config.COLORS["sidebar_text"], anchor="w",
        )
        text_label.pack(side="left", fill="x", expand=True, pady=10)

        row.icon_label = icon_label
        row.text_label = text_label
        row.item_key = item["key"]

        for widget in (row, icon_label, text_label):
            widget.bind("<Button-1>", lambda event, key=item["key"]: self.on_navigate(key))
            widget.bind("<Enter>", lambda event, r=row: self._on_hover(r, True))
            widget.bind("<Leave>", lambda event, r=row: self._on_hover(r, False))

        return row

    def _on_hover(self, row, is_hovering):
        """Give non-active rows a subtle highlight on mouse-over."""
        if row.item_key == self.active_key:
            return  # Active row keeps its highlighted color regardless of hover.

        color = config.COLORS["sidebar_hover"] if is_hovering else config.COLORS["sidebar_bg"]
        row.configure(bg=color)
        row.icon_label.configure(bg=color)
        row.text_label.configure(bg=color)

    # ------------------------------------------------------------------
    def _build_footer(self):
        footer = tk.Frame(self, bg=config.COLORS["sidebar_bg"])
        footer.pack(fill="x", side="bottom", pady=16)

        divider = tk.Frame(self, bg=config.COLORS["sidebar_bg_light"], height=1)
        divider.pack(fill="x", side="bottom")

        footer_label = tk.Label(
            footer, text="© 2026 Fraud Detector",
            font=config.FONTS["small"], justify="center",
            bg=config.COLORS["sidebar_bg"], fg=config.COLORS["text_muted"],
        )
        footer_label.pack()

    # ------------------------------------------------------------------
    def set_active(self, page_key):
        """
        Visually mark `page_key` as the active page and restore every
        other row back to its default (inactive) styling.
        """
        self.active_key = page_key
        for key, row in self.nav_rows.items():
            is_active = key == page_key
            bg = config.COLORS["sidebar_active"] if is_active else config.COLORS["sidebar_bg"]
            fg = config.COLORS["sidebar_text_active"] if is_active else config.COLORS["sidebar_text"]

            row.configure(bg=bg)
            row.icon_label.configure(bg=bg, fg=fg)
            row.text_label.configure(bg=bg, fg=fg, font=(
                config.FONTS["sidebar_item"] if not is_active
                else (config.FONT_FAMILY, 11, "bold")
            ))
