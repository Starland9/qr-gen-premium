"""UI utility helpers — Qt-specific conversions kept out of the service layer."""

from __future__ import annotations

from PIL import Image
from PySide6.QtGui import QGuiApplication, QImage

from core.exceptions import ExportError


def pil_to_qimage(pil_image: Image.Image) -> QImage:
    """Convert a PIL RGBA Image to a PySide6 QImage.

    The returned QImage owns its data (via .copy()), so it is safe to use
    after the source PIL image has been garbage-collected.
    """
    rgba = pil_image.convert("RGBA")
    raw = rgba.tobytes("raw", "RGBA")
    qimage = QImage(raw, rgba.width, rgba.height, QImage.Format.Format_RGBA8888)
    return qimage.copy()


def copy_to_clipboard(qimage: QImage) -> None:
    """Copy a QImage to the system clipboard."""
    try:
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setImage(qimage)
    except Exception as exc:
        raise ExportError(f"Clipboard copy failed: {exc}") from exc
