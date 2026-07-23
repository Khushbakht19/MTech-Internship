"""
config.py
------------------------------------------------------------------
Central configuration file for the Resume Screener Pro application.

This file stores:
    - File/folder paths
    - Application metadata
    - Window and layout dimensions
    - The "Emerald & Slate Professional" color theme
    - Fonts used throughout the GUI
    - Shared constants (score thresholds, etc.)

Keeping these values in a single module makes the whole application
easy to re-theme, resize, or reconfigure without touching GUI code.
------------------------------------------------------------------
"""

import os

# ==================================================================
# BASE PATHS
# ==================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

DB_PATH = os.path.join(DATA_DIR, "resume_screener.db")

# Ensure required folders exist before the app starts
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# ==================================================================
# APPLICATION METADATA
# ==================================================================
APP_NAME = "Resume Screener"
APP_VERSION = "2.0"
APP_AUTHOR = "BS Artificial Intelligence Student"
APP_SUBTITLE = "AI Powered Recruitment Assistant"
APP_YEAR = "2026"

# ==================================================================
# WINDOW / LAYOUT SETTINGS
# ==================================================================
WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 768
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 700

SIDEBAR_WIDTH = 230
HEADER_HEIGHT = 75

SPLASH_WIDTH = 560
SPLASH_HEIGHT = 340
SPLASH_DURATION_MS = 2200          # total time (ms) the splash screen stays visible

# ==================================================================
# THEME: "EMERALD & SLATE PROFESSIONAL"
# ==================================================================
COLORS = {
    # --- Sidebar (deep emerald) ---
    "sidebar_bg":            "#0B3D2E",
    "sidebar_bg_hover":      "#124A38",
    "sidebar_bg_active":     "#15593F",
    "sidebar_text":          "#E7F5EF",
    "sidebar_text_muted":    "#8FBFA9",
    "sidebar_accent":        "#22C55E",
    "sidebar_border":        "#0F4433",

    # --- Workspace (light slate) ---
    "workspace_bg":          "#F4F6F5",
    "card_bg":               "#FFFFFF",
    "card_border":           "#E4E9E6",

    # --- Header ---
    "header_bg":             "#FFFFFF",
    "header_border":         "#E5E7EB",

    # --- Text ---
    "text_primary":          "#1E293B",
    "text_secondary":        "#64748B",
    "text_muted":            "#94A3B8",
    "text_on_dark":          "#F8FAFC",

    # --- Accent (emerald) ---
    "accent_primary":        "#059669",
    "accent_primary_dark":   "#047857",
    "accent_primary_light":  "#D1FAE5",

    # --- Status colors ---
    "success":               "#16A34A",
    "warning":               "#F59E0B",
    "danger":                "#DC2626",
    "info":                  "#0EA5E9",

    # --- Tables ---
    "table_header_bg":       "#F1F5F4",
    "table_row_alt":         "#FAFBFA",
    "table_border":          "#E5E7EB",
    "table_selected":        "#D1FAE5",

    # --- Chart palette (used by matplotlib) ---
    "chart_palette": [
        "#059669", "#0EA5E9", "#F59E0B",
        "#8B5CF6", "#DC2626", "#14B8A6"
    ],
}

# ==================================================================
# FONTS
# ==================================================================
FONT_FAMILY = "Segoe UI"

FONTS = {
    "app_title":      (FONT_FAMILY, 18, "bold"),
    "page_title":     (FONT_FAMILY, 20, "bold"),
    "section_title":  (FONT_FAMILY, 13, "bold"),
    "subtitle":       (FONT_FAMILY, 11),
    "body":           (FONT_FAMILY, 10),
    "body_bold":      (FONT_FAMILY, 10, "bold"),
    "small":          (FONT_FAMILY, 9),
    "sidebar_item":   (FONT_FAMILY, 11),
    "sidebar_brand":  (FONT_FAMILY, 14, "bold"),
    "stat_value":     (FONT_FAMILY, 24, "bold"),
    "stat_label":     (FONT_FAMILY, 10),
    "table_header":   (FONT_FAMILY, 10, "bold"),
    "button":         (FONT_FAMILY, 10, "bold"),
}

# ==================================================================
# MATCH SCORE THRESHOLDS
# ==================================================================
# Used to color-code match scores consistently across the whole app.
SCORE_THRESHOLDS = {
    "excellent": 75,   # score >= 75  -> Excellent Match
    "good":      50,   # score >= 50  -> Good Match
    "average":   30,   # score >= 30  -> Average Match
    # anything below "average" is treated as "Low Match"
}


def get_score_label(score):
    """Return a human-readable label for a given match score (0-100)."""
    if score >= SCORE_THRESHOLDS["excellent"]:
        return "Excellent Match"
    elif score >= SCORE_THRESHOLDS["good"]:
        return "Good Match"
    elif score >= SCORE_THRESHOLDS["average"]:
        return "Average Match"
    return "Low Match"


def get_score_color(score):
    """Return a theme color matching the score category."""
    if score >= SCORE_THRESHOLDS["excellent"]:
        return COLORS["success"]
    elif score >= SCORE_THRESHOLDS["good"]:
        return COLORS["accent_primary"]
    elif score >= SCORE_THRESHOLDS["average"]:
        return COLORS["warning"]
    return COLORS["danger"]
