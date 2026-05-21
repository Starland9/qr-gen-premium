"""Export service for QR code images."""

from __future__ import annotations

from pathlib import Path

import qrcode
import qrcode.image.svg
from PySide6.QtGui import QImage, QGuiApplication

from core.exceptions import ExportError
from domain.models import ExportConfig, ExportFormat, QRConfig
from services.qr_generator import QRGeneratorService, _EC_MAP


class ExportService:
    """Service for exporting QR code images to various formats."""

    def __init__(self) -> None:
        self._generator = QRGeneratorService()

    def export(self, image: QImage, config: ExportConfig) -> Path:
        """Export QR code image to file, returns saved path."""
        try:
            output_dir = Path(config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            ext = config.format.value.lower()
            path = output_dir / f"{config.filename}.{ext}"
            if config.format == ExportFormat.SVG:
                raise ExportError("Use export_svg() for SVG format.")
            if config.format == ExportFormat.JPG:
                save_path = str(path)
                if not image.save(save_path, "JPEG", int(95 * config.scale)):
                    raise ExportError(f"Failed to save JPG to {path}")
            else:
                save_path = str(path)
                if not image.save(save_path, "PNG"):
                    raise ExportError(f"Failed to save PNG to {path}")
            return path
        except ExportError:
            raise
        except Exception as exc:
            raise ExportError(f"Export failed: {exc}") from exc

    def export_svg(self, qr_config: QRConfig, export_config: ExportConfig) -> Path:
        """Export as SVG using qrcode's SVG factory."""
        try:
            gen = QRGeneratorService()
            data = gen._build_qr_data(qr_config)
            output_dir = Path(export_config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            path = output_dir / f"{export_config.filename}.svg"
            factory = qrcode.image.svg.SvgPathImage
            img = qrcode.make(
                data,
                image_factory=factory,
                error_correction=_EC_MAP[qr_config.error_correction],
                box_size=qr_config.box_size,
                border=qr_config.border,
            )
            img.save(str(path))
            return path
        except Exception as exc:
            raise ExportError(f"SVG export failed: {exc}") from exc

    def copy_to_clipboard(self, image: QImage) -> None:
        """Copy QR image to system clipboard."""
        try:
            clipboard = QGuiApplication.clipboard()
            if clipboard is not None:
                clipboard.setImage(image)
        except Exception as exc:
            raise ExportError(f"Clipboard copy failed: {exc}") from exc
