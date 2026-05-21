"""Tests for QR code generator service."""

from __future__ import annotations

import pytest
from PIL import Image

from domain.models import ErrorCorrectionLevel, QRConfig, QRType
from services.qr_generator import QRGeneratorService


@pytest.fixture
def generator() -> QRGeneratorService:
    return QRGeneratorService()


class TestBuildQrData:
    def test_text(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.TEXT, data="Hello")
        assert generator._build_qr_data(config) == "Hello"

    def test_url(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.URL, data="https://example.com")
        assert generator._build_qr_data(config) == "https://example.com"

    def test_email(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.EMAIL, data="user@example.com")
        assert generator._build_qr_data(config) == "mailto:user@example.com"

    def test_phone(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.PHONE, data="+15551234567")
        assert generator._build_qr_data(config) == "tel:+15551234567"

    def test_sms(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.SMS, data="+15551234567|Hello there")
        result = generator._build_qr_data(config)
        assert result == "SMSTO:+15551234567:Hello there"

    def test_wifi(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.WIFI, data="WPA|MyNet|secret|false")
        result = generator._build_qr_data(config)
        assert "WIFI:" in result
        assert "MyNet" in result

    def test_geo(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.GEO, data="37.7749|-122.4194")
        result = generator._build_qr_data(config)
        assert result == "geo:37.7749,-122.4194"


class TestGenerate:
    """Tests for generate() — returns a PIL Image, no Qt dependency."""

    def test_returns_pil_image(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.TEXT, data="Test QR")
        image = generator.generate(config)
        assert isinstance(image, Image.Image)

    def test_size_respected(self, generator: QRGeneratorService) -> None:
        config = QRConfig(qr_type=QRType.TEXT, data="Size test", size=200)
        image = generator.generate(config)
        assert image.width == 200
        assert image.height == 200

    def test_error_correction_h(self, generator: QRGeneratorService) -> None:
        config = QRConfig(
            qr_type=QRType.URL,
            data="https://example.com",
            error_correction=ErrorCorrectionLevel.H,
        )
        image = generator.generate(config)
        assert image.width > 0
