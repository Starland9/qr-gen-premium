"""QR code decoder service.

Decodes QR (and other barcode) data from image files using zxing-cpp.
No Qt dependency — operates entirely on PIL Images and plain Python types.
"""

from __future__ import annotations

from pathlib import Path

import zxingcpp
from PIL import Image

from core.exceptions import DecodeError
from domain.models import DecodeResult


class QRDecoderService:
    """Service for reading QR codes embedded in image files."""

    def decode(self, image_path: str | Path) -> list[DecodeResult]:
        """Decode all QR / barcode symbols found in *image_path*.

        Args:
            image_path: Path to a PNG, JPG, BMP, GIF, or WEBP image.

        Returns:
            A list of :class:`DecodeResult` (one entry per symbol found).
            Returns an empty list if no symbols are detected.

        Raises:
            DecodeError: If the file cannot be opened or the decoding
                         pipeline raises an unexpected error.
        """
        path = Path(image_path)
        if not path.exists():
            raise DecodeError(f"Image file not found: {path}")
        try:
            pil_image = Image.open(path).convert("RGB")
            return self._decode_image(pil_image, str(path))
        except DecodeError:
            raise
        except Exception as exc:
            raise DecodeError(f"Failed to decode image '{path.name}': {exc}") from exc

    def decode_pil(self, pil_image: Image.Image, source_path: str = "") -> list[DecodeResult]:
        """Decode all QR / barcode symbols from an already-loaded PIL Image.

        Useful when the caller already holds a PIL Image in memory (e.g. a
        frame grabbed from a camera feed or a freshly generated QR code used
        in round-trip tests).

        Args:
            pil_image: A PIL Image in any mode (will be converted to RGB).
            source_path: Optional label stored in each :class:`DecodeResult`.

        Returns:
            A list of :class:`DecodeResult` instances.
        """
        try:
            rgb = pil_image.convert("RGB")
            return self._decode_image(rgb, source_path)
        except DecodeError:
            raise
        except Exception as exc:
            raise DecodeError(f"Failed to decode PIL image: {exc}") from exc

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _decode_image(self, rgb_image: Image.Image, source_path: str) -> list[DecodeResult]:
        """Run zxingcpp on *rgb_image* and wrap results in :class:`DecodeResult`."""
        hits = zxingcpp.read_barcodes(rgb_image)
        return [
            DecodeResult(
                text=hit.text,
                format=str(hit.format).replace("BarcodeFormat.", ""),
                source_path=source_path,
            )
            for hit in hits
        ]
