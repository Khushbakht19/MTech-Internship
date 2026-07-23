"""
config.py
---------
Central configuration file for the SMS Fraud Detector application.

This module stores every "constant" the rest of the app depends on:
file paths, window settings, the color palette, fonts, and a few
ML-related constants. Keeping all of this in one place means the GUI
modules never hard-code a color or a path -- they just import from
here. This makes the whole project much easier to re-theme or move.
"""

from pathlib import Path

# --------------------------------------------------------------------------
# BASE PATHS
# --------------------------------------------------------------------------
# BASE_DIR points to the project root (the folder this file lives in).
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"

# Make sure the folders that store generated files always exist.
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# SQLite database file.
DB_PATH = DATA_DIR / "sms_fraud.db"

# Trained ML artifacts (created the first time the app trains the model).
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
CLASSIFIER_PATH = MODELS_DIR / "naive_bayes_model.pkl"
METRICS_PATH = MODELS_DIR / "model_metrics.pkl"

# Folder where exported reports (CSV / PDF) are written.
REPORTS_DIR = BASE_DIR / "reports_exported"
REPORTS_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------------------------
# APPLICATION / WINDOW SETTINGS
# --------------------------------------------------------------------------
APP_NAME = "SMS Fraud Detector"
APP_VERSION = "2.0"

# Target resolution requested by the project brief.
WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 768
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 700

SPLASH_WIDTH = 520
SPLASH_HEIGHT = 320
SPLASH_DURATION_MS = 2200  # how long the splash screen stays on screen

SIDEBAR_WIDTH = 300
HEADER_HEIGHT = 64


# --------------------------------------------------------------------------
# COLOR PALETTE
# --------------------------------------------------------------------------
# A single dark-blue / white theme used across every screen so the app
# feels consistent, similar to a professional analytics dashboard.
COLORS = {
    # Sidebar
    "sidebar_bg": "#101B33",
    "sidebar_bg_light": "#152242",
    "sidebar_hover": "#1D2C52",
    "sidebar_active": "#2F6FED",
    "sidebar_text": "#C7D0E8",
    "sidebar_text_active": "#FFFFFF",

    # Main workspace
    "main_bg": "#F4F6FB",
    "card_bg": "#FFFFFF",
    "border": "#E7EAF3",

    # Header
    "header_bg": "#FFFFFF",
    "header_text": "#1E2A45",

    # Text
    "text_primary": "#1E2A45",
    "text_secondary": "#6B7897",
    "text_muted": "#9AA5BD",

    # Statistic-card accent colors
    "blue": "#2F6FED",
    "blue_light": "#EAF1FF",
    "green": "#1DBF73",
    "green_light": "#E4F9EF",
    "orange": "#FF9F43",
    "orange_light": "#FFF3E4",
    "red": "#F1416C",
    "red_light": "#FDECF1",
    "purple": "#7239EA",
    "purple_light": "#F1EAFD",

    # Status colors
    "spam": "#F1416C",
    "safe": "#1DBF73",

    # Misc
    "white": "#FFFFFF",
    "black": "#000000",
    "divider": "#EDEFF5",
}


# --------------------------------------------------------------------------
# FONTS
# --------------------------------------------------------------------------
FONT_FAMILY = "Segoe UI"

FONTS = {
    "splash_title": (FONT_FAMILY, 26, "bold"),
    "splash_subtitle": (FONT_FAMILY, 11),
    "page_title": (FONT_FAMILY, 20, "bold"),
    "section_title": (FONT_FAMILY, 13, "bold"),
    "card_value": (FONT_FAMILY, 24, "bold"),
    "card_label": (FONT_FAMILY, 10),
    "body": (FONT_FAMILY, 10),
    "body_bold": (FONT_FAMILY, 10, "bold"),
    "small": (FONT_FAMILY, 9),
    "sidebar_item": (FONT_FAMILY, 11),
    "sidebar_brand": (FONT_FAMILY, 14, "bold"),
    "button": (FONT_FAMILY, 10, "bold"),
}


# --------------------------------------------------------------------------
# NAVIGATION
# --------------------------------------------------------------------------
# Ordered list of pages shown in the sidebar. Each GUI page module
# registers itself under one of these keys inside main.py.
NAV_ITEMS = [
    {"key": "dashboard", "label": "Dashboard", "icon": "🏠"},
    {"key": "scanner", "label": "SMS Scanner", "icon": "🔍"},
    {"key": "history", "label": "Prediction History", "icon": "🕑"},
    {"key": "analytics", "label": "Analytics", "icon": "📊"},
    {"key": "reports", "label": "Reports", "icon": "📄"},
    {"key": "about", "label": "About", "icon": "ℹ️"},
]


# --------------------------------------------------------------------------
# MACHINE LEARNING SETTINGS
# --------------------------------------------------------------------------
# Train/test split ratio used when evaluating the Naive Bayes model.
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Keywords the app looks for inside a message to explain *why* it was
# flagged as spam. This powers the "Keyword Detection" requirement and
# the "Top Detected Threat" dashboard card.
SUSPICIOUS_KEYWORDS = [
    "winner", "won", "prize", "lottery", "free", "urgent", "click",
    "verify", "otp", "password", "bank", "account", "suspended",
    "click here", "claim", "reward", "congratulations", "gift",
    "loan", "cash", "credit", "limited", "offer", "act now",
    "confirm", "update your", "security alert", "blocked", "refund",
    "link", "login", "unauthorized", "expire", "expires", "kyc",
]

# Labels used consistently across the database and the ML pipeline.
LABEL_SPAM = "spam"
LABEL_HAM = "ham"
