"""QR code generation service.

Returns PIL Images — no Qt dependency.  The UI layer is responsible for
converting PIL Images to QImage when needed.
"""

from __future__ import annotations

import qrcode
import qrcode.constants
from PIL import Image

from core.exceptions import GenerationError
from domain.models import ErrorCorrectionLevel, QRConfig, QRType

_EC_MAP = {
    ErrorCorrectionLevel.L: qrcode.constants.ERROR_CORRECT_L,
    ErrorCorrectionLevel.M: qrcode.constants.ERROR_CORRECT_M,
    ErrorCorrectionLevel.Q: qrcode.constants.ERROR_CORRECT_Q,
    ErrorCorrectionLevel.H: qrcode.constants.ERROR_CORRECT_H,
}


class QRGeneratorService:
    """Service for generating QR code images."""

    def generate(self, config: QRConfig) -> Image.Image:
        """Generate QR code from config, returns a PIL RGBA Image."""
        try:
            data = self._build_qr_data(config)
            return self._make_pil_image(config, data)
        except Exception as exc:
            raise GenerationError(f"Failed to generate QR code: {exc}") from exc

    def generate_with_logo(self, config: QRConfig) -> Image.Image:
        """Generate QR code with centre logo overlay, returns a PIL RGBA Image."""
        try:
            data = self._build_qr_data(config)
            pil_image = self._make_pil_image(config, data)
            if config.logo_path:
                pil_image = self._overlay_logo(pil_image, config.logo_path)
            return pil_image
        except Exception as exc:
            raise GenerationError(f"Failed to generate QR code with logo: {exc}") from exc

    def _build_qr_data(self, config: QRConfig) -> str:
        """Format data string per QR type."""
        d = config.data
        match config.qr_type:
            case QRType.TEXT:
                return d
            case QRType.URL:
                return d
            case QRType.EMAIL:
                return f"mailto:{d}"
            case QRType.PHONE:
                return f"tel:{d}"
            case QRType.SMS:
                # data expected as "phone|message"
                parts = d.split("|", 1)
                phone = parts[0] if parts else d
                message = parts[1] if len(parts) > 1 else ""
                return f"SMSTO:{phone}:{message}"
            case QRType.VCARD:
                return d  # pre-formatted vCard string passed in
            case QRType.WIFI:
                # data expected as "security|ssid|password|hidden"
                parts = d.split("|")
                security = parts[0] if len(parts) > 0 else "WPA"
                ssid = parts[1] if len(parts) > 1 else ""
                password = parts[2] if len(parts) > 2 else ""
                hidden = parts[3] if len(parts) > 3 else "false"
                return f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden};;"
            case QRType.GEO:
                # data expected as "lat|lon"
                parts = d.split("|", 1)
                lat = parts[0] if parts else "0"
                lon = parts[1] if len(parts) > 1 else "0"
                return f"geo:{lat},{lon}"
            case QRType.IMAGE:
                return d  # data is a URL produced by image share service
            case _:
                return d

    def _make_pil_image(self, config: QRConfig, data: str) -> Image.Image:
        qr = qrcode.QRCode(
            version=None,
            error_correction=_EC_MAP[config.error_correction],
            box_size=config.box_size,
            border=config.border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=config.fill_color, back_color=config.back_color)
        img = img.convert("RGBA")
        img = img.resize((config.size, config.size), Image.LANCZOS)
        return img

    def _overlay_logo(self, base: Image.Image, logo_path: str) -> Image.Image:
        logo = Image.open(logo_path).convert("RGBA")
        base_w, base_h = base.size
        logo_size = int(min(base_w, base_h) * 0.2)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        pos = ((base_w - logo_size) // 2, (base_h - logo_size) // 2)
        result = base.copy()
        result.paste(logo, pos, logo)
        return result
