"""Toast notification widget."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QTimer, Qt
from PySide6.QtWidgets import QLabel, QWidget

_LEVEL_STYLES = {
    "success": "background-color: #1A3B2A; color: #4CAF82; border: 1px solid #4CAF82;",
    "error": "background-color: #3B1A1A; color: #FF5B5B; border: 1px solid #FF5B5B;",
    "info": "background-color: #1A1A3B; color: #6C63FF; border: 1px solid #6C63FF;",
    "warning": "background-color: #3B2E1A; color: #FFB347; border: 1px solid #FFB347;",
}


class NotificationWidget(QLabel):
    """Slide-in toast notification."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setContentsMargins(16, 10, 16, 10)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet(
            "border-radius: 10px; font-size: 13px; font-weight: 500; padding: 10px 16px;"
        )
        self.hide()
        self._anim_in = QPropertyAnimation(self, b"geometry")
        self._anim_in.setDuration(300)
        self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_out = QPropertyAnimation(self, b"geometry")
        self._anim_out.setDuration(250)
        self._anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim_out.finished.connect(self.hide)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._slide_out)

    def show_message(self, message: str, level: str = "success") -> None:
        """Display a toast message."""
        self._timer.stop()
        style = _LEVEL_STYLES.get(level, _LEVEL_STYLES["info"])
        self.setStyleSheet(
            f"{style} border-radius: 10px; font-size: 13px; font-weight: 500; padding: 10px 16px;"
        )
        self.setText(message)
        self.adjustSize()
        if self.parent():
            parent_w = self.parent().width()  # type: ignore[union-attr]
            x = parent_w - self.width() - 16
            end_y = 16
            start_y = -self.height() - 10
            self.setGeometry(QRect(x, start_y, self.width(), self.height()))
            self.show()
            self.raise_()
            self._anim_in.setStartValue(QRect(x, start_y, self.width(), self.height()))
            self._anim_in.setEndValue(QRect(x, end_y, self.width(), self.height()))
            self._anim_in.start()
            self._timer.start(3000)

    def _slide_out(self) -> None:
        if self.parent():
            parent_w = self.parent().width()  # type: ignore[union-attr]
            x = parent_w - self.width() - 16
            end_y = -self.height() - 10
            self._anim_out.setStartValue(self.geometry())
            self._anim_out.setEndValue(QRect(x, end_y, self.width(), self.height()))
            self._anim_out.start()
