
import sys
import os

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.seed_data import initialize_database_if_needed
from ui.styles import get_stylesheet
from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow


class Application:
    """Small wrapper class that owns the QApplication lifecycle."""

    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setStyleSheet(get_stylesheet())
        self.main_window = None

    def run(self):
        splash = SplashScreen(on_finished=self._launch_main_window)
        splash.show()
        self._splash_ref = splash  
        return self.qt_app.exec_()

    def _launch_main_window(self):
        db_manager = initialize_database_if_needed(
            db_path=os.path.join("data", "skillgap.db")
        )

        self.main_window = MainWindow(db_manager)
        self.main_window.show()
        self._splash_ref.finish(self.main_window)


def main():
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
