"""Tests for the QR code decoder service."""

from __future__ import annotations

from pathlib import Path

import pytest

from domain.models import DecodeResult, QRConfig, QRType
from services.qr_decoder import QRDecoderService
from services.qr_generator import QRGeneratorService


@pytest.fixture
def decoder() -> QRDecoderService:
    return QRDecoderService()


@pytest.fixture
def generator() -> QRGeneratorService:
    return QRGeneratorService()


class TestQRDecoderFromPilImage:
    """Round-trip tests: generate a QR code then decode it from a PIL Image."""

    def test_decode_text(self, decoder: QRDecoderService, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.TEXT, data="Hello decoder")
        pil_image = generator.generate(config)
        results = decoder.decode_pil(pil_image, source_path="test")
        assert len(results) >= 1
        assert results[0].text == "Hello decoder"

    def test_decode_url(self, decoder: QRDecoderService, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.URL, data="https://example.com")
        pil_image = generator.generate(config)
        results = decoder.decode_pil(pil_image)
        assert results[0].text == "https://example.com"

    def test_decode_returns_list_of_decode_result(
        self, decoder: QRDecoderService, generator: QRGeneratorService
    ) -> None:
        config = QRConfig(qr_type=QRType.TEXT, data="test")
        pil_image = generator.generate(config)
        results = decoder.decode_pil(pil_image)
        assert all(isinstance(r, DecodeResult) for r in results)

    def test_decode_result_has_format(
        self, decoder: QRDecoderService, generator: QRGeneratorService
    ) -> None:
        config = QRConfig(qr_type=QRType.TEXT, data="format check")
        pil_image = generator.generate(config)
        results = decoder.decode_pil(pil_image)
        assert results[0].format  # non-empty string

    def test_source_path_stored(
        self, decoder: QRDecoderService, generator: QRGeneratorService
    ) -> None:
        config = QRConfig(qr_type=QRType.TEXT, data="path test")
        pil_image = generator.generate(config)
        results = decoder.decode_pil(pil_image, source_path="/some/image.png")
        assert results[0].source_path == "/some/image.png"

    def test_empty_image_returns_empty_list(self, decoder: QRDecoderService) -> None:
        from PIL import Image

        blank = Image.new("RGB", (200, 200), color=(255, 255, 255))
        results = decoder.decode_pil(blank)
        assert results == []


class TestQRDecoderFromFile:
    """Tests that decode from an actual image file on disk."""

    def test_decode_from_png_file(
        self,
        decoder: QRDecoderService,
        generator: QRGeneratorService,
        tmp_path: Path,
    ) -> None:
        config = QRConfig(qr_type=QRType.TEXT, data="file decode test")
        pil_image = generator.generate(config)
        img_path = tmp_path / "test_qr.png"
        pil_image.save(str(img_path), "PNG")

        results = decoder.decode(img_path)
        assert len(results) >= 1
        assert results[0].text == "file decode test"

    def test_missing_file_raises_decode_error(self, decoder: QRDecoderService) -> None:
        from core.exceptions import DecodeError

        with pytest.raises(DecodeError, match="not found"):
            decoder.decode("/nonexistent/path/image.png")
