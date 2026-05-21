"""Image QR form — share an image via QR code.

The user picks a local image file.  The form offers two sharing strategies:

* **Share on LAN** — starts a local HTTP server; works on the same WiFi
  network while the app is open (no external accounts or internet needed).
* **Upload Online** — uploads anonymously to a free hosting service; the URL
  works globally and survives app closure (image is public).

When a shareable URL is ready the form emits ``data_changed`` and the main
window generates the QR code pointing to that URL.
"""

from __future__ import annotations

import threading
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.exceptions import ImageShareError
from domain.validators import ImageValidator, ValidationResult
from services.image_share_service import ImageUploaderService, LocalImageServerService

_ACCEPTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}
_DROP_HINT = "⬇  Drop an image here\nor click Browse"


class _DropZone(QFrame):
    """Drag-and-drop zone that accepts image files."""

    file_dropped = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAcceptDrops(True)
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label = QLabel(_DROP_HINT)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setWordWrap(True)
        self._label.setStyleSheet("color: #3C3F52; font-size: 13px; font-weight: 500;")
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


class ImageForm(QWidget):
    """Form for creating a QR code that shares a local image.

    Implements the same interface as :class:`~widgets.forms.base_form.BaseForm`
    (``data_changed`` signal, ``validate()``, ``get_data()``, ``get_qr_data()``)
    but uses a ``QVBoxLayout`` to accommodate richer UI elements.
    """

    data_changed = Signal()

    # Internal signals for cross-thread UI updates
    _share_success = Signal(str)   # emits URL
    _share_error = Signal(str)     # emits error message

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._server_svc = LocalImageServerService()
        self._upload_svc = ImageUploaderService()
        self._current_image_path: str = ""
        self._current_url: str = ""

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(12)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._setup_ui()

        self._share_success.connect(self._on_share_success)
        self._share_error.connect(self._on_share_error)

    # ------------------------------------------------------------------
    # BaseForm interface
    # ------------------------------------------------------------------

    def get_data(self) -> dict[str, str]:
        return {"image_path": self._current_image_path, "url": self._current_url}

    def validate(self) -> ValidationResult:
        if not self._current_url:
            return ValidationResult(
                is_valid=False,
                errors={"url": "Share the image first (LAN or Online)."},
            )
        return ValidationResult(is_valid=True)

    def get_qr_data(self) -> str:
        return self._current_url

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        # ── Drop zone ────────────────────────────────────────────────────
        self._drop_zone = _DropZone()
        self._drop_zone.file_dropped.connect(self._on_image_selected)
        self._layout.addWidget(self._drop_zone)

        # ── Browse button ────────────────────────────────────────────────
        browse_row = QHBoxLayout()
        self._browse_btn = QPushButton("Browse Image…")
        self._browse_btn.setObjectName("secondaryButton")
        self._browse_btn.clicked.connect(self._on_browse)
        browse_row.addStretch()
        browse_row.addWidget(self._browse_btn)
        browse_row.addStretch()
        self._layout.addLayout(browse_row)

        # ── Thumbnail ────────────────────────────────────────────────────
        self._thumb_label = QLabel()
        self._thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb_label.setFixedHeight(100)
        self._thumb_label.hide()
        self._layout.addWidget(self._thumb_label)

        # ── File name label ──────────────────────────────────────────────
        self._file_label = QLabel()
        self._file_label.setObjectName("subtitle")
        self._file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._file_label.setWordWrap(True)
        self._file_label.hide()
        self._layout.addWidget(self._file_label)

        # ── Share buttons ────────────────────────────────────────────────
        share_row = QHBoxLayout()
        share_row.setSpacing(8)

        self._lan_btn = QPushButton("📡  Share on LAN")
        self._lan_btn.setObjectName("accentButton")
        self._lan_btn.setEnabled(False)
        self._lan_btn.clicked.connect(self._on_share_lan)
        share_row.addWidget(self._lan_btn)

        self._online_btn = QPushButton("☁  Upload Online")
        self._online_btn.setObjectName("secondaryButton")
        self._online_btn.setEnabled(False)
        self._online_btn.clicked.connect(self._on_share_online)
        share_row.addWidget(self._online_btn)

        self._layout.addLayout(share_row)

        # ── Status / URL display ─────────────────────────────────────────
        self._status_label = QLabel("Select an image, then share it to generate a QR code.")
        self._status_label.setObjectName("subtitle")
        self._status_label.setWordWrap(True)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._status_label)

        self._url_display = QLineEdit()
        self._url_display.setReadOnly(True)
        self._url_display.setPlaceholderText("Shareable URL will appear here…")
        self._url_display.hide()
        self._layout.addWidget(self._url_display)

        # ── Stop server button ───────────────────────────────────────────
        stop_row = QHBoxLayout()
        self._stop_btn = QPushButton("⏹  Stop LAN Server")
        self._stop_btn.setObjectName("secondaryButton")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._on_stop_server)
        stop_row.addStretch()
        stop_row.addWidget(self._stop_btn)
        stop_row.addStretch()
        self._layout.addLayout(stop_row)

        self._layout.addStretch()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_browse(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.gif);;All files (*)",
        )
        if path:
            self._on_image_selected(path)

    def _on_image_selected(self, path: str) -> None:
        """Handle a dropped or browsed image — reset state and show thumbnail."""
        result = ImageValidator().validate({"image_path": path})
        if not result.is_valid:
            self._show_status(" / ".join(result.errors.values()), error=True)
            return

        self._current_image_path = path
        self._current_url = ""
        self._stop_server_silently()

        # Thumbnail
        pix = QPixmap(path)
        if not pix.isNull():
            pix = pix.scaled(
                280, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._thumb_label.setPixmap(pix)
            self._thumb_label.show()
        else:
            self._thumb_label.hide()

        self._file_label.setText(f"📁  {Path(path).name}")
        self._file_label.show()
        self._lan_btn.setEnabled(True)
        self._online_btn.setEnabled(True)
        self._url_display.clear()
        self._url_display.hide()
        self._stop_btn.setEnabled(False)
        self._show_status("Image selected. Click a share button to generate the QR code.")
        self.data_changed.emit()

    def _on_share_lan(self) -> None:
        if not self._current_image_path:
            return
        self._set_sharing_buttons_enabled(False)
        self._show_status("Starting local server…")
        try:
            url = self._server_svc.start(self._current_image_path)
            self._on_share_success(url)
            self._stop_btn.setEnabled(True)
        except ImageShareError as exc:
            self._on_share_error(str(exc))

    def _on_share_online(self) -> None:
        if not self._current_image_path:
            return
        self._set_sharing_buttons_enabled(False)
        self._show_status("Uploading… this may take a moment.")
        path = self._current_image_path

        def _worker() -> None:
            try:
                url = self._upload_svc.upload(path)
                self._share_success.emit(url)
            except Exception as exc:  # noqa: BLE001
                self._share_error.emit(str(exc))

        threading.Thread(target=_worker, name="ImageUpload", daemon=True).start()

    def _on_share_success(self, url: str) -> None:
        self._current_url = url
        self._url_display.setText(url)
        self._url_display.show()
        self._show_status("✔  QR code ready! Scan to open the image.")
        self._set_sharing_buttons_enabled(True)
        self.data_changed.emit()

    def _on_share_error(self, message: str) -> None:
        self._set_sharing_buttons_enabled(True)
        self._show_status(f"⚠  {message}", error=True)

    def _on_stop_server(self) -> None:
        self._stop_server_silently()
        self._current_url = ""
        self._url_display.clear()
        self._url_display.hide()
        self._stop_btn.setEnabled(False)
        self._show_status("Server stopped. Share again to regenerate the QR code.")
        self.data_changed.emit()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _stop_server_silently(self) -> None:
        if self._server_svc.is_running:
            self._server_svc.stop()

    def _set_sharing_buttons_enabled(self, enabled: bool) -> None:
        self._lan_btn.setEnabled(enabled and bool(self._current_image_path))
        self._online_btn.setEnabled(enabled and bool(self._current_image_path))

    def _show_status(self, message: str, *, error: bool = False) -> None:
        color = "#FF5B5B" if error else "#8B8FA8"
        self._status_label.setStyleSheet(f"color: {color};")
        self._status_label.setText(message)

    def hideEvent(self, event) -> None:  # type: ignore[override]
        """Stop the LAN server when the form is hidden (type switched)."""
        super().hideEvent(event)
        # Keep the server alive — the QR code may still be in use elsewhere.
        # Users who want to stop it can click "Stop LAN Server".
