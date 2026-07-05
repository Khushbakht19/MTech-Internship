"""
styles.py
---------
Central place for all visual styling (Qt Style Sheets / QSS).
Keeping the stylesheet in one Python string constant means every widget
in the application shares one consistent, professional dark theme with
blue accents - and it can be tweaked from a single location.
"""

# Color palette used throughout the application (documented for reference)
COLORS = {
    "background": "#1a1d29",
    "surface": "#232838",
    "surface_light": "#2c3347",
    "sidebar": "#161925",
    "accent": "#3b82f6",       # primary blue accent
    "accent_hover": "#5b9bff",
    "accent_dark": "#2563eb",
    "text_primary": "#e8eaf0",
    "text_secondary": "#9ca3b5",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "border": "#333b52",
}

MAIN_STYLESHEET = """
/* ===================== GLOBAL ===================== */
QWidget {
    background-color: #1a1d29;
    color: #e8eaf0;
    font-family: 'Segoe UI', 'Cantarell', sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #1a1d29;
}

/* ===================== SIDEBAR ===================== */
#Sidebar {
    background-color: #161925;
    border-right: 1px solid #2c3347;
}

#SidebarTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
    padding: 24px 20px 6px 20px;
}

#SidebarSubtitle {
    color: #9ca3b5;
    font-size: 11px;
    padding: 0px 20px 20px 20px;
}

QPushButton#NavButton {
    background-color: transparent;
    color: #9ca3b5;
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#NavButton:hover {
    background-color: #232838;
    color: #ffffff;
}

QPushButton#NavButton:checked {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: 600;
}

/* ===================== TOP BAR ===================== */
#TopBar {
    background-color: #232838;
    border-bottom: 1px solid #2c3347;
}

#PageTitle {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
}

#PageSubtitle {
    font-size: 12px;
    color: #9ca3b5;
}

/* ===================== CARDS ===================== */
.Card, #StatCard, #ChartCard, #ContentCard {
    background-color: #232838;
    border-radius: 14px;
    border: 1px solid #2c3347;
}

#StatCard {
    padding: 4px;
}

#StatCardTitle {
    color: #9ca3b5;
    font-size: 12px;
    font-weight: 600;
}

#StatCardValue {
    color: #ffffff;
    font-size: 26px;
    font-weight: 700;
}

#StatCardIcon {
    font-size: 26px;
}

/* ===================== BUTTONS ===================== */
QPushButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #5b9bff;
}

QPushButton:pressed {
    background-color: #2563eb;
}

QPushButton:disabled {
    background-color: #3a4257;
    color: #6b7280;
}

QPushButton#SecondaryButton {
    background-color: #2c3347;
    color: #e8eaf0;
}

QPushButton#SecondaryButton:hover {
    background-color: #3a4257;
}

QPushButton#DangerButton {
    background-color: #ef4444;
}

QPushButton#DangerButton:hover {
    background-color: #f87171;
}

/* ===================== INPUTS ===================== */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {
    background-color: #2c3347;
    border: 1px solid #333b52;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e8eaf0;
    selection-background-color: #3b82f6;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
    border: 1px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #2c3347;
    color: #e8eaf0;
    selection-background-color: #3b82f6;
    border: 1px solid #333b52;
    outline: none;
}

/* ===================== TABLES ===================== */
QTableWidget {
    background-color: #232838;
    alternate-background-color: #262c3d;
    gridline-color: #2c3347;
    border: 1px solid #2c3347;
    border-radius: 10px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 6px;
    border: none;
}

QHeaderView::section {
    background-color: #161925;
    color: #9ca3b5;
    padding: 10px;
    border: none;
    font-weight: 600;
    font-size: 12px;
}

QTableCornerButton::section {
    background-color: #161925;
    border: none;
}

/* ===================== SCROLLBARS ===================== */
QScrollBar:vertical {
    background: #1a1d29;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #333b52;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #3b82f6;
}

QScrollBar:horizontal {
    background: #1a1d29;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background: #333b52;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
    width: 0px;
}

/* ===================== PROGRESS BARS ===================== */
QProgressBar {
    background-color: #2c3347;
    border-radius: 8px;
    text-align: center;
    color: #ffffff;
    font-weight: 600;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 8px;
}

/* ===================== TABS ===================== */
QTabWidget::pane {
    border: 1px solid #2c3347;
    border-radius: 10px;
    background-color: #232838;
}

QTabBar::tab {
    background-color: #232838;
    color: #9ca3b5;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #3b82f6;
    color: #ffffff;
}

/* ===================== LABELS ===================== */
QLabel#SectionHeader {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#MutedLabel {
    color: #9ca3b5;
    font-size: 12px;
}

/* ===================== GROUPBOX ===================== */
QGroupBox {
    border: 1px solid #2c3347;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #9ca3b5;
}

/* ===================== SCROLL AREA ===================== */
QScrollArea {
    border: none;
    background: transparent;
}

/* ===================== TOOLTIP ===================== */
QToolTip {
    background-color: #2c3347;
    color: #e8eaf0;
    border: 1px solid #3b82f6;
    padding: 4px 8px;
    border-radius: 6px;
}
"""


def get_stylesheet():
    """Returns the full application stylesheet string."""
    return MAIN_STYLESHEET
