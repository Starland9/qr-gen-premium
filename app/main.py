"""Application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from core.config import APP_NAME, APP_VERSION
from ui.main_window import MainWindow
from ui.styles.theme import ThemeManager


def main() -> None:
    """Launch the QR Gen Premium application."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    ThemeManager.apply_dark(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
