"""
splash_screen.py
-----------------
A simple animated splash screen shown while the application initializes
the database. Gives the app a professional, polished first impression.
"""

from PyQt5.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor


class SplashScreen(QSplashScreen):
    """
    Custom splash screen with the app name, a tagline, and an animated
    progress bar. It calls `on_finished` once loading is complete.
    """

    def __init__(self, on_finished):
        # Build a solid-color pixmap as the background canvas
        pixmap = QPixmap(560, 340)
        pixmap.fill(QColor("#161925"))
        super().__init__(pixmap)

        self.on_finished = on_finished
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self._build_ui()

        self._progress_value = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_progress)
        self._timer.start(35)

    def _build_ui(self):
        """Builds the label/progress-bar overlay on top of the splash pixmap."""
        container = QWidget(self)
        container.setGeometry(0, 0, 560, 340)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(50, 90, 50, 50)
        layout.setSpacing(14)

        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 52px;")
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Employee Skills Gap Analyzer")
        title_label.setStyleSheet(
            "color: #ffffff; font-size: 24px; font-weight: 700;"
        )
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("HR Analytics & Workforce Readiness Platform")
        subtitle_label.setStyleSheet("color: #9ca3b5; font-size: 13px;")
        subtitle_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #232838;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Initializing database...")
        self.status_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        container.show()

    def _update_progress(self):
        """Advances the fake progress bar and updates status text."""
        self._progress_value += 4
        self.progress_bar.setValue(min(self._progress_value, 100))

        if self._progress_value < 40:
            self.status_label.setText("Initializing database...")
        elif self._progress_value < 75:
            self.status_label.setText("Loading employee & skill records...")
        elif self._progress_value < 100:
            self.status_label.setText("Preparing dashboard...")
        else:
            self.status_label.setText("Ready.")

        if self._progress_value >= 100:
            self._timer.stop()
            QTimer.singleShot(200, self.on_finished)
