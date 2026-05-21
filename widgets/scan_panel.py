"""Scan panel — decode QR codes from image files.

Provides a drag-and-drop / browse drop-zone, displays the decoded results,
and offers a "Use as text input" shortcut that emits the first decoded string
back to the generator.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.exceptions import DecodeError
from domain.models import DecodeResult
from services.qr_decoder import QRDecoderService

_ACCEPTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}

_DROP_HINT = "⬇  Drop an image here\nor click to browse"
_DROP_HINT_STYLE = "color: #3C3F52; font-size: 13px; font-weight: 500; qproperty-alignment: AlignCenter;"


class _DropZone(QFrame):
    """Drag-and-drop target that accepts image files."""

    file_dropped = Signal(str)  # emits absolute file path

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAcceptDrops(True)
        self.setMinimumHeight(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel(_DROP_HINT)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setWordWrap(True)
        self._label.setStyleSheet(_DROP_HINT_STYLE)
        layout.addWidget(self._label)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # type: ignore[override]
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            if Path(path).suffix.lower() in _ACCEPTED_EXTENSIONS:
                event.acceptProposedAction()
                self._set_active(True)
                return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:  # type: ignore[override]
        self._set_active(False)

    def dropEvent(self, event: QDropEvent) -> None:  # type: ignore[override]
        self._set_active(False)
        path = event.mimeData().urls()[0].toLocalFile()
        self.file_dropped.emit(path)

    def _set_active(self, active: bool) -> None:
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)


class _ResultCard(QFrame):
    """Compact card showing a single decoded result with a copy/use button."""

    use_requested = Signal(str)  # emits the decoded text

    def __init__(self, result: DecodeResult, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._setup_ui(result)

    def _setup_ui(self, result: DecodeResult) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Format badge + text row
        top_row = QHBoxLayout()
        badge = QLabel(result.format)
        badge.setObjectName("badge")
        top_row.addWidget(badge)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Decoded text
        text_label = QLabel(result.text)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        text_label.setObjectName("decodedText")
        layout.addWidget(text_label)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        use_btn = QPushButton("Use as input")
        use_btn.setObjectName("accentButton")
        use_btn.setFixedHeight(28)
        use_btn.clicked.connect(lambda: self.use_requested.emit(result.text))
        btn_row.addWidget(use_btn)
        layout.addLayout(btn_row)


class ScanPanel(QWidget):
    """Full panel for QR code scanning from image files.

    Emits:
        scan_text_selected(str): User clicked "Use as input" for a result;
                                 the main window should pre-fill the Text form.
    """

    scan_text_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._decoder = QRDecoderService()
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 16)
        outer.setSpacing(12)

        # Header
        header = QLabel("Scan QR from Image")
        header.setObjectName("sectionTitle")
        outer.addWidget(header)

        # Sub-header hint
        hint = QLabel("Drop a PNG / JPG / BMP / WEBP image or click Browse.")
        hint.setObjectName("subtitle")
        hint.setWordWrap(True)
        outer.addWidget(hint)

        # Drop zone
        self._drop_zone = _DropZone()
        self._drop_zone.file_dropped.connect(self._on_file_received)
        outer.addWidget(self._drop_zone)

        # Browse button
        browse_row = QHBoxLayout()
        self._browse_btn = QPushButton("Browse Image…")
        self._browse_btn.setObjectName("secondaryButton")
        self._browse_btn.clicked.connect(self._on_browse)
        browse_row.addStretch()
        browse_row.addWidget(self._browse_btn)
        browse_row.addStretch()
        outer.addLayout(browse_row)

        # Thumbnail
        self._thumb_label = QLabel()
        self._thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb_label.setFixedHeight(120)
        self._thumb_label.hide()
        outer.addWidget(self._thumb_label)

        # Status label
        self._status_label = QLabel()
        self._status_label.setObjectName("subtitle")
        self._status_label.setWordWrap(True)
        self._status_label.hide()
        outer.addWidget(self._status_label)

        # Results scroll area
        self._results_area = QScrollArea()
        self._results_area.setWidgetResizable(True)
        self._results_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self._results_area.hide()

        self._results_container = QWidget()
        self._results_layout = QVBoxLayout(self._results_container)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(8)
        self._results_area.setWidget(self._results_container)
        outer.addWidget(self._results_area, stretch=1)

        outer.addStretch()

    def _on_browse(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.gif);;All files (*)",
        )
        if path:
            self._on_file_received(path)

    def _on_file_received(self, path: str) -> None:
        """Handle a dropped or browsed image file."""
        self._show_thumbnail(path)
        self._clear_results()
        try:
            results = self._decoder.decode(path)
        except DecodeError as exc:
            self._show_status(f"⚠  {exc}", error=True)
            return
        if not results:
            self._show_status("No QR code found in this image.", error=False)
            return
        self._show_results(results)

    def _show_thumbnail(self, path: str) -> None:
        pix = QPixmap(path)
        if not pix.isNull():
            pix = pix.scaled(
                300, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._thumb_label.setPixmap(pix)
            self._thumb_label.show()
        else:
            self._thumb_label.hide()

    def _show_status(self, message: str, *, error: bool) -> None:
        color = "#FF5B5B" if error else "#8B8FA8"
        self._status_label.setStyleSheet(f"color: {color};")
        self._status_label.setText(message)
        self._status_label.show()
        self._results_area.hide()

    def _clear_results(self) -> None:
        self._status_label.hide()
        self._results_area.hide()
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_results(self, results: list[DecodeResult]) -> None:
        self._status_label.hide()
        for result in results:
            card = _ResultCard(result)
            card.use_requested.connect(self.scan_text_selected)
            self._results_layout.addWidget(card)
        self._results_layout.addStretch()
        self._results_area.show()
