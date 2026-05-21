"""Export service for QR code images.

This service operates on PIL Images so it has no Qt dependency.  Clipboard
copy is the only operation that requires a QImage and must be called from
the UI layer after conversion.
"""

from __future__ import annotations

from pathlib import Path

import qrcode
import qrcode.image.svg
from PIL import Image

from core.exceptions import ExportError
from domain.models import ExportConfig, ExportFormat, QRConfig
from services.qr_generator import _EC_MAP, QRGeneratorService


class ExportService:
    """Service for exporting QR code images to various formats."""

    def __init__(self) -> None:
        self._generator = QRGeneratorService()

    def export(self, pil_image: Image.Image, config: ExportConfig) -> Path:
        """Export a PIL Image to file and return the saved path."""
        try:
            if config.format == ExportFormat.SVG:
                raise ExportError("Use export_svg() for SVG format.")
            output_dir = Path(config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            ext = config.format.value.lower()
            path = output_dir / f"{config.filename}.{ext}"
            if config.format == ExportFormat.JPG:
                rgb_image = pil_image.convert("RGB")
                rgb_image.save(str(path), "JPEG", quality=95)
            else:
                pil_image.convert("RGBA").save(str(path), "PNG")
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
