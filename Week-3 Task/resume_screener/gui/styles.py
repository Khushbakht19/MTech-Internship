"""
styles.py
------------------------------------------------------------------
Defines the global ttk styling used throughout Resume Screener Pro,
implementing the "Emerald & Slate Professional" theme described in
the project brief.

This module is imported once by main_window.py and configures a
single shared ttk.Style() instance that every page then reuses.
Centralizing styles here keeps individual page files focused purely
on layout instead of repeating color/font declarations everywhere.
------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk

import config


def apply_theme(root):
    """
    Configures and returns a ttk.Style object implementing the
    Emerald & Slate Professional theme.

    Args:
        root (tk.Tk): the root application window.

    Returns:
        ttk.Style: the configured style object.
    """
    style = ttk.Style(root)

    # "clam" is the most customizable built-in ttk theme - required
    # to override colors properly (the default "vista"/"aqua" themes
    # ignore most color configuration options).
    style.theme_use("clam")

    colors = config.COLORS
    fonts = config.FONTS

    root.configure(bg=colors["workspace_bg"])

    # ==============================================================
    # GENERIC FRAME / LABEL STYLES
    # ==============================================================
    style.configure("Workspace.TFrame", background=colors["workspace_bg"])
    style.configure("Card.TFrame", background=colors["card_bg"], relief="flat")
    style.configure("Sidebar.TFrame", background=colors["sidebar_bg"])
    style.configure("Header.TFrame", background=colors["header_bg"])

    style.configure(
        "Workspace.TLabel",
        background=colors["workspace_bg"],
        foreground=colors["text_primary"],
        font=fonts["body"],
    )
    style.configure(
        "Card.TLabel",
        background=colors["card_bg"],
        foreground=colors["text_primary"],
        font=fonts["body"],
    )
    style.configure(
        "CardMuted.TLabel",
        background=colors["card_bg"],
        foreground=colors["text_secondary"],
        font=fonts["small"],
    )
    style.configure(
        "PageTitle.TLabel",
        background=colors["workspace_bg"],
        foreground=colors["text_primary"],
        font=fonts["page_title"],
    )
    style.configure(
        "SectionTitle.TLabel",
        background=colors["card_bg"],
        foreground=colors["text_primary"],
        font=fonts["section_title"],
    )
    style.configure(
        "Subtitle.TLabel",
        background=colors["workspace_bg"],
        foreground=colors["text_secondary"],
        font=fonts["subtitle"],
    )
    style.configure(
        "StatValue.TLabel",
        background=colors["card_bg"],
        foreground=colors["text_primary"],
        font=fonts["stat_value"],
    )
    style.configure(
        "StatLabel.TLabel",
        background=colors["card_bg"],
        foreground=colors["text_secondary"],
        font=fonts["stat_label"],
    )
    style.configure(
        "Header.TLabel",
        background=colors["header_bg"],
        foreground=colors["text_primary"],
        font=fonts["body"],
    )

    # ==============================================================
    # SIDEBAR STYLES
    # ==============================================================
    style.configure(
        "SidebarBrand.TLabel",
        background=colors["sidebar_bg"],
        foreground=colors["text_on_dark"],
        font=fonts["sidebar_brand"],
    )
    style.configure(
        "SidebarSubtitle.TLabel",
        background=colors["sidebar_bg"],
        foreground=colors["sidebar_text_muted"],
        font=fonts["small"],
    )
    style.configure(
        "SidebarItem.TLabel",
        background=colors["sidebar_bg"],
        foreground=colors["sidebar_text"],
        font=fonts["sidebar_item"],
        padding=(12, 10),
    )
    style.configure(
        "SidebarItemActive.TLabel",
        background=colors["sidebar_bg_active"],
        foreground="#FFFFFF",
        font=fonts["sidebar_item"],
        padding=(12, 10),
    )

    # ==============================================================
    # BUTTON STYLES
    # ==============================================================
    style.configure(
        "Primary.TButton",
        background=colors["accent_primary"],
        foreground="#FFFFFF",
        font=fonts["button"],
        padding=(14, 9),
        borderwidth=0,
        focusthickness=0,
    )
    style.map(
        "Primary.TButton",
        background=[("active", colors["accent_primary_dark"]), ("pressed", colors["accent_primary_dark"])],
    )

    style.configure(
        "Secondary.TButton",
        background=colors["card_bg"],
        foreground=colors["text_primary"],
        font=fonts["button"],
        padding=(14, 9),
        borderwidth=1,
        focusthickness=0,
        relief="solid",
    )
    style.map(
        "Secondary.TButton",
        background=[("active", colors["table_header_bg"])],
    )

    style.configure(
        "Danger.TButton",
        background=colors["danger"],
        foreground="#FFFFFF",
        font=fonts["button"],
        padding=(14, 9),
        borderwidth=0,
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#B91C1C")],
    )

    # ==============================================================
    # ENTRY / COMBOBOX STYLES
    # ==============================================================
    style.configure(
        "Modern.TEntry",
        fieldbackground="#FFFFFF",
        foreground=colors["text_primary"],
        bordercolor=colors["card_border"],
        lightcolor=colors["card_border"],
        darkcolor=colors["card_border"],
        padding=8,
    )
    style.configure(
        "Modern.TCombobox",
        fieldbackground="#FFFFFF",
        foreground=colors["text_primary"],
        padding=6,
    )

    # ==============================================================
    # TABLE (TREEVIEW) STYLES
    # ==============================================================
    style.configure(
        "Modern.Treeview",
        background="#FFFFFF",
        fieldbackground="#FFFFFF",
        foreground=colors["text_primary"],
        rowheight=32,
        font=fonts["body"],
        borderwidth=0,
    )
    style.configure(
        "Modern.Treeview.Heading",
        background=colors["table_header_bg"],
        foreground=colors["text_secondary"],
        font=fonts["table_header"],
        borderwidth=0,
        relief="flat",
        padding=(8, 8),
    )
    style.map(
        "Modern.Treeview",
        background=[("selected", colors["table_selected"])],
        foreground=[("selected", colors["text_primary"])],
    )
    style.map(
        "Modern.Treeview.Heading",
        background=[("active", colors["table_header_bg"])],
    )

    # ==============================================================
    # NOTEBOOK / SCROLLBAR STYLES
    # ==============================================================
    # Inherit default vertical & horizontal layout structures to fix "Layout Vertical.Modern.TScrollbar not found" crash
    style.layout("Vertical.Modern.TScrollbar", style.layout("Vertical.TScrollbar"))
    style.layout("Horizontal.Modern.TScrollbar", style.layout("Horizontal.TScrollbar"))

    style.configure(
        "Modern.TScrollbar",
        background=colors["workspace_bg"],
        troughcolor=colors["workspace_bg"],
        bordercolor=colors["workspace_bg"],
        arrowcolor=colors["text_secondary"],
        gripcount=0,
    )

    style.configure(
        "Vertical.Modern.TScrollbar",
        background=colors["workspace_bg"],
        troughcolor=colors["workspace_bg"],
        bordercolor=colors["workspace_bg"],
        arrowcolor=colors["text_secondary"],
        gripcount=0,
    )

    style.configure(
        "Modern.Horizontal.TProgressbar",
        background=colors["accent_primary"],
        troughcolor=colors["table_header_bg"],
        borderwidth=0,
    )

    return style


def get_score_badge_colors(score):
    """
    Returns a (background, foreground) color tuple for a match-score
    badge, matching the score category defined in config.py.
    Used by table renderers and cards to visually color-code scores.
    """
    colors = config.COLORS
    if score >= config.SCORE_THRESHOLDS["excellent"]:
        return colors["accent_primary_light"], colors["success"]
    elif score >= config.SCORE_THRESHOLDS["good"]:
        return "#DBEAFE", colors["accent_primary"]
    elif score >= config.SCORE_THRESHOLDS["average"]:
        return "#FEF3C7", colors["warning"]
    else:
        return "#FEE2E2", colors["danger"]