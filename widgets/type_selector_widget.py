"""QR type selector with pill buttons."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QScrollArea, QWidget

from domain.models import QRType


class TypeSelectorWidget(QWidget):
    """Horizontal pill-button row for selecting QR code type."""

    type_changed = Signal(object)  # emits QRType

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._buttons: dict[QRType, QPushButton] = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(False)
        self._current = QRType.TEXT
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(50)
        scroll.setFrameShape(scroll.frameShape().NoFrame)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(6)

        for qr_type in QRType:
            btn = QPushButton(qr_type.value)
            btn.setObjectName("pillButton")
            btn.setCheckable(False)
            btn.clicked.connect(lambda checked, t=qr_type: self._select(t))
            self._buttons[qr_type] = btn
            layout.addWidget(btn)

        layout.addStretch()
        scroll.setWidget(container)
        outer_layout.addWidget(scroll)
        self._select(QRType.TEXT)

    def _select(self, qr_type: QRType) -> None:
        """Select a QR type and update button styles."""
        self._current = qr_type
        for t, btn in self._buttons.items():
            btn.setProperty("selected", t == qr_type)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.type_changed.emit(qr_type)

    def select(self, qr_type: QRType) -> None:
        """Programmatically select a QR type (same as clicking the button)."""
        self._select(qr_type)

    def current_type(self) -> QRType:
        """Return the currently selected QR type."""
        return self._current
