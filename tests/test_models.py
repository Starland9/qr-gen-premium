"""Tests for domain models."""

from __future__ import annotations

from datetime import datetime

from domain.models import (
    ErrorCorrectionLevel,
    ExportConfig,
    ExportFormat,
    HistoryEntry,
    QRConfig,
    QRType,
)


class TestQRType:
    def test_all_types_present(self) -> None:
        names = {t.name for t in QRType}
        assert names == {"TEXT", "URL", "EMAIL", "PHONE", "SMS", "VCARD", "WIFI", "GEO", "IMAGE"}

    def test_values_are_strings(self) -> None:
        for t in QRType:
            assert isinstance(t.value, str)


class TestErrorCorrectionLevel:
    def test_levels(self) -> None:
        levels = {e.name for e in ErrorCorrectionLevel}
        assert levels == {"L", "M", "Q", "H"}


class TestQRConfig:
    def test_defaults(self) -> None:
        config = QRConfig()
        assert config.qr_type == QRType.TEXT
        assert config.data == ""
        assert config.fill_color == "#000000"
        assert config.back_color == "#FFFFFF"
        assert config.error_correction == ErrorCorrectionLevel.M
        assert config.logo_path is None

    def test_custom_values(self) -> None:
        config = QRConfig(
            qr_type=QRType.URL,
            data="https://example.com",
            size=400,
            fill_color="#FF0000",
        )
        assert config.qr_type == QRType.URL
        assert config.data == "https://example.com"
        assert config.size == 400
        assert config.fill_color == "#FF0000"


class TestExportConfig:
    def test_defaults(self) -> None:
        cfg = ExportConfig()
        assert cfg.format == ExportFormat.PNG
        assert cfg.filename == "qrcode"
        assert cfg.scale == 1.0


class TestHistoryEntry:
    def test_roundtrip(self) -> None:
        entry = HistoryEntry(qr_type=QRType.URL, data_preview="https://example.com")
        d = entry.to_dict()
        restored = HistoryEntry.from_dict(d)
        assert restored.id == entry.id
        assert restored.qr_type == QRType.URL
        assert restored.data_preview == "https://example.com"
        assert isinstance(restored.created_at, datetime)

    def test_auto_id(self) -> None:
        e1 = HistoryEntry(qr_type=QRType.TEXT, data_preview="hello")
        e2 = HistoryEntry(qr_type=QRType.TEXT, data_preview="world")
        assert e1.id != e2.id
