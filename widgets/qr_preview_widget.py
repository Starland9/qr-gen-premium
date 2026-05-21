"""QR code preview widget."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from domain.models import QRType
from services.export_service import ExportService


class QRPreviewWidget(QWidget):
    """Widget for displaying the generated QR code preview."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._export_service = ExportService()
        self._current_image: QImage | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Type badge
        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        self._badge = QLabel("TEXT")
        self._badge.setObjectName("badge")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_row.addStretch()
        badge_row.addWidget(self._badge)
        badge_row.addStretch()
        layout.addLayout(badge_row)

        # QR image area
        card = QFrame()
        card.setObjectName("card")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)

        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setMinimumSize(250, 250)
        self._image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._image_label.setText("✦  QR Preview\nwill appear here")
        self._image_label.setStyleSheet(
            "color: #3C3F52; font-size: 14px; font-weight: 500;"
        )
        card_layout.addWidget(self._image_label)
        layout.addWidget(card, stretch=1)

        # Copy button
        btn_row = QHBoxLayout()
        self._copy_btn = QPushButton("⎘  Copy to Clipboard")
        self._copy_btn.setObjectName("accentButton")
        self._copy_btn.setEnabled(False)
        self._copy_btn.clicked.connect(self._copy_to_clipboard)
        btn_row.addStretch()
        btn_row.addWidget(self._copy_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def update_preview(self, image: QImage) -> None:
        """Update the QR preview with a new image."""
        self._current_image = image
        self._copy_btn.setEnabled(True)
        self._refresh_pixmap()

    def update_badge(self, qr_type: QRType) -> None:
        """Update the type badge label."""
        self._badge.setText(qr_type.value.upper())

    def clear_preview(self) -> None:
        """Reset the preview to placeholder state."""
        self._current_image = None
        self._copy_btn.setEnabled(False)
        self._image_label.setPixmap(QPixmap())
        self._image_label.setText("✦  QR Preview\nwill appear here")
        self._image_label.setStyleSheet(
            "color: #3C3F52; font-size: 14px; font-weight: 500;"
        )

    def _refresh_pixmap(self) -> None:
        if self._current_image is None:
            return
        available = self._image_label.size()
        side = min(available.width(), available.height(), 400)
        pixmap = QPixmap.fromImage(self._current_image).scaled(
            side,
            side,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(pixmap)
        self._image_label.setText("")
        self._image_label.setStyleSheet("")

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._refresh_pixmap()

    def _copy_to_clipboard(self) -> None:
        if self._current_image is not None:
            self._export_service.copy_to_clipboard(self._current_image)
