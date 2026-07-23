"""
sidebar.py
------------------------------------------------------------------
Implements the always-visible left navigation sidebar, styled as a
deep emerald panel per the "Emerald & Slate Professional" theme.

The sidebar exposes a simple callback-based API: main_window.py
passes a single on_navigate(page_key) function, and the sidebar
calls it whenever the user clicks a navigation item. The sidebar
also tracks which item is currently active so it can highlight it.
------------------------------------------------------------------
"""

import tkinter as tk

import config


# Each entry: (page_key, icon, label)
NAV_ITEMS = [
    ("dashboard", "🏠", "Dashboard"),
    ("candidates", "👥", "Candidates"),
    ("jobs", "💼", "Jobs"),
    ("screening", "🔍", "Screening"),
    ("history", "🕓", "History"),
    ("analytics", "📊", "Analytics"),
    ("reports", "📁", "Reports"),
    ("about", "ℹ️", "About"),
]


class Sidebar(tk.Frame):
    """The application's left-hand navigation panel."""

    def __init__(self, parent, on_navigate):
        """
        Args:
            parent (tk.Widget): parent container.
            on_navigate (callable): called with a page_key string
                                    whenever a nav item is clicked.
        """
        colors = config.COLORS
        super().__init__(parent, bg=colors["sidebar_bg"], width=config.SIDEBAR_WIDTH)
        self.pack_propagate(False)

        self.on_navigate = on_navigate
        self.colors = colors
        self.nav_labels = {}   # page_key -> tk.Label widget
        self.active_page = None

        self._build_brand_section()
        self._build_navigation()
        self._build_footer()

    # ------------------------------------------------------------
    def _build_brand_section(self):
        """Builds the top branding area (logo + app name)."""
        colors = self.colors

        brand_frame = tk.Frame(self, bg=colors["sidebar_bg"])
        brand_frame.pack(fill="x", pady=(20, 10), padx=12)

        logo_row = tk.Frame(brand_frame, bg=colors["sidebar_bg"])
        logo_row.pack(fill="x")

        icon_label = tk.Label(
            logo_row, text="📄", font=("Segoe UI Emoji", 18),
            bg=colors["sidebar_bg"], fg=colors["sidebar_accent"]
        )
        icon_label.pack(side="left", padx=(0, 6))

        title_label = tk.Label(
            logo_row, text="Resume Screener", font=config.FONTS["sidebar_brand"],
            bg=colors["sidebar_bg"], fg=colors["text_on_dark"], anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)

        subtitle_label = tk.Label(
            brand_frame, text="                         HR ANALYTICS SUITE",
            font=("Segoe UI", 7, "bold"),
            bg=colors["sidebar_bg"], fg=colors["sidebar_text_muted"], anchor="w"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # Divider line beneath the branding
        divider = tk.Frame(self, bg=colors["sidebar_border"], height=1)
        divider.pack(fill="x", padx=12, pady=(14, 6))

    # ------------------------------------------------------------
    def _build_navigation(self):
        """Builds the list of clickable navigation items."""
        colors = self.colors

        nav_container = tk.Frame(self, bg=colors["sidebar_bg"])
        nav_container.pack(fill="x", pady=(6, 0))

        for page_key, icon, label_text in NAV_ITEMS:
            item_frame = tk.Frame(nav_container, bg=colors["sidebar_bg"], cursor="hand2")
            item_frame.pack(fill="x", padx=8, pady=2)

            item_label = tk.Label(
                item_frame,
                text=f"  {icon}   {label_text}",
                font=config.FONTS["sidebar_item"],
                bg=colors["sidebar_bg"],
                fg=colors["sidebar_text"],
                anchor="w",
                padx=8,
                pady=9,
            )
            item_label.pack(fill="x")

            # Bind clicks and hover effects on both the frame and label
            for widget in (item_frame, item_label):
                widget.bind("<Button-1>", lambda event, key=page_key: self.on_navigate(key))
                widget.bind("<Enter>", lambda event, key=page_key: self._on_hover(key, True))
                widget.bind("<Leave>", lambda event, key=page_key: self._on_hover(key, False))

            self.nav_labels[page_key] = (item_frame, item_label)

        self.set_active("dashboard")

    # ------------------------------------------------------------
    def _build_footer(self):
        """Builds a small footer showing the app version at the bottom."""
        colors = self.colors

        footer_frame = tk.Frame(self, bg=colors["sidebar_bg"])
        footer_frame.pack(side="bottom", fill="x", pady=14)

        divider = tk.Frame(footer_frame, bg=colors["sidebar_border"], height=1)
        divider.pack(fill="x", padx=12, pady=(0, 10))

        version_label = tk.Label(
            footer_frame, text=f"v{config.APP_VERSION}  ·  © {config.APP_YEAR}",
            font=("Segoe UI", 8),
            bg=colors["sidebar_bg"], fg=colors["sidebar_text_muted"]
        )
        version_label.pack(padx=12)

    # ------------------------------------------------------------
    def _on_hover(self, page_key, is_hovering):
        """Applies a subtle hover highlight to non-active nav items."""
        if page_key == self.active_page:
            return  # active item keeps its highlight regardless of hover

        item_frame, item_label = self.nav_labels[page_key]
        background = self.colors["sidebar_bg_hover"] if is_hovering else self.colors["sidebar_bg"]
        item_frame.configure(bg=background)
        item_label.configure(bg=background)

    # ------------------------------------------------------------
    def set_active(self, page_key):
        """
        Highlights the given page as active and resets all other
        items back to their default (inactive) appearance.
        """
        for key, (item_frame, item_label) in self.nav_labels.items():
            if key == page_key:
                item_frame.configure(bg=self.colors["sidebar_bg_active"])
                item_label.configure(
                    bg=self.colors["sidebar_bg_active"],
                    fg="#FFFFFF",
                    font=(config.FONT_FAMILY, 10, "bold"),
                )
            else:
                item_frame.configure(bg=self.colors["sidebar_bg"])
                item_label.configure(
                    bg=self.colors["sidebar_bg"],
                    fg=self.colors["sidebar_text"],
                    font=config.FONTS["sidebar_item"],
                )
        self.active_page = page_key