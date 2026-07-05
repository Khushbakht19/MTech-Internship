"""
widgets.py
----------
Small, reusable custom widgets shared across multiple pages of the
application (statistic cards, embedded matplotlib charts, colored
classification badges, progress bars for tables).

Centralizing these avoids duplicated code across dashboard.py,
department_analytics.py, gap_analysis.py, etc.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import Qt

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Matplotlib global style tuned to match the dark blue theme of the app
DARK_BG = "#232838"
TEXT_COLOR = "#e8eaf0"
GRID_COLOR = "#333b52"
ACCENT_PALETTE = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#a855f7", "#06b6d4"]


class StatCard(QFrame):
    """
    A single KPI card for the dashboard, e.g. "Total Employees: 20".
    Shows an icon/emoji, a title, and a big value.
    """

    def __init__(self, icon, title, value, accent_color="#3b82f6", parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)

        text_col = QVBoxLayout()
        text_col.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("StatCardTitle")

        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("StatCardValue")

        text_col.addWidget(title_label)
        text_col.addWidget(self.value_label)
        text_col.addStretch()

        icon_label = QLabel(icon)
        icon_label.setObjectName("StatCardIcon")
        icon_label.setFixedSize(52, 52)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {accent_color}33;
            border-radius: 14px;
            font-size: 24px;
        """)

        outer.addLayout(text_col, stretch=1)
        outer.addWidget(icon_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class ChartCard(QFrame):
    """
    A card container that wraps a matplotlib chart plus a title, used
    on the Dashboard and Department Analytics pages.
    """

    def __init__(self, title, figsize=(5, 3.4), parent=None):
        super().__init__(parent)
        self.setObjectName("ChartCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("SectionHeader")
        layout.addWidget(title_label)

        self.figure = Figure(figsize=figsize, facecolor=DARK_BG)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.canvas)

    def get_axes(self):
        """Clears the figure and returns a fresh axes object styled for dark mode."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(DARK_BG)
        ax.tick_params(colors=TEXT_COLOR, labelsize=8)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)
        ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.5)
        return ax

    def refresh(self):
        self.figure.tight_layout()
        self.canvas.draw()


def classification_color(classification):
    """Returns a hex color representing the severity of a classification label."""
    mapping = {
        "Expert / Fully Ready": "#22c55e",
        "Proficient": "#3b82f6",
        "Developing": "#f59e0b",
        "Needs Training": "#f97316",
        "Critical Gap": "#ef4444",
    }
    return mapping.get(classification, "#9ca3b5")


def make_colored_badge(text, color):
    """Returns a small QLabel styled as a colored rounded badge (for tables)."""
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(f"""
        background-color: {color}33;
        color: {color};
        border-radius: 8px;
        padding: 4px 10px;
        font-weight: 600;
        font-size: 11px;
    """)
    return label


def make_readiness_progress_bar(value):
    """Returns a QProgressBar colored according to the readiness score value."""
    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(int(value))
    bar.setTextVisible(True)
    bar.setFormat(f"{value:.0f}%")

    if value >= 90:
        color = "#22c55e"
    elif value >= 75:
        color = "#3b82f6"
    elif value >= 60:
        color = "#f59e0b"
    elif value >= 40:
        color = "#f97316"
    else:
        color = "#ef4444"

    bar.setStyleSheet(f"""
        QProgressBar {{
            background-color: #2c3347;
            border-radius: 8px;
            text-align: center;
            color: #ffffff;
            font-weight: 600;
        }}
        QProgressBar::chunk {{
            background-color: {color};
            border-radius: 8px;
        }}
    """)
    return bar
